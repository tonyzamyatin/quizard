# src.celery.celery_worker.py
from celery import Celery
from celery.signals import task_failure
import structlog

from src.injector.injector_setup import get_injector

logger = structlog.get_logger(__name__)


def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    """
    Handle Celery task failures
    Logs the task failure along with the task ID and exception
    """
    logger.error(f"Celery task failed: {task_id}", exc_info=exception, args=args, kwargs=kwargs, traceback=traceback)


# Handle Celery task failures
task_failure.connect(handle_task_failure)

if __name__ == '__main__':
    injector = get_injector()
    celery_app = injector.get(Celery)
    celery_app.start()
