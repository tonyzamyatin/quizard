# src/rest/tasks.py
from injector import Injector
from openai import OpenAIError
from src.custom_exceptions.internal_exceptions import QuizardError
from src.dtos.flashcard_generator_task_dto import FlashcardGeneratorTaskDto
from src.services.flashcard_service.flashcard_service import FlashcardService
from celery import shared_task
from celery.utils.log import get_task_logger

from src.injector import FlashcardServiceModule

logger = get_task_logger(__name__)

injector = Injector([FlashcardServiceModule()])

@shared_task(bind=True, ignore_result=False, track_started=True)
def flashcard_generator_task(self, params : FlashcardGeneratorTaskDto):
    """
    Generate flashcards based on input .



    The 'PROGRESS' state includes metadata with 'progress' and 'total' fields indicating the progress of generation.
    # TODO: add retries with exponential backoff

    Parameters
    ----------
    params: FlashcardGeneratorTaskDto
        The DTO containing the parameters for generating flashcards including language, mode, export format, and input.

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
        flashcard_service = injector.get(FlashcardService)
        update_progress(0, 1)  # Defensive programming
        flashcard_deck = flashcard_service.generate_flashcard_deck(params, update_progress)
        file = flashcard_service.export_flashcard_deck(flashcard_deck, params.export_format)
        self.update_state(state='SUCCESS',
                          meta={'file_type': params.export_format,
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
