import yaml
import os
import logging
from typing import List

from completion_messages import Messages
from flash_card import FlashCard
from flash_card_deck import FlashCardDeck
from flashcard_generator import FlashCardGenerator
from global_helpers import format_num, write_to_log
import tiktoken
import text_split


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
    def __init__(self, config_path: str):
        self.config = load_config(config_path)

    def run_test(self, base_path: str, csv_path: str):
        try:
            messages = self._initialize_messages(base_path)
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
                self._run_full_text(base_path, messages, "gpt-3.5-turbo", completion_token_limit)
                flashcards += self._generate_flashcards(messages)

            # Run medium-sized texts with 16k model
            elif total_prompt_size < prompt_limit_16k:
                write_to_log("Using 16k model...\n")
                completion_token_limit = 16000 - prompt_limit_16k
                self._run_full_text(base_path, messages, "gpt-3.5-turbo-16k", completion_token_limit)
                flashcards += self._generate_flashcards(messages)

            # Run long text using test splitting
            else:
                write_to_log(f"Using text splitting with the {self.config['model']['name']}...\n")

                # Choose model and calculate window size for text splitting based on the base_prompt_size
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

                input_user_prompts = text_split.split_text(
                    messages.input_user_prompt,
                    window_size,
                    self.config["tokens"]["text_splitting"]["window_overlap_factor"]
                )

                for input_user_prompt in input_user_prompts:
                    write_to_log(f'Processing text fragment No {count}')
                    count += 1

                    new_messages = Messages(
                        messages.example_user_prompt,
                        messages.example_system_prompt,
                        messages.example_response,
                        messages.input_system_prompt,
                        input_user_prompt
                    )
                    sub_prompt_size = self._calculate_total_prompt_size(new_messages)
                    formatted_sub_prompt_size = format_num(sub_prompt_size)
                    write_to_log(f"Calculated prompt size: {formatted_sub_prompt_size} tokens")

                    new_messages.insert_text_into_message(
                        'input_user_prompt',
                        os.path.join(base_path, 'insert_instructions.txt'),
                        0
                    )
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
        messages.insert_text_into_message('input_user_prompt', os.path.join(base_path, 'insert_instructions.txt'), 0)

    def _generate_flashcards(self, messages: Messages) -> List[FlashCard]:
        """Generates flashcards based on the provided messages."""
        generator = FlashCardGenerator(os.getenv('OPENAI_API_KEY'), messages.as_message_list(), self.config)
        return generator.generate_flashcards()

    @staticmethod
    def _initialize_messages(base_path: str) -> Messages:
        """Initializes Messages object from files."""
        return Messages(
            read_file(os.path.join(base_path, 'example/example_user_input.txt')),
            read_file(os.path.join(base_path, 'example/example_system_prompt.txt')),
            read_file(os.path.join(base_path, 'example/example_response.txt')),
            read_file(os.path.join(base_path, 'input/system_prompt.txt')),
            read_file(os.path.join(base_path, 'input/user_input.txt'))
        )

    @staticmethod
    def _save_flashcards_as_csv(flashcards: List[FlashCard], csv_path: str):
        """Saves the generated flashcards as a CSV file."""
        deck = FlashCardDeck(flashcards)
        deck.save_as_csv(csv_path)

# todo: Check run_config for specified export format and add conditional statement
# todo: Write Anki Exporter to optionally export the csv flashcards directly to the users Anki workspace, if connected
