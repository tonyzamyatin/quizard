import os
import openai
from dotenv import load_dotenv
from backend.src.app.app import FlashcardApp
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log, load_yaml_config, read_file

# Define backend This assumes that test.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_root_dir = os.path.join(os.path.dirname(backend_root_dir), 'output')
config_dir = os.path.join(backend_root_dir, 'config')
log_dir = os.path.join(backend_root_dir, 'logs')


if __name__ == '__test__':
    # Configure logging and load environment variables
    configure_logging()
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    run_config = load_yaml_config(config_dir, "run_config")
    test_config = load_yaml_config(config_dir, "test_config")

    start_log(log_dir)
    write_to_log(f"Running {test_config['test name']}\n")

    text_input = read_file(os.path.join(backend_root_dir, "input", test_config["text_input"]))

    # Initialize and run app with the text_input
    app = FlashcardApp(run_config)
    flashcard_deck = app.run(text_input)

    # Save the output as csv file
    flashcard_deck.save_as_csv(backend_root_dir, "output", test_config["test_name"])

