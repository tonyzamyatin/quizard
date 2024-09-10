from abc import ABC, abstractmethod
from typing import Any

from src.enums.task_states import TaskState


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
    def get_task_state(self, task_id: str) -> TaskState:
        """
        Get the state of the task.

        Parameters
        ----------
        task_id
            The ID of the task.

        Returns
        -------
        TaskState
            The state of the task.
        """
        pass

    @abstractmethod
    def get_task_info(self, task_id: str) -> dict:
        """
        Get the metadata of the task.

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
    def get_task_result(self, task_id: str) -> Any:
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

        Raises
        ------
        ResultNotFoundError
            If the task is not ready.
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

    @abstractmethod
    def generate_retrieval_token(self, task_id) -> str:
        """
        Generate a token for retrieving the task result.

        Parameters
        ----------
        task_id
            The ID of the task the result of which should be retrieved.

        Returns
        -------
        str
            The token for retrieving the task result.
        """
        pass

    @abstractmethod
    def verify_retrival_token(self, token) -> str:
        """
        Verify the token for retrieving the task result.

        Parameters
        ----------
        token
            The token to verify.

        Returns
        -------
        str
            The ID of the task the token corresponds to.

        Raises
        ------
        InvalidTokenError
            If the token is invalid.
        """
        pass
