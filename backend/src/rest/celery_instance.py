"""
This module is only responsible for creating and configuring the Celery instance.
Other modules may import the Celery instance from this module, thus avoiding circular imports.
"""
from celery import Celery


def make_celery(app_name, broker, backend):
    celery = Celery(app_name, broker=broker, backend=backend)
    return celery

