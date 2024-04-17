from typing import Optional, List

import structlog

from src.custom_exceptions.internal_exceptions import FlashcardInvalidFormatError, FlashcardPrefixError
from src.entities.flashcard.flashcard import Flashcard, FlashcardType

logger = structlog.getLogger(__name__)


def parse_flashcard(id: int, line: str) -> Flashcard:
    """
    Parses a single line into a Flashcard object.

    Parameters
    ----------
    id : int
        The flashcard number or ID.
    line : str
        A string representing the flashcard content in 'question;answer' format.

    Returns
    -------
    Flashcard
        A Flashcard object created from the parsed line.

    Raises
    ------
    FlashcardInvalidFormatError
        If the line does not conform to the expected 'question;answer' format.
    """
    split_line = line.split(';')
    if len(split_line) < 2:
        raise FlashcardInvalidFormatError(f"Invalid format")

    prefix_match = re.match(r'\[(.*?)\]', split_line[0])
    if not prefix_match:
        raise FlashcardPrefixError(f"Missing prefix")

    prefix = prefix_match.group(1).lower()
    front_side = split_line[0][len(prefix) + 2:].strip()
    flashcard_type = get_flashcard_type(prefix, id)

    return Flashcard(id, flashcard_type, front_side, split_line[1])


def get_flashcard_type(prefix: str, number: int) -> FlashcardType:
    """
    Determines the type of flashcards based on the prefix.

    Parameters
    ----------
    prefix : str
        The prefix indicating the type of the flashcard.
    number : int
        The flashcard number or ID.

    Returns
    -------
    FlashcardType
        The determined FlashcardType.

    Raises
    ------
    FlashcardPrefixError
        If the prefix does not match any known flashcard types.
    """
    if "term" in prefix:
        return FlashcardType.DEFINITION
    elif "concept" or "critical thinking" in prefix:
        return FlashcardType.OPEN_ENDED
    raise FlashcardPrefixError(f"Unexpected prefix", Flashcard(number, FlashcardType.UNKNOWN, '', ''))


def parse_flashcards(content: str, start_id=1, batch_number: Optional[int] = None) -> List[Flashcard]:
    """
    Parses the content into a list of Flashcard objects.

    Parameters
    ----------
    batch_number :  Optional[int]
        The number of the batch.
    content : str
        The content to parse into flashcards.
    generation_mode : str
        The mode of flashcard generation.
    start_id : int, optional
        The starting ID for the flashcards, by default 1.

    Returns
    -------
    List[Flashcard]
        A list of Flashcard objects generated from the content.
    """
    cards = []
    lines = content.replace('\n\n', '\n').split('\n')
    for cnt, line in enumerate(lines, start=start_id):
        try:
            flashcard = parse_flashcard(cnt, line)
            cards.append(flashcard)
        except FlashcardPrefixError as e:
            logger.warning("Flashcard prefix error", error=str(e), batch=batch_number, flashcard_number=cnt)
            cards.append(e.flashcard)
        except FlashcardInvalidFormatError as e:
            logger.error("Flashcard invalid format error", error=str(e), batch=batch_number, flashcard_number=cnt)
    return cards
