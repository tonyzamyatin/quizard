# src/services/task_service/flashcard_generator_task_service.py

from dependency_injector.wiring import inject, Provide
from itsdangerous import URLSafeSerializer, BadSignature

from src.custom_exceptions.external_exceptions import TokenAuthenticationError, ResultNotFoundError
from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck
from src.enums.task_states import TaskState
from src.container import Container
from src.services.task_service.task_service_interface import ITaskService
from src.celery.tasks import flashcard_generator_task


class FlashcardGeneratorTaskService(ITaskService):
    """
    Implementation of IFlashcardGeneratorTaskService.
    Essentially a wrapper for performing operations on the flashcard generator celery task.
    """

    @inject
    def __init__(self, flask_app=Provide[Container.flask_app], celery_app=Provide[Container.celery_app]):
        self.flask_app = flask_app
        self.celery_app = celery_app

    def start_task(self, task: FlashcardGeneratorTaskDto, *args, **kwargs):
        task_id = flashcard_generator_task.delay(task).id
        return task_id

    def get_task_state(self, task_id: str) -> TaskState:
        task = flashcard_generator_task.AsyncResult(task_id)
        return TaskState(task.state)

    def get_task_info(self, task_id: str) -> dict:
        task = flashcard_generator_task.AsyncResult(task_id)
        return task.info

    def get_task_result(self, task_id: str) -> FlashcardDeck:
        state = self.get_task_state(task_id)
        if state != TaskState.success.name:
            raise ResultNotFoundError(f"Task result for taskID: {task_id} not available.")
        task = flashcard_generator_task.AsyncResult(task_id)
        return task.result

    def get_task_traceback(self, task_id: str):
        task = flashcard_generator_task.AsyncResult(task_id)
        return task.traceback

    def cancel_task(self, task_id: str) -> None:
        self.celery_app.control.revoke(task_id, terminate=True)

    def generate_retrieval_token(self, task_id: str):
        s = URLSafeSerializer(self.flask_app.config['SECRET_KEY'])
        return s.dumps(task_id)

    def verify_retrival_token(self, token):
        try:
            s = URLSafeSerializer(self.flask_app.config['SECRET_KEY'])
            task_id = s.loads(token)
            return task_id
        except BadSignature:
            raise TokenAuthenticationError("Invalid or expired retrieval token link")
