from src.custom_exceptions.quizard_exceptions import UnsupportedOptionError
from src.flashcard_service.flashcard_deck.flashcard_deck import FlashcardDeck


def validate_export_format(export_format: str):
    """
    Validates the provided export format against the set of accepted export formats.

    Parameters
    ----------
    export_format : str
        The export format for the flashcards

    Raises
    ------
    UnsupportedOptionError
        If the paramet is invalid.
    """
    if export_format.lower() not in FlashcardExporter.EXPORT_FORMATS:
        raise UnsupportedOptionError(f"Invalid export format: {export_format}. Expected one of {FlashcardExporter.EXPORT_FORMATS}.")


class FlashcardExporter:
    EXPORT_FORMATS = ['csv', 'anki', 'list']

    def __init__(self, export_format: str) -> None:
        validate_export_format(export_format)
        self.export_format = export_format

    def export_flashcard_deck(self, flashcard_deck: FlashcardDeck):
        """
        Parameters
        ----------
        flashcard_deck : FlashcardDeck
            The flashcard deck to export

        Returns
        -------
            A zip file with the exported flashcards.
        """
        if self.export_format == 'csv':
            return flashcard_deck.to_csv_zip()
        if self.export_format == 'list':
            flashcard_dict_list = [{'id': card.id, 'type': card.type,
                                    'frontSide': card.front_side, 'backSide': card.back_side}
                                   for card in flashcard_deck.flashcards]
            return flashcard_dict_list
        # TODO: implement Anki Export
