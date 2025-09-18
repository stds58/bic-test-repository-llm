from typing import List
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from app.schemas.open_router_model import (
    BaseOpenRouterModel,
    ShortOpenRouterModel,
    SOpenRouterFilter,
    SShortOpenRouterFilter,
    GenerateRequest,
    GenerateResponse,
    CreateBenchMark,
)
from app.schemas.base import PaginationParams
from app.services.open_router_model_level3 import (
    find_many_item,
    benchmark_model_call,
    call_model_raw,
    generate_benchmark,
    stream_model_call,
)


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

        async def event_generator():
            try:
                # Преобразуем синхронный генератор в асинхронный
                for chunk in stream_model_call(request):
                    yield f" {json.dumps(chunk)}\n\n"
                yield " [DONE]\n\n"
            except Exception:
                yield " [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
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
    prompt_file: UploadFile = File(...), model: str = Form(...), runs: int = Form(5), visualize: bool = Form(False)
):
    request = CreateBenchMark(prompt_file=prompt_file, model=model, runs=runs, visualize=visualize)
    result = await generate_benchmark(query=request)
    return result


@router.get("/download_csv")
async def download_csv(filename: str):
    file_path = Path(filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(path=file_path, filename=filename, media_type="text/csv")
