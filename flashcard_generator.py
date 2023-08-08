import math
from typing import List
from example_messages import ExampleMessages
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
    csv = csv.replace('\n\n', '\n') # sanitize multiple newlines
    # we need to build a more robust parser
    lines = csv.split('\n')
    for line in lines:
        print(line)
        cards.append(parse_flashcard(line))

    return cards


class FlashCardGenerator:

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

        # load the encoding for the model
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        encoded_user_input = encoding.encode(user_input)
        print('tokens:')
        token_count = sum([len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in messages])
        # count of input tokens needs to be below 3k to use 4k model
        model = 'gpt-3.5-turbo'
        max_tokens: int = 1000
        if token_count > 3000:
            model = 'gpt-3.5-turbo-16k'
            max_tokens = math.floor(token_count / 3)
        # make API call
        openai.api_key = self.api_key
        print(model)
        print(max_tokens)
        completion35 = openai.ChatCompletion.create(model=model, messages=messages, max_tokens=max_tokens)
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

