# src/rest/tasks.py
from dependency_injector.wiring import inject, Provide
from openai import OpenAIError
from src.custom_exceptions.internal_exceptions import QuizardError
from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.container import Container
from src.services.flashcard_service.flashcard_service import FlashcardService
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# TODO: add retries with exponential backoff
@shared_task(bind=True, ignore_result=False, track_started=True)
@inject
def flashcard_generator_task(self, params: FlashcardGeneratorTaskDto, flashcard_service=Provide[Container.flashcard_service]):
    """
    Flashcard generator task.
    This task generates flashcards based on the provided parameters and stores the result in the backend used by Celery.

    Includes a custom state 'IN_PROGRESS' to indicate that information about the tasks progress. For the flashcard_generator_task progress
    information is represented by the fields 'currentBatch' and 'totalBatches' in task.info.

    Parameters
    ----------
    params: FlashcardGeneratorTaskDto
        The DTO containing the parameters for generating flashcards including language, mode, export format, and input.

    flashcard_service: FlashcardService
        The service used to generate flashcards, injected by the dependency injector.
    Returns
    -------
    FlashcardDeck
        The generated flashcards.

    Raises
    ------
    OpenAIError
        If an error occurs while interacting with the OpenAI API.
    QuizardError
        If a Quizard-specific error occurs during flashcard generation.
    """

    try:
        logger.info(f"Flashcard generation task started with task id: {self.request.id}")
        flashcard_deck = flashcard_service.generate_flashcard_deck(params, lambda c, t: update_progress(self, c, t))
        # Get the final progress from the task's meta field
        final_progress = self.request.chain.get('meta', {})
        current = final_progress.get('current_batch', 0)
        total = final_progress.get('total_batches', 0)
        # Update the state with the final progress before returning
        self.update_state(state='SUCCESS', meta={'current_batch': current, 'total_batches': total})

    except OpenAIError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except QuizardError as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise RuntimeError(f"Unexpected error in task: {e}")
    return flashcard_deck


def update_progress(task, current: int, total: int):
    task.update_state(state='IN_PROGRESS', meta={'current_batch': current, 'total_batches': total})
