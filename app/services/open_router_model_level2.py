import time
from app.crud.open_router_model import OpenRouterModelService
from app.schemas.open_router_model import SOpenRouterFilter, GenerateRequest, CreateBenchMark, BenchmarkResult
from app.schemas.base import PaginationParams
import csv
import statistics


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
    return {"response": response, "tokens_used": prompt_tokens, "latency_seconds": latency_seconds}


def generate_fulltext_item(query: GenerateRequest):
    items = OpenRouterModelService.generate_text(query=query)
    return items


async def generate_benchmark(query: CreateBenchMark):
    #items = await OpenRouterModelService.generate_benchmark(query=query)
    #return items
    """
                Запускает бенчмарк: для каждого промпта из файла делает N прогонов и замеряет latency.
                Сохраняет сырые данные в benchmark_results.csv.
                Возвращает агрегированную статистику.
            """
    from fastapi import HTTPException
    if not query.prompt_file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Только .txt файлы разрешены")

        # Читаем промпты из файла
    content = await query.prompt_file.read()
    prompts = content.decode("utf-8").strip().splitlines()
    if not prompts:
        raise HTTPException(status_code=400, detail="Файл пуст")

    # Подготовка CSV
    csv_filename = "benchmark_results.csv"
    csv_fieldnames = ["prompt", "run", "latency_seconds", "model", "error"]

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()

        run = 1
        LIST_LATENCY_SECONDS = []

        for prompt in prompts:
            query2 = GenerateRequest(
                prompt=prompt,
                model=query.model,
                max_tokens=50
            )
            data = generate_text_item(query=query2)

            writer.writerow({
                "prompt": prompt,
                "run": run,
                "latency_seconds": data.get("latency_seconds"),
                "model": query.model,
                "error": "error"
            })
            LIST_LATENCY_SECONDS.append(data.get("latency_seconds"))
            run += 1

    avg_latency = statistics.mean(LIST_LATENCY_SECONDS)
    min_latency = min(LIST_LATENCY_SECONDS)
    max_latency = max(LIST_LATENCY_SECONDS)
    std_dev = statistics.stdev(LIST_LATENCY_SECONDS)  # выборочное стандартное отклонение

    result = {
        "avg": avg_latency,
        "min": min_latency,
        "max": max_latency,
        "std_dev": std_dev
    }
    return result
