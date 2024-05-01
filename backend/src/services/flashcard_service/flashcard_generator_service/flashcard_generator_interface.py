# src/services/flashcard_service/flashcard_generator_service/flashcard_generator_interface.py

from abc import ABC, abstractmethod
from typing import Optional, Callable

from src.dtos.generator_task import FlashcardGeneratorTaskDto
from src.entities.flashcard_deck.flashcard_deck import FlashcardDeck


class IFlashcardGenerator(ABC):
    """
    Interface for flashcard generators.
    """
    @abstractmethod
    def generate_flashcard_deck(self, flashcards_generator_task: FlashcardGeneratorTaskDto, fn_update_progress: Optional[Callable], *args, **kwargs) -> FlashcardDeck:
        """
        Generate flashcards based on input.
        Parameters
        ----------
        flashcards_generator_task: FlashcardGeneratorTaskDto
            The DTO containing the parameters for generating flashcards including language, mode, export format, and input.
        fn_update_progress: Optional[Callable]
            Optional callback function.
        args
        kwargs
        Returns
        -------
        FlashcardDeck
            The generated flashcards.
        """
        pass
