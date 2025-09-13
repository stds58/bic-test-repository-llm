import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings


def setup_logging():
    # Создаем директорию для логов, если её нет
    log_dir = "../logs"

    # Создаем логгер
    logger = logging.getLogger("fastapi_app")
    logger.setLevel(logging.INFO)

    # Создаем обработчик для записи в файл с ротацией
    log_file = os.path.join(log_dir, "server_logs.txt")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=settings.LOG_FILE_MAX_SIZE * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    # Формат сообщений
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
