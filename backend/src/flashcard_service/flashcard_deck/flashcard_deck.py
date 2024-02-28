import json
import os
import zipfile
from io import StringIO, BytesIO
from typing import List
from src.flashcard_service.flashcard.flashcard import Flashcard


def _create_note_model_and_note(flashcard: Flashcard):
    """
    Creates a note model and note for a given flashcard.

    Parameters
    ----------
    flashcard : Flashcard
        The flashcard to create the model and note for.

    Returns
    -------
    tuple
        A tuple containing the note model and note.
    """
    note_model = {
        "name": "Basic",
        "fields": [
            {"name": "Front"},
            {"name": "Back"}
        ],
        "templates": [
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": "{{FrontSide}}<hr id=\"answer\">{{Back}}"
            }
        ]
    }
    note = {
        "deckName": "My Deck",
        "modelName": "Basic",
        "fields": {
            "Front": flashcard.front_side,
            "Back": flashcard.back_side
        },
        "tags": []
    }
    return note_model, note


class FlashcardDeck:
    """
    A class used to represent a deck of flashcards.

    ...

    Attributes
    ----------
    flashcards : List[Flashcard]
        a list of Flashcard objects

    Methods
    -------
    save_as_csv(filename: str):
        Saves the flashcard deck as a CSV file.

    sava_as_apkg(filename: str, media_files: List[str] = None):
        Saves the flashcard deck as an Anki package file (apkg).
        (Still n development, not tested)
    """

    def __init__(self, flashcards: List[Flashcard]):
        """
        Parameters
        ----------
        flashcards : List[Flashcard]
            a list of Flashcard objects to be included in the deck
        """
        self.flashcards = flashcards

    def __str__(self):
        return self.to_json()

    def to_json(self) -> str:
        return json.dumps(self, indent=4, default=vars)

    def to_dict_list(self):
        flashcard_dict_list = [{'id': card.id, 'type': card.type,
                                'frontSide': card.front_side, 'backSide': card.back_side}
                               for card in self.flashcards]
        return flashcard_dict_list

    def save_as_csv(self, filename: str):
        """
        Saves the flashcard deck as a CSV file.

        Parameters
        ----------
        filename : str
            The name of the file to save the deck to.

        Raises
        ------
        IOError
            If the file cannot be written.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for flashcard in self.flashcards:
                    f.write(flashcard.as_csv())
                    f.write('\n')
        except IOError as e:
            raise IOError(f"Failed to write to file {filename}: {e}")

    def save_as_apkg(self, filename: str, media_files: List[str] = None):
        """
        Saves the flashcard deck as an Anki package file (apkg).

        TODO: Complete the implementation of this method and ensure it works correctly.
        TODO: Add support for various features like media files, different note types, etc.

        Parameters
        ----------
        filename : str
            The name of the file to save the deck to.
        media_files : List[str], optional
            A list of media files to include in the package.

        Raises
        ------
        IOError
            If there is an error in creating or writing to the zip file.
        """
        try:
            with zipfile.ZipFile(filename, 'w') as zipf:
                media_files = media_files or []
                for media_file in media_files:
                    zipf.write(media_file, os.path.join('collection.media', os.path.basename(media_file)))

                collection_data = {
                    "note_models": [],
                    "notes": []
                }
                for flashcard in self.flashcards:
                    note_model, note = _create_note_model_and_note(flashcard)
                    collection_data["note_models"].append(note_model)
                    collection_data["notes"].append(note)

                zipf.writestr('collection.anki2', json.dumps(collection_data))
        except IOError as e:
            raise IOError(f"Failed to create or write to APKG file {filename}: {e}")
