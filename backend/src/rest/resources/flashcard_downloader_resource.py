from flask import make_response
from flask_restful import Resource

from src.celery.tasks import flashcard_generator_task
from src.custom_exceptions.external_exceptions import ValidationError, ResultNotFoundError
from src.enums.export_format import ExportFormat
from src.services.flashcard_service.flashcard_service import FlashcardService
from src.services.task_service.flashcard_generator_task_service import ITaskService


class FlashcardDownloaderResource(Resource):
    """
    API resource for downloading flashcards from the backend.
    """

    def __init__(self, task_service: ITaskService, flashcard_service: FlashcardService):
        self.task_service = task_service
        self.flashcard_service = flashcard_service


    # flashcards/retriever/<token>
    def get(self, token, file_type: ExportFormat):
        """
        Get the generated flashcards in the requested file format.

        Parameters
        ----------
        token: str
            The retrieval token for the flashcards.
        file_type: ExportFormat
            The requested file type for the flashcards.

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
        flashcard_deck = self.task_service.get_task_result(task_id)
        file = self.flashcard_service.export_flashcard_deck(flashcard_deck, file_type)
        if file_type == 'csv':
            filename = "flashcards.csv"
            mimetype = "text/csv"
        elif file_type == 'anki':
            filename = "flashcards.apkg"
            mimetype = "application/x-sqlite3"
        else:
            raise ValidationError("Unsupported file type")

        response = make_response(file)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = mimetype
        return response
