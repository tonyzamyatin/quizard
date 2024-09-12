from flask import Flask, request
from generate_flashcards import generate_flashcards
from dotenv import load_dotenv
import os
app = Flask(__name__)

# Loads env file from current directory
load_dotenv()
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/flashcards/generate", methods=['POST'])
def generate():

    flashcards = generate_flashcards(request.json['prompt'])

    # TODO Export flashcards as readable format e.g. anki

    return f"{flashcards}"

