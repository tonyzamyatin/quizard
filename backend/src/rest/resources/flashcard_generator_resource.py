# src/rest/resources/flashcard_generator_resource.py

import structlog
from flask import request, jsonify
from flask_restful import Resource
from humps import decamelize, camelize

from src.custom_exceptions.external_exceptions import TaskNotFoundError
from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.dtos.generator_task_info import GeneratorTaskInfoDto
from src.enums.task_states import TaskState
from src.services.task_service.task_service_interface import ITaskService
from src.utils.formatting_util import truncate_text

# Configure logging
logger = structlog.get_logger(__name__)


class FlashcardGeneratorResource(Resource):
    """
    API resource for generating flashcards.

    This resource handles POST requests to initiate flashcard generation tasks.
    """

    def __init__(self, task_service: ITaskService):
        self.task_service = task_service

    # flashcards/generator
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
        logger.info(
            "Received flashcard generation request",
            request_data={k: truncate_text(v) if k == "input_text" else v for k, v in json_data.items()}
        )
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

    # flashcards/generator/<task_id>
    def get(self, task_id):
        """
        Get the current progress or result of the flashcard generation task.
        """
        logger.info("Received task status request", task_id=task_id)
        task_response_dto = create_task_info_dto(self.task_service, task_id)
        response = jsonify(camelize(task_response_dto.dict()))
        if task_response_dto.task_state == TaskState.success:
            response.status_code = 200
        else:
            # Task did not complete yet, errors are handle by flask_error_handlers.py
            response.status_code = 202
        logger.info("Returning task status", task_id=task_id, task_response_dto=task_response_dto)
        return response

    # flashcards/generator/<task_id>
    def delete(self, task_id):
        """
        Cancel a flashcard generation task.
        Parameters
        ----------
        task_id
            The ID of the task to cancel.
        """
        logger.info("Received request to cancel task", task_id=task_id)
        self.task_service.cancel_task(task_id)
        logger.info("Task cancelled successfully", task_id=task_id)
        return {"message": "Cancellation successful"}, 200


def create_task_info_dto(task_service: ITaskService, task_id: str) -> GeneratorTaskInfoDto:
    task_state = task_service.get_task_state(task_id)
    task_info = task_service.get_task_info(task_id)
    current_batch = task_info.get('current_batch', None)
    total_batches = task_info.get('total_batches', None)

    task_info_dto = GeneratorTaskInfoDto(
        task_state=task_state,
        current_batch=current_batch,
        total_batches=total_batches)
    if task_state == TaskState.success:
        retrieval_token = task_service.generate_retrieval_token(task_id)
        task_info_dto.retrieval_token = retrieval_token
    elif task_state == 'REVOKED':
        raise TaskNotFoundError(f"Task with ID {task_id} was revoked")
    return task_info_dto
