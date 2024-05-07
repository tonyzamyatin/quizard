from flask import make_response, request
from flask_restful import Resource

from src.celery.tasks import flashcard_generator_task
from src.custom_exceptions.external_exceptions import ValidationError, ResultNotFoundError
from src.enums.generatorOptions import ExportFormat
from src.services.flashcard_service.flashcard_service import FlashcardService
from src.services.task_service.flashcard_generator_task_service import ITaskService


class FlashcardExporterResource(Resource):
    """
    API resource for exporting flashcards in the backend to a file.
    """

    def __init__(self, task_service: ITaskService, flashcard_service: FlashcardService):
        self.task_service = task_service
        self.flashcard_service = flashcard_service

    # flashcards/exporter/<token>?format=<file_format>
    def get(self, token):
        """
        flashcards/exporter/<token>?format=<file_format>
        Get the generated flashcards in the requested file format.
        Parameters
        ----------
        token: str
            The retrieval token for the flashcards.
        file_format: str
            The requested file type for the flashcards. Must be either 'csv' or 'apkg'.
        Returns
        -------
        Response
            The generated flashcards in the requested file format.

        Raises
        ------
        TokenAuthenticationError
            If the token is invalid.
        """
        file_format = request.args.get('format', default='', type=str)
        if file_format == '':
            raise ValidationError("File format not specified")
        try:
            file_format = ExportFormat[file_format]
        except ValueError:
            raise ValidationError(f"Unsupported file type: {file_format}")
        task_id = self.task_service.verify_retrival_token(token)
        flashcard_deck = self.task_service.get_task_result(task_id)
        file = self.flashcard_service.export_flashcard_deck(flashcard_deck, file_format)
        if file_format == 'csv':
            filename = "flashcards.csv"
            mimetype = "text/csv"
        elif file_format == 'anki':
            filename = "flashcards.apkg"
            mimetype = "application/x-sqlite3"

        response = make_response(file)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = mimetype
        return response
