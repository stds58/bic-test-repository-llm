from app.core.config import settings
from app.schemas.open_router_model import ShortOpenRouterModel, BaseOpenRouterModel
from .base_test import BaseAPITest


class TestOpenRouterAPI(BaseAPITest):
    def test_get_models_short(self):
        self.assert_valid_models(
            api_url=f"/{self.prefix}/models",
            model_schema=ShortOpenRouterModel,
            per_page=5,
            page=2
        )

    def test_get_fullmodels(self):
        self.assert_valid_models(
            api_url=f"/{self.prefix}/fullmodels",
            model_schema=BaseOpenRouterModel,
            per_page=5,
            page=2
        )

    def test_invalid_url(self):
        settings.OPEN_ROUTER_URL = "https://openrouter.ai/api/v1/xxx"
        self.assert_invalid_url(
            api_url=f"/{self.prefix}/models",
            model_schema=ShortOpenRouterModel,
            per_page=5,
            page=2
        )

    def test_valid_response_text(self):
        self.assert_valid_response_text(
            api_url=f"/{self.prefix}/generate",
            prompt="привет",
            model="nvidia/nemotron-nano-9b-v2:free"
        )

    def test_response_text_in_notfree_model(self):
        self.assert_notfree_model(
            api_url=f"/{self.prefix}/generate",
            prompt="привет",
            model="qwen/qwen3-next-80b-a3b-thinking"
        )

    def test_invalid_model(self):
        self.assert_invalid_model(
            api_url=f"/{self.prefix}/generate",
            prompt="привет",
            model="xxxxxx"
        )

    def test_invalid_response(self):
        settings.OPEN_ROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.assert_unauthorized(
            api_url=f"/{self.prefix}/generate",
            prompt="привет",
            model="qwen/qwen3-next-80b-a3b-thinking"
        )
