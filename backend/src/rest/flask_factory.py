from flask import Flask
from backend.src.rest.celery_config import create_celery_app


def create_flask_app(broker_url: str, result_backend: str) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=broker_url,
            result_backend=result_backend,
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    create_celery_app(app)
    return app
