import os
import openai
from dotenv import load_dotenv


def read_file(path) -> str:
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

# load the openai api key from .env file
load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

# print(openai.Model.list())
example_system_prompt = read_file('example_system_prompt.txt')
example_user_input = read_file('example_user_input.txt')
example_response = read_file('example_response.txt')

system_prompt = read_file('system_prompt.txt') # Generiere 5 flashcards ...
user_input = read_file('user_input.txt') # Ausgangstext

messages = [
    {"role": "user", "content": example_user_input},
    {"role": "system", "content": example_system_prompt},
    {"role": "assistant", "content": example_response},

    {"role": "user", "content": user_input},
    {"role": "system", "content": system_prompt}
]
completion35 = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=messages, max_tokens=1000)

print("---")
print(completion35)
print(completion35.response_ms)
text: str = completion35.choices[0].message.content

f = open('response.txt', 'w')

for e in text.split('\n'):
    print(e)
    print(e.split(';'))
    f.write(e)
    f.write('\n')
f.close()