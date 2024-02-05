from ..flashcard_service.flashcard.flashcard import Flashcard

# Base Exception for the Quizard application.
class QuizardError(Exception):
    """Parent class of all errors related to the Quizard application"""
    pass


# Exceptions related to configuration
class ConfigError(QuizardError):
    """Parent class of all errors related to config"""
    pass


class ConfigInvalidValueError(ConfigError):
    """Custom exception for invalid values specified in the run config"""
    pass


class ConfigLoadingError(ConfigError):
    """Custom exception for config loading issues."""
    pass


class UnsupportedLanguageError(ConfigError):
    """Custom exception for invalid or unsupported languages specified in the config"""
    pass


# Exceptions related to Flashcard generation
class FlashcardGenerationError(QuizardError):
    """Parent class of all errors related to flashcard generation."""
    pass


class FlashcardInvalidFormatError(FlashcardGenerationError):
    """Exception raised when the flashcard format is invalid."""
    pass


class FlashcardPrefixError(FlashcardInvalidFormatError):
    """Exception raised for unexpected prefixes."""

    def __init__(self, message: str, flashcard: Flashcard):
        super().__init__(message)
        self.flashcard = flashcard


# Exceptions related to other issues
class PromptSizeError(QuizardError):
    """Custom exception for prompt size issues."""
    pass
