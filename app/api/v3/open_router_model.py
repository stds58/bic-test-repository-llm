from typing import List
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.open_router_model import (
    BaseOpenRouterModel,
    ShortOpenRouterModel,
    SOpenRouterFilter,
    SShortOpenRouterFilter,
    GenerateRequest,
    GenerateResponse,
    CreateBenchMark,
    BenchmarkResult,
)
from app.schemas.base import PaginationParams
from app.services.open_router_model_level3 import (find_many_item, benchmark_model_call, call_model_raw,
                                                   generate_benchmark, stream_model_call)
from fastapi import File, Form, UploadFile



router = APIRouter()


@router.get("/models", summary="Get short models", response_model=List[ShortOpenRouterModel])
def get_models(
    filters: SShortOpenRouterFilter = Depends(), pagination: PaginationParams = Depends()
) -> ShortOpenRouterModel:
    items = find_many_item(filters=filters, pagination=pagination)
    return items


@router.get("/fullmodels", summary="Get full models", response_model=List[BaseOpenRouterModel])
def get_fullmodels(
    filters: SOpenRouterFilter = Depends(), pagination: PaginationParams = Depends()
) -> BaseOpenRouterModel:
    items = find_many_item(filters=filters, pagination=pagination)
    return items


# @router.post("/generate", summary="Get full response from ai", response_model=dict)
# def generate_text(request: GenerateRequest) -> dict:
#     result = benchmark_model_call(query=request)
#     return result

@router.post("/generate", summary="Get response from AI (supports SSE streaming)")
async def generate_text(request: GenerateRequest):
    if request.stream:
        # Возвращаем SSE-поток
        async def event_generator():
            try:
                # Преобразуем синхронный генератор в асинхронный
                for chunk in stream_model_call(request):
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:  # Логируем только если есть текст
                            pass
                            #print(f"[Stream] {content}", end="", flush=True)
                    yield f" {json.dumps(chunk)}\n\n"
                yield " [DONE]\n\n"
            except Exception as e:
                # Логируем ошибку, но не ломаем поток
                print(f"Stream error: {e}")
                yield " [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
    else:
        # Старое поведение — возвращаем JSON
        result = benchmark_model_call(query=request)
        return result


@router.post("/fullgenerate", summary="Get only text response from ai", response_model=GenerateResponse)
def fullgenerate_text(request: GenerateRequest) -> GenerateResponse:
    result = call_model_raw(query=request)
    return result


# @router.post("/benchmark", summary="Test api ai", response_model=List[BenchmarkResult])
# async def generate_benchmarks(request: CreateBenchMark = Depends()) -> BenchmarkResult:
#     result = await generate_benchmark(query=request)
#     return result

@router.post("/benchmark", summary="Test api ai")
async def generate_benchmarks(
    prompt_file: UploadFile = File(...),
    model: str = Form(...),
    runs: int = Form(5),
    visualize: bool = Form(False)
):
    request = CreateBenchMark(
        prompt_file=prompt_file,
        model=model,
        runs=runs,
        visualize=visualize
    )
    result = await generate_benchmark(query=request)
    return result