from typing import List
from fastapi import APIRouter, Depends
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
from app.services.open_router_model_level2 import (find_many_item, generate_text_item, generate_fulltext_item,
                                                   generate_benchmark)


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


@router.post("/generate", summary="Get full response from ai", response_model=dict)
def generate_text(request: GenerateRequest) -> dict:
    result = generate_text_item(query=request)
    return result


@router.post("/fullgenerate", summary="Get only text response from ai", response_model=GenerateResponse)
def fullgenerate_text(request: GenerateRequest) -> GenerateResponse:
    result = generate_fulltext_item(query=request)
    return result


@router.post("/benchmark", summary="Test api ai", response_model=BenchmarkResult)
async def generate_benchmarks(request: CreateBenchMark = Depends()) -> BenchmarkResult:
    result = await generate_benchmark(query=request)
    return result
