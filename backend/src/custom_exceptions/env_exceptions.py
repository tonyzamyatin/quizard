# src/custom_exceptions/env_exceptions.py
class EnvironmentLoadingError(EnvironmentError):
    """Custom exception for errors relating loading the .env file."""
    pass


class InvalidEnvironmentVariableError(EnvironmentError):
    """Custom exception for the attempted retrival of an undefined variable from .env."""
    pass
