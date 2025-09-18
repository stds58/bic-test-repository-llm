import json
from typing import Optional, List
from pydantic import Field
from fastapi import File, UploadFile, Form
from app.schemas.base import BaseFilter, BaseModel


class Architecture(BaseModel):
    modality: str
    input_modalities: List[str]
    output_modalities: List[str]
    tokenizer: str
    instruct_type: Optional[str] = None


class Pricing(BaseModel):
    prompt: str
    completion: str
    request: Optional[str] = None
    image: Optional[str] = None
    web_search: Optional[str] = None
    internal_reasoning: Optional[str] = None


class TopProvider(BaseModel):
    context_length: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    is_moderated: bool


class BaseOpenRouterModel(BaseModel):
    id: str
    canonical_slug: str
    hugging_face_id: Optional[str] = None
    name: str
    created: int
    description: str
    context_length: int
    architecture: Architecture
    pricing: Pricing
    top_provider: TopProvider
    per_request_limits: Optional[str] = None
    supported_parameters: List[str]


class ShortOpenRouterModel(BaseModel):
    id: str


class SOpenRouterFilter(BaseFilter):
    id: Optional[str] = None
    canonical_slug: Optional[str] = None
    hugging_face_id: Optional[str] = None
    name: Optional[str] = None
    created: Optional[int] = None
    description: Optional[str] = None
    context_length: Optional[int] = None
    per_request_limits: Optional[str] = None


class SShortOpenRouterFilter(BaseFilter):
    id: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Текст запроса к модели")
    model: str = Field(..., min_length=1, description="ID модели, например: 'meta-llama/llama-3-8b-instruct:free'")
    max_tokens: int = Field(512, ge=1, description="Максимальное количество токенов для генерации")
    stream: bool = Field(False, description="Потоковая передача ответа")


class Message(BaseModel):
    role: str
    content: str
    refusal: Optional[str] = None
    reasoning: Optional[str] = None


class Choice(BaseModel):
    logprobs: Optional[str] = None
    finish_reason: str
    native_finish_reason: str
    index: int
    message: Message


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[int] = None


class GenerateResponse(BaseModel):
    id: str
    provider: str
    model: str
    object: str
    created: int
    choices: List[Choice]
    usage: Usage


class CreateBenchMark(BaseModel):
    prompt_file: UploadFile = File(...)
    model: str = Field(..., min_length=1, description="ID модели, например: 'meta-llama/llama-3-8b-instruct:free'")
    runs: int = Field(default=5, gt=0, description="Количество тестов должно быть больше 0")
    visualize: bool = Field(default=False, description="Если true, возвращает html таблицу, иначе json")

    class Config:
        arbitrary_types_allowed = True


class BenchmarkResult(BaseModel):
    model: str
    prompt: str
    runs: int
    avg: float
    min: float
    max: float
    std_dev: float
