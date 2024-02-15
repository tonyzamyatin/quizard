from openai import OpenAIError, OpenAI
from src.custom_exceptions.quizard_exceptions import QuizardError
from src.flashcard_service.flashcard_service import FlashcardService
from celery import shared_task
from celery.utils.log import get_task_logger

from src.utils.global_helpers import get_env_variable

logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=False)
def generate_flashcards_task(self, config, model_name, lang, mode, input_text):
    """
    Generate flashcards based on input text using the FlashcardService.

    This task forwards the request to the FlashcardService and returns the generated flashcards as a list of dictionaries,
    each representing a flashcard. It also updates the task's state to 'PROGRESS' with the progress information.
    # TODO: add retries with exponential backoff

    Parameters
    ----------
    client : OpenAI
        The OpenAI client instance for API interactions.
    config : dict
        Configuration settings for the flashcard generation.
    model_name : str
        Name of the OpenAI model to use for generation.
    lang : str
        Language of the flashcards.
    mode : str
        Mode of flashcard generation.
    input_text : str
        The text input from which flashcards are generated.

    Returns
    -------
    list of dict
        A list of dictionaries, each representing a flashcard.

    Raises
    ------
    OpenAIError
        If an error occurs while interacting with the OpenAI API.
    QuizardError
        If a Quizard-specific error occurs during flashcard generation.

    Notes
    -----
    Each flashcard dictionary contains the following keys:
    - 'id': The ID of the flashcard.
    - 'type': The type of the flashcard.
    - 'frontSide': The content for the front side of the flashcard.
    - 'backSide': The content for the back side of the flashcard.

    The 'PROGRESS' state includes metadata with 'processed' and 'total' fields indicating the progress of generation.
    """

    def update_progress(processed, total):
        self.update_state(state='PROGRESS', meta={'progress': processed, 'total': total})

    try:
        client = OpenAI(api_key=get_env_variable("OPENAI_API_KEY"))
        flashcard_app = FlashcardService(openai=client, app_config=config,
                                         model_name=model_name, lang=lang, mode=mode)
        flashcards = flashcard_app.run(input_text, update_progress).flashcards
    except OpenAIError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except QuizardError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise RuntimeError(f"Unexpected error in task: {e}")

    # Format the flashcards for the response
    flashcard_dict_list = [{'id': card.id, 'type': card.type,
                            'frontSide': card.front_side, 'backSide': card.back_side}
                           for card in flashcards]
    return flashcard_dict_list
