import os
import re
import logging
from typing import List
from backend.src.flashcard.flashcard import Flashcard, FlashcardType
from backend.src.custom_exceptions.custom_exceptions import FlashcardInvalidFormatError
from backend.src.custom_exceptions.custom_exceptions import FlashcardPrefixError
from backend.src.utils.global_helpers import format_num
import openai


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
    elif "open-ended" in prefix:
        return FlashcardType.OPEN_ENDED
    elif "critical thinking" in prefix:
        return FlashcardType.CRITICAL_THINKING

    raise FlashcardPrefixError(f"Unexpected prefix for flashcard {number}", Flashcard(number, FlashcardType.UNKNOWN, '', ''))


def parse_flashcards(content: str, generation_mode: str) -> List[Flashcard]:
    cards = []
    lines = content.replace('\n\n', '\n').split('\n')
    for cnt, line in enumerate(lines, start=1):
        try:
            if generation_mode == 'autogen':  # For autogen mode, expect prefixes
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
        except (IndexError) as e:
            logging.error("Model output not in expected flashcard format: 'question;answer")
            print(f"""
            Model output not in expected flashcard format: 'question;answer:
            {line}    
            """)
            raise e

    return cards


class FlashcardGenerator:
    def __init__(self, api_key: str, messages: list, config: dict, generation_mode: str):
        self.api_key = api_key
        self.messages = messages
        self.config = config
        self.generation_mode = generation_mode

    def generate_flashcards(self) -> List[Flashcard]:
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
        return parse_flashcards(completion.choices[0].message.content, self.generation_mode)


def log_completion_metrics(completion):
    metrics = [
        f"Response time: {format_num(completion.response_ms)} ms",
        f"Completion size: {format_num(completion.usage.completion_tokens)} tokens",
        f"Total size: {format_num(completion.usage.total_tokens)} tokens\n"
    ]

    print("\n".join(metrics))
    with open(os.getenv('LOG_FILE', default='logs/logs.txt'), 'a') as f:
        f.write("\n".join(metrics))
