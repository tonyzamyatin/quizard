import yaml
import os
import logging
import tiktoken
from typing import List

from backend.src.utils.completion_messages import Messages
from backend.src.flashcard.flashcard import Flashcard
from backend.src.flashcard_deck.flashcard_deck import FlashcardDeck
from backend.src.flashcard_generator.flashcard_generator import FlashcardGenerator
from backend.src.utils.global_helpers import format_num, write_to_log
from backend.src.text_splitting import text_split

# Import custom exceptions
from backend.src.custom_exceptions.custom_exceptions import ConfigLoadingError
from backend.src.custom_exceptions.custom_exceptions import PromptSizeError


def load_config(config_path='config.yaml') -> dict:
    """Loads a configuration from a YAML file."""
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError:
        raise ConfigLoadingError(f"The configuration file '{config_path}' was not found.")
    except yaml.YAMLError:
        raise ConfigLoadingError(f"The configuration file '{config_path}' contains invalid YAML.")
    except Exception as e:
        raise ConfigLoadingError(f"An error occurred while loading the configuration file: {str(e)}")


def read_file(path: str) -> str:
    """Reads the file content from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestRunner:
    GENERATION_MODE = ['autogen', 'open_ended', 'definitions', 'quiz', 'cloze']

    def __init__(self, config_path: str, backend_root_dir: str):
        self.config = load_config(config_path)
        self.backend_root_dir = backend_root_dir
        self.generation_mode = self.config.get('flashcard_generation', {}).get('mode', 'default')

        # Check validity of specified deck type
        if self.generation_mode not in TestRunner.GENERATION_MODE:
            raise ConfigLoadingError(f"Invalid flashcard type: {self.generation_mode}. Expected one of {TestRunner.GENERATION_MODE}.")

    def run_test(self, test_path: str, csv_path: str):
        messages = self._initialize_messages(test_path)

        # Set language specified in the config file
        # lang_instruction = self._set_language(os.path.join(self.backend_root_dir, 'system_prompts/lang_instruction.txt'))
        with open(os.path.join(self.backend_root_dir, 'system_prompts/lang_instruction.txt'), "r") as f:
            lang_instruction = f.read()

        # Calculate total prompt size
        total_prompt_size = self._calculate_total_prompt_size(messages, lang_instruction)
        formatted_total_prompt_size = format_num(total_prompt_size)
        write_to_log(f"Total message length (calculated): {formatted_total_prompt_size} tokens")

        flashcards = []  # List to collect flashcards from each run
        count = 1  # Counter for debug print statements

        prompt_limit_4k = self.config["tokens"]["4k_model"]["prompt_limit"]
        prompt_limit_16k = self.config["tokens"]["16k_model"]["prompt_limit"]

        # Run short texts with 4k model
        if total_prompt_size < prompt_limit_4k:
            write_to_log("Using 4k model...\n")
            messages.insert_text_into_message('text_input', lang_instruction, 0)
            completion_token_limit = 4000 - prompt_limit_4k
            self._run_full_text(test_path, messages, "gpt-3.5-turbo", completion_token_limit)
            flashcards += self._generate_flashcards(messages)

        # Run medium-sized texts with 16k model
        elif total_prompt_size < prompt_limit_16k:
            write_to_log("Using 16k model...\n")
            messages.insert_text_into_message('text_input', lang_instruction, 0)
            completion_token_limit = 16000 - prompt_limit_16k
            self._run_full_text(test_path, messages, "gpt-3.5-turbo-16k", completion_token_limit)
            flashcards += self._generate_flashcards(messages)

        # Run long text using test splitting
        else:
            write_to_log(f"Using text splitting with the {self.config['model']['name']}...\n")

            # Split the text into fragments
            base_prompt_size = self._calculate_base_prompt_size(messages, lang_instruction)
            try:
                fragment_list = text_split.split_text(
                    messages.text_input,
                    base_prompt_size,
                    self.config
                )
            except PromptSizeError as e:
                logging.error(f"Prompt size error occurred: {str(e)}")
                print(f"Terminating the program due to the following PromptSizeError: {str(e)}")
                exit(1)

            for text_fragment in fragment_list:
                write_to_log(f'Processing text fragment No {count}')
                count += 1

                # Generate a new Messages for the new shorter text_fragment
                new_messages = Messages(
                    messages.system,
                    messages.example_user,
                    messages.example_assistant,
                    text_fragment
                )

                sub_prompt_size = self._calculate_total_prompt_size(new_messages)
                formatted_sub_prompt_size = format_num(sub_prompt_size)
                write_to_log(f"Calculated prompt size: {formatted_sub_prompt_size} tokens")

                # Add language instructions to the text_input to enable language recognition
                new_messages.insert_text_into_message('text_input', lang_instruction, 0)
                # Generate flashcards and add them to the flashcard list
                new_cards = self._generate_flashcards(new_messages)
                flashcards += new_cards
                for flashcard in new_cards:
                    print(flashcard.as_csv())

        self._save_flashcards_as_csv(flashcards, csv_path)

    def _calculate_total_prompt_size(self, messages: Messages, *additional_strings) -> int:
        """Calculates the total prompt size based on the message content."""
        encoding = tiktoken.encoding_for_model(self.config['model']['name'])
        # There are 18 additional tokens in the prompt due to the list format
        base_count =  18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in
             messages]
        )

        # Calculate the tokens for additional strings
        additional_count = sum([len(encoding.encode(s)) for s in additional_strings])
        return base_count + additional_count

    def _calculate_base_prompt_size(self, messages: Messages, *additional_strings) -> int:
        encoding = tiktoken.encoding_for_model(self.config['model']['name'])
        # There are 18 additional tokens in the prompt due to the list format
        message_list = messages.as_message_list()  # Call the as_message_list method to get the list of messages
        base_count =  18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role']))
             for message in message_list[:-1]]  # Slice to skip the last message
        )

        # Calculate the tokens for additional strings
        additional_count = sum([len(encoding.encode(s)) for s in additional_strings])
        return base_count + additional_count

    def _run_full_text(self, base_path: str, messages: Messages, model_name: str, completion_token_limit: int):
        """Runs the test using a specific model."""
        print(f"Using {model_name} for total prompt size.")
        self.config["model"]["name"] = model_name
        self.config["tokens"]["completion_limit"] = completion_token_limit
        messages.insert_text_into_message('text_input', os.path.join(base_path, 'lang_instruction.txt'), 0)

    # Modify this method
    def _generate_flashcards(self, messages: Messages) -> List[Flashcard]:
        """Generates flashcards based on the provided messages."""
        generator = FlashcardGenerator(os.getenv('OPENAI_API_KEY'), messages.as_message_list(), self.config, self.generation_mode)
        return generator.generate_flashcards()

    def _initialize_messages(self, test_path: str) -> Messages:
        """Initializes Messages object from files."""
        try:
            system_prompt_file = f"{self.generation_mode}.txt"
            return Messages(
                read_file(os.path.join(self.backend_root_dir, "system_prompts/generation_mode", system_prompt_file)),
                read_file(os.path.join(test_path, 'example_user.txt')),
                read_file(os.path.join(test_path, 'example_assistant.txt')),
                read_file(os.path.join(test_path, 'text_input.txt'))
            )
        except FileNotFoundError as e:
            raise ConfigLoadingError(f"System prompt file not found for generation mode {self.generation_mode}.")

    @staticmethod
    def _save_flashcards_as_csv(flashcards: List[Flashcard], csv_path: str):
        """Saves the generated flashcards as a CSV file."""
        deck = FlashcardDeck(flashcards)
        deck.save_as_csv(csv_path)

    def _set_language(self, lang_instruction_path: str) -> str:
        # Read the original text file with raw language instruction
        with open(lang_instruction_path, "r") as f:
            lang_instruction = f.read()

        # Replace placeholders
        lang = self.config["flashcard_generation"]["lang"]
        return lang_instruction.replace("${language}", lang.upper())


# todo: Check run_config for specified export format and add conditional statement
# todo: Write Anki Exporter to optionally export the csv flashcards directly to the users Anki workspace, if connected
