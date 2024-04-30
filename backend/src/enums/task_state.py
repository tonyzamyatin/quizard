from enum import Enum


class TaskStateEnum(Enum):
    """
    Enum class for task states.
    """
    processing = 'PROCESSING'
    started = 'STARTED'
    pending = 'PENDING'
    success = 'SUCCESS'
    failed = 'FAILED'
    cancelled = 'CANCELLED'
