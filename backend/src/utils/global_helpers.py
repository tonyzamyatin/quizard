import os
from typing import Optional, List

import yaml
from dotenv import load_dotenv

from src.custom_exceptions.env_exceptions import InvalidEnvironmentVariableError, EnvironmentLoadingError
from src.custom_exceptions.quizard_exceptions import ConfigLoadingError, UnsupportedOptionError

def load_yaml_config(config_dir: str, config_name: str) -> dict:
    """
    Loads a YAML configuration file.

    Parameters:
        config_dir (str): Directory where the config file is stored.
        config_name (str): Name of the YAML config file to load (with extension).

    Returns:
        dict: Contents of the YAML file.

    Raises:
        ConfigLoadingError: If the YAML file cannot be loaded due to parsing errors.
        FileNotFoundError: If the YAML file is not found.
        PermissionError: If there is no permission to read the file.
        IsADirectoryError: If the path refers to a directory instead of a file.
        OSError: If another OS-related error occurs.
    """
    file_path = os.path.join(config_dir, f"{config_name}")
    try:
        with open(file_path) as file:
            try:
                return yaml.load(file, Loader=yaml.FullLoader)
            except yaml.YAMLError as e:
                raise ConfigLoadingError(f"An error occurred while loading the YAML file: {e}")  # Raise custom exception
    except FileNotFoundError:
        raise ConfigLoadingError(f"The specified configuration file was not found: {file_path}")
    except PermissionError:
        raise ConfigLoadingError(f"No permission to read the configuration file: {file_path}")
    except IsADirectoryError:
        raise ConfigLoadingError(f"The specified path points to a directory, not a file: {file_path}")
    except OSError as e:
        raise ConfigLoadingError(f"An unexpected error occurred: {e}")


def load_environment_variables():
    """
    Load environment variables from the .env file.

    Raises
    ------
    EnvironmentLoadingError
        If the .env file cannot be loaded, this error is raised.
    """
    try:
        load_dotenv()
    except Exception:
        raise EnvironmentLoadingError("There was a problem loading .env.")


def get_env_variable(name: str, optional: bool = False) -> str:
    """
    Retrieves an environment variable.

    Parameters:
        name (str): Name of the environment variable.
        optional (bool): Whether the environment variable is optional.

    Returns:
        str: Value of the environment variable, or None if it's optional and not set.

    Raises:
        InvalidEnvironmentVariableError: If the environment variable is not set and not optional.
    """
    try:
        return os.environ[name]
    except KeyError:
        if optional:
            return None
        else:
            error_msg = f"Environment variable '{name}' not found."
            raise InvalidEnvironmentVariableError(error_msg)


def read_file(file_path: str) -> str:
    """
    Reads the content of a file.

    Parameters:
        file_path (str): Path to the file to read.

    Returns:
        str: Content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If read permission is denied.
        Exception: If an unexpected error occurs while reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found.")
    except PermissionError:
        raise PermissionError(f"Permission denied for reading the file {file_path}.")
    except OSError:
        raise OSError(f"An error occurred while reading the file {file_path}.")


def format_num(number: int) -> str:
    """
    Formats an integer number with thousands separators.

    Parameters:
        number (int): The number to format.

    Returns:
        str: The formatted number with dot separators.
    """
    reversed_str = str(number)[::-1]
    formatted_str = '.'.join(reversed_str[i:i + 3] for i in range(0, len(reversed_str), 3))
    return formatted_str[::-1]
    # return f"{number:,}".replace(',', '.')    TODO: Try out this


def inset_into_string(insert: str, target: str, position: int) -> str:
    """
    Inserts a string into a target string at a given position.

    Parameters:
        insert (str): The string to insert.
        target (str): The target string into which to insert.
        position (int): The position at which to insert the string. Bounds: -1 <= position <= len(target), where -1 is shorthand for appending.
    Returns:
        str: The combined string after insertion.

    Raises:
        ValueError: If the position is out of bounds of the target string.
    """
    if not (-1 <= position <= len(target)):
        raise ValueError(f"Position {position} is out of bounds for target string of length {len(target)}.")
    if position == -1:
        # Append the insert string to the end of the target string
        return target + insert
    else:
        # Insert the string at the specified position
        return target[:position] + insert + target[position:]


def validate_config_param(parameter: str, accepted_params: List[str]):
    """
    Validates a single configuration parameter against a list of accepted values.

    Parameters
    ----------
    parameter : str
        The parameter value to validate.
    accepted_params : List[str]
        List of accepted values for the parameter.

    Raises
    ------
    UnsupportedOptionError
        If the parameter value is not in the list of accepted values.
    """
    if parameter.lower() not in [param.lower() for param in accepted_params]:
        raise UnsupportedOptionError(f"Invalid parameter: {parameter}. Expected one of {accepted_params}.")
