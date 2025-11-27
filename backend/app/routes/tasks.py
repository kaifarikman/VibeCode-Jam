"""Роуты для работы с алгоритмическими задачами"""

import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Task, TaskSolution, User, Vacancy, UserContestTasks
from ..schemas import TaskRead, TaskTestsForSubmit

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/contest/{vacancy_id}', response_model=list[TaskRead])
async def get_contest_tasks(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить 3 задачи разной сложности для алгоритмического контеста
    
    Задачи генерируются один раз при первом входе пользователя на контест
    и привязываются к пользователю. При последующих запросах возвращаются
    те же самые задачи.
    """
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    
    # Проверяем, есть ли уже привязанные задачи для этого пользователя и вакансии
    existing_binding = await session.scalar(
        select(UserContestTasks).where(
            UserContestTasks.user_id == current_user.id,
            UserContestTasks.vacancy_id == vacancy_id
        )
    )
    
    if existing_binding:
        # Если задачи уже привязаны, возвращаем их в том же порядке
        task_ids = existing_binding.task_ids
        tasks = []
        for task_id in task_ids:
            task = await session.get(Task, task_id)
            if task:
                tasks.append(task)
        
        # Если некоторые задачи были удалены, возвращаем только существующие
        if len(tasks) < len(task_ids):
            # Обновляем привязку, убирая удаленные задачи
            existing_binding.task_ids = [task.id for task in tasks]
            await session.commit()
        
        # Конвертируем в TaskRead (без закрытых тестов)
        result = []
        for task in tasks:
            task_read = TaskRead.from_orm(task)
            result.append(task_read)
        
        return result
    
    # Если задач еще нет, генерируем новые
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
    
    # Берем ровно 3 задачи
    final_tasks = selected_tasks[:3]
    task_ids = [task.id for task in final_tasks]
    
    # Создаем привязку задач к пользователю
    user_contest_tasks = UserContestTasks(
        user_id=current_user.id,
        vacancy_id=vacancy_id,
        task_ids=task_ids
    )
    session.add(user_contest_tasks)
    await session.commit()
    
    # Конвертируем в TaskRead (без закрытых тестов)
    result = []
    for task in final_tasks:
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
    import logging
    logger = logging.getLogger(__name__)
    
    stmt = select(TaskSolution.task_id).where(
        TaskSolution.user_id == current_user.id,
        TaskSolution.vacancy_id == vacancy_id,
        TaskSolution.status == 'solved',
    )
    result = await session.scalars(stmt)
    solved_ids = list(result.all())
    
    logger.info(
        f"User {current_user.id} solved tasks for vacancy {vacancy_id}: {solved_ids}"
    )
    
    return solved_ids


@router.get('/contest/{vacancy_id}/completion-status')
async def get_contest_completion_status(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Проверить статус завершения контеста - все ли задачи решены"""
    # Получаем привязанные задачи
    binding = await session.scalar(
        select(UserContestTasks).where(
            UserContestTasks.user_id == current_user.id,
            UserContestTasks.vacancy_id == vacancy_id
        )
    )
    
    if not binding:
        return {
            'all_solved': False,
            'total_tasks': 0,
            'solved_tasks': 0,
            'task_ids': []
        }
    
    expected_task_ids = set(binding.task_ids)
    
    # Получаем решенные задачи
    solved_solutions = await session.scalars(
        select(TaskSolution).where(
            TaskSolution.user_id == current_user.id,
            TaskSolution.vacancy_id == vacancy_id,
            TaskSolution.status == 'solved'
        )
    )
    solved_task_ids = {sol.task_id for sol in solved_solutions.all()}
    
    all_solved = expected_task_ids.issubset(solved_task_ids)
    
    return {
        'all_solved': all_solved,
        'total_tasks': len(expected_task_ids),
        'solved_tasks': len(solved_task_ids.intersection(expected_task_ids)),
        'task_ids': list(expected_task_ids)
    }


@router.get('/{task_id}/last-solution')
async def get_last_solution(
    task_id: uuid.UUID,
    vacancy_id: uuid.UUID | None = Query(None, description='ID вакансии для фильтрации'),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить последнее решение задачи пользователя"""
    # Строим запрос
    stmt = select(TaskSolution).where(
        TaskSolution.user_id == current_user.id,
        TaskSolution.task_id == task_id,
    )
    
    # Если указан vacancy_id, фильтруем по нему
    if vacancy_id:
        stmt = stmt.where(TaskSolution.vacancy_id == vacancy_id)
    
    # Получаем последнее решение (по updated_at)
    stmt = stmt.order_by(desc(TaskSolution.updated_at)).limit(1)
    solution = await session.scalar(stmt)
    
    if not solution:
        return {'solution_code': None, 'language': None}
    
    return {
        'solution_code': solution.solution_code,
        'language': solution.language,
        'status': solution.status,
        'verdict': solution.verdict,
        'updated_at': solution.updated_at.isoformat(),
    }

