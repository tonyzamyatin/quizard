# External packages
from openai import OpenAI
from flask import request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
import redis
# Setup
from ..utils.global_helpers import configure_logging, load_yaml_config, get_env_variable
from .celery_config import create_celery_app
from .tasks import generate_flashcards_task
from .flask_factory import create_flask_app
# Exceptions
from ..custom_exceptions.env_exceptions import EnvironmentLoadingError

# Configure logging -- This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, '..', 'config')
log_dir = os.path.join(backend_root_dir, '..', 'logs')
configure_logging(log_dir)

# Load environment
try:
    load_dotenv()
except:
    raise EnvironmentLoadingError("There was a problem loading .env.")
rabbit_user = get_env_variable("RABBITMQ_DEFAULT_USER")
rabbit_password = get_env_variable("RABBITMQ_DEFAULT_PASS")
rabbit_port = get_env_variable("RABBITMQ_PORT")
rabbit_host = get_env_variable("RABBITMQ_HOST")
redis_password = get_env_variable("REDIS_PASSWORD")
redis_host = get_env_variable("REDIS_HOST")
redis_port = get_env_variable("REDIS_PORT")
redis_db_id = get_env_variable("REDIS_PRIMARY_DB_ID")

# TODO: Do we need to connect DB if we use Celery?
r = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db_id,
    password=redis_password,
    decode_responses=True)

# Define broker and backend url for Celery task queue
celery_broker_url = "amqp://" + rabbit_user + ":" + rabbit_password + "@localhost:" + rabbit_port + "/" + rabbit_host
celery_result_backend = "redis://" + redis_password + "@" + redis_host + ":" + redis_port + "/" + redis_db_id

# Set up Flask and Celery
flask_app = create_flask_app(celery_broker_url, celery_result_backend)
celery_app = create_celery_app(flask_app)
CORS(flask_app)
api = Api(flask_app)


# TODO: Start celery workers

class FlashcardGenerator(Resource):
    def __init__(self):
        # TODO: Login and user authentication at some point
        self.client = OpenAI(api_key=get_env_variable("OPENAI_API_KEY"))
        self.run_config = load_yaml_config(config_dir, get_env_variable("GENERATED_CONFIG_FILE"))

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
        # To pass arguments to tasks, Celery has to serialize them to a format that it can pass to other processes. Therefore, passing complex objects
        # is not recommended. Pass the minimal amount of data necessary to fetch or recreate any complex data within the task.
        # TODO: Make sure all the arguments are serializable without problems.
        task = generate_flashcards_task.delay(self.client, self.run_config, model_name, lang, mode, input_text)

        # TODO: Look into streaming the flashcards using OpenAI and Flask streaming capabilities
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
    # Avoid using the flask.run method in production. Instead, use a production-grade server like Gunicorn or uWSGI
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
