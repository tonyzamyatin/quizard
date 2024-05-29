# src/injector/injector_setup.py
from injector import Injector
from src.injector.injector import ConfigModule, AppModule

# Initialize the Injector with all necessary modules
injector = Injector([
    ConfigModule(),
    AppModule()
])


def get_injector():
    """
        Returns the singleton Injector instance configured with the application's modules.

        This function ensures that there is only one instance of the Injector
        throughout the application lifecycle, providing a consistent dependency
        injection context.

        The Injector is pre-configured with the following modules:
        - ConfigModule: Provides external service configurations and instances.
        - AppModule: Provides the Flask app, Celery app, and all service instances.

        Returns:
            Injector: The singleton Injector instance configured with the application's modules.

    """
    return injector
