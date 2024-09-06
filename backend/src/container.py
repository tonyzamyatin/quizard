# src/container.py
import sys

from dependency_injector import containers, providers
from openai import OpenAI

from src.rest.flask_factory import create_flask_app
from src.utils.env_util import load_environment_variables, get_env_variable, create_celery_broker_url, create_celery_result_backend_url


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    flask_app = providers.Singleton(
        create_flask_app,
        broker_url=config.celery_broker_url,
        result_backend_url=config.celery_result_backend_url,
        import_name=__name__,
    )

    openai_client = providers.Factory(
        OpenAI,
        api_key=config.openai_api_key,
    )

    # Define of dummy services, to be replaced with actual services when calling configure_services (this is to avoid circular imports)
    celery_app = providers.Factory(object)
    flashcard_generator = providers.Factory(object)
    flashcard_service = providers.Factory(object)
    flashcard_generator_task_service = providers.Factory(object)


# Global container instance to ensure singleton behavior
_container = None


def configure_services(container: Container) -> None:
    """
    Configure the services of the container. This function is used to override the default services with the actual services.
    Parameters
    ----------
    container: Container
        The container instance
    """
    # Import the services inside function to avoid circular imports
    from src.celery.celery_config import create_celery_app
    from src.services.flashcard_service.flashcard_generator_service.flashcard_generator import FlashcardGenerator
    from src.services.flashcard_service.flashcard_service import FlashcardService
    from src.services.task_service.flashcard_generator_task_service import FlashcardGeneratorTaskService

    container.celery_app = providers.Singleton(
        create_celery_app,
        flask_app=container.flask_app,
    )

    container.flashcard_generator.override(
        providers.Factory(
            FlashcardGenerator,
            client=container.openai_client,
        )
    )

    container.flashcard_service.override(
        providers.Factory(
            FlashcardService,
            flashcard_generator=container.flashcard_generator,
        )
    )

    container.flashcard_generator_task_service.override(
        providers.Factory(
            FlashcardGeneratorTaskService,
            flask_app=container.flask_app,
            celery_app=container.celery_app,
        )
    )


def get_container() -> Container:
    """
    Get the global container instance. If the container is not initialized, a new global container is started.
    Returns
    -------
    Container
        The global container instance
    """
    global _container
    if _container is None:
        _container = start_container()
    return _container


def start_container() -> Container:
    """
    Initializes, configures and wires a container instance.
    Returns
    -------
    Container
        The container instance
    """
    load_environment_variables()
    container = Container()
    container.config.from_dict({
        'openai_api_key': get_env_variable('OPENAI_API_KEY'),
        'secret_key': get_env_variable('SECRET_KEY'),
        'celery_broker_url': create_celery_broker_url(),
        'celery_result_backend_url': create_celery_result_backend_url(),
    })
    container.wire(modules=[sys.modules['__main__'], 'src.celery.tasks'])
    configure_services(container)
    return container
