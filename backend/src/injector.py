from injector import inject, Injector, Module, singleton
from openai import OpenAI

from src.services.task_service.flashcard_generator_task_service import FlashcardGeneratorTaskService
from src.utils.global_helpers import get_env_variable
from src.services.flashcard_service.flashcard_generator_service.flashcard_generator import FlashcardGenerator
from src.services.flashcard_service.flashcard_service import FlashcardService


class ConfigModule(Module):
    def configure(self, binder):
        binder.bind(
            OpenAI,
            to=OpenAI(api_key=get_env_variable('OPENAI_API_KEY')),
            scope=singleton,
        )


class FlashcardGeneratorModule(Module):
    @singleton
    @inject
    def provide_flashcard_generator(self, client: OpenAI) -> FlashcardGenerator:
        return FlashcardGenerator(client)


class FlashcardServiceModule(Module):
    @singleton
    @inject
    def provide_flashcard_service(self, flashcard_generator: FlashcardGenerator) -> FlashcardService:
        return FlashcardService(flashcard_generator)


class TaskServiceModule(Module):
    @singleton
    @inject
    def provide_task_service(self, flashcard_service: FlashcardService) -> FlashcardGeneratorTaskService:
        return FlashcardGeneratorTaskService(flashcard_service)
