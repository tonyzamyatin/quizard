# src/services/flashcard_service/flashcard_generator/flashcard_generator_interface.py

from abc import ABC, abstractmethod
from typing import Optional, Callable


class IFlashcardGenerator(ABC):
    """
    Interface for flashcard generators.
    """
    @abstractmethod
    def generate_flashcards(self, flashcards_generator_task: any, update_progress: Optional[Callable], *args, **kwargs) -> any:
        """
        Generate flashcards based on input.
        Parameters
        ----------
        flashcards_generator_task: any
            The DTO containing the parameters for generating flashcards including language, mode, export format, and input.
        update_progress: Optional[Callable]
            Optional callback function.
        args
        kwargs
        Returns
        -------
        any
            The generated flashcards.
        """
        pass
