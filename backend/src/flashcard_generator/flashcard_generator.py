import os
import re
import logging
import time
from typing import List
from backend.src.flashcard.flashcard import Flashcard, FlashcardType
from backend.src.custom_exceptions.quizard_exceptions import FlashcardInvalidFormatError
from backend.src.custom_exceptions.quizard_exceptions import FlashcardPrefixError
from backend.src.utils.completion_messages import Messages
from backend.src.utils.global_helpers import format_num
from openai import OpenAI


def parse_flashcard(number: int, line: str) -> Flashcard:
    split_line = line.split(';')
    if len(split_line) < 2:
        raise FlashcardInvalidFormatError(f"Invalid format for flashcard {number}")

    prefix_match = re.match(r'\[(.*?)\]', split_line[0])
    if not prefix_match:
        raise FlashcardInvalidFormatError(f"No prefix found for flashcard {number}")

    prefix = prefix_match.group(1).lower()
    front_side = split_line[0][len(prefix) + 2:].strip()
    flashcard_type = get_flashcard_type(prefix, number)

    return Flashcard(number, flashcard_type, front_side, split_line[1])


def get_flashcard_type(prefix: str, number: int) -> FlashcardType:
    if "term" in prefix:
        return FlashcardType.DEFINITION
    elif "concept" or "critical thinking" in prefix:
        return FlashcardType.OPEN_ENDED
    raise FlashcardPrefixError(f"Unexpected prefix for flashcard {number}", Flashcard(number, FlashcardType.UNKNOWN, '', ''))


def parse_flashcards(content: str, generation_mode: str) -> List[Flashcard]:
    cards = []
    lines = content.replace('\n\n', '\n').split('\n')
    for cnt, line in enumerate(lines, start=1):
        try:
            if generation_mode == 'practice':  # For practice mode, expect prefixes (mixed format)
                flashcard = parse_flashcard(cnt, line)
            else:  # For static modes, assume the flashcard type from the mode
                flashcard = Flashcard(cnt, FlashcardType[generation_mode.upper()], line.split(";")[0], line.split(";")[1])
            cards.append(flashcard)
        except (FlashcardInvalidFormatError, FlashcardPrefixError) as e:
            if isinstance(e, FlashcardPrefixError):
                logging.warning(e)
                cards.append(e.flashcard)
            else:
                logging.error(e)
        except IndexError as e:
            logging.error("Model output not in expected flashcard format: 'question;answer")
            print(f"""
            Model output not in expected flashcard format: 'question;answer:
            {line}    
            """)
            raise e

    return cards


class FlashcardGenerator:
    GENERATION_MODE = ['practice', 'definitions', 'quiz', 'cloze']

    def __init__(self, client: OpenAI, model_config: dict, generation_mode: str):
        self.client = client
        self.model_config = model_config
        self.generation_mode = generation_mode

    def generate_flashcards(self, model: str, messages: Messages, max_tokens: int) -> List[Flashcard]:
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages.as_message_list(),
            max_tokens=max_tokens,
            temperature=self.model_config.get("temperature", 0.7),
            top_p=self.model_config.get("top_p", 1.0),
            frequency_penalty=self.model_config.get("frequency_penalty", 0.0),
            presence_penalty=self.model_config.get("presence_penalty", 0.0)
        )
        receive_time_sec = int(round(time.time()))
        log_completion_metrics(completion, receive_time_sec)
        return parse_flashcards(completion.choices[0].message.content, self.generation_mode)


def log_completion_metrics(completion, receive_time_sec):
    response_time_sec = receive_time_sec - completion.created
    metrics = [
        f"Response time: {format_num(response_time_sec)} sec",
        f"Completion size: {format_num(completion.usage.completion_tokens)} tokens",
        f"Total size: {format_num(completion.usage.total_tokens)} tokens\n"
    ]

    print("\n".join(metrics))
    with open(os.getenv('LOG_FILE', default='logs/logs.txt'), 'a') as f:
        f.write("\n\n".join(metrics))
