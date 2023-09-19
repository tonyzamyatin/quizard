import json
from typing import List

from backend.src.flashcard.flashcard import Flashcard


class FlashcardDeck:
    def __init__(self, flashcards: List[Flashcard]):
        self.flashcards = flashcards

    def __str__(self):
        return json.dumps(self, indent=4, default=vars)

    def save_as_csv(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            for flashcard in self.flashcards:
                f.write(flashcard.as_csv())
                f.write('\n')
