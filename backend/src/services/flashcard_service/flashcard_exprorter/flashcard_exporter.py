import csv
import random
import zipfile
from io import StringIO, BytesIO

import genanki
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck


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


def export_as_csv(flashcard_deck: FlashcardDeck) -> bytes:
    """
    Parameters
    ----------
    flashcard_deck : FlashcardDeck
        The flashcard deck to export

    Returns
    -------
    bytes
        The csv file containing the flashcards.
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


def export_as_apkg(flashcard_deck: FlashcardDeck) ->  bytes:
    """
    Parameters
    ----------
    flashcard_deck : FlashcardDeck
        The flashcard deck to export

    Returns
    -------
    bytes
        The apkg file containing the flashcards.
    """
    anki_deck = _create_anki_deck('flashcards', flashcard_deck)
    return _save_anki_deck(anki_deck)
