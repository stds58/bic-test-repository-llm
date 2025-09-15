import functools
import requests
from app.exceptions.openrouter import (
    OpenRouterTimeoutException,
    OpenRouterHTTPException,
    OpenRouterUnavailableException,
    OpenRouterResponseParseException,
    OpenRouterRateLimitException,
)
from app.exceptions.base import CustomInternalServerException


def handle_openrouter_errors(func):
    """
    Декоратор для централизованной обработки ошибок при вызовах к OpenRouter API.
    Оборачивает функцию и перехватывает исключения
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout as e:
            raise OpenRouterTimeoutException(str(e))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise OpenRouterRateLimitException(str(e))
            raise OpenRouterHTTPException(str(e))
        except requests.exceptions.RequestException:
            raise OpenRouterUnavailableException()
        except (KeyError, IndexError, ValueError) as e:
            raise OpenRouterResponseParseException(str(e))
        except Exception as e:
            raise CustomInternalServerException(f"Неизвестная ошибка: {str(e)}")

    return wrapper
