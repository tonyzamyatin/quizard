import os.path

from example_messages import ExampleMessages
from flashcard_generator import FlashCardGenerator


def read_file(path) -> str:
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def run_test(base_path: str, csv_path: str):
    # Load example used in query
    example_system_prompt = read_file(os.path.join(base_path, 'example/example_system_prompt.txt'))
    example_user_input = read_file(os.path.join(base_path, 'example/example_user_input.txt'))
    example_response = read_file(os.path.join(base_path, 'example/example_response.txt'))

    # Load the user input and system prompt
    system_prompt = read_file(os.path.join(base_path, 'input/system_prompt.txt'))  # Generiere 5 flashcards ...
    user_input = read_file(os.path.join(base_path, 'input/user_input.txt'))  # Ausgangstext

    example_messages = ExampleMessages(example_user_input, example_system_prompt, example_response)
    service = FlashCardGenerator(os.getenv('OPENAI_API_KEY'), example_messages)
    deck = service.generate(user_input, system_prompt)
    deck.save_as_csv(csv_path)