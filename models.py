import os
import openai
from dotenv import load_dotenv
openai.organization = "org-x2xkluCOyFQaVAdlsXM0cxWG"
load_dotenv('env')
openai.api_key = os.getenv('OPENAI_API_KEY')
print(openai.Model.list())