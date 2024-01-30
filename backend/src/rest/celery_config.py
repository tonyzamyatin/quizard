from celery import Celery, Task
from flask import Flask


def create_celery_app(flask_app: Flask) -> Celery:
    """
    This creates and returns a Celery app object. Celery configuration is taken from the CELERY key in the Flask configuration. The Celery app is set
    as the default, so that it is seen during each request. The Task subclass automatically runs task functions with a Flask app context active, so
    that services like your database connections are available.
    For more information on integrating Celery with Flask: https://flask.palletsprojects.com/en/2.3.x/patterns/celery/a
    What is Celery? Here's a quick intro: https://docs.celeryq.dev/en/stable/index.html
    """

    class FlaskTask(Task):

        # This method overrides the __call__ method of the base task. When a task is executed, it will run within the Flask application context
        # (flask_app.app_context()). This is crucial for tasks that rely on the Flask context, such as those that use database connections or
        # application configurations.
        def __call__(self, *args: object, **kwargs: object) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    # Set the Task attribute of the Celery instance to the custom FlaskTask class, ensuring that all tasks created by this Celery app use
    # the Flask application context.
    celery_app = Celery(flask_app.name, task_cls=FlaskTask)
    celery_app.config_from_object(flask_app.config["CELERY"])
    celery_app.set_default()
    flask_app.extensions["celery"] = celery_app
    return celery_app
