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

    pass


def parse_flashcard(number: int, line: str):
    split = line.split(';')

    # Check that split has at least two elements before attempting to access them
    if len(split) < 2:
        raise InvalidFlashCardFormatError(f"Invalid format for flashcard {number}: Missing ';' or content after ';'")

    # Check if the prefix is at the beginning
    prefix_match = re.match(r'\[(.*?)\]', split[0])
    if prefix_match:
        prefix = prefix_match.group(1).lower()

        # Remove prefix from front_side
        front_side = split[0][split[0].find(']') + 1:].strip()

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


def parse_flashcards(content: str) -> List[FlashCard]:
    cards = []
    content = content.replace('\n\n', '\n')
    lines = content.split('\n')
    cnt = 0
    for line in lines:
        print(line)
        cnt += 1
        try:
            flashcard = parse_flashcard(cnt, line)
            cards.append(flashcard)
            print(flashcard)
        except (InvalidFlashCardFormatError, FlashCardWarning) as e:
            if isinstance(e, FlashCardWarning):
                logging.warning(f"Unexpected prefix for flashcard {cnt}: {e}")
                cards.append(e.flashcard)  # Append the unknown-type flashcard
                print(e.flashcard)
            else:
                logging.error(f"Invalid format for flashcard {cnt}: {e}")

    return cards


class FlashCardGenerator:

    # constructor
    def __init__(self, api_key, messages: list, config: dict):
        self.api_key = api_key
        self.messages = messages
        self.config = config

    # generates flashcards corresponding to the given input text
    def generate_flashcards(self) -> List[FlashCard]:
        # The automated switch to 16k was moved to test_runner

        print(self.messages)

        # make API call
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

        f = open(os.getenv('LOG_FILE', default='log/log.txt'), 'a')
        f.write('-------\n')
        f.write(str(completion))
        f.write('\n')
        f.write(f"Response time: {str(completion.response_ms)}")
        f.write('\n')
        f.close()

        print(f"Model:{completion.model}")
        print(f"Response time (ms): {completion.response_ms}")
        print(f"Prompt tokens: {completion.usage.prompt_tokens}")
        print(f"Completion tokens: {completion.usage.completion_tokens}")
        print(f"Total tokens: {completion.usage.total_tokens}")
        print(f"Max tokens: {self.config['model']['max_tokens']}\n")

        content = completion.choices[0].message.content

        # parse the response and return a new deck
        return parse_flashcards(content)
