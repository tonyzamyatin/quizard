import os

import structlog
from celery.exceptions import TaskError
from flask import request, jsonify, make_response
from flask_restful import Resource, Api
from flask_cors import CORS
from openai import OpenAI, OpenAIError
from werkzeug.exceptions import HTTPException

from src.celery.celery import setup_applications
from src.custom_exceptions.api_exceptions import HealthCheckError, TaskNotFoundError
from src.custom_exceptions.quizard_exceptions import ConfigLoadingError, QuizardError
from config.logging_config import setup_logging
from src.flashcard_service.flashcard_service import FlashcardService
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
    response = jsonify(data)
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
            raise ConfigLoadingError(f"Failed to load critical application configuration")
            # shutdown_application(celery_app=celery_app, reason="Failed to load critical application configuration.", error_info={'error': str(e)})

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
            json_data = request.get_json(force=True)
            # Validate expected json format here and raise custom KeyError

            validate_config_param(json_data["mode"], FlashcardService.GENERATION_MODE)
            validate_config_param(json_data["lang"], FlashcardService.SUPPORTED_LANGS)
            task = generate_flashcards_task.delay(
                config=self.app_config,
                model_name=json_data["model_name"],
                lang=json_data["lang"],
                mode=json_data["mode"],
                input_text=json_data["input_text"]
            )
            logger.info("Flashcard generation task started", task_id=task.id)
            logger.info("Returning JSON response", response_data={'task_id': task.id})
            response = jsonify({'task_id': task.id})
            response.status_code = 202
            return response
        except OpenAIError:
            raise
        except QuizardError:
            raise
        # Catch custom key error here and raise an HTTP exception to be caught by Flask's exception handler
        except Exception:
            raise


api.add_resource(FlashcardGenerator, '/api/mvp/flashcards/generate/start')


class Progress(Resource):
    """
    API resource for tracking the progress of a flashcard generation task.
    """

    def get(self, task_id):
        """
        Get the current progress or result of the flashcard generation task.
        """
        try:
            task = generate_flashcards_task.AsyncResult(task_id)
            if task is None:
                raise TaskNotFoundError(f"Unable to retrieve task with taskId: {task_id}")
            data = self._get_task_response_dict(task)
            response = jsonify(data)
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
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Unexpected error", error=e, exc_info=True)
            return jsonify({'error': str(e)}), 500

    @staticmethod
    def _get_task_response_dict(task):
        """Constructs a response dict based on the task state."""
        data = {'state': task.state}
        if task.state == 'PROCESSING' or task.state == 'STARTED' or task.state == 'PENDING':
            data.update({
                'progress': task.info.get('progress', 0),
                'total': task.info.get('total', 1),  # Avoid division by zero
            })
        elif task.state == 'SUCCESS':
            data['flashcards'] = task.get(timeout=1)
            data['progress'] = 1
            data['total'] = 1
        elif task.state == 'FAILURE':
            logger.error("Task failed", error=task.error, exc_info=True)
            data['error'] = str(task.error)  # Assuming task.error contains error
            task.forget()
        return data


api.add_resource(Progress, '/api/mvp/flashcards/generate/progress/<task_id>')


@flask_app.route('/api/mvp/flashcards/generate/cancel/<task_id>')
def cancel_flashcards(task_id):
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": "Cancellation successful"}, 200
    except Exception as e:
        logger.error(f"Failed to cancel celery task {task_id}", error=str(e), exc_info=True)
        return {"error": str(e)}, 500


@flask_app.route('/api/mvp/health')
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
