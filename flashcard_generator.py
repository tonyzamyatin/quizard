import math
import os
from typing import List
from completion_messages import Messages
from flash_card import FlashCard
from flash_card_deck import FlashCardDeck
import openai
import tiktoken


def parse_flashcard(line):
    split = line.split(';')
    print(split)
    return FlashCard(split[0], split[1])


def parse_flashcards(csv: str) -> List[FlashCard]:
    cards = []
    csv = csv.replace('\n\n', '\n')  # sanitize multiple newlines
    # we need to build a more robust parser
    lines = csv.split('\n')
    for line in lines:
        print(line)
        cards.append(parse_flashcard(line))

    return cards


class FlashCardGenerator:

    # constructor
    def __init__(self, api_key, messages: list, config: dict):
        self.api_key = api_key
        self.messages = messages;
        self.config = config

    # generates a deck of flashcards
    def generate_deck(self) -> FlashCardDeck:
        # The automated switch to 16k was moved to test_runner

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
        print(completion)
        print(completion.response_ms)
        f.write(str(completion))
        f.write('\n')
        f.write(str(completion.response_ms))
        f.write('\n')
        f.close()
        csv = completion.choices[0].message.content

        # parse the response and return a new deck
        return FlashCardDeck(parse_flashcards(csv))
