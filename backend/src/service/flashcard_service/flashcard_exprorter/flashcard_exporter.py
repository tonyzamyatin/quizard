import csv
import random
import zipfile
from io import StringIO, BytesIO

import genanki

from src.custom_exceptions.quizard_exceptions import UnsupportedOptionError
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck


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


def _save_as_csv(flashcard_deck: FlashcardDeck) -> bytes:
    """
    Returns a ZIP containing the flashcard deck as a CSV file.
    """
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    for flashcard in flashcard_deck.flashcards:
        csv_writer.writerow([flashcard.front_side, flashcard.back_side])

    csv_buffer.seek(0)  # Rewind the buffer to the beginning

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('flashcards.csv', csv_buffer.getvalue())

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def _create_anki_deck(deck_name: str, flashcard_deck: FlashcardDeck) -> genanki.Deck:
    model_id = random.randrange(1 << 30, 1 << 31)
    my_model = genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ])

    deck_id = random.randrange(1 << 30, 1 << 31)
    anki_deck = genanki.Deck(deck_id, deck_name)

    for flashcard in flashcard_deck.flashcards:
        note = genanki.Note(model=my_model, fields=[flashcard.front_side, flashcard.back_side])
        anki_deck.add_note(note)

    return anki_deck


def _save_anki_deck(anki_deck: genanki.Deck) -> bytes:
    apkg_buffer = BytesIO()
    genanki.Package(anki_deck).write_to_file(apkg_buffer)
    apkg_buffer.seek(0)  # Rewind the buffer to the beginning
    return apkg_buffer.getvalue()


class FlashcardExporter:
    EXPORT_FORMATS = ['csv', 'apkg', 'list']

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
            return _save_as_csv(flashcard_deck)
        if self.export_format == 'apkg':
            anki_deck = _create_anki_deck('flashcards', flashcard_deck)
            return _save_anki_deck(anki_deck)
        if self.export_format == 'list':
            flashcard_dict_list = [{'id': card.id, 'type': card.type,
                                    'frontSide': card.front_side, 'backSide': card.back_side}
                                   for card in flashcard_deck.flashcards]
            return flashcard_dict_list
