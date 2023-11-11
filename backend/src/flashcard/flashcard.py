import json
from enum import Enum


class FlashcardType(str, Enum): # define enum as subclass of string so it can be serialized
    UNKNOWN = 'UNKNOWN'
    DEFINITION = 'DEFINITION'
    OPEN_ENDED = 'OPEN_ENDED'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE'
    CLOZE = 'CLOZE'


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

    def to_json(self):
        return json.dumps(self, default=lambda obj: obj.__dict__)