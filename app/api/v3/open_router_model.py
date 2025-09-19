from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile, Request, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.core.config import settings
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


EXPORT_DIR = settings.BENCHMARK_EXPORT_DIR

V3_DIR = Path(__file__).resolve().parent
API_DIR = V3_DIR.parent
APP_DIR = API_DIR.parent
TEMPLATES_DIR = APP_DIR / "templates"

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


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


@router.post("/generate", summary="Get response from AI (supports SSE streaming)")
async def generate_text(request: GenerateRequest, stream: bool = Query(False)):
    if stream:
        try:
            generator = stream_model_call(request)
            return StreamingResponse(
                generator,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to start streaming") from e

    result = benchmark_model_call(query=request)
    return result


@router.post("/fullgenerate", summary="Get only text response from ai", response_model=GenerateResponse)
def fullgenerate_text(request: GenerateRequest) -> GenerateResponse:
    result = call_model_raw(query=request)
    return result


@router.post("/benchmark", summary="Test api ai")
async def generate_benchmarks(
    request: Request,
    prompt_file: UploadFile = File(...),
    model: str = Form(...),
    runs: int = Form(5),
    visualize: bool = Query(False),
):
    benchmark_request = CreateBenchMark(prompt_file=prompt_file, model=model, runs=runs, visualize=visualize)
    result = await generate_benchmark(query=benchmark_request)
    if visualize:
        return templates.TemplateResponse(
            "benchmark_results.html",
            {
                "request": request,
                "model_name": model,
                "csv_filename": result["csv_filename"],
                "results": result["results"],
            },
        )
    return result


@router.get("/download_csv")
async def download_csv(filename: str):
    file_path = (EXPORT_DIR / filename).resolve()

    if not file_path.is_relative_to(EXPORT_DIR):
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(path=file_path, filename=filename, media_type="text/csv")
