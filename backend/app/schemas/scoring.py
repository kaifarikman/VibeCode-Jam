"""Схемы для подсчета баллов"""

from pydantic import BaseModel, Field
from typing import Literal


class ScoringRequest(BaseModel):
    """Запрос на расчет финального балла"""
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description='Сложность задачи')
    tests_passed: int = Field(..., ge=0, description='Количество пройденных тестов')
    total_tests: int = Field(..., gt=0, description='Общее количество тестов')
    time_taken_seconds: float = Field(..., ge=0, description='Время выполнения в секундах')
    code_quality_score: float = Field(..., ge=0, le=100, description='Оценка качества кода (0-100)')
    communication_score: float = Field(..., ge=0, le=100, description='Оценка коммуникации (0-100)')
    hints_used: list[Literal["surface", "medium", "deep"]] = Field(
        default_factory=list,
        description='Список использованных подсказок'
    )


class ScoringResponse(BaseModel):
    """Ответ с финальным баллом"""
    final_score: float = Field(..., ge=0, le=100, description='Финальный балл (0-100)')
    breakdown: dict = Field(..., description='Разбивка расчета')

