import json
import os
from typing import List

from completion_messages import Messages
from flash_card import FlashCard
from flash_card_deck import FlashCardDeck
from flashcard_generator import FlashCardGenerator
import tiktoken
import text_split


class ConfigLoadError(Exception):
    """Custom exception for config loading issues."""
    pass


def load_config(config_path='config.json') -> dict:
    """Loads a configuration from a JSON file."""
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        raise ConfigLoadError(f"The configuration file '{config_path}' was not found.")
    except json.JSONDecodeError:
        raise ConfigLoadError(f"The configuration file '{config_path}' contains invalid JSON.")
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
        messages = self._initialize_messages(base_path)
        total_prompt_size = self._calculate_total_prompt_size(messages)

        flashcards = []  # List to collect flashcards from each run
        count = 1  # Counter for debug print statements

        # Run short texts with 4k model
        if total_prompt_size < 3000:
            self._run_full_text(base_path, messages, "gpt-3.5-turbo", 1000)
            flashcards += self._generate_flashcards(messages)
        # Run medium-sized texts with 16k model
        elif total_prompt_size < 12000:
            self._run_full_text(base_path, messages, "gpt-3.5-turbo-16k", 4000)
            flashcards += self._generate_flashcards(messages)
        # Run long text using test splitting
        else:
            input_user_prompts = text_split.split_text(
                messages.input_user_prompt,
                self.config['flashcards']['window_overlap'],
                self.config['flashcards']['window_size']
            )

            for input_user_prompt in input_user_prompts:
                print(f'Text split: {count}')
                count += 1

                new_messages = Messages(
                    messages.example_user_prompt,
                    messages.example_system_prompt,
                    messages.example_response,
                    messages.input_system_prompt,
                    input_user_prompt
                )

                new_messages.insert_text_into_message(
                    'input_user_prompt',
                    os.path.join(base_path, 'insert_instructions.txt'),
                    0
                )

                new_cards = self._generate_flashcards(new_messages)
                print(f"Character length of generated flashcards {count}: {len(new_cards)}.")
                flashcards += new_cards

        self._save_flashcards_as_csv(flashcards, csv_path)

    def _calculate_total_prompt_size(self, messages: Messages) -> int:
        """Calculates the total prompt size based on the message content."""
        encoding = tiktoken.encoding_for_model(self.config['model']['name'])
        return sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in
             messages.as_message_list()]
        )

    def _run_full_text(self, base_path: str, messages: Messages, model_name: str, max_tokens: int):
        """Runs the test using a specific model."""
        print(f"Using {model_name} for total prompt size.")
        self.config["model"]["name"] = model_name
        self.config["model"]["max_tokens"] = max_tokens
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
