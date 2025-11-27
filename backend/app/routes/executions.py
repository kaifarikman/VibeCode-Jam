"""Роуты для выполнения кода"""

import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Execution, Task, TaskSolution, User
from ..schemas import ExecutionRead, ExecutionRequest, ExecutionStatus

router = APIRouter(prefix='/executions', tags=['executions'])
settings = get_settings()


@router.post('', response_model=ExecutionRead, status_code=status.HTTP_201_CREATED)
async def create_execution(
    request: ExecutionRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Создать задачу на выполнение кода"""
    # Создаем запись в БД
    execution = Execution(
        user_id=current_user.id,
        language=request.language,
        status='pending',
        files=request.files,
        task_id=request.task_id,
        vacancy_id=request.vacancy_id,
        is_submit=request.is_submit,
    )
    session.add(execution)
    await session.flush()

    # Отправляем задачу в executor service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            executor_request = {
                'execution_id': str(execution.id),
                'language': request.language,
                'files': request.files,
                'timeout': request.timeout,
            }
            if request.test_cases:
                executor_request['test_cases'] = [
                    {'input': tc.input, 'output': tc.output} for tc in request.test_cases
                ]
            
            response = await client.post(
                f'{settings.executor_service_url}/execute',
                json=executor_request,
            )
            if response.status_code != 202:
                execution.status = 'failed'
                execution.error_message = f'Executor service error: {response.text}'
                await session.commit()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail='Executor service unavailable',
                )
    except httpx.RequestError as exc:
        execution.status = 'failed'
        execution.error_message = f'Executor service connection error: {str(exc)}'
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Cannot connect to executor service',
        ) from exc

    await session.commit()
    await session.refresh(execution)
    # Используем from_orm для правильной обработки result
    return ExecutionRead.from_orm(execution)


@router.get('/{execution_id}', response_model=ExecutionRead)
async def get_execution(
    execution_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Получить информацию о выполнении"""
    execution = await session.scalar(
        select(Execution).where(
            Execution.id == execution_id, Execution.user_id == current_user.id
        )
    )
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Execution not found'
        )
    # Используем from_orm для правильной обработки result
    return ExecutionRead.from_orm(execution)


@router.get('', response_model=list[ExecutionRead])
async def list_executions(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0,
):
    """Получить список выполнений пользователя"""
    result = await session.scalars(
        select(Execution)
        .where(Execution.user_id == current_user.id)
        .order_by(Execution.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    executions = list(result.all())
    # Используем from_orm для правильной обработки result
    return [ExecutionRead.from_orm(exec) for exec in executions]


@router.post('/{execution_id}/callback', status_code=status.HTTP_200_OK)
async def execution_callback(
    execution_id: uuid.UUID,
    callback_data: dict,
    session: AsyncSession = Depends(get_session),
):
    """Callback от executor service с результатами выполнения"""
    execution = await session.get(Execution, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Execution not found'
        )

    execution.status = callback_data.get('status', 'failed')
    execution.result = callback_data.get('result')
    execution.error_message = callback_data.get('error_message')
    
    if callback_data.get('started_at'):
        started_str = callback_data['started_at'].replace('Z', '+00:00')
        execution.started_at = datetime.fromisoformat(started_str)
    if callback_data.get('completed_at'):
        completed_str = callback_data['completed_at'].replace('Z', '+00:00')
        execution.completed_at = datetime.fromisoformat(completed_str)

    # Если это Submit, сохраняем решение (независимо от результата)
    # Получаем вердикт из result (может быть dict или уже объект)
    result_dict = execution.result if isinstance(execution.result, dict) else (execution.result.model_dump() if hasattr(execution.result, 'model_dump') else {})
    verdict = result_dict.get('verdict') if result_dict else None
    
    # Получаем test_results
    test_results = result_dict.get('test_results') if result_dict else None
    
    # Если вердикт не установлен, но есть test_results, определяем вердикт по результатам тестов
    if not verdict and test_results:
        # Проверяем, все ли тесты прошли
        all_passed = all(tr.get('passed', False) for tr in test_results if isinstance(tr, dict))
        if all_passed and len(test_results) > 0:
            verdict = 'ACCEPTED'
        elif len(test_results) > 0:
            verdict = 'WRONG ANSWER'
    
    if (
        execution.is_submit
        and execution.task_id
        and execution.status == 'completed'
        and execution.result
    ):
        # Проверяем, есть ли уже решение для этой задачи
        existing_solution = await session.scalar(
            select(TaskSolution).where(
                TaskSolution.user_id == execution.user_id,
                TaskSolution.task_id == execution.task_id,
                TaskSolution.vacancy_id == execution.vacancy_id,
            )
        )
        
        # Получаем код решения из files
        solution_code = ''
        if execution.files:
            # Берем первый файл (обычно solution.py, solution.ts и т.д.)
            solution_code = list(execution.files.values())[0] if execution.files else ''
        
        # Определяем статус и вердикт
        is_accepted = verdict == 'ACCEPTED'
        new_status = 'solved' if is_accepted else 'attempted'
        new_verdict = verdict if verdict else None
        
        if existing_solution:
            # Обновляем существующее решение
            # Если задача уже была решена, не меняем статус на attempted
            if existing_solution.status == 'solved' and not is_accepted:
                # Задача была решена, но новое решение не прошло - обновляем только код и результаты
                existing_solution.solution_code = solution_code
                existing_solution.test_results = test_results
                existing_solution.execution_id = execution.id
            else:
                # Обновляем статус и вердикт
                existing_solution.status = new_status
                existing_solution.verdict = new_verdict
                existing_solution.solution_code = solution_code
                existing_solution.test_results = test_results
                existing_solution.execution_id = execution.id
        else:
            # Создаем новое решение
            solution = TaskSolution(
                user_id=execution.user_id,
                task_id=execution.task_id,
                vacancy_id=execution.vacancy_id,
                status=new_status,
                verdict=new_verdict,
                solution_code=solution_code,
                language=execution.language,
                test_results=test_results,
                execution_id=execution.id,
            )
            session.add(solution)

    await session.commit()
    return {'detail': 'Callback processed'}

