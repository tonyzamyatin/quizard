import json

from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS

from backend.src.flashcard.flashcard import Flashcard, FlashcardType

app = Flask(__name__)
CORS(app)
api = Api(app)

class FlashCardGenerator(Resource):

    def post(self):
        json_data = request.get_json(force=True)
        print(json_data)  # print the received data
        # parse mode
        mode = json_data['mode']
        input_text = json_data['inputText']
        print('mode: {}'.format(mode))
        print('input text: {}'.format(input_text))
        example_flashcard = Flashcard(1, FlashcardType.DEFINITION, 'What is a flashcard?', 'A flashcard is...')
        # todo call the generator with mode and input text and assign the results to the flashcards array
        flashcards = [example_flashcard]
        flashcards_as_dict = [{'id': card.id, 'type': card.type, 'frontSide': card.frontside, 'backSide': card.backside} for card in flashcards]
        return jsonify({'flashCards': flashcards_as_dict})


api.add_resource(FlashCardGenerator, '/api/v1/flashcard/generate')

if __name__ == '__main__':
    app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
