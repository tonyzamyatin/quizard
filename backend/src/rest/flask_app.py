# src.rest.flask_app.py

import structlog
from dependency_injector.wiring import Provide, inject
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.config.logging_config import setup_logging
from src.container import Container, get_container
from src.custom_exceptions.internal_exceptions import InvalidEnvironmentVariableError
from src.rest.resources.flashcard_exporter_resource import FlashcardExporterResource
from src.rest.resources.flashcard_generator_resource import FlashcardGeneratorResource
from src.rest.resources.health_check_resource import HealthCheckResource
from src.utils.env_util import get_env_variable

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)

flashcards_base_url = '/api/flashcards'
flashcard_generator_url = f'{flashcards_base_url}/generator'
flashcard_exporter_url = f'{flashcards_base_url}/exporter'


@inject
def setup_api(flask_app: Flask, task_service=Provide[Container.flashcard_generator_task_service],
              flashcard_service=Provide[Container.flashcard_service]) -> None:
    """
    Set up the Flask API endpoints. Must be called after the container is started, because the services are injected
    """
    CORS(flask_app)
    api = Api(flask_app)
    api.add_resource(FlashcardGeneratorResource,
                     flashcard_generator_url, f'{flashcard_generator_url}/<task_id>',
                     resource_class_kwargs={'task_service': task_service})
    api.add_resource(FlashcardExporterResource,
                     flashcard_exporter_url, f'{flashcard_exporter_url}/<token>',
                     resource_class_kwargs={'task_service': task_service, 'flashcard_service': flashcard_service})
    api.add_resource(HealthCheckResource, '/health')


if __name__ == '__main__':
    container = get_container()
    flask_app = container.flask_app()
    setup_api(flask_app)

    try:
        environment = get_env_variable('ENVIRONMENT')
    except InvalidEnvironmentVariableError:
        environment = 'production'
    if environment == 'development':
        logger.info("Starting Flask development server...")
        flask_app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.info("WSGI server (Gunicorn or similar) will run Flask in production.")