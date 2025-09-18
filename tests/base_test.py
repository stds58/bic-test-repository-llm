from typing import Type
from pydantic import BaseModel
from fastapi.testclient import TestClient
from app.main import app


class BaseAPITest:
    """Базовый класс для всех API-тестов"""
    def __init__(self):
        self.prefix = 'api'

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)

    def assert_valid_models(
        self,
        api_url: str,
        model_schema: Type[BaseModel],
        page: int = 2,
        per_page: int = 5
    ):
        """
        Общая логика валидации списка моделей.
        :param api_url: URL эндпоинта (/models или /fullmodels)
        :param model_schema: Pydantic-модель, которой должен соответствовать каждый элемент
        :param page: номер страницы
        :param per_page: ожидаемое количество записей
        """
        response = self.client.get(api_url, params={"page": page, "per_page": per_page})
        assert response.status_code == 200, f"Ошибка при запросе {api_url}: {response.json()}"
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть списком"
        assert len(data) == per_page, f"Ожидалось {per_page} моделей, получено {len(data)}"
        [model_schema(**item) for item in data]

    def assert_invalid_url(
        self,
        api_url: str,
        model_schema: Type[BaseModel],
        page: int = 2,
        per_page: int = 5
    ):
        response = self.client.get(api_url)
        assert response.status_code == 503, f"Ошибка при запросе {api_url}: {response.json()}"
        data = response.json()
        assert data == {"detail": "OpenRouter API временно недоступен"}


    def assert_valid_response_text(self,api_url: str,prompt: str,model: str):
        """Проверяет, что текстовый ответ корректный"""
        response = self.client.post(
            api_url,
            json={
                "prompt": prompt,
                "model": model
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, str)
        assert len(data) > 0

    def assert_notfree_model(self,api_url: str,prompt: str,model: str):
        """Проверяет, что в платную модель не зайти"""
        response = self.client.post(
            api_url,
            json={
                "prompt": prompt,
                "model": model
            },
        )
        assert response.status_code == 502
        assert response.json() == {
            'detail': '402 Client Error: Payment Required for url: https://openrouter.ai/api/v1/chat/completions'
        }

    def assert_invalid_model(self,api_url: str,prompt: str,model: str):
        """Проверяет, что модель неправильно указана"""
        response = self.client.post(
            api_url,
            json={
                "prompt": prompt,
                "model": model
            },
        )
        assert response.status_code == 502
        assert response.json() == {
            'detail': '400 Client Error: Bad Request for url: https://openrouter.ai/api/v1/chat/completions'
        }


    def assert_unauthorized(self,api_url: str,prompt: str,model: str):
        """Проверяет, что текстовый ответ некорректный"""
        response = self.client.post(
            api_url,
            json={
                "prompt": prompt,
                "model": model
            },
        )
        assert response.status_code == 502
        assert response.json() == {
            'detail': '401 Client Error: Unauthorized for url: https://openrouter.ai/api/v1/chat/completions'}
