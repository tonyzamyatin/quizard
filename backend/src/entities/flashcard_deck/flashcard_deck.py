# src/flashcard_service/flashcard_deck/flashcard_deck.py
import json
import os
import zipfile
from typing import List
from src.entities.flashcard.flashcard import Flashcard


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
        DEPRECATED
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
