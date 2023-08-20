import json
import os.path

from dotenv import load_dotenv
from example_messages import ExampleMessages
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
        # Load example used in query
        example_system_prompt = read_file(os.path.join(base_path, 'example/example_system_prompt.txt'))
        example_user_input = read_file(os.path.join(base_path, 'example/example_user_input.txt'))
        example_response = read_file(os.path.join(base_path, 'example/example_response.txt'))

        # Specify number of flashcards to be generated
        if self.config["flashcards"].get("active"):
            set_flashcard_number(os.path.join(base_path, 'input/system_prompt.txt'), self.config["flashcards"].get("number_to_generate"))

        # Load the user input and system prompt
        system_prompt = read_file(os.path.join(base_path, 'input/system_prompt.txt'))
        user_input = read_file(os.path.join(base_path, 'input/user_input.txt'))

        example_messages = ExampleMessages(example_user_input, example_system_prompt, example_response)
        service = FlashCardGenerator(os.getenv('OPENAI_API_KEY'), example_messages, self.config)
        deck = service.generate(user_input, system_prompt)
        deck.save_as_csv(csv_path)
