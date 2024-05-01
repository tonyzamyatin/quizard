# src/custom_exceptions/external_exceptions.py
class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass


class NotFoundException(Exception):
    """Exception raised for not resource found errors."""
    pass


class TokenAuthenticationError(AuthenticationError):
    """Exception raised for token authentication errors."""
    pass


class TaskNotFoundError(NotFoundException):
    """Exception raised if task is not found"""
    pass


class ResultNotFoundError(NotFoundException):
    """Exception raised if task result is not found"""
    pass


class HealthCheckError(Exception):
    """Exception raised for failed health check."""
    pass
