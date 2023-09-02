import os
import re
import logging
from typing import List
from flash_card import FlashCard
from flash_card import FlashCardType
from flash_card_deck import FlashCardDeck
import openai


class InvalidFlashCardFormatError(Exception):
    """Exception raised when the flashcard format is invalid."""
    pass


class FlashCardWarning(InvalidFlashCardFormatError):
    """Exception raised for unexpected prefixes."""

    def __init__(self, message: str, flashcard: FlashCard):
        super().__init__(message)
        self.flashcard = flashcard


# Function to parse individual flashcard
def parse_flashcard(number: int, line: str):
    split = line.split(';')

    if len(split) < 2:
        raise InvalidFlashCardFormatError(f"Invalid format for flashcard {number}: Missing ';' or content after ';'")

    prefix_match = re.match(r'\[(.*?)\]', split[0])

    if prefix_match:
        prefix = prefix_match.group(1).lower()
        # Remove prefix from front_side
        front_side = split[0][split[0].find(']') + 1:].strip()

        # Handle flashcards based on their prefixes
        if "term" in prefix:
            return FlashCard(number, FlashCardType.TERM, front_side, split[1])
        elif "open-ended" in prefix:
            return FlashCard(number, FlashCardType.OPEN_ENDED, front_side, split[1])
        elif "critical thinking" in prefix:
            return FlashCard(number, FlashCardType.CRITICAL_THINKING, front_side, split[1])
        else:
            flashcard = FlashCard(number, FlashCardType.UNKNOWN, front_side, split[1])
            raise FlashCardWarning(f"Unexpected prefix for flashcard {number}", flashcard)
    else:
        raise InvalidFlashCardFormatError(f"No prefix found for flashcard {number}")


# Function to parse multiple flashcards from the content
def parse_flashcards(content: str) -> List[FlashCard]:
    cards = []
    content = content.replace('\n\n', '\n')
    lines = content.split('\n')

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


# Class to handle the flashcard generation
class FlashCardGenerator:

    def __init__(self, api_key, messages: list, config: dict):
        self.api_key = api_key
        self.messages = messages
        self.config = config

    # Method to generate flashcards
    def generate_flashcards(self) -> List[FlashCard]:
        openai.api_key = self.api_key
        completion = openai.ChatCompletion.create(
            model=self.config["model"].get("name"),
            messages=self.messages,
            max_tokens=self.config["model"].get("max_tokens"),
            temperature=self.config["model"].get("temperature", 0.7),
            top_p=self.config["model"].get("top_p", 1.0),
            frequency_penalty=self.config["model"].get("frequency_penalty", 0.0),
            presence_penalty=self.config["model"].get("presence_penalty", 0.0)
        )

        with open(os.getenv('LOG_FILE', default='log/log.txt'), 'a') as f:
            f.write('-------\n')
            f.write(str(completion))
            f.write('\n')
            f.write(f"Response time: {str(completion.response_ms)}\n")

        print(f"Model:{completion.model}")
        print(f"Response time (ms): {completion.response_ms}")
        print(f"Prompt tokens: {completion.usage.prompt_tokens}")
        print(f"Completion tokens: {completion.usage.completion_tokens}")
        print(f"Total tokens: {completion.usage.total_tokens}")
        print(f"Max tokens: {self.config['model']['max_tokens']}\n")

        content = completion.choices[0].message.content
        return parse_flashcards(content)
