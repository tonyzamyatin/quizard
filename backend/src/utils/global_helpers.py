import os
import logging
import yaml
from backend.src.custom_exceptions.custom_exceptions import ConfigLoadingError


def configure_logging(log_dir):
    log_file = os.getenv('DEBUG_LOG', default='debug.log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, log_file)

    logging.basicConfig(
        filename=log_path,
        filemode='a',
        level=logging.WARNING,  # Set to DEBUG level when debugging
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_yaml_config(config_dir, config_name: str) -> dict:
    try:
        with open(os.path.join(config_dir, f"{config_name}.yaml")) as file:
            try:
                return yaml.load(file, Loader=yaml.FullLoader)
            except yaml.YAMLError as e:
                raise ConfigLoadingError(f"An error occurred while loading the YAML file: {e}")  # Raise custom exception
    except FileNotFoundError:
        logging.error("The file was not found.")
        raise FileNotFoundError("The specified configuration file was not found.")
    except PermissionError:
        logging.error("Permission denied.")
        raise PermissionError("You do not have permission to read the configuration file.")
    except IsADirectoryError:
        logging.error("Expected a file, but found a directory.")
        raise IsADirectoryError("The specified path points to a directory, not a file.")
    except OSError as e:
        logging.error(f"An OSError occurred: {e}")
        raise OSError(f"An unexpected error occurred: {e}")


def start_log(log_dir):
    log_path = os.path.join(log_dir, os.getenv('LOG_FILE', default='logs/logs.txt'))
    with open(log_path, 'a') as f:
        f.write('\n-----------------------------------------------------------------------------------------------------------\n')


def write_to_log(message: str):
    """Write to the logs and also print the message."""
    with open(os.getenv('LOG_FILE', default='logs/logs.txt'), 'a') as f:
        f.write(message + '\n')
    print(message)


def read_file(file_path: str) -> str:
    """Reads the file content from the given path."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        raise FileNotFoundError(f"File {file_path} not found.")
    except PermissionError:
        logging.error(f"Permission denied for reading the file {file_path}.")
        raise PermissionError(f"Permission denied for reading the file {file_path}.")
    except Exception as e:
        logging.error(f"An error occurred while reading the file {file_path}: {str(e)}")
        raise Exception(f"An error occurred while reading the file {file_path}: {str(e)}")



def format_num(number: int) -> str:
    """Formats an integer by adding a dot every three digits."""
    reversed_str = str(number)[::-1]
    formatted_str = '.'.join(reversed_str[i:i + 3] for i in range(0, len(reversed_str), 3))
    return formatted_str[::-1]


def inset_into_string(insert: str, target: str, position: int):
    if position == -1:
        return target + insert
    else:
        return target[:position] + insert + target[position:]
