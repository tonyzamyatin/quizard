# src.rest.app.py
import os

import structlog
from humps import camelize, decamelize
from celery.exceptions import TaskError
from flask import request, jsonify, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from itsdangerous import URLSafeSerializer, BadSignature
from openai import OpenAIError
from werkzeug.exceptions import HTTPException

from src.celery.celery import setup_applications
from src.custom_exceptions.api_exceptions import HealthCheckError, TaskNotFoundError
from src.custom_exceptions.quizard_exceptions import ConfigLoadingError, QuizardError
from config.logging_config import setup_logging
from src.service.flashcard_service.flashcard_service import FlashcardService
from src.utils.global_helpers import load_yaml_config, get_env_variable, validate_config_param
from src.rest.tasks import generate_flashcards_task

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)

# Configure logging_config -- This assumes that flashcard_service.py is in backend_root/src/rest
backend_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_dir = os.path.join(backend_root_dir, 'config')

# Create Flask and Celery apps
flask_app, celery_app = setup_applications()
flask_app.config['SECRET_KEY'] = get_env_variable('SECRET_KEY')
# Setup API
CORS(flask_app)
api = Api(flask_app)


def standard_error_response(error_code, error_message, description=None):
    data = {
        'error': {
            'code': error_code,
            'message': error_message,
            'description': description
        }
    }
    response = jsonify(camelize(data))
    response.status_code = error_code
    return response


@flask_app.errorhandler(HTTPException)
def handle_exception(e):
    """Handle all HTTP exceptions."""
    return standard_error_response(e.code, e.name, e.description)


@flask_app.errorhandler(OpenAIError)
def handle_unexpected_error(e):
    """Handle OpenAI errors specifically."""
    logger.error("OpenAI-specific error", error=e, exc_info=True)
    return standard_error_response(502, 'OpenAI Error', str(e))


@flask_app.errorhandler(QuizardError)
def handle_unexpected_error(e):
    """Handle Quizard errors specifically."""
    logger.error("Quizard-specific error", error=e, exc_info=True)
    return standard_error_response(500, 'Quizard Error', str(e))


@flask_app.errorhandler(HealthCheckError)
def handle_health_check_error(e):
    logger.error("Health check error", error=e, exc_info=True)
    return standard_error_response(503, 'Service Unavailable', str(e))


@flask_app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Handle all unexpected exceptions."""
    logger.error(f"Unexpected error", error=e, exc_info=True)
    return standard_error_response(500, 'Unexpected Error', str(e))


def _get_task_response_dict(task):
    """Constructs a response dict based on the task state."""
    data = {'state': task.state}
    if task.state == 'PROCESSING' or task.state == 'STARTED' or task.state == 'PENDING':
        data.update({
            'progress': task.info.get('progress', 0),
            'total': task.info.get('total', 1),  # Avoid division by zero
        })
    elif task.state == 'SUCCESS':
        data['download_token'] = generate_download_token(task.id)
        data['progress'] = 1
        data['total'] = 1
    elif task.state == 'FAILURE':
        logger.error("Task failed", error=task.error, exc_info=True)
        data['error'] = str(task.error)  # Assuming task.error contains error
        task.forget()
    return data


def generate_download_token(task_id):
    s = URLSafeSerializer(flask_app.config['SECRET_KEY'])
    return s.dumps(task_id)


def verify_download_token(token):
    s = URLSafeSerializer(flask_app.config['SECRET_KEY'])
    try:
        task_id = s.loads(token)
        return task_id
    except BadSignature:
        return None


class FlashcardGenerator(Resource):
    """
    API resource for generating flashcards.

    This resource handles POST requests to initiate flashcard generation tasks.
    """

    def __init__(self):
        """
        Initialize the FlashcardGenerator resource.

        Raises
        ------
        ConfigLoadingError
            If the configuration file for the generator cannot be loaded, this error is raised.
        """
        try:
            self.app_config = load_yaml_config(config_dir, get_env_variable("GENERATOR_CONFIG_FILE"))
        except ConfigLoadingError as e:
            logger.critical(f"Failed to load critical application configuration", error=str(e), exc_info=True)
            raise ConfigLoadingError(f"Failed to load critical application configuration")
            # shutdown_application(celery_app=celery_app, reason="Failed to load critical application configuration.", error_info={'error': str(e)})

    # flashcards/generate       (post mapping)
    def post(self):
        """
        Handle POST requests to initiate a flashcard generation task.
        # TODO: Validate expected JSON format
        Returns
        -------
        Response
            JSON response containing the task ID if successful, or an error message.

        Raises
        ------
        OpenAIError
            If an error occurs while interacting with the OpenAI API.
        QuizardError
            If a Quizard-specific error occurs during the processing.
        Exception
            For any other unforeseen exceptions.
        """
        try:
            json_data = decamelize(request.get_json(force=True))
            # Validate expected json format here and raise custom KeyError

            validate_config_param(json_data["mode"], FlashcardService.GENERATION_MODE)
            validate_config_param(json_data["lang"], FlashcardService.SUPPORTED_LANGS)
            task = generate_flashcards_task.delay(
                config=self.app_config,
                model_name=json_data["model_name"],
                lang=json_data["lang"],
                mode=json_data["mode"],
                export_format=json_data["export_format"],
                input_text=json_data["input_text"]
            )
            logger.info("Flashcard generation task started", task_id=task.id)
            logger.info("Returning JSON response", response_data={'task_id': task.id})
            response_data = camelize({'task_id': task.id})
            response = jsonify(response_data)
            response.status_code = 202
            return response
        except OpenAIError as e:
            logger.error("OpenAI-specific error", error=e, exc_info=True)
            raise
        except QuizardError as e:
            logger.error("Quizard-specific error", error=e, exc_info=True)
            raise
        # Catch custom key error here and raise an HTTP exception to be caught by Flask's exception handler
        except Exception as e:
            logger.error(f"Unexpected error", error=e, exc_info=True)
            raise

    # flashcards/generate/<task_id>     (get mapping)
    @staticmethod
    def get(task_id):
        """
        Get the current progress or result of the flashcard generation task.
        """
        try:
            task = generate_flashcards_task.AsyncResult(task_id)
            if task is None:
                logger.warning(f"Task not found with taskId: {task_id}")
                raise TaskNotFoundError(f"Unable to retrieve task with taskId: {task_id}")
            data = _get_task_response_dict(task)
            response = jsonify(camelize(data))
            if task.state == 'PROCESSING' or task.state == 'STARTED' or task.state == 'PENDING':
                response.status_code = 202
            elif task.state == 'SUCCESS':
                response.status_code = 200
            elif task.state == 'CANCELLED':
                response.status_code = 502
            elif task.state == 'FAILURE':
                response.status_code = 500  # or another appropriate 4xx or 5xx code
            return response
        except OpenAIError as e:
            logger.error("OpenAI-specific error", error=e, exc_info=True)
            return jsonify({'error': str(e)}), 502
        except QuizardError as e:
            logger.error("Quizard-specific error", error=e, exc_info=True)
            return jsonify({'error': str(e)}), 500
        except TaskError as e:
            logger.warning(f"Task not found with taskId: {task_id}")
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Unexpected error", error=e, exc_info=True)
            return jsonify({'error': str(e)}), 500

    # flashcards/generate/<task_id> (delete mapping)
    @staticmethod
    def delete(task_id):
        try:
            celery_app.control.revoke(task_id, terminate=True)
            return {"message": "Cancellation successful"}, 200
        except Exception as e:
            logger.error(f"Failed to cancel celery task {task_id}", error=str(e), exc_info=True)
            return {"error": str(e)}, 500


api.add_resource(FlashcardGenerator, '/flashcards/generate')


@flask_app.route('/flashcards/download/<token>')
def download_file(token):
    task_id = verify_download_token(token)
    if task_id:
        task = generate_flashcards_task.AsyncResult(task_id)
        if task.state == 'SUCCESS':
            file_content = task.result  # file content in bytes
            file_type = task.info.get('file_type')

            if file_type == 'csv':
                filename = "flashcards.csv"
                mimetype = "text/csv"
            elif file_type == 'anki':
                filename = "flashcards.apkg"
                mimetype = "application/x-sqlite3"
            else:
                return "Unsupported file type", 400

            response = make_response(file_content)
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = mimetype
            return response
        else:
            return "File not available", 404
    else:
        return "Invalid or expired download link", 403


@flask_app.route('/health')
def health_check():
    missing_vars = []
    critical_vars = ["GENERATOR_CONFIG_FILE", "OPENAI_API_KEY", "RABBITMQ_DEFAULT_USER", "RABBITMQ_DEFAULT_PASS",
                     "RABBITMQ_HOST", "RABBITMQ_PORT",
                     "REDIS_HOST", "REDIS_PORT", "REDIS_PRIMARY_DB_ID"]

    for var in critical_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        logger.critical(f"Missing critical environment variables", missing_vars=missing_vars)
        raise HealthCheckError(f"Missing critical environment variables: {', '.join(missing_vars)}")
    else:
        health_status = "healthy"
        http_status = 200
        message = "All systems operational"

    response = jsonify({"status": health_status, "message": message})
    response.status_code = http_status
    return response


if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    # flask_app.run(debug=True)
    # Avoid using the flask.run method in production. Instead, use a production-grade server like Gunicorn or uWSGI
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
    flask_app.run(debug=False, host='0.0.0.0', port=5000)
