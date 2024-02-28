# celery.py
from celery.signals import task_failure
import structlog
from src.custom_exceptions.env_exceptions import EnvironmentLoadingError
from src.custom_exceptions.quizard_exceptions import QuizardError
from src.rest.flask_factory import create_flask_app
from src.rest.celery_config import create_celery_app
from src.utils.global_helpers import get_env_variable, load_environment_variables

logger = structlog.get_logger(__name__)


def setup_applications():
    """
    Set up Flask and Celery applications with appropriate configurations.

    This function loads environment variables, creates the broker URL and result backend for Celery,
    and initializes the Flask and Celery applications. If any error occurs during these processes,
    the application will shut down.

    Returns
    -------
    tuple
        A tuple containing the Flask app and Celery app instances.

    Raises
    ------
    EnvironmentLoadingError, RuntimeError
        If there's an error loading environment variables or initializing the Flask or Celery apps.
    """
    try:
        load_environment_variables()
        celery_broker_url = create_celery_broker_url()
        celery_result_backend = create_celery_result_backend()
        flask_app = create_flask_app(celery_broker_url, celery_result_backend)
        celery_app = create_celery_app(flask_app)
        return flask_app, celery_app
    except (EnvironmentLoadingError, RuntimeError) as e:
        raise QuizardError("Failed to initialize Flask or Celery application.")
        # shutdown_application(reason="Failed to initialize applications.", error_info={'error': str(e)})


def create_celery_broker_url() -> str:
    """
    Create the broker URL for Celery based on environment variables.

    Returns
    -------
    str
        The broker URL string.

    Raises
    ------
    EnvironmentLoadingError
        If required environment variables are not set, this error is raised.
    """
    try:
        rabbit_user = get_env_variable("RABBITMQ_DEFAULT_USER")
        rabbit_password = get_env_variable("RABBITMQ_DEFAULT_PASS")
        rabbit_port = get_env_variable("RABBITMQ_PORT")
        rabbit_host = get_env_variable("RABBITMQ_HOST")
    except EnvironmentLoadingError as e:
        raise e
    return f"amqp://{rabbit_user}:{rabbit_password}@{rabbit_host}:{rabbit_port}"


def create_celery_result_backend() -> str:
    """
    Create the result backend URL for Celery based on environment variables.

    Returns
    -------
    str
        The result backend URL string.

    Raises
    ------
    EnvironmentLoadingError
        If required environment variables are not set, this error is raised.
    """
    try:
        redis_host = get_env_variable("REDIS_HOST")
        redis_port = get_env_variable("REDIS_PORT")
        redis_db_id = get_env_variable("REDIS_PRIMARY_DB_ID")
        redis_password = get_env_variable("REDIS_PASSWORD", optional=True)
    except EnvironmentLoadingError:
        raise

    if redis_password:
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db_id}"
        logger.info("Connecting to Redis with password.")
    else:
        redis_url = f"redis://{redis_host}:{redis_port}/{redis_db_id}"
        logger.info("Connecting to Redis without a password.")

    return redis_url


def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **other_kwargs):
    """
    Handle Celery task failures.

    This function is called whenever a Celery task fails. It logs the error using Flask's logging setup.
    """
    logger.error(f"Celery task failed: {task_id}", exc_info=exception, args=args, kwargs=kwargs, traceback=traceback)


task_failure.connect(handle_task_failure)
_, celery_app = setup_applications()

if __name__ == '__main__':
    celery_app.start()
