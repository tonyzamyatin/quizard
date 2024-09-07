from typing import Optional

from pydantic import BaseModel

from src.enums.task_states import TaskState


class GeneratorTaskInfoDto(BaseModel):
    """
    Data transfer object for the flashcard generator task state.
    Based on mutable BaseModel, convenient for response creation.
    Note: Pydantic automatically converts string values to the corresponding enum values.
    task_state : TaskState
        The current state of the task.
    current_batch : int
        The current flashcard batch of the task.
    total_batches : int
        The total number of flashcard batches.
    retrieval_token : str
        The token to retrieve the generated flashcards.
    """
    task_state: TaskState
    current_batch: Optional[int] = None
    total_batches: Optional[int] = None
    retrieval_token: Optional[str] = None
