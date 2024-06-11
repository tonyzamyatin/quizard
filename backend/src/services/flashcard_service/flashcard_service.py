# src/flashcard_service/flashcard_service.py
from typing import Optional, Callable

from dependency_injector.wiring import inject, Provide

from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck
from src.enums.generatorOptions import ExportFormat
from src.container import Container
from src.services.flashcard_service.flashcard_export import export_as_apkg, export_as_csv


# TODO: Validate DTOs (especially length of input text!)

class FlashcardService:
    """
    Service for everything flashcard related.
    """

    @inject
    def __init__(self, flashcard_generator=Provide[Container.flashcard_generator]):
        self.flashcard_generator = flashcard_generator

    def generate_flashcard_deck(self, flashcards_request_dto: FlashcardGeneratorTaskDto,
                                fn_update_progress: Optional[Callable[[int, int], None]]) -> FlashcardDeck:
        return self.flashcard_generator.generate_flashcard_deck(flashcards_request_dto, fn_update_progress)

    @staticmethod
    def export_flashcard_deck(flashcard_deck: FlashcardDeck, export_format: ExportFormat) -> bytes:
        """
        Exports the generated flashcards to the specified format.

        Parameters
        ----------
        flashcard_deck : FlashcardDeck
            The deck of generated flashcards.
        export_format : ExportFormat
            The format in which to export the flashcards.

        Returns
        -------
        bytes
            The exported flashcards in the specified format.
        """
        if export_format == ExportFormat.anki:
            return export_as_apkg(flashcard_deck)
        elif export_format == ExportFormat.csv:
            return export_as_csv(flashcard_deck)
