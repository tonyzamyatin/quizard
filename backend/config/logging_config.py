import logging
import os
from logging.handlers import RotatingFileHandler

import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging():
    current_script_dir = os.path.dirname(__file__)
    default_log_file_path = os.path.join(os.path.dirname(os.path.dirname(current_script_dir)), 'logs', 'default.log')
    log_file_path = os.getenv('LOG_FILE_PATH', default_log_file_path)
    log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_to_file = os.getenv('LOG_TO_FILE', 'no').lower() == 'yes'
    log_format = '%(message)s'

    if log_to_file:
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
        handlers = [handler]
    else:
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
