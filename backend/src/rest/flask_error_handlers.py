# src/rest/flask_error_handlers.py
import pydantic
import structlog
from flask import jsonify
from humps import camelize
from werkzeug.exceptions import HTTPException
from openai import OpenAIError

from src.custom_exceptions import external_exceptions
from src.custom_exceptions.internal_exceptions import QuizardError

logger = structlog.get_logger(__name__)


def standard_error_response(error_code, error_name, description=None):
    data = {
        'name': error_name,
        'description': description
    }
    response = jsonify(camelize(data))
    response.status_code = error_code
    return response


def init_app(flask_app):
    @flask_app.errorhandler(HTTPException)
    def handle_exception(e):
        """Handle all HTTP exceptions."""
        return standard_error_response(e.code, e.name, e.description)

    @flask_app.errorhandler(external_exceptions.AuthenticationError)
    def handle_authentication_error(e):
        logger.error("Authentication error", error=e, exc_info=True)
        return standard_error_response(401, 'Authentication Error', str(e))

    @flask_app.errorhandler(external_exceptions.NotFoundException)
    def handle_not_found_error(e):
        logger.error("Not Found error", error=e, exc_info=True)
        return standard_error_response(404, 'Not Found', str(e))

    @flask_app.errorhandler((external_exceptions.ValidationError, pydantic.ValidationError))
    def handle_validation_error(e):
        logger.error("Validation error", error=e, exc_info=True)
        return standard_error_response(422, 'Validation Error', str(e))

    @flask_app.errorhandler(QuizardError)
    def handle_unexpected_error(e):
        """Handle Quizard errors specifically."""
        logger.error("Quizard-specific error", error=e, exc_info=True)
        return standard_error_response(500, 'Quizard Error', str(e))

    @flask_app.errorhandler(OpenAIError)
    def handle_unexpected_error(e):
        """Handle OpenAI errors specifically."""
        logger.error("OpenAI-specific error", error=e, exc_info=True)
        return standard_error_response(502, 'OpenAI Error', str(e))

    @flask_app.errorhandler(external_exceptions.HealthCheckError)
    def handle_health_check_error(e):
        logger.error("Health check error", error=e, exc_info=True)
        return standard_error_response(503, 'Service Unavailable', str(e))

    @flask_app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle all unexpected exceptions."""
        logger.error(f"Unexpected error", error=e, exc_info=True)
        return standard_error_response(500, 'Unexpected Error', str(e))
