import json
import os
import logging
import openai
import traceback
from dotenv import load_dotenv
from backend.tests.test_runner import TestRunner
from backend.src.utils.global_helpers import write_to_log


# Configure logging
def configure_logging():
    log_file = os.getenv('DEBUG_LOG', default='debug.log')
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_path = os.path.join(logs_dir, log_file)

    logging.basicConfig(
        filename=log_path,
        filemode='a',
        level=logging.DEBUG,  # Set to DEBUG level
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# todo: Define the root directory of your backend code.
# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_configs_dir = os.path.join(backend_root_dir, 'tests', 'test_configs')
log_dir = os.path.join(backend_root_dir, 'logs')


# Read the current test configuration
def read_current_test_config():
    with open(os.path.join(test_configs_dir, "current_test_config.json"), 'r') as f:
        return json.load(f)


# Start a new section in the logs
def start_log():
    log_path = os.path.join(log_dir, os.getenv('LOG_FILE', default='logs/logs.txt'))
    with open( log_path, 'a') as f:
        f.write('\n-----------------------------------------------------------------------------------------------------------\n')


# Get specific test folders from the terminal
def get_test_folders():
    while True:
        logging.debug("Getting user input for test folder selection.")
        user_input = input("Enter 'f' to use the test config file, 'n' to enter a new test_config file, or 'l' to use a list of test folders: ")
        current_test_config = read_current_test_config()
        full_path = os.path.join(test_configs_dir, current_test_config["current_test_config"])
        logging.debug(f"Read saved test config: {current_test_config['current_test_config']}")

        if user_input == 'f':
            try:
                logging.debug("Attempting to use saved test config.")
                print(os.environ)
                # Debugging
                logging.debug(f"Full path: {full_path}")
                logging.debug(f"Available test configs in: {os.listdir(test_configs_dir)}.")

                if os.path.isfile(full_path):
                    logging.debug(f"{full_path} exists.")
                else:
                    logging.debug(f"{full_path} does not exist.")

                if os.access(full_path, os.R_OK):
                    logging.debug(f"File {full_path} is accessible to read")
                else:
                    logging.debug(f"File {full_path} is not readable")

                with open(full_path, 'r', encoding='UTF-8') as file:
                    folder_names = [line.strip() for line in file if line.strip()]
                    start_log()
                    write_to_log(f"Using {current_test_config['current_test_config']} as test configuration...")
                    return folder_names
            except FileNotFoundError:
                print(os.environ)
                logging.debug(f"Could not open {full_path} for reading.")
                logging.debug(f"Stack trace: {traceback.format_exc()}")
                logging.debug(f"Environment: {os.environ}")
                logging.debug(f"Path repr: {repr(full_path)}")
                print(f"File {current_test_config['current_test_config']} not found. Please enter a valid file.")

        elif user_input == 'n':
            while True:
                new_test_config = input("Enter name of test_config file to use as new test configuration: ")
                logging.debug(f"New test config entered: {new_test_config}")
                if not new_test_config.endswith(".txt"):
                    logging.warning("File name does not end with '.txt'.")
                    print("File name must end with '.txt'.")
                    continue
                full_path = os.path.join(test_configs_dir, new_test_config)

                # Debugging
                logging.debug(f"Full path: {full_path}")
                logging.debug(f"Available test configs in: {os.listdir(test_configs_dir)}.")

                if os.path.isfile(full_path):
                    logging.debug(f"{full_path} exists.")
                else:
                    logging.debug(f"{full_path} does not exist.")

                if os.access(full_path, os.R_OK):
                    logging.debug(f"File {full_path} is accessible to read")
                else:
                    logging.debug(f"File {full_path} is not readable")

                try:
                    logging.debug("Attempting to open new test config.")
                    file = open(full_path, 'r')
                    file.close()
                    logging.debug("File could be opened.")
                except FileNotFoundError:
                    logging.warning(f"File {new_test_config} not found.")
                    stack_trace = traceback.format_exc()
                    logging.warning(f"Stack trace: {stack_trace}")
                except Exception as e:
                    logging.warning(f"Exception caught: {e}")
                    stack_trace = traceback.format_exc()
                    logging.warning(f"Stack trace: {stack_trace}")

                try:
                    with open(full_path, 'r', encoding='UTF-8') as file:
                        folder_names = [line.strip() for line in file if line.strip()]
                        logging.debug("Folder names were collected.")
                        start_log()
                        logging.debug(f"Starting running log.")
                        write_to_log(f"Using {new_test_config} as new test configuration...")
                        logging.debug(f"Writing to log works.")
                        current_test_config['current_test_config'] = new_test_config
                        logging.debug("")
                    with open(os.path.join(test_configs_dir, 'current_test_config.json'), 'w') as f:
                        json.dump(current_test_config, f)
                    return folder_names
                except FileNotFoundError:
                    logging.warning(f"File not found: There was an issue with reading {new_test_config}.")
                    print(f"File {new_test_config} not found. Please enter a valid file.")

        elif user_input == 'l':
            folder_list = input("Enter comma-separated list of test folders: ")
            logging.debug(f"Folder list entered: {folder_list}")
            folder_names = [folder_name.strip() for folder_name in folder_list.split(',')]
            start_log()
            write_to_log(f"Using the following test folders: {folder_names}")
            return folder_names

        else:
            logging.warning("Unknown command entered.")
            print("Unknown command, please try again.")


if __name__ == '__main__':
    # Configure logging and load environment variables
    configure_logging()
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Get specific test folders from terminal
    test_folders = get_test_folders()

    # Initialize and run tests
    test_runner = TestRunner(os.path.join(backend_root_dir, 'config', 'run_config.yaml'), backend_root_dir)
    write_to_log(f"Using the following test folders: {test_folders}\n")

    for folder in test_folders:
        test_folder_path = os.path.join(test_configs_dir, '..', folder)
        if os.path.isdir(test_folder_path):
            test_runner.run_test(test_folder_path, f'output/{folder}.csv')
        else:
            write_to_log(f"No such folder found: {folder}")