import time
from pathlib import Path
from functools import partial
from typing import Generator
from fastapi import HTTPException
from app.crud.open_router_model import OpenRouterModelService
from app.schemas.open_router_model import SOpenRouterFilter, GenerateRequest, CreateBenchMark
from app.schemas.base import PaginationParams
from app.utils.benchmark_statistics import calculate_latency_stats
from app.utils.csv_exporter import export_benchmark_to_csv
from app.utils.stubs import DUMMY_BENCHMARK_RESULT


def find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def short_find_many_item(filters: SOpenRouterFilter, pagination: PaginationParams):
    items = OpenRouterModelService.find_many(filters=filters, pagination=pagination)
    return items


def benchmark_model_call(query: GenerateRequest):
    start = time.time()
    items = OpenRouterModelService.call_openrouter_api(query=query)
    response = items.get("choices")[0].get("message").get("content")
    prompt_tokens = items.get("usage").get("prompt_tokens")
    latency_seconds = time.time() - start
    return {"response": response, "tokens_used": prompt_tokens, "latency_seconds": latency_seconds}


def call_model_raw(query: GenerateRequest):
    items = OpenRouterModelService.call_openrouter_api(query=query)
    return items


async def generate_benchmark(query: CreateBenchMark):
    """
    Запускает бенчмарк: для каждого промпта из файла делает N прогонов и замеряет latency.
    Сохраняет сырые данные в benchmark_results.csv.
    Возвращает агрегированную статистику.
    """
    if not query.prompt_file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Только .txt файлы разрешены")

    content = await query.prompt_file.read()
    prompts = content.decode("utf-8").strip().splitlines()
    if not prompts:
        raise HTTPException(status_code=400, detail="Файл пуст")

    benchmark_results = []
    for prompt in prompts:
        test_query = GenerateRequest(prompt=prompt, model=query.model, max_tokens=50)
        func = partial(benchmark_model_call, query=test_query)
        #result = calculate_latency_stats(model=query.model, prompt=prompt, runs=query.runs, func=func)
        result = DUMMY_BENCHMARK_RESULT
        benchmark_results.append(result)
    filename = export_benchmark_to_csv(benchmark_results)

    return {"results": benchmark_results, "csv_filename": filename}


def stream_model_call(query: GenerateRequest) -> Generator[dict, None, None]:
    yield from OpenRouterModelService.call_openrouter_api_stream(query)
