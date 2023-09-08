
from backend.src.custom_exceptions.invalid_flashcard_format_error import InvalidFlashCardFormatError


class FlashCardWarning(InvalidFlashCardFormatError):
    """Exception raised for unexpected prefixes."""

    def __init__(self, message: str, flashcard: FlashCard):
        super().__init__(message)
        self.flashcard = flashcard
