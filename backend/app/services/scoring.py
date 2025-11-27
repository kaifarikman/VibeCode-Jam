"""Сервис для расчета финального балла за решение задачи"""


class ScoringService:
    """Сервис для расчета финального балла"""
    
    # Штрафы за подсказки
    HINT_PENALTIES = {
        'surface': 5.0,
        'medium': 15.0,
        'deep': 30.0,
    }
    
    # Множители сложности
    DIFFICULTY_MULTIPLIERS = {
        'easy': 1.0,
        'medium': 1.2,
        'hard': 1.5,
    }
    
    # Лимиты времени (в секундах)
    TIME_LIMITS = {
        'easy': 300,    # 5 минут
        'medium': 600,  # 10 минут
        'hard': 900,    # 15 минут
    }
    
    @classmethod
    def calculate_final_score(
        cls,
        difficulty: str,
        tests_passed: int,
        total_tests: int,
        time_taken_seconds: float,
        code_quality_score: float,  # 0-100
        communication_score: float,  # 0-100
        hints_used: list[str] = None
    ) -> float:
        """Рассчитывает финальный балл по формуле из ML сервиса
        
        Args:
            difficulty: Сложность задачи (easy, medium, hard)
            tests_passed: Количество пройденных тестов
            total_tests: Общее количество тестов
            time_taken_seconds: Время выполнения в секундах
            code_quality_score: Оценка качества кода (0-100)
            communication_score: Оценка коммуникации (0-100)
            hints_used: Список использованных подсказок (surface, medium, deep)
            
        Returns:
            float: Финальный балл (0.0-100.0)
        """
        if hints_used is None:
            hints_used = []
        
        # 1. Нормализация метрик к диапазону 0-1
        correctness = tests_passed / total_tests if total_tests > 0 else 0.0
        code_quality = code_quality_score / 100.0
        communication = communication_score / 100.0
        
        # 2. Расчет временного балла
        time_limit = cls.TIME_LIMITS.get(difficulty, 600)
        time_score = max(0.0, 1.0 - (time_taken_seconds / time_limit) * 0.5)
        
        # 3. Взвешенная сумма (40% корректность + 20% качество + 20% коммуникация + 20% время)
        base_score = (
            0.40 * correctness +
            0.20 * code_quality +
            0.20 * communication +
            0.20 * time_score
        )
        
        # 4. Применение множителя сложности
        multiplier = cls.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
        score = base_score * multiplier * 100.0
        
        # 5. Вычитание штрафов за подсказки
        total_penalty = sum(cls.HINT_PENALTIES.get(hint, 0.0) for hint in hints_used)
        final_score = score - total_penalty
        
        # 6. Ограничение результата диапазоном 0-100
        return max(0.0, min(100.0, final_score))


# Глобальный экземпляр сервиса
scoring_service = ScoringService()

