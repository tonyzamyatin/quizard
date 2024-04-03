# src/rest/flask_error_handlers.py

import structlog
from flask import jsonify
from humps import camelize
from werkzeug.exceptions import HTTPException
from openai import OpenAIError

from src.custom_exceptions.api_exceptions import HealthCheckError, TaskNotFoundError
from src.custom_exceptions.quizard_exceptions import ConfigLoadingError, QuizardError

logger = structlog.get_logger(__name__)


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


def init_app(flask_app):
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
