import re
import time

import openai
import structlog
from typing import List, Optional
from openai import OpenAI
from src.flashcard_service.flashcard.flashcard import Flashcard, FlashcardType
from src.custom_exceptions.quizard_exceptions import FlashcardInvalidFormatError, FlashcardPrefixError
from src.flashcard_service.completion_messages.completion_messages import Messages
from src.utils.global_helpers import format_num

logger = structlog.getLogger(__name__)


def parse_flashcard(number: int, line: str) -> Flashcard:
    """
    Parses a single line into a Flashcard object.

    Parameters
    ----------
    number : int
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
        raise FlashcardInvalidFormatError(f"Missing prefix")

    prefix = prefix_match.group(1).lower()
    front_side = split_line[0][len(prefix) + 2:].strip()
    flashcard_type = get_flashcard_type(prefix, number)

    return Flashcard(number, flashcard_type, front_side, split_line[1])


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


def parse_flashcards(content: str, generation_mode: str, start_id=1, batch_number: Optional[int] = None) -> List[Flashcard]:
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
            flashcard = parse_flashcard(cnt, line) if generation_mode == 'practice' else \
                Flashcard(id=cnt, type=FlashcardType[generation_mode.upper()], front_side=line.split(";")[0], back_side=line.split(";")[1])
            cards.append(flashcard)
        except FlashcardPrefixError as e:
            logger.warning("Flashcard prefix error", error=str(e), batch=batch_number, flashcard_number=cnt)
            cards.append(e.flashcard)
        except FlashcardInvalidFormatError as e:
            logger.error("Flashcard invalid format error", error=str(e), batch=batch_number, flashcard_number=cnt)
    return cards


class FlashcardGenerator:
    """
    A class to generate flashcards using the OpenAI GPT model.

    Parameters
    ----------
    client : OpenAI
        The OpenAI client object.
    model_config : dict
        A dictionary containing model configuration parameters.
    generation_mode : str
        The mode of flashcard generation.

    Attributes
    ----------
    client : OpenAI
        The OpenAI client object.
    model_config : dict
        A dictionary containing model configuration parameters.
    generation_mode : str
        The mode of flashcard generation.
    """

    def __init__(self, client: OpenAI, model_config: dict, generation_mode: str):
        self.client = client
        self.model_config = model_config
        self.generation_mode = generation_mode

    def generate_flashcards(self, model: str, messages: Messages, max_tokens: int, start_id=1, batch_number: Optional[int] = None) -> List[Flashcard]:
        """
        Generates a list of flashcards using the OpenAI GPT model.
        Optionally includes a batch number in the logging_config information.
        TODO: Handle OpenAIErrors adequately.

        Parameters
        ----------
        model : str
            The name of the model to use for generation.
        messages : Messages
            A Message object containing the input message sequence.
        max_tokens : int
            The maximum number of tokens to generate.
        start_id : int, optional
            The starting ID for the generated flashcards, by default 1.
        batch_number : Optional[int], optional
            The batch number in the context of multiple batch processing, by default None.

        Returns
        -------
        List[Flashcard]
            A list of generated Flashcard objects.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages.as_message_list(),
                max_tokens=max_tokens,
                temperature=self.model_config.get("temperature", 0.7),
                top_p=self.model_config.get("top_p", 1.0),
                frequency_penalty=self.model_config.get("frequency_penalty", 0.0),
                presence_penalty=self.model_config.get("presence_penalty", 0.0)
            )
            receive_time_sec = round(time.time(), 3)
            log_completion_metrics(response, receive_time_sec, batch_number)
            return parse_flashcards(content=response.choices[0].message.content, generation_mode=self.generation_mode, start_id=start_id, batch_number=batch_number)
        except openai.BadRequestError as e:
            # Handle error 400
            logger.error("OpenAI API Error occurred", error=f"Error 400: {e}")
            raise
        except openai.AuthenticationError as e:
            # Handle error 401
            logger.error("OpenAI API Error occurred", error=f"Error 401: {e}")
            raise
        except openai.PermissionDeniedError as e:
            # Handle error 403
            logger.error("OpenAI API Error occurred", error=f"Error 403: {e}")
            raise
        except openai.NotFoundError as e:
            # Handle error 404
            logger.error("OpenAI API Error occurred", error=f"Error 404: {e}")
            raise
        except openai.UnprocessableEntityError as e:
            # Handle error 422
            logger.error("OpenAI API Error occurred", error=f"Error 422: {e}")
            raise
        except openai.RateLimitError as e:
            # Handle error 429
            logger.error("OpenAI API Error occurred", error=f"Error 429: {e}")
            raise
        except openai.InternalServerError as e:
            # Handle error >=500
            logger.error("OpenAI API Error occurred", error=f"Error >=500: {e}")
            raise
        except openai.APIConnectionError as e:
            # Handle API connection error
            logger.error("OpenAI API Error occurred", error=f"API connection error: {e}")
            raise


def log_completion_metrics(completion: openai.Completion, receive_time_sec: float, batch_number: Optional[int] = None):
    """
    Logs the metrics of a completion response, including optional batch information.

    Parameters
    ----------
    completion : openai.Completion
        The completion response from the OpenAI API.
    receive_time_sec : float
        The time at which the completion was received.
    batch_number : Optional[int], optional
        The batch number in the context of multiple batch processing, by default None.
    """
    response_time_sec = round(receive_time_sec - completion.created, 3)
    logger.info(
        "Completion metrics logged",
        response_time_sec=response_time_sec,
        completion_tokens=format_num(completion.usage.completion_tokens),
        total_tokens=format_num(completion.usage.total_tokens),
        batch=batch_number if batch_number is not None else 'N/A'  # Or simply omit batch_number if it's None
    )
