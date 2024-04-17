# src.rest.api.py

import structlog
from flask_restful import Api
from flask_cors import CORS
from injector import Injector

from src.celery.celery import setup_applications
from config.logging_config import setup_logging
from src.rest.resources.flashcard_retriever_resource import FlashcardRetrieverResource
from src.rest.resources.flashcard_generator_resource import FlashcardGeneratorResource
from src.rest.resources.health_check_resource import HealthCheckResource
from src.injector import TaskServiceModule
from src.services.task_service.flashcard_generator_task_service import FlashcardGeneratorTaskService
from src.utils.global_helpers import get_env_variable

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)

# Create Flask and Celery apps
flask_app, celery_app = setup_applications()
flask_app.config['SECRET_KEY'] = get_env_variable('SECRET_KEY')

# Setup API
CORS(flask_app)
api = Api(flask_app)

# Initialize the Injector
injector = Injector([TaskServiceModule()])

# Get the TaskService instance from the injector
task_service = injector.get(FlashcardGeneratorTaskService)

api.add_resource(FlashcardGeneratorResource, '/flashcards/generator', resource_class_kwargs={'task_service': task_service})
api.add_resource(FlashcardRetrieverResource, '/flashcards/retriever', resource_class_kwargs={'task_service': task_service})
api.add_resource(HealthCheckResource, '/health')


if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    # flask_app.run(debug=True)
    # Avoid using the flask.run method in production. Instead, use a production-grade server like Gunicorn or uWSGI
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
    flask_app.run(debug=False, host='0.0.0.0', port=5000)
