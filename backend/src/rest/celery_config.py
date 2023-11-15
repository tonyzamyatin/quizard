from celery import Celery

# Initialize Celery
celery = Celery(__name__)


def init_celery(flask_app):
    """
    Initialize Celery and create a new Celery object.
    """
    celery.conf.update(flask_app.config)
    # Stores the base Task class provided by Celery which will be used to create custom task classes.
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        # This method overrides the __call__ method of the base task. When a task is executed, it will run within the Flask application context
        # (flask_app.app_context()). This is crucial for tasks that rely on the Flask context, such as those that use database connections or
        # application configurations.
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    # Set the Task attribute of the Celery instance to the custom ContextTask class, ensuring that all tasks created by this Celery app use
    # the Flask application context.
    celery.Task = ContextTask
    return celery
