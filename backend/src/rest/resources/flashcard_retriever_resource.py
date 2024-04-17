from flask import make_response
from flask_restful import Resource

from src.celery.tasks import flashcard_generator_task
from src.custom_exceptions.external_exceptions import ValidationError, ResultNotFoundError
from src.services.task_service.flashcard_generator_task_service import ITaskService


class FlashcardRetrieverResource(Resource):
    """
    API resource for retrieving flashcards from the backend.
    """

    def __init__(self, task_service: ITaskService):
        self.task_service = task_service

    # flashcards/retriever/<token>
    def get(self, token):
        """
        Get the generated flashcards in the requested file format.

        Parameters
        ----------
        token: str
            The retrieval token for the flashcards.

        Returns
        -------
        Response
            The generated flashcards in the requested file format.

        Raises
        ------
        TokenAuthenticationError
            If the token is invalid.
        """
        task_id = self.task_service.verify_retrival_token(token)
        task = flashcard_generator_task.AsyncResult(task_id)
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
                raise ValidationError("Unsupported file type")

            response = make_response(file_content)
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = mimetype
            return response
        else:
            raise ResultNotFoundError("File not available")
