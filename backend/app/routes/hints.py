"""API эндпоинты для работы с подсказками"""

import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.auth import get_current_user
from ..database import get_session
from ..models import Task, HintUsage
from ..schemas.hint_usage import HintRequest, HintResponse
from ..services.ml_client import ml_client

router = APIRouter(prefix='/hints', tags=['hints'])


@router.post('/request', response_model=HintResponse)
async def request_hint(
    request: HintRequest,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Запросить подсказку для задачи
    
    Проверяет, не использована ли уже подсказка этого уровня,
    и возвращает подсказку из задачи.
    """
    # Получаем задачу
    task = await session.get(Task, request.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    
    # Если у задачи нет подсказок, генерируем их через ML сервис
    if not task.hints:
        try:
            # Генерируем подсказки через ML сервис
            from ..services.ml_client import ml_client
            
            # Получаем данные задачи для генерации подсказок
            # Парсим open_tests для получения примеров
            examples = []
            if task.open_tests:
                try:
                    open_tests_data = json.loads(task.open_tests) if isinstance(task.open_tests, str) else task.open_tests
                    examples = [{'input': t.get('input', ''), 'output': t.get('output', '')} for t in open_tests_data]
                except (json.JSONDecodeError, TypeError):
                    examples = []
            
            # Генерируем подсказки через ML сервис
            # Используем эндпоинт /hints/generate из ML сервиса
            import httpx
            from ..core.config import get_settings
            settings = get_settings()
            
            async with httpx.AsyncClient(timeout=settings.ml_service_timeout / 1000) as client:
                response = await client.post(
                    f'{settings.ml_service_url}/hints/generate',
                    json={
                        'task_description': task.description,
                        'task_difficulty': task.difficulty or 'medium',
                        'input_format': 'Стандартный ввод',
                        'output_format': 'Стандартный вывод',
                        'examples': examples,
                    }
                )
                response.raise_for_status()
                hints_data = response.json()
                
                # Конвертируем подсказки в формат для сохранения
                hints_list = []
                for hint in hints_data.get('hints', []):
                    # hint может быть Pydantic объектом или dict
                    if hasattr(hint, 'dict'):
                        hint_dict = hint.dict()
                    elif hasattr(hint, 'model_dump'):
                        hint_dict = hint.model_dump()
                    else:
                        hint_dict = hint
                    
                    hints_list.append({
                        'level': hint_dict.get('level'),
                        'content': hint_dict.get('content', hint_dict.get('hint', '')),
                        'penalty': hint_dict.get('penalty', 0.0)
                    })
                
                # Сохраняем подсказки в задачу
                task.hints = hints_list
                await session.commit()
                await session.refresh(task)
        except Exception as e:
            # Если не удалось сгенерировать подсказки, возвращаем ошибку
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Не удалось сгенерировать подсказки: {str(e)}'
            )
    
    # Парсим подсказки из JSON
    try:
        if isinstance(task.hints, str):
            hints_list = json.loads(task.hints)
        else:
            hints_list = task.hints
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка при чтении подсказок'
        )
    
    # Находим подсказку нужного уровня
    hint = None
    for h in hints_list:
        if h.get('level') == request.hint_level:
            hint = h
            break
    
    if not hint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Подсказка уровня {request.hint_level} не найдена'
        )
    
    # Проверяем, не использована ли уже эта подсказка
    existing_usage = await session.scalar(
        select(HintUsage).where(
            HintUsage.user_id == current_user.id,
            HintUsage.task_id == request.task_id,
            HintUsage.hint_level == request.hint_level
        )
    )
    
    if existing_usage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Эта подсказка уже использована'
        )
    
    # Создаем запись об использовании подсказки
    hint_usage = HintUsage(
        user_id=current_user.id,
        task_id=request.task_id,
        vacancy_id=task.vacancy_id,
        hint_level=request.hint_level,
        penalty=hint.get('penalty', 0.0)
    )
    session.add(hint_usage)
    await session.flush()
    
    # Подсчитываем количество использованных подсказок
    from sqlalchemy import func as sql_func
    used_count_result = await session.execute(
        select(sql_func.count(HintUsage.id)).where(
            HintUsage.user_id == current_user.id,
            HintUsage.task_id == request.task_id
        )
    )
    used_count = used_count_result.scalar() or 0
    
    # Всего подсказок 3
    total_hints = 3
    remaining_hints = max(0, total_hints - used_count)
    
    await session.commit()
    
    return HintResponse(
        content=hint.get('content', ''),
        penalty=hint.get('penalty', 0.0),
        remaining_hints=remaining_hints
    )


@router.get('/used/{task_id}', response_model=list[str])
async def get_used_hints(
    task_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить список использованных подсказок для задачи"""
    # Проверяем существование задачи
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    
    # Получаем использованные подсказки
    result = await session.scalars(
        select(HintUsage.hint_level).where(
            HintUsage.user_id == current_user.id,
            HintUsage.task_id == task_id
        )
    )
    
    return list(result.all())


@router.get('/available/{task_id}', response_model=list[str])
async def get_available_hint_levels(
    task_id: uuid.UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить список доступных уровней подсказок для задачи"""
    # Получаем задачу
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    
    # Получаем использованные подсказки
    used_result = await session.scalars(
        select(HintUsage.hint_level).where(
            HintUsage.user_id == current_user.id,
            HintUsage.task_id == task_id
        )
    )
    used_levels = set(used_result.all())
    
    # Если подсказок нет в задаче, возвращаем все три уровня (они будут сгенерированы при первом запросе)
    if not task.hints:
        all_levels = ['surface', 'medium', 'deep']
        return [level for level in all_levels if level not in used_levels]
    
    # Парсим подсказки
    try:
        if isinstance(task.hints, str):
            hints_list = json.loads(task.hints)
        else:
            hints_list = task.hints
    except (json.JSONDecodeError, TypeError):
        # Если ошибка парсинга, возвращаем все уровни
        all_levels = ['surface', 'medium', 'deep']
        return [level for level in all_levels if level not in used_levels]
    
    # Получаем все уровни подсказок
    all_levels = [h.get('level') for h in hints_list if h.get('level')]
    
    # Возвращаем доступные (неиспользованные) уровни
    return [level for level in all_levels if level not in used_levels]

