from typing import Generic, List, Optional, TypeVar
import requests
from pydantic import BaseModel as PydanticModel
from app.core.config import settings
from app.schemas.base import PaginationParams
from app.schemas.open_router_model import GenerateRequest
from app.exceptions.exeption_wrapper import handle_openrouter_errors
from app.exceptions.retry_wrapper import exponential_retry_wrapper
import csv
import time
import uuid
import json
from typing import Generator
import httpx


# pylint: disable-next=no-name-in-module,invalid-name
ModelType = TypeVar("ModelType", bound=PydanticModel)
# pylint: disable-next=no-name-in-module,invalid-name
FilterSchemaType = TypeVar("FilterSchemaType", bound=PydanticModel)
# pylint: disable-next=no-name-in-module,invalid-name
RequestSchemaType = TypeVar("RequestSchemaType", bound=PydanticModel)
# pylint: disable-next=no-name-in-module,invalid-name
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=PydanticModel)


# pylint: disable-next=too-few-public-methods
class FiltrMixin:
    @classmethod
    def _apply_filters(cls, models_data, filters: FilterSchemaType):
        filter_dict = filters.model_dump(exclude_none=True)
        filtered_models = []

        for model_data in models_data:
            match = True
            for field, value in filter_dict.items():
                model_value = model_data.get(field)
                if isinstance(value, str):
                    if not isinstance(model_value, str) or value not in model_value:
                        match = False
                else:
                    if model_value != value:
                        match = False
            if match:
                filtered_models.append(model_data)
        return filtered_models


# pylint: disable-next=too-few-public-methods
class PaginationMixin:
    @classmethod
    def _apply_pagination(cls, models_data, pagination: PaginationParams):
        start = (pagination.page - 1) * pagination.per_page
        end = start + pagination.per_page
        return models_data[start:end]


class BaseAPIService(FiltrMixin, PaginationMixin, Generic[FilterSchemaType, ModelType]):
    filter_schema: type[FilterSchemaType]
    pydantic_model: type[ModelType]
    request_schema: type[RequestSchemaType]
    reponse_schema: type[ResponseSchemaType]

    @classmethod
    @handle_openrouter_errors
    @exponential_retry_wrapper
    def find_many(
        cls,
        filters: Optional[FilterSchemaType] = None,
        pagination: Optional[PaginationParams] = None,
        timeout: int = 10,
    ) -> List[ModelType]:
        headers = {
            "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
            "HTTP-Referer": settings.OPEN_ROUTER_URL,
            "X-Title": "My FastAPI App",
        }

        response = requests.get(settings.OPEN_ROUTER_URL, headers=headers, timeout=timeout)
        response.raise_for_status()

        data = response.json()
        models_data = data.get("data", [])

        if filters is not None:
            models_data = cls._apply_filters(models_data, filters)

        if pagination:
            models_data = cls._apply_pagination(models_data, pagination)

        validated_models = [cls.pydantic_model(**model_data) for model_data in models_data]

        return validated_models

    @classmethod
    @handle_openrouter_errors
    @exponential_retry_wrapper
    def call_openrouter_api(cls, query: RequestSchemaType, timeout: int = 30) -> ResponseSchemaType:
        """
        Отправляет запрос в OpenRouter и возвращает текст ответа модели.
        """
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
            "HTTP-Referer": settings.OPEN_ROUTER_URL,
            "X-Title": "My FastAPI App",
            "Content-Type": "application/json",
        }

        payload = {
            "model": query.model,
            "messages": [{"role": "user", "content": query.prompt}],
            "max_tokens": query.max_tokens
        }

        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data

    @classmethod
    @handle_openrouter_errors
    @exponential_retry_wrapper
    def call_openrouter_api_stream(cls, query: RequestSchemaType, timeout: int = 30) -> Generator[dict, None, None]:
        """
        Отправляет запрос в OpenRouter API в режиме стриминга.
        """
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.OPEN_ROUTER_API_KEY}",
            "HTTP-Referer": settings.OPEN_ROUTER_URL,
            "X-Title": "My FastAPI App",
            "Content-Type": "application/json",
        }

        payload = {
            "model": query.model,
            "messages": [{"role": "user", "content": query.prompt}],
            "max_tokens": query.max_tokens,
            "stream": True,
        }

        request_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        created_at = int(time.time())

        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=timeout)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line == "[DONE]":
                    break

                # Обрабатываем как с префиксом "data: ", так и без
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[len("data: "):]
                else:
                    data_str = decoded_line

                if data_str:
                    try:
                        chunk = json.loads(data_str)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            chunk.setdefault("id", request_id)
                            chunk.setdefault("created", created_at)
                            chunk.setdefault("model", query.model)
                        yield chunk
                    except json.JSONDecodeError:
                        continue

        # Финальный чанк
        yield {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created_at,
            "model": query.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
        }
