from app.crud.base import BaseAPIService
from app.schemas.open_router_model import BaseOpenRouterModel, SOpenRouterFilter


class OpenRouterModelService(BaseAPIService[SOpenRouterFilter, BaseOpenRouterModel]):
    filter_schema = SOpenRouterFilter
    pydantic_model = BaseOpenRouterModel
