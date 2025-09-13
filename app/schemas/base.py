from typing import Annotated
from pydantic import BaseModel, ConfigDict
from fastapi import Query


class BaseFilter(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",  # Позволяет игнорировать лишние поля
        # extra="forbid"  # Запретить передачу лишних полей
    )


class PaginationParams(BaseModel):
    page: Annotated[int, Query(default=1, ge=1)]
    per_page: Annotated[int, Query(default=10, ge=1, lt=100)]
