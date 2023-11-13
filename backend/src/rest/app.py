import json
from openai import OpenAI
from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
from backend.src.app.app import FlashcardApp
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config

# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, '..', 'config')
log_dir = os.path.join(backend_root_dir, '..', 'logs')

from backend.src.flashcard.flashcard import Flashcard, FlashcardType

app = Flask(__name__)
CORS(app)
api = Api(app)

class FlashCardGenerator(Resource):
    def __init__(self):
        configure_logging(log_dir)
        load_dotenv()

        # TODO: Login and user authentication

        openai.api_key = os.getenv('OPENAI_API_KEY')
        run_config = load_yaml_config(config_dir, "run_config")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Initialize and run app with the text_input
        self.app = FlashcardApp(run_config, client)

    def post(self):
        json_data = request.get_json(force=True)
        print(json_data)  # print the received data
        # parse mode
        mode = json_data['mode']
        input_text = json_data['inputText']
        print('mode: {}'.format(mode))
        print('input text: {}'.format(input_text))
        example_flashcard = Flashcard(1, FlashcardType.DEFINITION, 'What is a flashcard?', 'A flashcard is...')
        # TODO: call the generator with mode and input text and assign the results to the flashcards array
        flashcard_deck = self.app.run(input_text)
        #example_flashcard = Flashcard(1, FlashcardType.DEFINITION, 'What is a flashcard?', 'A flashcard is...')
        flashcards = flashcard_deck.flashcards
        flashcards_as_dict = [{'id': card.id, 'type': card.type, 'frontSide': card.frontside, 'backSide': card.backside} for card in flashcards]
        return jsonify({'flashCards': flashcards_as_dict})


api.add_resource(FlashCardGenerator, '/api/v1/flashcard/generate')

if __name__ == '__main__':
    app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
