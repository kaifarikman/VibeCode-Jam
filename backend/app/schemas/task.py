"""Схемы для алгоритмических задач"""

import json
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    """Тестовый случай"""
    input: str = Field(..., description='Входные данные')
    output: str = Field(..., description='Ожидаемый вывод')


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description='Название задачи')
    description: str = Field(..., min_length=1, description='Условие задачи')
    topic: str | None = Field(None, max_length=100, description='Тема/категория задачи')
    difficulty: str = Field(default='medium', description='Уровень сложности: easy, medium, hard')
    open_tests: list[TestCase] | None = Field(None, description='Открытые тесты (видимые пользователю)')
    hidden_tests: list[TestCase] | None = Field(None, description='Закрытые тесты (для финальной проверки)')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии, к которой привязана задача')


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255, description='Название задачи')
    description: str | None = Field(None, min_length=1, description='Условие задачи')
    topic: str | None = Field(None, max_length=100, description='Тема/категория задачи')
    difficulty: str | None = Field(None, description='Уровень сложности: easy, medium, hard')
    open_tests: list[TestCase] | None = Field(None, description='Открытые тесты')
    hidden_tests: list[TestCase] | None = Field(None, description='Закрытые тесты')
    vacancy_id: uuid.UUID | None = Field(None, description='ID вакансии')


class TaskRead(BaseModel):
    """Чтение задачи (без закрытых тестов для пользователей)"""
    id: uuid.UUID
    title: str
    description: str
    topic: str | None
    difficulty: str
    open_tests: list[TestCase] | None
    hidden_tests: list[TestCase] | None = None  # Всегда None для пользователей
    vacancy_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, task):
        """Создать TaskRead из модели Task с парсингом JSON"""
        data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'topic': task.topic,
            'difficulty': task.difficulty,
            'vacancy_id': task.vacancy_id,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        }
        
        # Парсим JSON тесты
        if task.open_tests:
            try:
                data['open_tests'] = json.loads(task.open_tests)
            except (json.JSONDecodeError, TypeError):
                data['open_tests'] = None
        else:
            data['open_tests'] = None
            
        # Скрытые тесты не отправляем на фронтенд
        data['hidden_tests'] = None
        
        return cls(**data)

    class Config:
        from_attributes = True


class TaskTestsForSubmit(BaseModel):
    """Тесты для Submit (открытые + закрытые, только для executor)"""
    open_tests: list[TestCase] | None
    hidden_tests: list[TestCase] | None

    @classmethod
    def from_orm(cls, task):
        """Создать TaskTestsForSubmit из модели Task с парсингом JSON"""
        open_tests = None
        hidden_tests = None
        
        if task.open_tests:
            try:
                open_tests = json.loads(task.open_tests)
            except (json.JSONDecodeError, TypeError):
                open_tests = None
        
        if task.hidden_tests:
            try:
                hidden_tests = json.loads(task.hidden_tests)
            except (json.JSONDecodeError, TypeError):
                hidden_tests = None
        
        return cls(open_tests=open_tests, hidden_tests=hidden_tests)


class TaskReadWithHidden(TaskRead):
    """Версия TaskRead с закрытыми тестами (для админки)"""
    hidden_tests: list[TestCase] | None

    @classmethod
    def from_orm(cls, task):
        """Создать TaskReadWithHidden из модели Task с парсингом JSON"""
        data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'topic': task.topic,
            'difficulty': task.difficulty,
            'vacancy_id': task.vacancy_id,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
        }
        
        # Парсим JSON тесты
        if task.open_tests:
            try:
                data['open_tests'] = json.loads(task.open_tests)
            except (json.JSONDecodeError, TypeError):
                data['open_tests'] = None
        else:
            data['open_tests'] = None
            
        if task.hidden_tests:
            try:
                data['hidden_tests'] = json.loads(task.hidden_tests)
            except (json.JSONDecodeError, TypeError):
                data['hidden_tests'] = None
        else:
            data['hidden_tests'] = None
        
        return cls(**data)
