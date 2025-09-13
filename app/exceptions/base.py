from typing import Callable
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """Базовый класс для всех кастомных бизнес-исключений"""

    pass


class CustomHTTPException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Внутренняя ошибка сервера"
    log_func: Callable = logging.info

    def __init__(self, detail: str = None):
        # Если detail передан — используем его, иначе — классовый по умолчанию
        final_detail = detail if detail is not None else self.__class__.detail
        super().__init__(status_code=self.__class__.status_code, detail=final_detail)

    def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        self.log_func("%s: %s", self.detail, str(exc))
        return JSONResponse(
            content={"message": self.detail},
            status_code=self.status_code,
        )


class CustomNotFoundException(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Ресурс не найден"


class CustomBadRequestException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Неверный запрос"


class CustomForbiddenException(CustomHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещен"


class CustomUnauthorizedException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не авторизован"


class CustomInternalServerException(CustomHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"
    log_func = logger.error
