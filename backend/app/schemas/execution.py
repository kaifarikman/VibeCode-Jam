from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    input: str = Field(..., description='Входные данные')
    output: str = Field(..., description='Ожидаемый вывод')


class ExecutionRequest(BaseModel):
    language: str = Field(..., description='Язык программирования (python, typescript, go, java)')
    files: dict[str, str] = Field(..., description='Файлы кода {path: content}')
    timeout: int = Field(default=30, ge=1, le=300, description='Таймаут выполнения в секундах')
    test_cases: list[TestCase] | None = Field(None, description='Тестовые случаи для проверки решения')
    task_id: uuid.UUID | None = Field(None, description='ID задачи (для контеста)')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии (для контеста)')
    is_submit: bool = Field(default=False, description='Это Submit (все тесты) или Run (только открытые)')


class TestResult(BaseModel):
    test_index: int
    input: str
    expected_output: str
    actual_output: str
    passed: bool
    duration_ms: int


class ExecutionResult(BaseModel):
    stdout: str = Field(default='', description='Стандартный вывод')
    stderr: str = Field(default='', description='Ошибки')
    exit_code: int = Field(..., description='Код возврата')
    duration_ms: int = Field(..., description='Время выполнения в миллисекундах')
    verdict: str | None = Field(None, description='Вердикт (ACCEPTED, WRONG ANSWER, etc.)')
    test_results: list[TestResult] | None = Field(None, description='Результаты тестов')


class ExecutionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    language: str
    status: str
    files: dict[str, Any]
    result: ExecutionResult | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    @classmethod
    def from_orm(cls, execution):
        """Создать ExecutionRead из модели Execution с правильной обработкой result"""
        data = {
            'id': execution.id,
            'user_id': execution.user_id,
            'language': execution.language,
            'status': execution.status,
            'files': execution.files,
            'error_message': execution.error_message,
            'created_at': execution.created_at,
            'started_at': execution.started_at,
            'completed_at': execution.completed_at,
        }
        
        # Правильно обрабатываем result - он может быть dict или уже ExecutionResult
        if execution.result:
            if isinstance(execution.result, dict):
                data['result'] = ExecutionResult(**execution.result)
            else:
                data['result'] = execution.result
        else:
            data['result'] = None
        
        return cls(**data)

    class Config:
        from_attributes = True


class ExecutionStatus(BaseModel):
    id: uuid.UUID
    status: str
    result: ExecutionResult | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True

