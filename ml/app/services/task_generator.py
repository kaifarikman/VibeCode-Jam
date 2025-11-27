from app.core.config import settings
from app.services.llm_client import llm_client
from app.models.schemas import Task
from app.services.hint_service import hint_service
import json

class TaskGenerator:
    """Генератор алгоритмических задач с использованием LLM."""
    
    async def generate_task(self, difficulty: str) -> Task:
        """Генерирует задачу заданного уровня сложности.
        
        Args:
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
            
        Returns:
            Task: Сгенерированная задача с описанием и скрытыми тестами
        """
        # 1. Генерируем описание задачи с помощью AWQ модели
        prompt = self._get_generation_prompt(difficulty)
        
        task_data = await llm_client.generate_json(
            model=settings.MODEL_AWQ,
            messages=[
                {"role": "system", "content": "Ты эксперт по созданию алгоритмических задач для собеседований. Генерируй задачи ТОЛЬКО на русском языке."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        # 2. Генерируем скрытые тесты с помощью Coder модели
        hidden_tests = await self._generate_hidden_tests(task_data)
        task_data["hidden_tests"] = hidden_tests
        task_data["difficulty"] = difficulty
        
        # 3. Генерируем подсказки для задачи
        hints = await hint_service.generate_hints(
            task_description=task_data.get("description", ""),
            task_difficulty=difficulty,
            input_format=task_data.get("input_format", ""),
            output_format=task_data.get("output_format", ""),
            examples=task_data.get("examples", [])
        )
        task_data["hints"] = [hint.dict() for hint in hints]
        
        return Task(**task_data)

    async def _generate_hidden_tests(self, task_data: dict) -> list[str]:
        """Генерирует скрытые тесты для задачи.
        
        Args:
            task_data: Данные задачи (title, description, input_format)
            
        Returns:
            list[str]: Список входных данных для тестов
        """
        prompt = f"""
        Для следующей алгоритмической задачи сгенерируй 5 разнообразных скрытых тестовых входных данных, которые покрывают граничные случаи.
        
        Название задачи: {task_data.get('title')}
        Описание: {task_data.get('description')}
        Формат входных данных: {task_data.get('input_format')}
        
        Верни ТОЛЬКО JSON массив строк, где каждая строка - это входные данные для программы.
        Пример формата: ["1 2 3", "100", "-5 0 5"]
        """
        
        try:
            tests = await llm_client.generate_json(
                model=settings.MODEL_CODER,
                messages=[
                    {"role": "system", "content": "Ты QA инженер, генерирующий тестовые случаи."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            if isinstance(tests, list):
                return tests
            if isinstance(tests, dict) and "tests" in tests:
                return tests["tests"]
            return []  # Резервный вариант
        except Exception as e:
            print(f"Ошибка при генерации скрытых тестов: {e}")
            return []

    def _get_generation_prompt(self, difficulty: str) -> str:
        """Формирует промпт для генерации задачи в зависимости от уровня сложности.
        
        Args:
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
            
        Returns:
            str: Промпт для LLM
        """
        base_prompt = """
        Сгенерируй алгоритмическую задачу для собеседования НА РУССКОМ ЯЗЫКЕ.
        
        ВАЖНО: 
        - Верни ТОЛЬКО валидный JSON, без дополнительного текста
        - НЕ используй теги <think> или другие обертки
        - Весь текст должен быть на русском языке
        
        Формат JSON:
        {
          "title": "string (название задачи на русском)",
          "description": "string (подробное описание задачи на русском)",
          "input_format": "string (формат входных данных на русском)",
          "output_format": "string (формат выходных данных на русском)",
          "examples": [{"input": "string", "output": "string"}],
          "constraints": ["string"]
        }
        """
        
        if difficulty == "easy":
            return base_prompt + """
            Сложность: ЛЕГКАЯ.
            Темы: Базовые массивы, строки, простая математика, циклы.
            Сложность алгоритма: O(n) или O(1).
            Примеры задач: Найти максимальный элемент, подсчитать четные числа, перевернуть строку.
            """
        elif difficulty == "medium":
            return base_prompt + """
            Сложность: СРЕДНЯЯ.
            Темы: Хеш-таблицы, Два указателя, Скользящее окно, Логика сортировки (без встроенных функций), Вложенные циклы.
            Сложность алгоритма: O(n^2) или O(n log n).
            Примеры задач: Первый уникальный символ, Переместить нули, Наибольший общий префикс.
            """
        else: # hard
            return base_prompt + """
            Сложность: ВЫСОКАЯ.
            Темы: Сложные реализации сортировок (QuickSort, MergeSort), Рекурсия, Деревья, Основы динамического программирования.
            Ограничение: Явно попроси реализовать конкретный алгоритм (например, QuickSort) вручную.
            """

task_generator = TaskGenerator()
