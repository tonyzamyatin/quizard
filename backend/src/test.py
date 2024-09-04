from dependency_injector.wiring import inject, Provide

from src.container import get_container, Container
from src.services.task_service.task_service_interface import ITaskService


@inject
def di_test(task_service3: ITaskService = Provide[Container.flashcard_generator_task_service]):
    print("Task service injected by container:", task_service3.__class__)


if __name__ == '__main__':
    container = get_container()

    task_service1 = container.flashcard_generator_task_service()
    print("Task service provided directly by container:", task_service1.__class__)

    task_service2 = Provide[Container.flashcard_generator_task_service]
    print("Task service provided indirectly by container:", task_service2.__class__)

    di_test(task_service3=container.flashcard_generator_task_service)
