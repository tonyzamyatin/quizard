# src/rest/tasks.py
from openai import OpenAIError, OpenAI
from src.custom_exceptions.quizard_exceptions import QuizardError
from src.service.flashcard_service import FlashcardService
from celery import shared_task
from celery.utils.log import get_task_logger

from src.utils.global_helpers import get_env_variable

logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=False, track_started=True)
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
        Name of the OpenAI model to use for generation. Must valid and a supported model.
    lang : str
        Language of the flashcards. Must valid and a supported language.
    mode : str
        Mode of flashcard generation. Must valid and a supported mode.
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

    The 'PROGRESS' state includes metadata with 'progress' and 'total' fields indicating the progress of generation.
    """

    def update_progress(progress: int, total: int):
        self.update_state(state='PROCESSING', meta={'progress': progress, 'total': total})

    try:
        client = OpenAI(api_key=get_env_variable("OPENAI_API_KEY"))
        flashcard_app = FlashcardService(openai=client, app_config=config,
                                         model_name=model_name, lang=lang, mode=mode)
        flashcard_deck = flashcard_app.run(input_text, update_progress)
    except OpenAIError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except QuizardError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise RuntimeError(f"Unexpected error in task: {e}")

    return flashcard_deck.to_dict_list()     # Result needs to be serializable for Celery to store in results backend
