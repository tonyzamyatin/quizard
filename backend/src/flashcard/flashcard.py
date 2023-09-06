import json
from enum import Enum


class FlashCardType(Enum):
    UNKNOWN = 0
    DEFINITION = 1
    OPEN_ENDED = 2
    CRITICAL_THINKING = 3
    QUIZ = 4
    CLOZE = 5


class FlashCard:
    def __init__(self, id: int, type: FlashCardType, frontside: str, backside: str):
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
