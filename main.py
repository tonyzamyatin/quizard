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
    user_input = input("Enter the name of a test folder, a comma-separated list of test folders, or 'all': ")

    if user_input.lower() == 'all':
        return 'all'

    # Splitting the input by comma and stripping any whitespace from each folder name
    test_folders = [folder.strip() for folder in user_input.split(',')]
    return test_folders


# Load the openai api key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
os.getenv('OPENAI_API_KEY')

test_folders = get_test_folders()
test_runner = TestRunner('run_config.json')

if test_folders == 'all':
    print("Using all test folders...")
    for folder in os.listdir('tests'):
        if os.path.isdir(os.path.join('tests', folder)):
            print(folder)
            test_runner.run_test(os.path.join('tests', folder), 'output/' + folder + '.csv')
else:
    print(f"Using the following test folders: {test_folders}")
    for folder in test_folders:
        if os.path.isdir(os.path.join('tests', folder)):
            test_runner.run_test(os.path.join('tests', folder), 'output/' + folder + '.csv')
        else:
            print(f"No such folder found: {folder}")

exit()

