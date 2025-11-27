"""Роуты для работы с алгоритмическими задачами"""

import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Task, TaskSolution, User, Vacancy
from ..schemas import TaskRead, TaskTestsForSubmit

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/contest/{vacancy_id}', response_model=list[TaskRead])
async def get_contest_tasks(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить 3 задачи разной сложности для алгоритмического контеста"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    
    # Получаем задачи, привязанные к этой вакансии, или все задачи, если нет привязки
    stmt = select(Task).where(
        (Task.vacancy_id == vacancy_id) | (Task.vacancy_id.is_(None))
    )
    all_tasks = await session.scalars(stmt)
    tasks_list = list(all_tasks.all())
    
    if len(tasks_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет задач в базе для этой вакансии'
        )
    
    # Группируем задачи по сложности
    by_difficulty: dict[str, list[Task]] = {'easy': [], 'medium': [], 'hard': []}
    for task in tasks_list:
        difficulty = task.difficulty or 'medium'
        if difficulty in by_difficulty:
            by_difficulty[difficulty].append(task)
    
    # Выбираем по одной задаче каждого уровня сложности
    selected_tasks: list[Task] = []
    for difficulty in ['easy', 'medium', 'hard']:
        if by_difficulty[difficulty]:
            selected_tasks.append(random.choice(by_difficulty[difficulty]))
    
    # Если не хватает задач, дополняем случайными
    while len(selected_tasks) < 3:
        remaining = [t for t in tasks_list if t not in selected_tasks]
        if not remaining:
            break
        selected_tasks.append(random.choice(remaining))
    
    # Перемешиваем порядок
    random.shuffle(selected_tasks)
    
    # Конвертируем в TaskRead (без закрытых тестов)
    result = []
    for task in selected_tasks[:3]:
        task_read = TaskRead.from_orm(task)
        result.append(task_read)
    
    return result


@router.get('/{task_id}', response_model=TaskRead)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить задачу по ID (без закрытых тестов)"""
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    
    return TaskRead.from_orm(task)


@router.get('/{task_id}/tests-for-submit', response_model=TaskTestsForSubmit)
async def get_task_tests_for_submit(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить все тесты задачи для Submit (открытые + закрытые, только для executor)"""
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    
    return TaskTestsForSubmit.from_orm(task)


@router.get('/solved/{vacancy_id}', response_model=list[uuid.UUID])
async def get_solved_tasks(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить список ID решенных задач для пользователя по вакансии"""
    stmt = select(TaskSolution.task_id).where(
        TaskSolution.user_id == current_user.id,
        TaskSolution.vacancy_id == vacancy_id,
        TaskSolution.status == 'solved',
    )
    result = await session.scalars(stmt)
    return list(result.all())

