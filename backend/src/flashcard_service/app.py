import logging
import os
from openai import OpenAI
from typing import List

import tiktoken

# Import custom exceptions
from ..custom_exceptions.quizard_exceptions import ConfigLoadingError, PromptSizeError, UnsupportedLanguageError
from ..flashcard_service.flashcard.flashcard import Flashcard
from ..flashcard_service.flashcard_deck.flashcard_deck import FlashcardDeck
from ..flashcard_service.flashcard_generator.flashcard_generator import FlashcardGenerator
from ..text_splitting import text_split
from ..utils.completion_messages import Messages
from ..utils.global_helpers import format_num, write_to_log_and_print, inset_into_string, read_file


class FlashcardService:
    def __init__(self, client: OpenAI, config: dict, model_name: str, lang: str, mode: str):
        self.config = config
        self.client = client
        self.model_name = model_name
        self.generation_mode = mode
        self.lang = lang
        self.backend_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # TODO: Introduce logic to check whether given model is part of OpenAIs available models. Desirably, hardcoded and regularly synced with OpenAI's
        # list of available models, which is supported by us for the given task.
        if self.generation_mode not in FlashcardGenerator.GENERATION_MODE:
            raise ConfigLoadingError(f"Invalid flashcard generation mode: {self.generation_mode}. Expected one of {FlashcardGenerator.GENERATION_MODE}.")

        if lang not in config["system"]["supported_langs"]:
            raise UnsupportedLanguageError(f"The specified language '{self.lang}' is not supported or does not "
                                           f"exist.")

        # Initialize the components of the message send to the OpenAI API
        self.system_prompt = read_file(os.path.join(self.backend_root_dir, "prompt/system/generation_mode", self.generation_mode, f"{self.lang}.txt"))
        self.example_user = read_file(os.path.join(self.backend_root_dir, "prompt/example/", self.config['flashcard_generation']['example_prompt'],
                                                   self.lang,
                                                   "example_user.txt"))
        self.example_assistant = read_file(
            os.path.join(self.backend_root_dir, "prompt/example/", self.config['flashcard_generation']['example_prompt'],
                         self.lang,
                         "example_assistant.txt"))
        self.additional_prompt = read_file(
            os.path.join(self.backend_root_dir, "prompt/additional/", self.config['flashcard_generation']['additional_prompt'],
                         f"{self.lang}.txt"))

    def run(self, text_input: str, update_progress=None):
        # TODO: Add language detection

        # Initialize flashcard generator
        flashcard_generator = FlashcardGenerator(self.client, self.config["model"], self.generation_mode)

        flashcards: List[Flashcard] = []  # List to collect flashcards from each run

        # TODO: Update code to support new available models: gpt-3.5-turbo-1106 primarily, but also gpt-4-turbo-1106 (premium tier coming soon)
        prompt_limit_4k = self.config["tokens"]["4k_model"]["prompt_limit"]

        # Initialize messages sent to the OpenAI API
        messages = Messages(
            self.system_prompt,
            self.example_user,
            self.example_assistant,
            inset_into_string(self.additional_prompt, text_input, 0)
        )
        # Calculate total prompt size
        total_prompt_size = self._calculate_total_prompt_size(messages)
        formatted_total_prompt_size = format_num(total_prompt_size)
        write_to_log_and_print(f"Total message length (calculated): {formatted_total_prompt_size} tokens")

        # Run short texts as a single prompt.
        # NOTE: gpt-3.5-turbo-1106 has a context window of 16,385. We only use 4.096 tokens, like the legacy modell
        # since a smaller context window has proved to generate a larger number of flashcards that at the same time
        # gp more in depth.
        # TODO: Introduce separate logic for generating flashcards using other models and context windows.
        if total_prompt_size < prompt_limit_4k:
            write_to_log_and_print("Using 4k model...\n")
            # Add language instructions to the text inputs
            print(f"Generating flashcards in one go using {self.model_name}...\n")
            max_tokens = 4096 - prompt_limit_4k
            flashcards += flashcard_generator.generate_flashcards("gpt-3.5-turbo", messages, max_tokens)

        else:
            write_to_log_and_print(f"Generating flashcards by text splitting using {self.model_name}...\n")

            # Split the text into fragments
            base_prompt_size = self._calculate_base_prompt_size(messages, self.additional_prompt)
            print(f"Base prompt size: {base_prompt_size}")
            try:
                fragment_list = text_split.split_text(self.model_name, text_input, base_prompt_size, self.config["tokens"])
                total_batches = len(fragment_list)
            except PromptSizeError as e:
                logging.error(f"Prompt size error occurred: {str(e)}")
                print(f"Terminating the program due to the following PromptSizeError: {str(e)}")
                exit(1)
            write_to_log_and_print(f"Text was split into {len(fragment_list)} fragments.\n")

            for index in range(total_batches):
                write_to_log_and_print(f'\nProcessing batch No {index + 1}/{total_batches} batches')

                # Generate a new Messages for the new shorter fragment
                new_messages = Messages(
                    messages.system,
                    messages.example_user,
                    messages.example_assistant,
                    inset_into_string(self.additional_prompt, fragment_list[index], 0)
                )

                sub_prompt_size = self._calculate_total_prompt_size(new_messages)
                formatted_sub_prompt_size = format_num(sub_prompt_size)
                write_to_log_and_print(f"Calculated prompt size: {formatted_sub_prompt_size} tokens")
                max_tokens = 4096 - sub_prompt_size

                # Generate flashcards and add them to the flashcard list
                new_cards = flashcard_generator.generate_flashcards("gpt-3.5-turbo", new_messages, max_tokens)
                flashcards += new_cards
                # Update progress
                index += 1
                # Call update_progress to make information about the progress available to other (independent) parts of the system
                if update_progress:
                    update_progress(index, len(fragment_list))
                for flashcard in new_cards:
                    print(flashcard.as_csv())

        flashcard_deck = FlashcardDeck(flashcards)
        return flashcard_deck

    def _calculate_total_prompt_size(self, messages: Messages, *additional_strings) -> int:
        """Calculates the total prompt size based on the message content."""
        encoding = tiktoken.encoding_for_model(self.model_name)
        # There are 18 additional tokens in the prompt due to the list format
        base_count = 18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in
             messages]
        )

        # Calculate the tokens for additional strings
        additional_count = sum([len(encoding.encode(s)) for s in additional_strings])
        return base_count + additional_count

    def _calculate_base_prompt_size(self, messages: Messages, *additional_strings) -> int:
        encoding = tiktoken.encoding_for_model(self.model_name)
        # There are 18 additional tokens in the prompt due to the list format
        message_list = messages.as_message_list()  # Call the as_message_list method to get the list of messages
        base_count = 18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role']))
             for message in message_list[:-1]]  # Slice to skip the last message containing the text_input
        )

        # Calculate the tokens for additional strings
        additional_count = sum([len(encoding.encode(s)) for s in additional_strings])
        return base_count + additional_count

    @staticmethod
    def _save_flashcards_as_csv(flashcards: List[Flashcard], csv_path: str):
        """Saves the generated flashcards as a CSV file."""
        deck = FlashcardDeck(flashcards)
        deck.save_as_csv(csv_path)

# todo: Check run_config for specified export format and add conditional statement
# todo: Write Anki Exporter to optionally export the csv flashcards directly to the users Anki workspace, if connected
