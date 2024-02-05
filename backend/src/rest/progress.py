from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import os

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
