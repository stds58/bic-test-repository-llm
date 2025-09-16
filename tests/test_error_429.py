from unittest.mock import patch, Mock
from .base_test import BaseAPITest
import requests


class TestOpenRouterAPI(BaseAPITest):
    def test_rate_limit_429_error(self):
        """Проверяет обработку ошибки 429 Too Many Requests от OpenRouter API"""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.url = "https://openrouter.ai/api/v1/models"
            http_error = requests.exceptions.HTTPError("429 Client Error: Too Many Requests")
            http_error.response = mock_response
            mock_response.raise_for_status.side_effect = http_error
            mock_get.return_value = mock_response
            response = self.client.get(f"/{self.prefix}/models", params={"page": 1, "per_page": 5})
            assert response.status_code in (429,), f"Ожидался 429, получен {response.status_code}"


#pytest tests/test_error_429.py -v -s