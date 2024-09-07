from enum import Enum


class TaskState(Enum):
    """
    Enum class for task states.
    The states reflect the states of a Celery Task with the addition of the custom state
    'IN_PROGRESS' to indicate that the task is being executed and progress information is available.
    (see https://docs.celeryproject.org/en/stable/userguide/tasks.html#states).
    """
    pending = 'PENDING'
    started = 'STARTED'
    in_progress = 'IN_PROGRESS'
    success = 'SUCCESS'
    failure = 'FAILURE'
    retry = 'RETRY'
    revoked = 'REVOKED'
