# Base class for API errors
class FlaskAPIError(Exception):
    """Base class for exceptions in the API."""
    pass


# Specific API error classes
class APIRequestError(FlaskAPIError):
    """Exception raised for errors in the API request."""
    pass


class TaskNotFoundError(APIRequestError):
    """Exception raised if task is not found"""
    pass


class APIDataValidationError(FlaskAPIError):
    """Exception raised for errors due to invalid data provided to the API."""
    pass


class APIAuthenticationError(FlaskAPIError):
    """Exception raised for errors in API authentication."""
    pass


class APIAuthorizationError(FlaskAPIError):
    """Exception raised for errors in API authorization."""
    pass


class APIResourceNotFoundError(FlaskAPIError):
    """Exception raised when a requested resource is not found in the API."""
    pass


# Flashcard-related API error classes
class FlashcardAPIError(FlaskAPIError):
    """Base class for exceptions in the flashcard API."""
    pass


class FlashcardGenerationError(FlashcardAPIError):
    """Exception raised during the flashcard generation process."""
    pass


class FlashcardInputError(FlashcardAPIError):
    """Exception raised for invalid input to the flashcard generation endpoint."""
    pass


class HealthCheckError(FlashcardAPIError):
    """Exception raised for failed health check."""
    pass
