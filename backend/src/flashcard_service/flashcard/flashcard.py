import json
from enum import Enum


class FlashcardType(str, Enum):
    """
    Enum class for different types of flashcards.

    Attributes
    ----------
    UNKNOWN : str
        Represents an unknown type of flashcard.
    DEFINITION : str
        Represents a definition type of flashcard.
    OPEN_ENDED : str
        Represents an open-ended question type of flashcard.
    MULTIPLE_CHOICE : str
        Represents a multiple-choice type of flashcard.
    CLOZE : str
        Represents a cloze deletion type of flashcard.
    """
    UNKNOWN = 'UNKNOWN'
    DEFINITION = 'DEFINITION'
    OPEN_ENDED = 'OPEN_ENDED'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE'
    CLOZE = 'CLOZE'


class Flashcard:
    """
    A class representing a flashcard.

    Parameters
    ----------
    id : int
        The unique identifier of the flashcard.
    type : FlashcardType
        The type of the flashcard (e.g., definition, multiple choice).
    front_side : str
        The content displayed on the front side of the flashcard.
    back_side : str
        The content displayed on the back side of the flashcard.

    Attributes
    ----------
    id : int
        The unique identifier of the flashcard.
    type : FlashcardType
        The type of the flashcard.
    front_side : str
        The content on the front side of the flashcard.
    back_side : str
        The content on the back side of the flashcard.
    """

    def __init__(self, id: int, type: FlashcardType, front_side: str, back_side: str):
        self.id = id
        self.type = type
        self.front_side = front_side
        self.back_side = back_side

    def __str__(self):
        """
        Create a string representation of the flashcard.

        Returns
        -------
        str
            A string describing the flashcard, including its type and content on both sides.
        """
        return (f'[{self.type.name}]\n'
                f'Front side: {self.front_side}\n'
                f'Back side: {self.back_side}\n')

    def as_csv(self) -> str:
        """
        Convert the flashcard to a CSV-compatible format.

        Returns
        -------
        str
            A string representing the flashcard in CSV format, with the front and back sides separated by a semicolon.
        """
        return self.front_side + ';' + self.back_side

    def to_json(self):
        """
        Convert the flashcard to a JSON format.

        Returns
        -------
        str
            A JSON string representing the flashcard.
        """
        return json.dumps(self, default=lambda obj: obj.__dict__)
