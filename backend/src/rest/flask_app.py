# src.rest.flask_app.py

import structlog
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from config.logging_config import setup_logging
from src.injector.injector_setup import get_injector
from src.rest.resources.flashcard_exporter_resource import FlashcardExporterResource
from src.rest.resources.flashcard_generator_resource import FlashcardGeneratorResource
from src.rest.resources.health_check_resource import HealthCheckResource
from src.services.flashcard_service.flashcard_service import FlashcardService
from src.services.task_service.flashcard_generator_task_service import FlashcardGeneratorTaskService

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)

# Inject dependencies
injector = get_injector()
flask_app = injector.get(Flask)
task_service = injector.get(FlashcardGeneratorTaskService)
flashcard_service = injector.get(FlashcardService)

# Setup API
CORS(flask_app)
api = Api(flask_app)
api.add_resource(FlashcardGeneratorResource, '/flashcards/generator', resource_class_kwargs={'task_service': task_service})
api.add_resource(FlashcardExporterResource, '/flashcards/exporter', resource_class_kwargs={'task_service': task_service, 'flashcard_service': flashcard_service})
api.add_resource(HealthCheckResource, '/health')


if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    # flask_app.run(debug=True)
    # Avoid using the flask.run method in production. Instead, use a production-grade server like Gunicorn or uWSGI
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
    flask_app.run(debug=False, host='0.0.0.0', port=5000)
