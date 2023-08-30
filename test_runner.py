import json
import math
import os.path
from typing import List

import tiktoken

import text_split
from completion_messages import Messages
from flash_card import FlashCard
from flash_card_deck import FlashCardDeck
from flashcard_generator import FlashCardGenerator


class ConfigLoadError(Exception):
    """
    Custom exception for config loading issues.
    """
    pass


def load_config(config_path='config.json') -> dict:
    """
    Loads a configuration from a JSON file.

    Args:
    - config_path (str): Path to the JSON configuration file.

    Returns:
    - dict: The configuration parameters.

    Raises:
    - ConfigLoadError: If there's an issue loading the config file.
    """

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


def read_file(path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


# todo, this doesn't make sense because the test files are getting changed
# it would only make sense to change the number in the already read text
def set_flashcard_number(file_path, number):
    """
    Replaces the second word of each line in the file if it's an underscore.

    Args:
    - file_path (str): The path to the text file.
    - replacement (str): The string to replace the underscore with.

    Returns:
    - str: The modified text.
    """

    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []

    for line in lines:
        words = line.split()
        if len(words) > 1 and words[1] == "_":
            words[1] = str(number)
        modified_lines.append(' '.join(words))

    modified_text = '\n'.join(modified_lines)

    with open(file_path, 'w') as file:
        file.write(modified_text)


class TestRunner:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)

    def run_test(self, base_path: str, csv_path: str):
        print(base_path)
        # Load example used in query
        example_system_prompt = read_file(os.path.join(base_path, 'example/example_system_prompt.txt'))
        example_user_input = read_file(os.path.join(base_path, 'example/example_user_input.txt'))
        example_response = read_file(os.path.join(base_path, 'example/example_response.txt'))
        # Load the user input and system prompt
        input_system_prompt = read_file(os.path.join(base_path, 'input/system_prompt.txt'))
        input_user_prompt = read_file(os.path.join(base_path, 'input/user_input.txt'))

        input_user_prompts = (
            text_split.split_text(input_user_prompt, 2000, 2400)) # 2k and 2.4k for 4k model, 10k, 10.4k respectivey for 16k model
        flashcards: List[FlashCard] = []
        count = 1
        for input_user_prompt in input_user_prompts:
            print(f'text split: {count}')
            count += 1
            messages = Messages(example_user_input, example_system_prompt, example_response, input_system_prompt,
                                input_user_prompt)

            # Add additional instructions for language detection to input_user_prompt
            messages.insert_text_into_message('input_user_prompt', os.path.join(base_path, 'insert_instructions.txt'), 0)
            message_list = messages.as_message_list()


            # Run config
            # Load the encoding for the model
            encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
            total_prompt_size = sum(
                [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in message_list])

            # count of input tokens needs to be below 3k to use 4k model
            if total_prompt_size > 3000:
                print(total_prompt_size)
                self.config["model"]["name"] = "gpt-3.5-turbo-16k"
                self.config["model"]["max_tokens"] = math.floor(total_prompt_size / 3)

            # Set flashcard number
            if self.config["flashcards"].get("active"):
                if not self.config["flashcards"].get("manual"):
                    # messages[4] is the user input in the message list.
                    number_to_generate = self.config["flashcards"].get("number_to_generate")
                    set_flashcard_number(os.path.join(base_path, 'input/system_prompt.txt'), number_to_generate)

            generator = FlashCardGenerator(os.getenv('OPENAI_API_KEY'), message_list, self.config)
            new_cards = generator.generate_flashcards()
            print(len(new_cards))
            flashcards = flashcards + new_cards
        deck = FlashCardDeck(flashcards)
        deck.save_as_csv(csv_path)
