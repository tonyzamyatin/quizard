from flask import Flask


def create_flask_app(broker_url: str, result_backend: str) -> Flask:
    """
    Create and configure a Flask application instance with Celery configurations.

    Parameters
    ----------
    broker_url : str
        The URL of the message broker that Celery will use.
    result_backend : str
        The URL of the backend used to store task results.

    Returns
    -------
    Flask
        A configured Flask application instance.

    Raises
    ------
    KeyError
        If the environment variables necessary for Flask or Celery configuration are missing.
    RuntimeError
        If there is an issue creating the Flask app or the Celery app.

    Notes
    -----
    The function configures the Flask app to use the specified message broker and result backend for Celery tasks.
    It also initializes a Celery app with the newly created Flask app context.

    Examples
    --------
    >>> flask_app = create_flask_app('pyamqp://guest@localhost//', 'redis://localhost:6379/0')
    >>> flask_app.name
    'flask.app'
    """
    try:
        app = Flask(__name__)
        app.config.from_mapping(
            CELERY=dict(
                broker_url=broker_url,
                result_backend=result_backend,
            ),
        )
        app.config.from_prefixed_env()  # Load configuration from environment variables
    except KeyError as e:
        # KeyError is raised if an environment variable is missing
        raise RuntimeError(f"Environment variable for Flask or Celery config missing: {e}")
    except RuntimeError as e:
        # RuntimeError is raised by create_celery_app if issues with Celery occur
        raise e
    except Exception as e:
        # Catch-all for any other unexpected exceptions
        raise RuntimeError(f"Failed to create or configure the Flask app: {e}")

    return app
