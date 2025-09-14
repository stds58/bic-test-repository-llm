import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings


def setup_logging():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "..", "logs")
    log_dir = os.path.abspath(log_dir)

    logger = logging.getLogger("fastapi_app")
    logger.setLevel(logging.INFO)

    log_file = os.path.join(log_dir, "server_logs.txt")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=settings.LOG_FILE_MAX_SIZE * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
