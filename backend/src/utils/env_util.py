import os

from dotenv import load_dotenv

from src.celery.celery_worker import logger
from src.custom_exceptions.internal_exceptions import EnvironmentLoadingError, InvalidEnvironmentVariableError


def load_environment_variables():
    """
    Load environment variables from the .env file.

    Raises
    ------
    EnvironmentLoadingError
        If the .env file cannot be loaded, this error is raised.
    """
    try:
        load_dotenv()
    except Exception:
        raise EnvironmentLoadingError("There was a problem loading .env.")


def get_env_variable(name: str, optional: bool = False) -> str:
    """
    Retrieves an environment variable.

    Parameters:
        name (str): Name of the environment variable.
        optional (bool): Whether the environment variable is optional.

    Returns:
        str: Value of the environment variable, or None if it's optional and not set.

    Raises:
        InvalidEnvironmentVariableError: If the environment variable is not set and not optional.
    """
    try:
        return os.environ[name]
    except KeyError:
        if optional:
            return None
        else:
            error_msg = f"Environment variable '{name}' not found."
            raise InvalidEnvironmentVariableError(error_msg)


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


def create_celery_result_backend_url() -> str:
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
