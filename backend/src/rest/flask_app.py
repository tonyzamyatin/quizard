# src.rest.flask_app.py

import structlog
from dependency_injector.wiring import Provide, inject
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.config.logging_config import setup_logging
from src.container import Container, get_container
from src.rest.resources.flashcard_exporter_resource import FlashcardExporterResource
from src.rest.resources.flashcard_generator_resource import FlashcardGeneratorResource
from src.rest.resources.health_check_resource import HealthCheckResource

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)


@inject
def setup_api(flask_app: Flask, task_service=Provide[Container.flashcard_generator_task_service],
              flashcard_service=Provide[Container.flashcard_service]) -> None:
    """
    Set up the Flask API endpoints. Must be called after the container is started, because the services are injected
    """
    CORS(flask_app)
    api = Api(flask_app)
    api.add_resource(FlashcardGeneratorResource,
                     '/flashcards/generator', '/flashcards/generator/<task_id>',
                     resource_class_kwargs={'task_service': task_service})
    api.add_resource(FlashcardExporterResource,
                     '/flashcards/exporter', '/flashcards/exporter/<token>',
                     resource_class_kwargs={'task_service': task_service, 'flashcard_service': flashcard_service})
    api.add_resource(HealthCheckResource, '/health')


if __name__ == '__main__':
    container = get_container()
    flask_app = container.flask_app()
    setup_api(flask_app)

    # TODO: Turn of debug mode and use production-ready server
    # flask_app.run(debug=True)
    # Avoid using the flask.run method in production. Instead, use a production-grade server like Gunicorn or uWSGI
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
    flask_app.run(debug=False, host='0.0.0.0', port=5000)
