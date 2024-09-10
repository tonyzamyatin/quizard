# src/utils/file_util.py
import os
from pathlib import Path

import yaml

from src.custom_exceptions.internal_exceptions import ConfigLoadingError


def load_yaml_config(config_dir: Path, config_name: str) -> dict:
    """
    Loads a YAML configuration file.

    Parameters:
        config_dir (Path): Directory where the config file is stored.
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
    file_path = config_dir / config_name
    try:
        with open(file_path) as file:
            try:
                return yaml.safe_load(file)
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