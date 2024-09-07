# src/celery/tasks.py
from dependency_injector.wiring import inject, Provide
from openai import OpenAIError
from src.custom_exceptions.internal_exceptions import QuizardError
from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.container import Container
from src.enums.task_states import TaskState
from src.services.flashcard_service.flashcard_service import FlashcardService
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


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
        flashcard_deck = flashcard_service.generate_flashcard_deck(params, lambda cb, tbs: update_progress(self, cb, tbs))
        self.update_state(state=TaskState.success)
        return flashcard_deck

    except OpenAIError as e:
        update_state_with_exception(self, e)
        raise
    except QuizardError as e:
        update_state_with_exception(self, e)
        raise
    except Exception as e:
        update_state_with_exception(self, e)
        raise RuntimeError(f"Unexpected error in task: {e}")


def update_progress(task, current_batch: int, total_batches: int):
    task.update_state(state=TaskState.in_progress, meta={'current_batch': current_batch, 'total_batches': total_batches})


def update_state_with_exception(task, e: Exception):
    task.update_state(state=TaskState.failure, meta={'error': str(e), 'exc_type': type(e).__name__})
