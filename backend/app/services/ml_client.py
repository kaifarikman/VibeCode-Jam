"""Клиент для взаимодействия с ML микросервисом"""

import logging
import httpx
from typing import Any

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class MLClient:
    """Клиент для работы с ML микросервисом"""
    
    def __init__(self):
        self.base_url = settings.ml_service_url
        self.timeout = settings.ml_service_timeout / 1000  # Конвертируем мс в секунды
    
    async def generate_task(self, difficulty: str, topic: str | None = None, use_mock: bool = False) -> dict[str, Any]:
        """Генерирует задачу через ML сервис
        
        Args:
            difficulty: Уровень сложности (easy, medium, hard)
            topic: Опциональная тема задачи
            use_mock: Если True, использует mock endpoint вместо реальной генерации
            
        Returns:
            dict: Задача с полями title, description, examples, hidden_tests, hints
        """
        endpoint = '/generate-task-mock' if use_mock else '/generate-task'
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f'{self.base_url}{endpoint}',
                    json={'difficulty': difficulty, 'topic': topic} if topic else {'difficulty': difficulty}
                )
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                # Если не удалось подключиться к реальному эндпоинту, пробуем mock
                if not use_mock:
                    logger.warning(f'Failed to generate task via ML service: {e}. Trying mock endpoint...')
                    return await self.generate_task(difficulty, topic, use_mock=True)
                raise
    
    async def evaluate_code(
        self,
        code: str,
        task_difficulty: str,
        task_description: str,
        hidden_tests: list[str]
    ) -> dict[str, Any]:
        """Оценивает код через ML сервис
        
        Args:
            code: Код пользователя
            task_difficulty: Сложность задачи
            task_description: Описание задачи
            hidden_tests: Список скрытых тестов (inputs)
            
        Returns:
            dict: Результат оценки с полями correctness_score, efficiency_score,
                  clean_code_score, feedback, passed
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/evaluate',
                json={
                    'code': code,
                    'task_difficulty': task_difficulty,
                    'task_description': task_description,
                    'hidden_tests': hidden_tests
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def check_anti_cheat(self, code: str, problem_description: str) -> dict[str, Any]:
        """Проверяет код на плагиат и AI-генерацию
        
        Args:
            code: Код пользователя
            problem_description: Описание задачи
            
        Returns:
            dict: Результат проверки с полями is_suspicious, confidence, reason
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/anti-cheat/check',
                json={
                    'code': code,
                    'problem_description': problem_description
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def evaluate_communication(
        self,
        problem_description: str,
        user_explanation: str,
        code: str | None = None
    ) -> dict[str, Any]:
        """Оценивает коммуникативные навыки
        
        Args:
            problem_description: Описание задачи
            user_explanation: Объяснение пользователя
            code: Опциональный код
            
        Returns:
            dict: Результат оценки с полями communication_score, feedback
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            json_data = {
                'problem_description': problem_description,
                'user_explanation': user_explanation
            }
            if code:
                json_data['code'] = code
            
            response = await client.post(
                f'{self.base_url}/communication/evaluate',
                json=json_data
            )
            response.raise_for_status()
            return response.json()


# Глобальный экземпляр клиента
ml_client = MLClient()

