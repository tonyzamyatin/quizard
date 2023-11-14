import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.src.app.app import FlashcardApp
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config, read_file
from backend.src.custom_exceptions.env_exceptions import EnvironmentLoadingError, InvalidEnvironmentVariableError
from backend.src.custom_exceptions.quizard_exceptions import ConfigLoadingError

# Define backend This assumes that test.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_root_dir = os.path.join(os.path.dirname(backend_root_dir), 'output')
config_dir = os.path.join(backend_root_dir, 'config')
log_dir = os.path.join(backend_root_dir, 'logs')


# Configure logging and load environment variables
configure_logging(log_dir)
load_dotenv()
run_config = load_yaml_config(config_dir, "run_config")
test_config = load_yaml_config(config_dir, "test_config")
print(test_config)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

start_log(log_dir)

# TODO: Make log class with global variable log_dir, else it creates a log file in src each time.
# TODO: Fix logging (logging is fucked up) and add timestamps to each log.
write_to_log_and_print(f"Running {test_config['test_name']}\n")

text_input = read_file(os.path.join(backend_root_dir, "input", test_config["text_input"]))
lang = run_config["flashcard_generation"]["lang"]
mode = run_config["flashcard_generation"]["mode"]

# Initialize and run app with the text_input
app = FlashcardApp(client=client, config=run_config, model_name="gpt-3.5-turbo-1106", lang=lang, mode=mode)
flashcard_deck = app.run(text_input)

# Save the output as csv file
flashcard_deck.save_as_csv(os.path.join(output_root_dir, test_config["test_name"]))

