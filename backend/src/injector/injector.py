from __future__ import annotations
from typing import TYPE_CHECKING

from celery import Celery
from flask import Flask
from injector import inject, Module, singleton, Binder
from openai import OpenAI

from src.rest.celery_config import create_celery_app
from src.rest.flask_factory import create_flask_app
from src.utils.env_util import load_environment_variables, get_env_variable, create_celery_broker_url, create_celery_result_backend_url

if TYPE_CHECKING:
    # Import only for type checking to avoid circular dependencies
    from src.services.task_service.flashcard_generator_task_service import FlashcardGeneratorTaskService
    from src.services.flashcard_service.flashcard_generator_service.flashcard_generator import FlashcardGenerator
    from src.services.flashcard_service.flashcard_service import FlashcardService


class ConfigModule(Module):
    def configure(self, binder: Binder):
        binder.bind(
            OpenAI,
            to=OpenAI(api_key=get_env_variable('OPENAI_API_KEY')),
            scope=singleton,
        )


class AppModule(Module):

    @singleton
    def provide_flask_app(self) -> Flask:
        load_environment_variables()
        celery_broker_url = create_celery_broker_url()
        celery_result_backend_url = create_celery_result_backend_url()
        flask_app = create_flask_app(celery_broker_url, celery_result_backend_url)
        flask_app.config['SECRET_KEY'] = get_env_variable('SECRET_KEY')
        return flask_app

    @singleton
    @inject
    def provide_celery_app(self, flask_app: Flask) -> Celery:
        celery_app = create_celery_app(flask_app)
        return celery_app

    @singleton
    @inject
    def provide_flashcard_generator(self, client: OpenAI) -> FlashcardGenerator:
        return FlashcardGenerator(client)

    @singleton
    @inject
    def provide_flashcard_service(self, flashcard_generator: FlashcardGenerator) -> FlashcardService:
        return FlashcardService(flashcard_generator)

    @singleton
    @inject
    def provide_task_service(self, flask_app: Flask, celery_app: Celery) -> FlashcardGeneratorTaskService:
        return FlashcardGeneratorTaskService(flask_app, celery_app)
