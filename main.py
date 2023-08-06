import os
import openai
from dotenv import load_dotenv

# load the openai api key from .env file
load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

print(openai.Model.list())