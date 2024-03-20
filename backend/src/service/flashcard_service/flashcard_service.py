# src/flashcard_service/flashcard_service.py
import structlog
import os
import time
from typing import List, Optional, Callable

import tiktoken
from openai import OpenAI, OpenAIError

from src.entities.flashcard.flashcard import Flashcard
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck
from src.service.flashcard_service.flashcard_generator.flashcard_generator import FlashcardGenerator
from src.service.flashcard_service.text_splitting import text_split
from src.entities.completion_messages.completion_messages import Messages
from src.utils.global_helpers import format_num, inset_into_string, read_file, validate_config_param
from src.custom_exceptions.quizard_exceptions import PromptSizeError, ConfigInvalidValueError

logger = structlog.getLogger(__name__)


def load_message_components(backend_root_dir: str, app_config: dict, generation_mode: str, lang: str) -> (str, str, str, str):
    """
    Initializes the message components for the OpenAI API request.
    """
    try:
        system_prompt_path = os.path.join(backend_root_dir, "prompts/system/generation_mode", generation_mode, f"{lang}.txt")
        example_user_path = os.path.join(backend_root_dir, "prompts/example/", app_config['flashcard_generation']['example_prompt'], lang,
                                         "example_user.txt")
        example_assistant_path = os.path.join(backend_root_dir, "prompts/example/", app_config['flashcard_generation']['example_prompt'], lang,
                                              "example_assistant.txt")
        additional_prompt_path = os.path.join(backend_root_dir, "prompts/additional/", app_config['flashcard_generation']['additional_prompt'],
                                              f"{lang}.txt")

        system_prompt = read_file(system_prompt_path)
        example_user = read_file(example_user_path)
        example_assistant = read_file(example_assistant_path)
        additional_prompt = read_file(additional_prompt_path)

    except OSError as e:
        logger.error(f"File read error in load_message_components: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in load_message_components: {e}")
        raise

    return system_prompt, example_user, example_assistant, additional_prompt


def validate_prompt_size(prompt_size: int, prompt_token_limit: int):
    """
    Validates the size of the prompts against the given token limit.

    Raises
    ------
    PromptSizeError
        If the prompts exceeds the token limit.
    """
    if prompt_size > prompt_token_limit:
        raise PromptSizeError(f"Prompt size of {format_num(prompt_size)} exceeds set prompts token limit.")


def compute_prompt_tokens(encoding: tiktoken.Encoding, system_prompt: str, example_user: str, example_assistant: str,
                          additional_prompt: str, prompt_token_limit: int) -> int:
    """
    Compute the total tokens of the prompts given the prompts components.

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
            "Invalid Prompt Size",
            error=e,
            prompt_tokens=prompt_tokens,
            prompt_token_limit=prompt_token_limit
        )
        raise
    return prompt_tokens


def load_token_limits(app_config: dict) -> (int, int, int):
    app_token_limit = app_config['token_limits']['app_limit']
    prompt_token_limit = app_config['token_limits']['prompt_limit']
    completion_token_limit = app_config['token_limits']['completion_limit']
    try:
        validate_token_limits(app_token_limit, prompt_token_limit, completion_token_limit)
    except ConfigInvalidValueError as e:
        logger.warning("Invalid token limits", extra={
            "event": e,
            "app_token_limit": app_token_limit,
            "prompt_token_limit": prompt_token_limit,
            "completion_token_limit": completion_token_limit})
    return app_token_limit, prompt_token_limit, completion_token_limit


def validate_token_limits(app_token_limit: int, prompt_token_limit: int, completion_token_limit: int):
    """

    """
    if app_token_limit - (prompt_token_limit + completion_token_limit) <= 0:
        raise ConfigInvalidValueError("The sum of the prompts token and the completion token limits exceeds the total token limit of the app.")


class FlashcardService:
    """
    Service to generate flashcards using OpenAI's language models.

    Attributes
    ----------
    openai : OpenAI
        Client instance for interacting with the OpenAI API.
    model_name : str
        Name of the OpenAI model to use.
    encoding : tiktoken.Encoding
        Encoding object for the model.
    generation_mode : str
        Mode of flashcard generation.
    lang : str
        Language of the flashcards.
    prompt_token_limit : int
        Token limit for the prompts.
    completion_token_limit : int
        Token limit for the completion.
    """

    GENERATION_MODE = ['practice', 'definitions', 'quiz', 'cloze']
    SUPPORTED_LANGS = ['auto', 'de', 'en']
    EXPORT_FORMATS = ['csv', 'anki', 'list']

    def __init__(self, openai: OpenAI, app_config: dict, model_name: str, lang: str, mode: str):
        """
        Initializes the FlashcardService with necessary configurations.

        Parameters
        ----------
        openai : OpenAI
            The OpenAI client object.
        app_config : dict
            Configuration settings for the app.
        model_name : str
            The name of the model to use for generation.
        lang : str
            The language in which the flashcards will be generated.
        mode : str
            The mode of flashcard generation.
        """
        self.openai = openai
        validate_config_param(mode, FlashcardService.GENERATION_MODE)
        validate_config_param(lang, FlashcardService.SUPPORTED_LANGS)
        self.generation_mode = mode.lower()
        self.lang = lang.lower()
        self.model_name = model_name
        self.model_config = app_config.get('model', None)  # Use default values if app_config is not defined
        self.text_splitting_config = app_config.get('text_splitting', None)  # Use default values if app_config is not defined
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.backend_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.app_token_limit, self.prompt_token_limit, self.completion_token_limit = load_token_limits(app_config)
        self.system_prompt, self.example_user, self.example_assistant, self.additional_prompt = load_message_components(self.backend_root_dir,
                                                                                                                        app_config,
                                                                                                                        self.generation_mode,
                                                                                                                        self.lang)
        self.prompt_tokens = compute_prompt_tokens(self.encoding, self.system_prompt, self.example_user, self.example_assistant,
                                                   self.additional_prompt, self.prompt_token_limit)

    def run(self, user_input: str, update_progress: Optional[Callable[[int, int], None]] = None) -> FlashcardDeck:
        """
        Generates flashcards based on the provided user input.

        Parameters
        ----------
        user_input : str
            The user input text from which flashcards are to be generated.
        update_progress : Optional[Callable[[int, int], None]]
            Optional callback function to update progress.

        Returns
        -------
        FlashcardDeck
            A deck of generated flashcards.
        """
        flashcard_generator = FlashcardGenerator(client=self.openai, model_config=self.model_config, generation_mode=self.generation_mode)
        try:
            flashcards = self.generate_flashcards(user_input, flashcard_generator, update_progress)
        except OpenAIError:
            raise
        flashcard_deck = FlashcardDeck(flashcards)
        return flashcard_deck

    def generate_flashcards(self, user_input: str, flashcard_generator: FlashcardGenerator,
                            update_progress: Optional[Callable[[int, int], None]]) -> List[Flashcard]:
        """
        Generates flashcards from the given user input.
        # TODO: Handle errors on IO and API calls.
        # TODO: Add parallelization
        Parameters
        ----------
        user_input : str
            The user input text from which flashcards are to be generated.
        flashcard_generator : FlashcardGenerator
            The flashcard generator instance.
        update_progress : Optional[Callable[[int, int], None]]
            Optional callback function to update progress.

        Returns
        -------
        List[Flashcard]
            A list of generated flashcards.
        """
        # Add an instruction at the top of the input text.
        input_text = inset_into_string(insert=self.additional_prompt, target=user_input, position=0)

        # Initialize messages sent to OpenAI API
        messages = Messages(
            system=self.system_prompt,
            example_user=self.example_user,
            example_assistant=self.example_assistant,
            input_text=input_text
        )

        # Log start time
        start_time = time.time()
        logger.info(
            "Flashcard generation started",
            model_name=self.model_name,
            generation_mode=self.generation_mode,
            language=self.lang,
            token_est=format_num(messages.compute_input_tokens(encoding=self.encoding))
        )
        # Compute total tokens of the messages
        total_message_tokens = messages.compute_total_tokens(encoding=self.encoding)

        # Empty flashcard list to store generated flashcards
        flashcards: List[Flashcard] = []

        # For short texts generate the flashcards in a single run
        if total_message_tokens < self.app_token_limit:
            flashcards += flashcard_generator.generate_flashcards(model=self.model_name, messages=messages, max_tokens=self.completion_token_limit)
        # For longer texts, splut the text into fragments and generate flashcards in multiple batches
        else:
            # Split the text into fragments
            fragment_size = self.app_token_limit - (self.prompt_tokens + self.completion_token_limit)
            fragment_list = text_split.split_text(
                encoding=self.encoding,
                text=user_input,
                fragment_size=fragment_size,
                overlap_type=self.text_splitting_config.get('overlap_type', 'absolute'),
                overlap=self.text_splitting_config.get('overlap', 100)
            )

            total_batch_num = len(fragment_list)
            for batch in range(total_batch_num):
                input_text = inset_into_string(self.additional_prompt, fragment_list[batch], 0)
                # Generate a new Message for the new shorter fragment
                new_message = Messages(
                    system=self.system_prompt,
                    example_user=self.example_user,
                    example_assistant=self.example_assistant,
                    input_text=input_text
                )

                # Generate flashcards and add them to the flashcard list
                start_id = len(flashcards) + 1
                new_cards = flashcard_generator.generate_flashcards(
                    model=self.model_name,
                    messages=new_message,
                    max_tokens=self.completion_token_limit,
                    start_id=start_id,
                    batch_number=batch + 1
                )
                # Append new flashcards and update
                flashcards += new_cards
                # Call update_progress to make information about the progress available to other (independent) parts of the system
                if update_progress:
                    update_progress(batch + 1, len(fragment_list))

        # Log end time
        end_time = time.time()
        logger.info("Flashcard generation completed", total_flashcards=len(flashcards), duration=round(end_time - start_time, 3), )
        return flashcards
