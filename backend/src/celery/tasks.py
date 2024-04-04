# src/rest/tasks.py
from openai import OpenAIError, OpenAI
from src.custom_exceptions.quizard_exceptions import QuizardError
from src.dto.flashcards_request_dto import FlashcardsRequestDto
from src.services.flashcard_service.flashcard_service import FlashcardService, export
from celery import shared_task
from celery.utils.log import get_task_logger
from src.utils.global_helpers import get_env_variable

logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=False, track_started=True)
def flashcard_generator_task(self, flashcards_request_dto: FlashcardsRequestDto):
    """
    Generate flashcards based on input text using the FlashcardService.

    This task forwards the request to the FlashcardService and returns the generated flashcards as a list of dictionaries,
    each representing a flashcard. It also updates the task's state to 'PROGRESS' with the progress information.

    The 'PROGRESS' state includes metadata with 'progress' and 'total' fields indicating the progress of generation.
    # TODO: add retries with exponential backoff

    Parameters
    ----------
    flashcards_request_dto : FlashcardsRequestDto
        The request data for generating flashcards.

    Returns
    -------
    file: bytes
        The generated flashcards in the requested format.

    Raises
    ------
    OpenAIError
        If an error occurs while interacting with the OpenAI API.
    QuizardError
        If a Quizard-specific error occurs during flashcard generation.
    """

    def update_progress(progress: int, total: int):
        self.update_state(state='PROCESSING', meta={'progress': progress, 'total': total})

    try:
        logger.info(f"Flashcard generation task started with task id: {self.request.id}")
        flashcard_service = FlashcardService()
        update_progress(0, 1)  # Defensive programming
        flashcard_deck = flashcard_service.generate_flashcards(flashcards_request_dto, update_progress)
        file = export(flashcard_deck, flashcards_request_dto.export_format)
        self.update_state(state='SUCCESS',
                          meta={'file_type': flashcards_request_dto.export_format,
                                })
    except OpenAIError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except QuizardError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise RuntimeError(f"Unexpected error in task: {e}")
    return file
