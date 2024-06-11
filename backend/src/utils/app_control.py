# src/utils/app_control.py
import sys

import celery
import openai
import structlog

logger = structlog.get_logger()


def shutdown_application(reason: str = '', celery_app: celery.Celery = None, openai_client: openai.OpenAI = None, **error_info):
    """
    Shuts down the application by performing clean-up operations and then
    terminating the process immediately.

    Parameters
    ----------
    openai_client : openai.OpenAI, optional
        The OpenAI client instance to shut down. If not specified, OpenAI clean-up will be skipped.
    celery_app : Celery, optional
        The Celery application instance to shut down. If not specified, Celery clean-up will be skipped.
    reason : str, optional
        A message describing the reason for the shutdown. The default is an empty string.
    **error_info: dict, optional
        Additional logging information provided as keyword arguments for structural logging.

    Raises
    ------
    Exception
        If any exception occurs during the clean-up process, it will be logged as an error, but the
        application will still attempt to shut down immediately.

    Notes
    -----
    This function uses `os._exit(1)` to terminate the process, which exits without calling cleanup handlers,
    flushing stdio buffers, etc. This should be used in situations where a quick exit is preferred over
    a graceful shutdown.
    """
    logger.critical("Application shutdown initiated", reason=reason, **error_info)

    # Gracefully shutdown Celery workers, if a Celery app is provided
    if celery_app:
        try:
            # Close the Celery connection
            with celery_app.connection() as connection:
                connection.close()
                logger.info("Celery connection closed")

            # If using a persistent broker like Redis, close the broker connection
            broker_connection = celery_app.connection_for_write()
            broker_connection.close()
            logger.info("Celery broker connection closed")
        except Exception as e:
            logger.error("Error during Celery shutdown", error=str(e))

    if openai_client:
        try:
            openai_client.close()
            logger.info("OpenAI client closed")
        except Exception as e:
            logger.error("Error during OpenAI client shutdown", error=str(e))

    # Perform any other necessary cleanup here

    # Terminate the process
    sys.exit()
