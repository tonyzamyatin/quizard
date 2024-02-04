import json

import openai
from openai import OpenAI
from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS
import os
from dotenv import load_dotenv
from backend.src.app.app import FlashcardApp
from backend.src.custom_exceptions.env_exceptions import EnvironmentLoadingError, InvalidEnvironmentVariableError
from backend.src.custom_exceptions.quizard_exceptions import ConfigLoadingError
from backend.src.custom_exceptions.api_exceptions import APIAuthenticationError
from backend.src.utils.global_helpers import configure_logging, start_log, write_to_log_and_print, load_yaml_config

# This assumes that main.py is in backend/src/
backend_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = os.path.join(backend_root_dir, '..', 'config')
log_dir = os.path.join(backend_root_dir, '..', 'logs')

app = Flask(__name__)
CORS(app)
api = Api(app)





if __name__ == '__main__':
    # TODO: Turn of debug mode and use production-ready server
    app.run(debug=True)
    # use different server for prod -> doesn't really matter since we don't have auth yet
    # https://stackoverflow.com/questions/51025893/flask-at-first-run-do-not-use-the-development-server-in-a-production-environmen
