# src/flashcard_service/flashcard_generator_service/flashcard_generator.py
import os
import time

import openai
import structlog
from typing import List, Optional, Callable

import tiktoken
from dependency_injector.wiring import inject, Provide
from openai import OpenAI
from openai.types.chat import ChatCompletion

from src.enums.generatorOptions import GeneratorMode, SupportedLanguage
from src.utils.path_util import get_system_prompt_path, get_example_prompt_path, get_additional_prompt_path
from src.custom_exceptions.internal_exceptions import PromptSizeError
from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.entities.completion_messages.completion_messages import Messages
from src.entities.flashcard.flashcard import Flashcard
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck
from src.container import Container
from src.services.flashcard_service.flashcard_generator_service.flashcard_generator_interface import IFlashcardGenerator
from src.services.flashcard_service.flashcard_generator_service.flashcard_parsing import parse_flashcards
from src.services.flashcard_service.flashcard_generator_service.quizard_config import QuizardConfig

from src.utils.file_util import read_file
from src.utils.formatting_util import format_num, inset_into_string

logger = structlog.getLogger(__name__)


class FlashcardGenerator(IFlashcardGenerator):
    """
    A class to generate flashcards using the OpenAI GPT model.

    Parameters
    ----------
    client : OpenAI
        The OpenAI client object.

    Attributes
    ----------
    client : OpenAI
        The OpenAI client object.
    model_config : dict
        A dictionary containing model configuration parameters.
    text_splitting_config: dict
        ...
    """

    @inject
    def __init__(self, client=Provide[Container.openai_client]):
        self.client = client
        self.model_config = QuizardConfig.get_model_config()
        self.text_splitting_config = QuizardConfig.get_text_splitting_config()
        self.token_limits = QuizardConfig.get_token_limits()
        self.prompt_config = QuizardConfig.get_prompt_config()

    def generate_flashcard_deck(self, flashcards_generator_task: FlashcardGeneratorTaskDto, fn_update_progress: Optional[Callable], *args,
                                **kwargs) -> FlashcardDeck:
        """
        Generate flashcards based on input.
        Parameters
        ----------
        flashcards_generator_task: FlashcardGeneratorTaskDto
            The DTO containing the parameters for generating flashcards including language, mode, export format, and input.
        fn_update_progress: Optional[Callable]
            Optional callback function to update the caller about the current progress of the generation process.
            Takes in two arguments: current batch and total number of batches.
        args
        kwargs
        Returns
        -------
        FlashcardDeck
            The generated flashcards.
        """

        # Load the prompts
        (system_prompt,
         example_user_prompt,
         example_assistant_prompt,
         additional_prompt) = load_prompts(self.prompt_config, flashcards_generator_task.mode, flashcards_generator_task.lang)

        app_token_limit = self.token_limits['app_limit']
        prompt_token_limit = self.token_limits['prompt_limit']
        completion_token_limit = self.token_limits['completion_limit']

        encoding = tiktoken.encoding_for_model(self.model_config['model_name'])

        # Estimate prompt tokes
        prompt_tokens = calculate_prompt_tokens(encoding, system_prompt, example_user_prompt, example_assistant_prompt, additional_prompt,
                                                prompt_token_limit)
        # Add an instruction at the top of the input text.
        modified_input_text = inset_into_string(insert=additional_prompt, target=flashcards_generator_task.input_text, position=0)

        # Initialize messages sent to OpenAI API
        messages = Messages(
            system=system_prompt,
            example_user=example_user_prompt,
            example_assistant=example_assistant_prompt,
            input_text=modified_input_text
        )

        # Log start time
        start_time = time.time()
        logger.info(
            "Flashcard generation started",
            generation_mode=flashcards_generator_task.mode,
            language=flashcards_generator_task.lang,
            token_est=format_num(messages.compute_input_tokens(encoding=encoding))
        )
        # Compute total tokens of the messages
        total_message_tokens = messages.compute_total_tokens(encoding=encoding)

        # Empty flashcard list to store generated flashcards
        flashcards: List[Flashcard] = []

        # For short texts generate the flashcards in a single run
        if total_message_tokens < app_token_limit:
            if fn_update_progress:
                # Set progress to 0
                fn_update_progress(0, 1)

            completion = self.make_gpt_completion_request(messages=messages, max_tokens=completion_token_limit)
            receive_time_sec = round(time.time(), 3)
            log_completion_metrics(completion, receive_time_sec)

            completion_message_content = completion.choices[0].message.content
            flashcards += parse_flashcards(completion_message_content)
            if fn_update_progress:
                fn_update_progress(1, 1)

        # For longer texts, splut the text into fragments and generate flashcards in multiple batches
        else:
            # Split the text into fragments
            fragment_size = app_token_limit - (prompt_tokens + completion_token_limit)
            fragment_list = split_text(
                encoding=encoding,
                text=modified_input_text,
                fragment_size=fragment_size,
                overlap_type=self.text_splitting_config['overlap_type'],
                overlap=self.text_splitting_config['overlap']
            )

            if fn_update_progress:
                # Set progress to 0
                fn_update_progress(0, len(fragment_list))

            total_batch_num = len(fragment_list)
            for batch in range(total_batch_num):
                modified_input_text = inset_into_string(additional_prompt, fragment_list[batch], 0)
                # Generate a new Message for the new shorter fragment
                new_message = Messages(
                    system=system_prompt,
                    example_user=example_user_prompt,
                    example_assistant=example_assistant_prompt,
                    input_text=modified_input_text
                )

                completion = self.make_gpt_completion_request(
                    messages=new_message,
                    max_tokens=completion_token_limit
                )
                receive_time_sec = round(time.time(), 3)
                log_completion_metrics(completion, receive_time_sec, batch)
                completion_message_content = completion.choices[0].message.content

                start_id = len(flashcards) + 1
                flashcards += parse_flashcards(completion_message_content, start_id, batch)
                if fn_update_progress:
                    fn_update_progress(batch + 1, len(fragment_list))

        # Log end time
        end_time = time.time()
        logger.info("Flashcard generation completed", total_flashcards=len(flashcards), duration=round(end_time - start_time, 3), )
        flashcard_deck = FlashcardDeck(flashcards)
        return flashcard_deck

    def make_gpt_completion_request(self, messages: Messages, max_tokens: int) \
            -> ChatCompletion:
        """
        Make a GPT completion request to the OpenAI API.

        Parameters
        ----------
        messages : Messages
            A Messages object containing the input message sequence.
        max_tokens : int
            The maximum number of tokens to generate.

        Returns
        -------
        ChatCompletion
            The completion response from the OpenAI API.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_config["model_name"],
                messages=messages.as_message_list(),
                max_tokens=max_tokens,
                temperature=self.model_config.get("temperature", 0.7),
                top_p=self.model_config.get("top_p", 1.0),
                frequency_penalty=self.model_config.get("frequency_penalty", 0.0),
                presence_penalty=self.model_config.get("presence_penalty", 0.0)
            )
            return response
        except openai.BadRequestError as e:
            # Handle error 400
            logger.error("OpenAI API Error occurred", error=f"Error 400: {e}")
            raise
        except openai.AuthenticationError as e:
            # Handle error 401
            logger.error("OpenAI API Error occurred", error=f"Error 401: {e}")
            raise
        except openai.PermissionDeniedError as e:
            # Handle error 403
            logger.error("OpenAI API Error occurred", error=f"Error 403: {e}")
            raise
        except openai.NotFoundError as e:
            # Handle error 404
            logger.error("OpenAI API Error occurred", error=f"Error 404: {e}")
            raise
        except openai.UnprocessableEntityError as e:
            # Handle error 422
            logger.error("OpenAI API Error occurred", error=f"Error 422: {e}")
            raise
        except openai.RateLimitError as e:
            # Handle error 429
            logger.error("OpenAI API Error occurred", error=f"Error 429: {e}")
            raise
        except openai.InternalServerError as e:
            # Handle error >=500
            logger.error("OpenAI API Error occurred", error=f"Error >=500: {e}")
            raise
        except openai.APIConnectionError as e:
            # Handle API connection error
            logger.error("OpenAI API Error occurred", error=f"API connection error: {e}")
            raise


def log_completion_metrics(completion: openai.Completion, receive_time_sec: float, batch_number: Optional[int] = None):
    """
    Logs the metrics of a completion response, including optional batch information.

    Parameters
    ----------
    completion : openai.Completion
        The completion response from the OpenAI API.
    receive_time_sec : float
        The time at which the completion was received.
    batch_number : Optional[int], optional
        The batch number in the context of multiple batch processing, by default None.
    """
    response_time_sec = round(receive_time_sec - completion.created, 3)
    logger.info(
        "Completion metrics logged",
        response_time_sec=response_time_sec,
        completion_tokens=format_num(completion.usage.completion_tokens),
        total_tokens=format_num(completion.usage.total_tokens),
        batch=batch_number if batch_number is not None else 'N/A'
    )


def load_prompts(prompt_config: dict, generation_mode: GeneratorMode, lang: SupportedLanguage) -> (str, str, str, str):
    """
    Initializes the message components for the OpenAI API request.
    """
    example_prompt_name = prompt_config.get('example_prompt')
    additional_prompt_name = prompt_config.get('additional_prompt')

    system_prompt = read_file(get_system_prompt_path(generation_mode, lang))
    example_user_prompt = read_file(get_example_prompt_path(example_prompt_name, 'user', lang))
    example_assistant_prompt = read_file(get_example_prompt_path(example_prompt_name, 'assistant', lang))
    additional_prompt = read_file(get_additional_prompt_path(additional_prompt_name, lang))

    return system_prompt, example_user_prompt, example_assistant_prompt, additional_prompt


def calculate_prompt_tokens(encoding: tiktoken.Encoding, system_prompt: str, example_user: str, example_assistant: str,
                            additional_prompt: str, prompt_token_limit: int) -> int:
    """
    Calculate the total tokens of the prompts given the prompts components.

    Raises
    ------
    PromptSizeError
        If the prompts exceeds the token limit.
    """
    prompt_tokens = len(encoding.encode(system_prompt + example_user + example_assistant + additional_prompt))
    try:
        validate_prompt_size(prompt_tokens, prompt_token_limit)
    except PromptSizeError as e:
        logger.error(
            "Invalid Prompt Size of Prepared Prompt",
            error=e,
            prompt_tokens=prompt_tokens,
            prompt_token_limit=prompt_token_limit
        )
        raise
    return prompt_tokens


def validate_prompt_size(prompt_size: int, prompt_token_limit: int):
    """
    Validates the size of the prompts against the given token limit.

    Raises
    ------
    ValidationError
        If the prompts exceeds the token limit.
    """
    if prompt_size > prompt_token_limit:
        raise PromptSizeError(f"Prompt size of {format_num(prompt_size)} exceeds set prompts token limit.")


def split_text(encoding: tiktoken.Encoding, text: str, fragment_size: int, overlap_type: str, overlap: float) -> List[str]:
    """
    Split a given text into fragments based on specified encoding, fragment size, and overlap settings.

    Parameters
    ----------
    encoding : tiktoken.Encoding
        Encoding object for the desired model.
    text : str
        Text to be split into fragments.
    fragment_size : int
        Size of each text fragment in tokens.
    overlap_type : str
        Type of overlap ('absolute' or 'relative') used in text splitting.
    overlap : float
        Value of overlap. Interpreted as absolute or relative based on overlap_type.

    Returns
    -------
    List[str]
        List of text fragments.

    Raises
    ------
    ConfigInvalidValueError
        If the overlap type is neither 'absolute' nor 'relative'.
    """
    if overlap_type == 'absolute':
        abs_overlap = overlap
    elif overlap_type == 'relative':
        abs_overlap = fragment_size * overlap

    encoded_text = encoding.encode(text)
    fragments = []

    current_start = 0
    while current_start < len(encoded_text):
        current_end = current_start + fragment_size
        current_fragment = encoded_text[current_start:current_end]
        fragments.append(encoding.decode(current_fragment))
        current_start += int(fragment_size - abs_overlap)

    return fragments
