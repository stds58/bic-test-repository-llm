from .base import CustomHTTPException
from fastapi import status


class OpenRouterTimeoutException(CustomHTTPException):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    detail = "Таймаут при запросе к OpenRouter API"


class OpenRouterHTTPException(CustomHTTPException):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Ошибка HTTP при запросе к OpenRouter API"


class OpenRouterResponseParseException(CustomHTTPException):
    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Не удалось распарсить ответ от OpenRouter API"


class OpenRouterUnavailableException(CustomHTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "OpenRouter API временно недоступен"


class OpenRouterInvalidRequestException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Некорректный запрос к OpenRouter API"
