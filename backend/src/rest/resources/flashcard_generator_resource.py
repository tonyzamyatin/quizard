# src/rest/resources/flashcard_generator_resource.py
# TODO: Throw exceptions with descriptive error messages instead of generic ones

import structlog
from flask import request, jsonify
from flask_restful import Resource
from humps import decamelize, camelize

from config.logging_config import setup_logging
from src.custom_exceptions.external_exceptions import TaskNotFoundError
from src.dtos.flashcard_generator_task_dto import FlashcardGeneratorTaskDto
from src.services.task_service.flashcard_generator_task_service import IFlashcardGeneratorTaskService

# Configure logging
setup_logging()
logger = structlog.get_logger(__name__)


class FlashcardGeneratorResource(Resource):
    """
    API resource for generating flashcards.

    This resource handles POST requests to initiate flashcard generation tasks.
    """

    def __init__(self, task_service: IFlashcardGeneratorTaskService):
        self.task_service = task_service

    # flashcards/generate
    def post(self):
        """
        Handle POST requests to initiate a flashcard generation task.
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
        json_data = decamelize(request.get_json(force=True))
        # Validate expected json format here and raise custom KeyError
        flashcard_task_dto = FlashcardGeneratorTaskDto(
            lang=json_data["lang"],
            mode=json_data["mode"],
            export_format=json_data["export_format"],
            input_text=json_data["input_text"]
        )

        task_id = self.task_service.start_task(flashcard_task_dto)
        logger.info("Started flashcard generator task", task_id=task_id)
        response_data = {'task_id': task_id}
        logger.info("Returning JSON response", response_data=response_data)
        response = jsonify(camelize(response_data))
        response.status_code = 202
        return response

    # flashcards/generate/<task_id>
    def get(self, task_id):
        """
        Get the current progress or result of the flashcard generation task.
        """
        task_state = self.task_service.get_task_state(task_id)
        task_info = self.task_service.get_task_info(task_id)

        data = {'state': task_state}
        response = jsonify(camelize(data))  # Default response containing task state

        if task_state == 'PROCESSING' or task_state == 'STARTED' or task_state == 'PENDING':
            if task_info is None:
                # Task with specified ID does not exist
                raise TaskNotFoundError(task_id)
            else:
                data.update({
                    'progress': task_info.get('progress'),
                    'total': task_info.get('total'),
                })
                response = jsonify(camelize(data))
                response.status_code = 202
        elif task_state == 'SUCCESS':
            data['download_token'] = self.task_service.generate_retrieval_token(task_id)
            response = jsonify(camelize(data))
            response.status_code = 200
        elif task_state == 'CANCELLED':
            response.status_code = 410
        return response

    # flashcards/generate/<task_id>
    def delete(self, task_id):
        """
        Cancel a flashcard generation task.
        Parameters
        ----------
        task_id
            The ID of the task to cancel.
        """
        self.task_service.cancel_task(task_id)
        return {"message": "Cancellation successful"}, 200
