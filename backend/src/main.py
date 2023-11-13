import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.src.app.app import FlashcardApp
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config

# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, 'config')
log_dir = os.path.join(backend_root_dir, 'logs')

if __name__ == '__main__':
    # Configure logging and load environment variables
    configure_logging(log_dir)
    load_dotenv()

    # TODO: Login and user authentication

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    run_config = load_yaml_config(config_dir, "run_config")

    # Use Flask app to get text input from user, either as a .txt or as a pdf.
    # TODO: Build PDF reader
    text_input = ""

    # Initialize and run app with the text_input
    app = FlashcardApp(run_config, client)
    flashcard_deck = app.run(text_input)

    # Return the flashcard deck as a downloadable .csv file using Flask
    # TODO: Return as downloadable Anki Deck.

    # TODO: Enable users to connect their Anki Account and export their flashcards directly there.
    # https://foosoft.net/projects/anki-connect/

    #  TODO: Eventually create a flashcard studying tool on the website.
