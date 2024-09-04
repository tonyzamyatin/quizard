# src.celery_config.celery_worker.py
from celery.signals import task_failure
import structlog

from src.container import get_container

logger = structlog.get_logger(__name__)


def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    """
    Handle Celery task failures
    Logs the task failure along with the task ID and exception
    """
    logger.error(f"Celery task failed: {task_id}", exc_info=exception, args=args, kwargs=kwargs, traceback=traceback)


# Handle Celery task failures
task_failure.connect(handle_task_failure)

# Get the container
container = get_container()
celery_app = container.celery_app()

if __name__ == '__main__':
    celery_app.start()
