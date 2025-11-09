import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists (project-level logs/ folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

BACKEND_LOG = os.path.join(LOG_DIR, 'backend.log')

FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'


def _setup_file_logger(name: str, filename: str, level=logging.INFO):
    logger = logging.getLogger(name)
    # Avoid adding handlers multiple times when imported repeatedly
    if not logger.handlers:
        logger.setLevel(level)
        fh = RotatingFileHandler(filename, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8')
        fh.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(fh)
        # Also log to console for convenience
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(sh)
    return logger


# Named logger for backend
backend_logger = _setup_file_logger('backend', BACKEND_LOG)


def get_logger(module_name: str | None = None):
    """Return the backend logger. Module name is accepted for readability in log records.

    All Python backend modules should call get_logger(__name__) and use the returned logger.
    """
    if module_name:
        return logging.getLogger(f'backend.{module_name}')
    return backend_logger
