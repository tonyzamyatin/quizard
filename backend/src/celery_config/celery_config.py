# src/rest/celery_config.py
from celery import Celery, Task
from dependency_injector.wiring import inject, Provide
from flask import Flask

from src.container import Container


@inject
def create_celery_app(flask_app=Provide[Container.flask_app]) -> Celery:
    """
    Create and return a Celery application object configured for a Flask application.

    This function creates a Celery object and sets up a custom task class (`FlaskTask`)
    to ensure that each Celery task is executed within the Flask application context.
    This is essential for tasks that rely on Flask's context, such as database access.

    Parameters
    ----------
    flask_app : Flask
        The Flask application instance used for configuring the Celery application.

    Returns
    -------
    Celery
        A Celery application instance configured for the Flask application.

    Raises
    ------
    RuntimeError
        If there is an issue configuring the Celery application.

    Examples
    --------
    >>> from flask import Flask
    >>> app = Flask(__name__)
    >>> my_celery_app = create_celery_app(app)
    >>> isinstance(my_celery_app, Celery)
    True

    Notes
    -----
    The function configures the Celery app based on the 'CELERY' key in the Flask app's
    configuration. It's important to have the necessary Celery configuration defined
    under this key in the Flask configuration.
    """

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    try:
        celery_app = Celery(flask_app.name, task_cls=FlaskTask)
        celery_app.config_from_object(flask_app.config["CELERY"])
        celery_app.autodiscover_tasks(['src.rest.tasks'])
        celery_app.conf.task_track_started = True
        celery_app.conf.task_ignore_result = False
        celery_app.set_default()
        celery_app.conf.update(
            task_serializer='pickle',
            result_serializer='pickle',
            accept_content=['pickle', 'json'],
        )
        flask_app.extensions["celery_config"] = celery_app
    except KeyError as e:
        # Raised if the 'CELERY' key is missing in the Flask app's configuration
        raise RuntimeError(f"Missing 'CELERY' key in Flask configuration: {e}")
    except Exception as e:
        # General catch-all for other unexpected exceptions
        raise RuntimeError(f"Failed to create or configure the Celery app: {e}")

    return celery_app
