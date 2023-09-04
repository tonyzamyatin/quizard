import os
import re
import logging
from typing import List
from flash_card import FlashCard, FlashCardType
from global_helpers import format_num
import openai


class InvalidFlashCardFormatError(Exception):
    """Exception raised when the flashcard format is invalid."""
    pass


class FlashCardWarning(InvalidFlashCardFormatError):
    """Exception raised for unexpected prefixes."""

    def __init__(self, message: str, flashcard: FlashCard):
        super().__init__(message)
        self.flashcard = flashcard


def parse_flashcard(number: int, line: str) -> FlashCard:
    split_line = line.split(';')
    if len(split_line) < 2:
        raise InvalidFlashCardFormatError(f"Invalid format for flashcard {number}")

    prefix_match = re.match(r'\[(.*?)\]', split_line[0])
    if not prefix_match:
        raise InvalidFlashCardFormatError(f"No prefix found for flashcard {number}")

    prefix = prefix_match.group(1).lower()
    front_side = split_line[0][len(prefix) + 2:].strip()
    flashcard_type = get_flashcard_type(prefix, number)

    return FlashCard(number, flashcard_type, front_side, split_line[1])


def get_flashcard_type(prefix: str, number: int) -> FlashCardType:
    if "term" in prefix:
        return FlashCardType.TERM
    elif "open-ended" in prefix:
        return FlashCardType.OPEN_ENDED
    elif "critical thinking" in prefix:
        return FlashCardType.CRITICAL_THINKING

    raise FlashCardWarning(f"Unexpected prefix for flashcard {number}", FlashCard(number, FlashCardType.UNKNOWN, '', ''))


def parse_flashcards(content: str) -> List[FlashCard]:
    cards = []
    lines = content.replace('\n\n', '\n').split('\n')
    for cnt, line in enumerate(lines, start=1):
        try:
            flashcard = parse_flashcard(cnt, line)
            cards.append(flashcard)
        except (InvalidFlashCardFormatError, FlashCardWarning) as e:
            if isinstance(e, FlashCardWarning):
                logging.warning(f"Unexpected prefix for flashcard {cnt}: {e}")
                cards.append(e.flashcard)
            else:
                logging.error(f"Invalid format for flashcard {cnt}: {e}")
    return cards


class FlashCardGenerator:
    def __init__(self, api_key: str, messages: list, config: dict):
        self.api_key = api_key
        self.messages = messages
        self.config = config

    def generate_flashcards(self) -> List[FlashCard]:
        openai.api_key = self.api_key
        completion = openai.ChatCompletion.create(
            model=self.config["model"].get("name"),
            messages=self.messages,
            max_tokens=self.config["tokens"].get("completion_limit"),
            temperature=self.config["model"].get("temperature", 0.7),
            top_p=self.config["model"].get("top_p", 1.0),
            frequency_penalty=self.config["model"].get("frequency_penalty", 0.0),
            presence_penalty=self.config["model"].get("presence_penalty", 0.0)
        )
        log_completion_metrics(completion)
        return parse_flashcards(completion.choices[0].message.content)


def log_completion_metrics(completion):
    metrics = [
        f"Response time: {format_num(completion.response_ms)} ms",
        f"Completion size: {format_num(completion.usage.completion_tokens)} tokens",
        f"Total size: {format_num(completion.usage.total_tokens)} tokens\n"
    ]

    print("\n".join(metrics))
    with open(os.getenv('LOG_FILE', default='log/log.txt'), 'a') as f:
        f.write("\n".join(metrics))
