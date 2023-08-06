import os
import openai
from dotenv import load_dotenv

from example_messages import ExampleMessages
from flashcard_service import FlashCardService


def read_file(path) -> str:
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

# Load the openai api key from .env file
load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load example used in query
example_system_prompt = read_file('example/example_system_prompt.txt')
example_user_input = read_file('example/example_user_input.txt')
example_response = read_file('example/example_response.txt')

# Load the user input and system prompt
system_prompt = read_file('input/system_prompt.txt') # Generiere 5 flashcards ...
user_input = read_file('input/user_input.txt') # Ausgangstext

example_messages = ExampleMessages(example_user_input, example_system_prompt, example_response)
service = FlashCardService(os.getenv('OPENAI_API_KEY'), example_messages)
deck = service.generate(user_input, system_prompt)
deck.save_as_csv('output/generated.csv')
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