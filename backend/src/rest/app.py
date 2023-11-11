from flask import Flask, request, jsonify
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
        return {'flashCards': []}
        # this is just example output

api.add_resource(FlashCardGenerator, '/api/v1/flashcard/generate')

if __name__ == '__main__':
    app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
