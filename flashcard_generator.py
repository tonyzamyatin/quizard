import math
import os
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
    csv = csv.replace('\n\n', '\n')  # sanitize multiple newlines
    # we need to build a more robust parser
    lines = csv.split('\n')
    for line in lines:
        print(line)
        cards.append(parse_flashcard(line))

    return cards


class FlashCardGenerator:

    # constructor
    def __init__(self, api_key, example_messages: ExampleMessages, config: dict):
        self.api_key = api_key
        self.exampleMessages = example_messages
        self.config = config

    # generates a deck of flashcards
    def generate(self, user_input, system_prompt) -> FlashCardDeck:
        # Put message to be used in chat completion together
        messages: [] = self.exampleMessages.as_message_list()
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "system", "content": system_prompt})

        # load the encoding for the model
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        encoded_user_input = encoding.encode(user_input)
        print('tokens:')
        token_count = sum(
            [len(encoding.encode(message['content'])) + len(encoding.encode(message['role'])) for message in messages])

        # count of input tokens needs to be below 3k to use 4k model
        max_tokens = self.config["model"].get("max_tokens")
        model = self.config["model"].get("name")
        if token_count > self.config["tokens"].get("prompt_limit") or token_count > 3000:
            model = 'gpt-3.5-turbo-16k'
            max_tokens = math.floor(token_count / 3)

        # make API call
        openai.api_key = self.api_key
        print(model)
        print(max_tokens)
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
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
