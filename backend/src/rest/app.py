# External packages
import time
import openai
from openai import OpenAI
from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
# Setup
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config
from celery_config import init_celery
from tasks import generate_flashcards_task
# Exceptions
from backend.src.custom_exceptions.env_exceptions import EnvironmentLoadingError, InvalidEnvironmentVariableError
from backend.src.custom_exceptions.quizard_exceptions import ConfigLoadingError
from backend.src.custom_exceptions.api_exceptions import APIAuthenticationError

# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, '..', 'config')
log_dir = os.path.join(backend_root_dir, '..', 'logs')

# Global variables
env_openai_api_key = "OPENAI_API_KEY"
config_name = "run_config"
# Get urls of Redis server from .env
env_celery_broker_url = "CELERY_BROKER_URL"
env_celery_result_backend = "CELERY_RESULT_BACKEND"

# TODO: Setup Redis server and add the actual urls in .env OR just use Docker and a docker-compose.yml file in combination with a Docker image of a Red
# Redis service from Docker Hub. No need to install Redis or set up server manually -> speeds up development

# Redis is an open-source, in-memory data structure store, used as a database, cache, and message broker. It supports various data structures such as
# strings, hashes, lists, sets, and more. Redis has a high performance due to its in-memory nature, making it very suitable for tasks that require
# quick read/write operations.
# Since Redis stores all data in memory, make sure your server has enough RAM to handle your workload.
# Use tools like Flower for Celery to monitor task queues and workers.

# Set up Flask and Celery
app = Flask(__name__)
CORS(app)
api = Api(app)

try:
    load_dotenv()
except:
    raise EnvironmentLoadingError("There was a problem loading .env.")

try:
    celery_broker_url = os.getenv(env_celery_broker_url)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_celery_broker_url}' not found.")
try:
    celery_result_backend = os.getenv(env_celery_result_backend)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_celery_result_backend}' not found.")

# Update the config
app.config.update(
    CELERY_BROKER_URL=celery_broker_url,
    CELERY_RESULT_BACKEND=celery_result_backend
)

# Make celery after updating the config
celery = init_celery(app)


class FlashcardGenerator(Resource):
    def __init__(self):
        configure_logging(log_dir)

        try:
            load_dotenv()
        except:
            raise EnvironmentLoadingError("There was a problem loading .env.")

        # TODO: Login and user authentication at some point
        try:
            api_key = os.getenv(env_openai_api_key)
        except:
            raise InvalidEnvironmentVariableError(f"Environment variable '{env_openai_api_key}' not found.")

        try:
            openai.api_key = api_key
        except:
            raise APIAuthenticationError(f"Invalid OpenAI API key.")
        self.client = OpenAI(api_key=api_key)

        try:
            self.run_config = load_yaml_config(config_dir, config_name)
        except:
            raise ConfigLoadingError(f"Unable to fing '{config_name} in directory '{config_dir}'.")

    def post(self):
        # TODO: Log request + answer
        json_data = request.get_json(force=True)

        # TODO: Get following arguments from frontend
        input_text = json_data['inputText']
        lang = json_data["lang"]
        mode = json_data['mode']
        export_format = json_data["export_format"]
        model_name = "gpt-3.5-turbo-1106"  # TODO: Implement logic to choose model name based on the users tier (when we have user accounts)

        # Start the Celery task
        task = generate_flashcards_task.delay(self.client, self.run_config, model_name, lang, mode, input_text)

        # TODO: Look into streaming the flashcards using OpenAIs and Flasks streaming capabilities
        # TODO: Save flashcards to a database for persistent storage, user history, and service improvement
        return jsonify({'task_id': task.id}), 202

    # TODO: Implement get_status(task_id)


api.add_resource(FlashcardGenerator, '/api/v1/flashcards/generate')


class Progress(Resource):
    def get(self, task_id):
        task = generate_flashcards_task.AsyncResult(task_id)
        if task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'progress': task.info.get('processed', 0),
                'total': task.info.get('total', 1),
            }
        else:
            response = {'state': task.state}
        return jsonify(response)


api.add_resource(Progress, '/api/v1/flashcards/generate/progress/<task_id>')

if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
