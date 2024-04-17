# src/flashcard_service/flashcard_service.py
import structlog
import os
import time
from typing import List, Optional, Callable

import tiktoken
from openai import OpenAI

from src.dtos.flashcard_generator_task_dto import FlashcardGeneratorTaskDto
from src.entities.flashcard.flashcard import Flashcard
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck
from src.services.flashcard_service.flashcard_exprorter.flashcard_exporter import export_as_apkg, export_as_csv
from src.services.flashcard_service.flashcard_generator.flashcard_generator import FlashcardGenerator
from src.services.flashcard_service.text_splitting import text_split
from src.entities.completion_messages.completion_messages import Messages
from src.utils.global_helpers import format_num, inset_into_string, read_file, load_yaml_config, get_env_variable
from src.custom_exceptions.internal_exceptions import ConfigInvalidValueError, ConfigLoadingError
from src.custom_exceptions.external_exceptions import PromptSizeError, ValidationError

logger = structlog.getLogger(__name__)

src_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_dir = os.path.join(src_root, 'config')
try:
    app_config = load_yaml_config(config_dir, get_env_variable("GENERATOR_CONFIG_FILE"))
except ConfigLoadingError as e:
    logger.critical(f"Failed to load critical application configuration", error=str(e), exc_info=True)
    raise ConfigLoadingError(f"Failed to load critical application configuration")


def load_prompts(prompt_config: dict, generation_mode: str, lang: str) -> (str, str, str, str):
    """
    Initializes the message components for the OpenAI API request.
    """
    try:
        system_prompt_path = os.path.join(src_root, "prompts/system/generation_mode", generation_mode, f"{lang}.txt")
        example_user_prompt_path = os.path.join(src_root, "prompts/example/", prompt_config['example_prompt'], "example_user",
                                                f"{lang}.txt")
        example_assistant_prompt_path = os.path.join(src_root, "prompts/example/", prompt_config['example_prompt'], lang,
                                                     "example_assistant", f"{lang}.txt")
        additional_prompt_path = os.path.join(src_root, "prompts/additional/", prompt_config['additional_prompt'],
                                              f"{lang}.txt")

        system_prompt = read_file(system_prompt_path)
        example_user_prompt = read_file(example_user_prompt_path)
        example_assistant_prompt = read_file(example_assistant_prompt_path)
        additional_prompt = read_file(additional_prompt_path)

    except OSError as e:
        logger.error(f"File read error in load_message_components: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in load_message_components: {e}")
        raise

    return system_prompt, example_user_prompt, example_assistant_prompt, additional_prompt


def validate_prompt_size(prompt_size: int, prompt_token_limit: int):
    """
    Validates the size of the prompts against the given token limit.

    Raises
    ------
    PromptSizeError
        If the prompts exceeds the token limit.
    """
    if prompt_size > prompt_token_limit:
        raise ValidationError(f"Prompt size of {format_num(prompt_size)} exceeds set prompts token limit.")


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
    except ValidationError as e:
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
    return app_config['token_limits']


def validate_token_limits(app_token_limit: int, prompt_token_limit: int, completion_token_limit: int):
    if app_token_limit - (prompt_token_limit + completion_token_limit) <= 0:
        logger.warning("Invalid token limits", extra={
            "event": e,
            "app_token_limit": app_token_limit,
            "prompt_token_limit": prompt_token_limit,
            "completion_token_limit": completion_token_limit})
        raise ConfigInvalidValueError("The sum of the prompts token and the completion token limits exceeds the total token limit of the app.")


def export(flashcard_deck: FlashcardDeck, export_format: str) -> bytes:
    """
    Exports the generated flashcards to the specified format.

    Parameters
    ----------
    flashcard_deck : FlashcardDeck
        The deck of generated flashcards.
    export_format : str
        The format in which to export the flashcards.

    Returns
    -------
    bytes
        The exported flashcards in the specified format.
    """
    if export_format == 'apkg':
        return export_as_apkg(flashcard_deck)
    elif export_format == 'csv':
        return export_as_csv(flashcard_deck)


class FlashcardService:
    """
    Service to generate flashcards using OpenAI's language models.

    Attributes
    ----------
    openai : OpenAI
        Client instance for interacting with the OpenAI API.
    encoding : tiktoken.Encoding
        Encoding object for the model.
    prompt_token_limit : int
        Token limit for the prompts.
    completion_token_limit : int
        Token limit for the completion.
    """

    def __init__(self):
        """
        Initializes the FlashcardService with necessary configurations.

        Parameters
        ----------
        """
        self.openai = OpenAI(api_key=get_env_variable("OPENAI_API_KEY"))
        self.model_config = app_config.get('model')
        self.flashcard_generator = FlashcardGenerator(client=self.openai, model_config=self.model_config)
        self.prompt_config = app_config.get('prompt')
        self.text_splitting_config = app_config.get('text_splitting')
        self.encoding = tiktoken.encoding_for_model(self.model_config['model_name'])
        self.app_token_limit, self.prompt_token_limit, self.completion_token_limit = load_token_limits(app_config)

    def generate_flashcards(self, flashcards_request_dto: FlashcardGeneratorTaskDto,
                            update_progress: Optional[Callable[[int, int], None]]) -> FlashcardDeck:
        """
        Generates flashcards from the given user input.
        # TODO: Handle errors on IO and API calls.
        # TODO: Add parallelization
        Parameters
        ----------
        flashcards_request_dto : FlashcardsRequestDto
            The request data for generating flashcards.
        update_progress : Optional[Callable[[int, int], None]]
            Optional callback function to update progress.

        Returns
        -------
        List[Flashcard]
            A list of generated flashcards.
        """
        # Load the prompts
        (system_prompt,
         example_user_prompt,
         example_assistant_prompt,
         additional_prompt) = load_prompts(app_config, flashcards_request_dto.lang, flashcards_request_dto.mode)

        # Estimate prompt tokes
        prompt_tokens = compute_prompt_tokens(self.encoding, system_prompt, example_user_prompt, example_assistant_prompt, additional_prompt,
                                              self.prompt_token_limit)
        # Add an instruction at the top of the input text.
        modified_input_text = inset_into_string(insert=additional_prompt, target=flashcards_request_dto.input_text, position=0)

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
            generation_mode=flashcards_request_dto.generation_mode,
            language=flashcards_request_dto.lang,
            token_est=format_num(messages.compute_input_tokens(encoding=self.encoding))
        )
        # Compute total tokens of the messages
        total_message_tokens = messages.compute_total_tokens(encoding=self.encoding)

        # Empty flashcard list to store generated flashcards
        flashcards: List[Flashcard] = []

        # For short texts generate the flashcards in a single run
        if total_message_tokens < self.app_token_limit:
            flashcards += self.flashcard_generator.generate_flashcards(messages=messages, max_tokens=self.completion_token_limit)
        # For longer texts, splut the text into fragments and generate flashcards in multiple batches
        else:
            # Split the text into fragments
            fragment_size = self.app_token_limit - (prompt_tokens + self.completion_token_limit)
            fragment_list = text_split.split_text(
                encoding=self.encoding,
                text=modified_input_text,
                fragment_size=fragment_size,
                overlap_type=self.text_splitting_config.get('overlap_type', 'absolute'),
                overlap=self.text_splitting_config.get('overlap', 100)
            )

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

                # Generate flashcards and add them to the flashcard list
                start_id = len(flashcards) + 1
                new_cards = self.flashcard_generator.generate_flashcards(
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
        flashcard_deck = FlashcardDeck(flashcards)
        return flashcard_deck
