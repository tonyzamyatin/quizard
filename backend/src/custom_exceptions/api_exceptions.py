# Base class for API errors
class APIError(Exception):
    """Base class for exceptions in the API."""
    pass


# Specific API error classes
class APIRequestError(APIError):
    """Exception raised for errors in the API request."""
    pass


class APIDataValidationError(APIError):
    """Exception raised for errors due to invalid data provided to the API."""
    pass


class APIAuthenticationError(APIError):
    """Exception raised for errors in API authentication."""
    pass


class APIAuthorizationError(APIError):
    """Exception raised for errors in API authorization."""
    pass


class APIResourceNotFoundError(APIError):
    """Exception raised when a requested resource is not found in the API."""
    pass


# Flashcard-related API error classes
class FlashcardAPIError(APIError):
    """Base class for exceptions in the flashcard API."""
    pass


class FlashcardGenerationError(FlashcardAPIError):
    """Exception raised during the flashcard generation process."""
    pass


class FlashcardInputError(FlashcardAPIError):
    """Exception raised for invalid input to the flashcard generation endpoint."""
    pass
