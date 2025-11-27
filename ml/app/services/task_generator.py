from app.core.config import settings
from app.services.llm_client import llm_client
from app.models.schemas import Task
from app.services.hint_service import hint_service
from app.services.code_executor import code_executor
import json
import re

class TaskGenerator:
    """Генератор алгоритмических задач с использованием LLM."""
    
    async def generate_task(self, difficulty: str, language: str | None = None) -> Task:
        """Генерирует задачу заданного уровня сложности.
        
        Args:
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
            language: Предпочитаемый язык эталонного решения
            
        Returns:
            Task: Сгенерированная задача с описанием и скрытыми тестами
        """
        supported_languages = {'python', 'go', 'java', 'typescript'}
        preferred_language = (language or 'python').lower()
        if preferred_language not in supported_languages:
            preferred_language = 'python'
        
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
        
        # 2. Генерируем тесты, чтобы получить 3 открытых и 15 закрытых вариантов
        hidden_test_inputs = await self._generate_hidden_tests(task_data) or []
        
        # Гарантируем, что тестов не менее 18 штук (3 открытых + 15 закрытых)
        while len(hidden_test_inputs) < 18:
            hidden_test_inputs.extend(hidden_test_inputs or ["1\n1"])
        hidden_test_inputs = hidden_test_inputs[:18]
        
        # 3. Генерируем эталонное решение
        canonical_solutions: dict[str, str] = {}
        python_solution = await self._generate_canonical_solution(task_data, difficulty, language='python')
        if python_solution:
            canonical_solutions['python'] = python_solution
        
        if preferred_language != 'python':
            lang_solution = await self._generate_canonical_solution(
                task_data,
                difficulty,
                language=preferred_language,
                reference_solution=python_solution,
            )
            if lang_solution:
                canonical_solutions[preferred_language] = lang_solution
        
        canonical_for_storage = canonical_solutions.get(preferred_language) or python_solution
        task_data["canonical_solution"] = canonical_for_storage or None
        task_data["canonical_solutions"] = canonical_solutions or None
        
        # 4. Генерируем outputs для тестов с помощью эталонного решения, если оно есть
        test_cases: list[dict[str, str]] = []
        if python_solution:
            executor_results = code_executor.execute(python_solution, hidden_test_inputs)
            if executor_results and len(executor_results) == len(hidden_test_inputs):
                all_success = all(res.get("success") for res in executor_results)
                if all_success:
                    test_cases = [
                        {"input": res["input"], "output": res.get("output", "")}
                        for res in executor_results
                    ]
        
        # 5. Если выполнение эталонного решения не удалось, используем LLM для генерации outputs
        if not test_cases or len(test_cases) < len(hidden_test_inputs):
            hidden_tests_with_outputs = await self._generate_hidden_test_outputs(task_data, hidden_test_inputs)
            test_cases = hidden_tests_with_outputs or []
        
        # Фоллбек: если всё равно не получили outputs, создаём пустые пары
        if not test_cases:
            test_cases = [{"input": inp, "output": ""} for inp in hidden_test_inputs]
        
        # Нормализуем длину массива тестов
        while len(test_cases) < 18:
            base = test_cases[len(test_cases) % len(test_cases)]
            test_cases.append({"input": base["input"], "output": base["output"]})
        test_cases = test_cases[:18]
        
        # Разбиваем на 3 открытых и 15 закрытых тестов
        open_test_cases = [dict(input=case["input"], output=case["output"]) for case in test_cases[:3]]
        hidden_test_cases = [dict(input=case["input"], output=case["output"]) for case in test_cases[3:18]]
        
        # Сохраняем открытые тесты как examples, закрытые как hidden_tests(+inputs)
        task_data["examples"] = open_test_cases
        task_data["hidden_tests_full"] = hidden_test_cases
        task_data["hidden_tests"] = [case["input"] for case in hidden_test_cases]
        task_data["difficulty"] = difficulty
        
        # 5. Генерируем подсказки для задачи
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
        """Генерирует скрытые тесты для задачи (только inputs).
        
        Args:
            task_data: Данные задачи (title, description, input_format)
            
        Returns:
            list[str]: Список входных данных для тестов
        """
        prompt = f"""
        Для следующей алгоритмической задачи сгенерируй 18 разнообразных тестовых входных данных, которые покрывают базовые, граничные и стрессовые случаи.
        Первые 3 теста должны быть относительно простыми (они станут открытыми), остальные 15 — более сложными (закрытые).
        
        Название задачи: {task_data.get('title')}
        Описание: {task_data.get('description')}
        Формат входных данных: {task_data.get('input_format')}
        
        Верни ТОЛЬКО JSON массив строк, где каждая строка - это входные данные для программы.
        Пример формата: ["1 2 3", "100", "-5 0 5"]
        Количество элементов массива должно быть РОВНО 18.
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
            sanitized: list[str] = []
            if isinstance(tests, list):
                for item in tests:
                    if isinstance(item, str):
                        sanitized.append(item.strip())
                    elif isinstance(item, dict) and "input" in item:
                        sanitized.append(str(item["input"]))
            elif isinstance(tests, dict) and "tests" in tests:
                for item in tests["tests"]:
                    if isinstance(item, str):
                        sanitized.append(item.strip())
                    elif isinstance(item, dict) and "input" in item:
                        sanitized.append(str(item["input"]))
            return sanitized
        except Exception as e:
            print(f"Ошибка при генерации скрытых тестов: {e}")
            return []
    
    async def _generate_hidden_test_outputs(self, task_data: dict, hidden_test_inputs: list[str]) -> list[dict]:
        """Генерирует outputs для скрытых тестов на основе описания задачи и примеров.
        
        Args:
            task_data: Данные задачи (title, description, examples, input_format, output_format)
            hidden_test_inputs: Список входных данных для скрытых тестов
            
        Returns:
            list[dict]: Список тестов с input и output в формате [{"input": "...", "output": "..."}, ...]
        """
        examples_text = "\n".join([
            f"Вход: {ex.get('input', '')}\nВыход: {ex.get('output', '')}"
            for ex in task_data.get('examples', [])
        ])
        
        prompt = f"""
        Для следующей алгоритмической задачи сгенерируй правильные выходные данные для каждого входного теста.
        
        Название задачи: {task_data.get('title')}
        Описание: {task_data.get('description')}
        Формат входных данных: {task_data.get('input_format')}
        Формат выходных данных: {task_data.get('output_format')}
        
        Примеры:
        {examples_text}
        
        Входные тесты (сгенерируй для каждого правильный выход):
        {json.dumps(hidden_test_inputs, ensure_ascii=False, indent=2)}
        
        Верни ТОЛЬКО JSON массив объектов в формате:
        [{{"input": "входные данные", "output": "выходные данные"}}, ...]
        
        ВАЖНО: Все выходные данные должны быть правильными согласно описанию задачи и примерам.
        """
        
        try:
            results = await llm_client.generate_json(
                model=settings.MODEL_CODER,
                messages=[
                    {"role": "system", "content": "Ты эксперт по алгоритмическим задачам. Генерируй правильные выходные данные для тестов и используй только JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # Низкая температура для более точных результатов
            )
            
            paired_results: list[dict] = []
            if isinstance(results, list):
                for idx, inp in enumerate(hidden_test_inputs):
                    candidate = results[idx] if idx < len(results) else None
                    if isinstance(candidate, dict) and "output" in candidate:
                        paired_results.append({"input": inp, "output": str(candidate["output"])})
                    elif isinstance(candidate, str):
                        paired_results.append({"input": inp, "output": candidate})
                    else:
                        paired_results.append({"input": inp, "output": ""})
                return paired_results
            
            # Если результат не список, возвращаем заглушки
            return [{"input": inp, "output": ""} for inp in hidden_test_inputs]
        except Exception as e:
            print(f"Ошибка при генерации outputs для скрытых тестов: {e}")
            # Fallback: возвращаем тесты с пустыми outputs
            return [{"input": inp, "output": ""} for inp in hidden_test_inputs]
    
    async def _generate_canonical_solution(
        self,
        task_data: dict,
        difficulty: str,
        language: str = 'python',
        reference_solution: str | None = None,
    ) -> str:
        """Генерирует эталонное решение на указанном языке."""
        language_names = {
            'python': 'Python',
            'go': 'Go',
            'java': 'Java',
            'typescript': 'TypeScript',
        }
        io_guidance = {
            'python': "- Код должен читать вход через input()/sys.stdin и печатать через print().",
            'go': "- Используй пакет bufio и os.Stdin для чтения. Функция main в пакете main, вывод через fmt.Println.",
            'java': "- Используй класс Main с методом public static void main. Читай через BufferedReader/Scanner, вывод через System.out.",
            'typescript': "- Запускается в Node.js. Читай ввод через require('fs').readFileSync(0, 'utf8').",
        }
        reference_block = ''
        if reference_solution and language != 'python':
            reference_block = f"""
Вот корректное решение на Python, на которое можно опираться:
```
{reference_solution}
```
Напиши эквивалент на {language_names.get(language, language.title())}, соблюдая стиль и требования языка.
"""
        prompt = f"""
Ты опытный инженер по алгоритмам. Напиши оптимальное решение задачи НА {language_names.get(language, language.title()).upper()}.
        
        Название задачи: {task_data.get('title')}
        Описание: {task_data.get('description')}
        Формат входных данных: {task_data.get('input_format')}
        Формат выходных данных: {task_data.get('output_format')}
        Ограничения: {task_data.get('constraints')}
        Примеры: {json.dumps(task_data.get('examples', []), ensure_ascii=False)}
        
        Требования:
- Решение должно читать данные из стандартного ввода и выводить результат в стандартный вывод.
- Используй только стандартную библиотеку языка.
        - Решение должно быть оптимальным по времени и памяти для уровня сложности {difficulty}.
- Не добавляй комментарии, объяснения и Markdown. Верни ТОЛЬКО чистый код.
{io_guidance.get(language, '')}
{reference_block}
        """
        try:
            content = await llm_client.generate(
                model=settings.MODEL_CODER,
                messages=[
                    {"role": "system", "content": f"Ты пишешь рабочие решения алгоритмических задач на {language_names.get(language, language.title())}."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.15,
                max_tokens=2048,
            )
            return self._extract_code_block(content)
        except Exception as e:
            print(f"Ошибка при генерации решения на {language}: {e}")
            return ""
    
    def _extract_code_block(self, content: str) -> str:
        """Извлекает код из ответа модели, удаляя маркдауны."""
        if "```" in content:
            parts = content.split("```")
            # Обычно код внутри первого блока после троекратных кавычек
            if len(parts) >= 2:
                candidate = parts[1]
                # Удаляем возможное указание языка в первой строке
                candidate_lines = candidate.split('\n')
                if candidate_lines:
                    first_line = candidate_lines[0].strip()
                    if len(candidate_lines) > 1 and len(first_line) < 15 and first_line.isalpha():
                        candidate_lines = candidate_lines[1:]
                content = '\n'.join(candidate_lines)
        return content.strip()

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
        - В массиве examples должно быть ровно 3 объекта с корректными парами {"input": "...", "output": "..."}
        
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
