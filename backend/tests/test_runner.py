import yaml
import os
import logging
from typing import List

from backend.src.utils.completion_messages import Messages
from backend.src.flashcard.flashcard import FlashCard
from backend.src.flashcard_deck.flashcard_deck import FlashCardDeck
from backend.src.flashcard_generator.flashcard_generator import FlashCardGenerator
from backend.src.utils.global_helpers import format_num, write_to_log
import tiktoken
from backend.src.text_splitting import text_split


class ConfigLoadError(Exception):
    """Custom exception for config loading issues."""
    pass


class PromptSizeError(Exception):
    """Custom exception for prompt size issues."""
    pass


def load_config(config_path='config.yaml') -> dict:
    """Loads a configuration from a YAML file."""
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError:
        raise ConfigLoadError(f"The configuration file '{config_path}' was not found.")
    except yaml.YAMLError:
        raise ConfigLoadError(f"The configuration file '{config_path}' contains invalid YAML.")
    except Exception as e:
        raise ConfigLoadError(f"An error occurred while loading the configuration file: {str(e)}")


def read_file(path: str) -> str:
    """Reads the file content from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestRunner:
    GENERATION_MODE = ['autogen', 'open_ended', 'definitions', 'quiz', 'cloze']

    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.generation_mode = self.config.get('flashcard_generation', {}).get('mode', 'default')

        # Check validity of specified deck type
        if self.generation_mode not in TestRunner.GENERATION_MODE:
            raise ConfigLoadError(f"Invalid flashcard type: {self.generation_mode}. Expected one of {TestRunner.GENERATION_MODE}.")

    def run_test(self, test_path: str, csv_path: str):
        try:
            messages = self._initialize_messages(test_path)

            total_prompt_size = self._calculate_total_prompt_size(messages)
            formatted_total_prompt_size = format_num(total_prompt_size)
            write_to_log(f"Total message length (calculated): {formatted_total_prompt_size} tokens")

            flashcards = []  # List to collect flashcards from each run
            count = 1  # Counter for debug print statements

            prompt_limit_4k = self.config["tokens"]["4k_model"]["prompt_limit"]
            prompt_limit_16k = self.config["tokens"]["16k_model"]["prompt_limit"]

            # Run short texts with 4k model
            if total_prompt_size < prompt_limit_4k:
                write_to_log("Using 4k model...\n")
                completion_token_limit = 4000 - prompt_limit_4k
                self._run_full_text(test_path, messages, "gpt-3.5-turbo", completion_token_limit)
                flashcards += self._generate_flashcards(messages)

            # Run medium-sized texts with 16k model
            elif total_prompt_size < prompt_limit_16k:
                write_to_log("Using 16k model...\n")
                completion_token_limit = 16000 - prompt_limit_16k
                self._run_full_text(test_path, messages, "gpt-3.5-turbo-16k", completion_token_limit)
                flashcards += self._generate_flashcards(messages)

            # Run long text using test splitting
            else:
                write_to_log(f"Using text splitting with the {self.config['model']['name']}...\n")

                # Choose model and calculate window size for text splitting based on the size of the base prompt (prompt without text_input)
                base_prompt_size = self._calculate_base_prompt_size(messages)
                if self.config["model"]["name"] == "gpt-3.5-turbo" and base_prompt_size < self.config["tokens"]["4k_model"]["base_prompt_limit"]:
                    window_size = 4000 - base_prompt_size - self.config["tokens"]["4k_model"]["completion_limit"]
                elif base_prompt_size < self.config["tokens"]["16k_model"]["base_prompt_limit"]:
                    window_size = 16000 - base_prompt_size - self.config["tokens"]["16k_model"]["completion_limit"]
                else:
                    # If the base_prompt_size exceeds the base_prompt_limit, raise an exception.
                    raise PromptSizeError(
                        f"The base prompt size of {base_prompt_size} exceeds the allowed base prompt limit. "
                        "You may need to adjust the base prompt size, base prompt limit, or the completion limit.")

                # Split the text into fragments
                fragment_list = text_split.split_text(
                    messages.text_input,
                    window_size,
                    self.config["tokens"]["text_splitting"]["window_overlap_factor"]
                )

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
                    new_messages.insert_text_into_message(
                        'text_input',
                        'system_prompts/lang_instruction.txt',
                        0
                    )

                    # Generate flashcards and add them to the flashcard list
                    new_cards = self._generate_flashcards(new_messages)
                    flashcards += new_cards

            self._save_flashcards_as_csv(flashcards, csv_path)
        except PromptSizeError as e:
            logging.error(f"Prompt size error occurred: {str(e)}")
            print(f"Terminating the program due to the following PromptSizeError: {str(e)}")
            exit(1)
        # except Exception as e:
        #     logging.error(f"An unexpected error occurred: {str(e)}")
        #     print(f"Terminating the program due to an unexpected error: {str(e)}")
        #     exit(1)

    def _calculate_total_prompt_size(self, messages: Messages) -> int:
        """Calculates the total prompt size based on the message content."""
        encoding = tiktoken.encoding_for_model(self.config['model']['name'])
        # There are 18 additional tokens in the prompt due to the list format
        return 18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in
             messages]
        )

    def _calculate_base_prompt_size(self, messages: Messages) -> int:
        encoding = tiktoken.encoding_for_model(self.config['model']['name'])
        # There are 18 additional tokens in the prompt due to the list format
        message_list = messages.as_message_list()  # Call the as_message_list method to get the list of messages
        return 18 + sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role']))
             for message in message_list[:-1]]  # Slice to skip the last message
        )

    def _run_full_text(self, base_path: str, messages: Messages, model_name: str, completion_token_limit: int):
        """Runs the test using a specific model."""
        print(f"Using {model_name} for total prompt size.")
        self.config["model"]["name"] = model_name
        self.config["tokens"]["completion_limit"] = completion_token_limit
        messages.insert_text_into_message('text_input', os.path.join(base_path, 'lang_instruction.txt'), 0)

    # Modify this method
    def _generate_flashcards(self, messages: Messages) -> List[FlashCard]:
        """Generates flashcards based on the provided messages."""
        generator = FlashCardGenerator(os.getenv('OPENAI_API_KEY'), messages.as_message_list(), self.config, self.generation_mode)
        return generator.generate_flashcards()

    def _initialize_messages(self, test_path: str) -> Messages:
        """Initializes Messages object from files."""
        try:
            system_prompt_file = f"{self.generation_mode}.txt"
            return Messages(
                read_file(os.path.join(f'backend/system_prompts/generation_mode/{system_prompt_file}')),
                read_file(os.path.join(test_path, 'example_user.txt')),
                read_file(os.path.join(test_path, 'example_assistant.txt')),
                read_file(os.path.join(test_path, 'text_input.txt'))
            )
        except FileNotFoundError as e:
            raise ConfigLoadError(f"System prompt file not found for generation mode {self.generation_mode}.")

    @staticmethod
    def _save_flashcards_as_csv(flashcards: List[FlashCard], csv_path: str):
        """Saves the generated flashcards as a CSV file."""
        deck = FlashCardDeck(flashcards)
        deck.save_as_csv(csv_path)

# todo: Check run_config for specified export format and add conditional statement
# todo: Write Anki Exporter to optionally export the csv flashcards directly to the users Anki workspace, if connected
