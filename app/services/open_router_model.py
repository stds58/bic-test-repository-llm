import time
from app.crud.open_router_model import OpenRouterModelService
from app.schemas.open_router_model import SOpenRouterFilter, GenerateRequest
from app.schemas.base import PaginationParams


def find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def short_find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def generate_text_item(query: GenerateRequest):
    start = time.time()
    items = OpenRouterModelService.generate_text(query=query)
    response = items.get("choices")[0].get("message").get("content")
    prompt_tokens = items.get("usage").get("prompt_tokens")
    latency_seconds = time.time() - start
    return {"response": response, "prompt_tokens": prompt_tokens, "latency_seconds": latency_seconds}


def generate_fulltext_item(query: GenerateRequest):
    items = OpenRouterModelService.generate_text(query=query)
    return items
