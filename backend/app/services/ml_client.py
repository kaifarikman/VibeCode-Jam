"""Клиент для взаимодействия с ML микросервисом"""

import httpx
from typing import Any

from app.core.config import get_settings

settings = get_settings()


class MLClient:
    """Клиент для работы с ML микросервисом"""
    
    def __init__(self):
        self.base_url = settings.ml_service_url
        self.timeout = settings.ml_service_timeout / 1000  # Конвертируем мс в секунды
    
    async def generate_task(self, difficulty: str, topic: str | None = None) -> dict[str, Any]:
        """Генерирует задачу через ML сервис
        
        Args:
            difficulty: Уровень сложности (easy, medium, hard)
            topic: Опциональная тема задачи
            
        Returns:
            dict: Задача с полями title, description, examples, hidden_tests, hints
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/generate-task',
                json={'difficulty': difficulty, 'topic': topic} if topic else {'difficulty': difficulty}
            )
            response.raise_for_status()
            return response.json()
    
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
    
    async def calculate_score(
        self,
        difficulty: str,
        tests_passed: int,
        total_tests: int,
        time_taken_seconds: float,
        code_quality_score: float,
        communication_score: float,
        hints_used: list[str]
    ) -> float:
        """Рассчитывает финальный балл с учетом подсказок
        
        Args:
            difficulty: Сложность задачи
            tests_passed: Количество пройденных тестов
            total_tests: Общее количество тестов
            time_taken_seconds: Время выполнения в секундах
            code_quality_score: Оценка качества кода (0-100)
            communication_score: Оценка коммуникации (0-100)
            hints_used: Список использованных подсказок (surface, medium, deep)
            
        Returns:
            float: Финальный балл (0.0-100.0)
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{self.base_url}/score',
                json={
                    'difficulty': difficulty,
                    'tests_passed': tests_passed,
                    'total_tests': total_tests,
                    'time_taken_seconds': time_taken_seconds,
                    'code_quality_score': code_quality_score,
                    'communication_score': communication_score,
                    'hints_used': hints_used
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get('final_score', 0.0)
    
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

