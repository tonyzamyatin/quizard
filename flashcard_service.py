from typing import List

from example_messages import ExampleMessages
from flash_card import FlashCard
from flash_card_deck import FlashCardDeck
import openai


def parse_flashcard(line):
    split = line.split(';')
    return FlashCard(split[0], split[1])


def parse_flashcards(csv) -> List[FlashCard]:
    cards = []
    lines = csv.split('\n')
    for line in lines:
        cards.append(parse_flashcard(line))

    return cards


class FlashCardService:

    # constructor
    def __init__(self, api_key, example_messages: ExampleMessages):
        self.api_key = api_key
        self.exampleMessages = example_messages

    # generates a deck of flashcards
    def generate(self, user_input, system_prompt) -> FlashCardDeck:
        # build
        messages: [] = self.exampleMessages.as_message_list()
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "system", "content": system_prompt})

        # make API call
        openai.api_key = self.api_key
        completion35 = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, max_tokens=1000)
        f = open('log.txt', 'a')
        f.write('-------\n')
        print(completion35)
        print(completion35.response_ms)
        f.write(str(completion35))
        f.write('\n')
        f.write(str(completion35.response_ms))
        f.write('\n')
        f.close()
        csv = completion35.choices[0].message.content

        # parse the response and return a new deck
        return FlashCardDeck(parse_flashcards(csv))

