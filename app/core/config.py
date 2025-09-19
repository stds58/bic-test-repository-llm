"""
Класс настроек приложения
"""
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


load_dotenv()


class Settings(BaseSettings):
    OPEN_ROUTER_API_KEY: str
    OPEN_ROUTER_URL: str
    LOG_FILE_MAX_SIZE: int
    DEBUG: bool
    SESSION_MIDDLEWARE_SECRET_KEY: str

    BENCHMARK_EXPORT_DIR: Path = Path("./exports").resolve()

    model_config = ConfigDict(extra="ignore")


@lru_cache()
def get_settings():
    """
    кеширует экземпляр объекта настроек Settings, чтобы избежать повторной инициализации
    """
    return Settings()


settings = get_settings()
