# External packages
import openai
from openai import OpenAI
from flask import request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
import redis

from backend.src.rest.flask_factory import create_flask_app
# Setup
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config
from celery_config import create_celery_app
from tasks import generate_flashcards_task
# Exceptions
from backend.src.custom_exceptions.env_exceptions import EnvironmentLoadingError, InvalidEnvironmentVariableError
from backend.src.custom_exceptions.quizard_exceptions import ConfigLoadingError
from backend.src.custom_exceptions.api_exceptions import APIAuthenticationError

# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, '..', 'config')
log_dir = os.path.join(backend_root_dir, '..', 'logs')

# Define running configuration for flashcard generation
config_name = "run_config"

# Global variables with the keys in the .env file
env_openai_api_key = "OPENAI_API_KEY"
env_redis_password = "REDIS_PW"
env_redis_host = "REDIS_HOST"
env_redis_port = "REDIS_PORT"
env_redis_db_id = "REDIS_PRIMARY_DB_ID"

# Celery needs a broker to handle the messages and a backend to store the results. One option would be using a Redis server for both (or RabbitMQ as a
# broker.
# Redis is an open-source, in-memory data structure store, used as a database, cache, and message broker. It supports various data structures such as
# strings, hashes, lists, sets, and more. Redis has a high performance due to its in-memory nature, making it very suitable for tasks that require
# quick read/write operations.
# Since Redis stores all data in memory, make sure your server has enough RAM to handle your workload. Use tools like Flower for Celery to monitor
# task queues and workers. Remote control means the ability to inspect and manage workers at runtime using the 'celery inspect' and 'celery control'
# commands (and other tools using the remote control API).

# TODO: Setup Redis server and add the actual urls in .env.OR just use Docker and a docker-compose.yml file in combination with a Docker image of a
#  Redis service from Docker Hub. No need to install Redis or set up server manually -> speeds up development
# Using Redis: https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html#broker-redis
#


try:
    load_dotenv()
except:
    raise EnvironmentLoadingError("There was a problem loading .env.")

try:
    redis_password = os.getenv(env_redis_password)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_redis_password}' not found.")
try:
    redis_host_name = os.getenv(env_redis_host)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_redis_host}' not found.")
try:
    redis_port = os.getenv(env_redis_port)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_redis_port}' not found.")
try:
    redis_db_id = os.getenv(env_redis_db_id)
except:
    raise InvalidEnvironmentVariableError(f"Environment variable '{env_redis_db_id}' not found.")

# Do we need to connect DB if we use Celery?
r = redis.Redis(
    host=redis_host_name,
    port=redis_port,
    db=redis_db_id,
    password=redis_password,
    decode_responses=True)

celery_broker_url = "set broker urls"       # TODO: Use RabbitMQ as broker (avoid upgrading to Redis paid plan to use two databases)
celery_result_backend = "redis://" + redis_password + "@" + redis_host_name + ":" + redis_port + "/" + redis_db_id

# Set up Flask and Celery
flask_app = create_flask_app(celery_broker_url, celery_result_backend)
celery_app = create_celery_app(flask_app)
CORS(flask_app)
api = Api(flask_app)


# TODO: Start celery workers

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

        input_text = json_data['inputText']
        lang = json_data["lang"]
        mode = json_data['mode']
        export_format = json_data["export_format"]
        model_name = "gpt-3.5-turbo-1106"
        # TODO: Get model_name from config (for now), and later
        #  implement logic to choose model name based on the users tier (when we have user accounts).

        # Start the Celery task
        # To pass arguments to tasks, Celery has to serialize them to a format that it can pass to other processes. Therefore, passing complex objects is not recommended.
        # Pass the minimal amount of data necessary to fetch or recreate any complex data within the task.
        # TODO: Make sure all the arguments are serializable without problems.
        task = generate_flashcards_task.delay(self.client, self.run_config, model_name, lang, mode, input_text)

        # TODO: Look into streaming the flashcards using OpenAIs and Flasks streaming capabilities
        # TODO: Save flashcards to a database for persistent storage, user history, and improving flashcard generation.
        return jsonify({'task_id': task.id}), 202


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
            # TODO: Check whether task was successful. If so, retrieve flashcards from celery backend and include them in the response.
            #  Else catch the specific error and handle the error appropriately.
        return jsonify(response)


api.add_resource(Progress, '/api/v1/flashcards/generate/progress/<task_id>')

if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    flask_app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
