"""Роуты для выполнения кода"""

import logging
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import get_settings
from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Application, Execution, Task, TaskSolution, User, UserContestTasks
from ..schemas import ExecutionRead, ExecutionRequest, ExecutionStatus

logger = logging.getLogger(__name__)
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
    logger.info(
        f"Received callback for execution_id={execution_id}, "
        f"status={callback_data.get('status')}, "
        f"has_result={callback_data.get('result') is not None}"
    )
    
    execution = await session.get(Execution, execution_id)
    if not execution:
        logger.error(f"Execution not found: {execution_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Execution not found'
        )

    execution.status = callback_data.get('status', 'failed')
    execution.result = callback_data.get('result')
    execution.error_message = callback_data.get('error_message')
    
    # Логируем результат для отладки
    result_dict = execution.result if isinstance(execution.result, dict) else {}
    verdict = result_dict.get('verdict') if result_dict else None
    logger.info(
        f"Updated execution: id={execution_id}, status={execution.status}, "
        f"is_submit={execution.is_submit}, task_id={execution.task_id}, "
        f"verdict={verdict}, has_result={execution.result is not None}"
    )
    
    if callback_data.get('started_at'):
        started_str = callback_data['started_at'].replace('Z', '+00:00')
        execution.started_at = datetime.fromisoformat(started_str)
    if callback_data.get('completed_at'):
        completed_str = callback_data['completed_at'].replace('Z', '+00:00')
        execution.completed_at = datetime.fromisoformat(completed_str)

    # Если это Submit, сохраняем решение (независимо от результата)
    # Получаем вердикт из result (может быть dict или уже объект)
    result_dict = execution.result if isinstance(execution.result, dict) else (execution.result.model_dump() if hasattr(execution.result, 'model_dump') else {})
    
    # Получаем test_results
    test_results = result_dict.get('test_results') if result_dict else None
    
    # Получаем вердикт из result
    verdict = result_dict.get('verdict') if result_dict else None
    
    # Нормализуем verdict: если это пустая строка, считаем как None
    if verdict == '':
        verdict = None
    
    # Если вердикт не установлен, но есть test_results, определяем вердикт по результатам тестов
    if verdict is None and test_results and isinstance(test_results, list) and len(test_results) > 0:
        # Проверяем, все ли тесты прошли
        # test_results может содержать dict объекты или уже распарсенные объекты
        all_passed = True
        for tr in test_results:
            if isinstance(tr, dict):
                passed = tr.get('passed', False)
                # Также проверяем exit_code, если он есть
                exit_code = tr.get('exit_code', 0)
                if exit_code != 0:
                    passed = False
                if not passed:
                    all_passed = False
                    break
            else:
                # Если это не dict, пытаемся получить атрибут
                passed = getattr(tr, 'passed', False) if hasattr(tr, 'passed') else False
                exit_code = getattr(tr, 'exit_code', 0) if hasattr(tr, 'exit_code') else 0
                if exit_code != 0 or not passed:
                    all_passed = False
                    break
        
        if all_passed:
            verdict = 'ACCEPTED'
        else:
            verdict = 'WRONG ANSWER'
        
        logger.info(
            f"Determined verdict from test_results: {verdict}, "
            f"all_passed={all_passed}, total_tests={len(test_results)}, "
            f"execution_id={execution.id}"
        )
    
    if (
        execution.is_submit
        and execution.task_id
        and execution.status == 'completed'
        and execution.result
    ):
        # Используем блокировку для защиты от race conditions
        # Проверяем, есть ли уже решение для этой задачи с блокировкой строки
        existing_solution = await session.scalar(
            select(TaskSolution)
            .where(
                TaskSolution.user_id == execution.user_id,
                TaskSolution.task_id == execution.task_id,
                TaskSolution.vacancy_id == execution.vacancy_id,
            )
            .with_for_update(skip_locked=True)  # Блокируем строку, но пропускаем если уже заблокирована
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
        
        logger.info(
            f"Processing Submit: execution_id={execution.id}, task_id={execution.task_id}, "
            f"verdict={verdict}, is_accepted={is_accepted}, new_status={new_status}, "
            f"existing_solution={existing_solution is not None}"
        )
        
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
            logger.info(f"Created new TaskSolution: task_id={execution.task_id}, status={new_status}")

    try:
        await session.commit()
        logger.info(
            f"Successfully saved solution for execution_id={execution.id}, "
            f"task_id={execution.task_id}, status={new_status if 'new_status' in locals() else 'unknown'}, "
            f"verdict={verdict}"
        )
        
        # После коммита, если задача решена, проверяем, все ли задачи решены
        if 'new_status' in locals() and new_status == 'solved' and execution.vacancy_id:
            logger.info(
                f"Task {execution.task_id} marked as SOLVED for user {execution.user_id}, "
                f"vacancy {execution.vacancy_id}"
            )
            
            # Проверяем, все ли задачи контеста решены
            await check_and_update_application_status(
                session, execution.user_id, execution.vacancy_id
            )
    except Exception as e:
        logger.error(f"Failed to save solution for execution_id={execution.id}: {e}", exc_info=True)
        await session.rollback()
        raise
    
    return {'detail': 'Callback processed'}


async def check_and_update_application_status(
    session: AsyncSession,
    user_id: uuid.UUID,
    vacancy_id: uuid.UUID,
):
    """Проверить, все ли задачи решены, и обновить статус заявки"""
    from ..models import Application, UserContestTasks
    
    # Получаем привязанные задачи для этого пользователя и вакансии
    binding = await session.scalar(
        select(UserContestTasks).where(
            UserContestTasks.user_id == user_id,
            UserContestTasks.vacancy_id == vacancy_id
        )
    )
    
    if not binding:
        logger.warning(f"No contest tasks binding found for user {user_id}, vacancy {vacancy_id}")
        return
    
    expected_task_ids = set(binding.task_ids)
    
    # Получаем все решенные задачи для этой вакансии
    solved_solutions = await session.scalars(
        select(TaskSolution).where(
            TaskSolution.user_id == user_id,
            TaskSolution.vacancy_id == vacancy_id,
            TaskSolution.status == 'solved'
        )
    )
    solved_task_ids = {sol.task_id for sol in solved_solutions.all()}
    
    # Проверяем, все ли задачи решены
    all_solved = expected_task_ids.issubset(solved_task_ids)
    
    if all_solved:
        # Обновляем статус заявки на 'algo_test_completed'
        application = await session.scalar(
            select(Application).where(
                Application.user_id == user_id,
                Application.vacancy_id == vacancy_id
            )
        )
        
        if application and application.status != 'algo_test_completed':
            application.status = 'algo_test_completed'
            await session.commit()
            logger.info(
                f"Application {application.id} status updated to 'algo_test_completed' "
                f"for user {user_id}, vacancy {vacancy_id}"
            )

