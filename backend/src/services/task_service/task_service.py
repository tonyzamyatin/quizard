from abc import ABC, abstractmethod

from celery.result import AsyncResult


class ITaskService(ABC):
    """
    Interface for task services.
    """
    @abstractmethod
    def start_task(self, task_params_dto: any, *args, **kwargs) -> str:
        """
        Start a task.
        Parameters
        ----------
        task_params_dto: any
            The parameters of the task.
        args
        kwargs

        Returns
        -------
        task_id: str
            The ID of the task.
        """
        pass

    @abstractmethod
    def get_task_state(self, task_id: str) -> str:
        """
        Get the state of the task.
        Parameters
        ----------
        task_id
            The ID of the task.
        Returns
        -------
        str
            The state of the task.
        """
        pass

    @abstractmethod
    def get_task_info(self, task_id: str) -> dict:
        """
        Get the information of the task.
        Parameters
        ----------
        task_id: str

        Returns
        -------
        dict
            The task's metadata
        """
        pass

    @abstractmethod
    def get_task_result(self, task_id: str) -> AsyncResult:
        """
        Get the result of the task if it is ready.
        Parameters
        ----------
        task_id
            The ID of the task.
        Returns
        -------
        Any
            The result of the task.
        """
        pass

    @abstractmethod
    def get_task_traceback(self, task_id: str) -> str:
        """
        Get the traceback of the task.
        Parameters
        ----------
        task_id
            The ID of the task.
        Returns
        -------
        str
            The traceback of the task.
        """
        pass

    @abstractmethod
    def cancel_task(self, task_id: str) -> None:
        """
        Cancel a task.
        Parameters
        ----------
        task_id: str
            The ID of the task.
        """
        pass

