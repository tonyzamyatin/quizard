import os
import openai
from dotenv import load_dotenv

from test_runner import TestRunner


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
# messages = [
#     {"role": "user", "content": example_user_input},
#     {"role": "system", "content": example_system_prompt},
#     {"role": "assistant", "content": example_response},
#     {"role": "user", "content": user_input},
#     {"role": "system", "content": system_prompt}
# ]
# completion35 = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, max_tokens=1000)
#
# print("---")
# print(completion35)
# print(completion35.response_ms)
# text: str = completion35.choices[0].message.content
#
# f = open('output/response.txt', 'w')
#
# for e in text.split('\n'):
#     print(e)
#     print(e.split(';'))
#     f.write(e)
#     f.write('\n')
# f.close()
#
# service = FlashCardService('test')
