# config/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

import structlog
from dotenv import load_dotenv

from src.utils.path_util import get_project_root, get_logs_dir

# Load environment variables
load_dotenv()


def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_format = '%(message)s'

    # Only use StreamHandler to send logs to console (stdout) and let Docker manage the logs accessible via `docker logs`
    handlers = [logging.StreamHandler()]

    logging.basicConfig(level=log_level, format=log_format, handlers=handlers)

    # Render logs based on environment: In production use structured JSON logging, in development use readable console logging
    if os.getenv('ENVIRONMENT', 'development').lower() == 'production':
        renderer = structlog.processors.JSONRenderer(sort_keys=True)
    else:
        renderer = structlog.dev.ConsoleRenderer()

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            renderer
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
