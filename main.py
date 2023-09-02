import os
import logging
import openai
from dotenv import load_dotenv
from test_runner import TestRunner

logging.basicConfig(filename=os.getenv('FLASHCARD_ERRORS_LOG_PATH', default='log/flashcard_errors.log'),
                    filemode='a',
                    level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def get_test_folders():
    while True:
        user_input = input("Enter 'f' to use a test_config file or 'l' to use a list of test folders: ")
        # Handling of test_config files
        if user_input == 'f':
            while True:
                user_input = input("Enter name of test config to run: ")
                if not user_input.endswith(".txt"):
                    print("File name must end with '.txt'.")
                # Attempt to read the file and get the folder names
                try:
                    with open(os.path.join('teste_configs', user_input), 'r') as file:
                        folder_names = [line.strip() for line in file.readlines() if line.strip() != '']
                    return folder_names
                except FileNotFoundError:
                    print(f"File {user_input} not found. Please enter a valid file.")

        # Handling of comme seperated lists of folders
        elif user_input == 'l':
            while True:
                user_input = input("Enter comma seperated list of test folders: ")
                try:
                    folder_names = [folder_name.strip() for folder_name in user_input.split(',')]
                    return folder_names
                except:
                    print("Test folder names must be seperated by ','.")
        else:
            print("Unknown command, please try again.")


# Load the openai api key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
os.getenv('OPENAI_API_KEY')

# Get specific test folders from terminal
test_folders = get_test_folders()

# Load running configuration
test_runner = TestRunner('run_config.json')

# Run tests
print(f"Using the following test folders: {test_folders}")
for folder in test_folders:
    if os.path.isdir(os.path.join('tests', folder)):
        test_runner.run_test(os.path.join('tests', folder), 'output/' + folder + '.csv')
    else:
        print(f"No such folder found: {folder}")

exit()
