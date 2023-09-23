import json
from enum import Enum


class FlashcardType(Enum):
    UNKNOWN = 0
    DEFINITION = 1
    OPEN_ENDED = 2
    MULTIPLE_CHOICE = 3
    CLOZE = 5


class Flashcard:
    def __init__(self, id: int, type: FlashcardType, frontside: str, backside: str):
        self.id = id
        self.type = type
        self.frontside = frontside
        self.backside = backside

    def __str__(self):
        return (f'[{self.type.name}]\n'
                f'Front side: {self.frontside}\n'
                f'Back side: {self.backside}\n')

    def as_csv(self) -> str:
        return self.frontside + ';' + self.backside
