# local_dev/run.py
import os
import structlog

from openai import OpenAI
from dotenv import load_dotenv

from config.logging_config import setup_logging
from src.services.flashcard_service import FlashcardService
from src.utils.file_util import load_yaml_config, read_file

# Assuming a project structure like:
# backend/
# ├── config/
# │   └── ...
# ├── local_dev/
# │   ├── run.py
# │   ├── input/
# │   └── output/
# ├── logs/
# │   └── ...
# ├── src/
# │   ├── flashcard_service/
# │   │   └── ...
# │   ├── rest/
# │   │   └── ...
# │   ├── utils/
# │   │   └── ...
# │   └── ...
# ├── tests/
# │   └── ...
# ├── .env
# └── ...
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_root_dir = os.path.join(backend_root_dir, 'local_dev', 'output')
config_dir = os.path.join(backend_root_dir, 'config')
log_dir = os.path.join(backend_root_dir, 'logs')


# Configure logging_config
setup_logging()
logger = structlog.getLogger(__name__)
logger.info("Logging setup complete.")
# Load environment variables
load_dotenv()
# Load configs
app_config = load_yaml_config(config_dir, 'quizard_config.yaml')
run_config = load_yaml_config(config_dir, 'run_config.yaml')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Get input text
input_text = read_file(str(os.path.join(backend_root_dir, 'local_dev', 'input', run_config['text_input'])))
# Get variable parameters from run_config
model_name = run_config['model_name']
lang = run_config['lang']
mode = run_config['mode']

# Initialize and run flashcard_service with the text_input
app = FlashcardService(openai=client, app_config=app_config, model_name=model_name, lang=lang, mode=mode)
flashcard_deck = app.generate(user_input=input_text)

# Save the output as csv file
flashcard_deck.save_as_csv(os.path.join(output_root_dir, run_config['run_name']))
