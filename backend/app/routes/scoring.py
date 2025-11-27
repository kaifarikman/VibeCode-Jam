"""Роуты для подсчета финального балла"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies.auth import get_current_user, get_current_user_optional
from ..models import Application, Execution, HintUsage, Task, TaskSolution, User
from ..schemas.scoring import ScoringRequest, ScoringResponse
from ..services.scoring import scoring_service

router = APIRouter(prefix='/scoring', tags=['scoring'])


@router.post('/calculate', response_model=ScoringResponse)
async def calculate_score(
    request: ScoringRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Рассчитать финальный балл по метрикам
    
    Используется для расчета финального балла после завершения контеста.
    """
    # Убеждаемся, что hints_used - это список и правильно обработан
    hints_used_list = list(request.hints_used) if request.hints_used is not None else []
    
    # Валидация: проверяем, что все подсказки валидны
    valid_hint_levels = {'surface', 'medium', 'deep'}
    hints_used_list = [h for h in hints_used_list if h in valid_hint_levels]
    
    # Рассчитываем финальный балл
    final_score = scoring_service.calculate_final_score(
        difficulty=request.difficulty,
        tests_passed=request.tests_passed,
        total_tests=request.total_tests,
        time_taken_seconds=request.time_taken_seconds,
        code_quality_score=request.code_quality_score,
        communication_score=request.communication_score,
        hints_used=hints_used_list
    )
    
    # Формируем разбивку для отладки
    correctness = request.tests_passed / request.total_tests if request.total_tests > 0 else 0.0
    time_limit = scoring_service.TIME_LIMITS.get(request.difficulty, 600)
    time_score = max(0.0, 1.0 - (request.time_taken_seconds / time_limit) * 0.5)
    multiplier = scoring_service.DIFFICULTY_MULTIPLIERS.get(request.difficulty, 1.0)
    
    # Используем тот же список hints_used, что и для расчета
    total_penalty = sum(scoring_service.HINT_PENALTIES.get(hint, 0.0) for hint in hints_used_list)
    
    base_score_value = (
        0.40 * correctness +
        0.20 * (request.code_quality_score / 100.0) +
        0.20 * (request.communication_score / 100.0) +
        0.20 * time_score
    )
    score_before_penalty = base_score_value * multiplier * 100.0
    
    breakdown = {
        'correctness': correctness,
        'code_quality': request.code_quality_score / 100.0,
        'communication': request.communication_score / 100.0,
        'time_score': time_score,
        'base_score': score_before_penalty,
        'multiplier': multiplier,
        'penalties': {
            'hints_used': hints_used_list,
            'total_penalty': total_penalty
        },
        'final_score': final_score,
        'score_before_penalty': score_before_penalty,
        'score_after_penalty': score_before_penalty - total_penalty
    }
    
    return ScoringResponse(final_score=final_score, breakdown=breakdown)


@router.post('/calculate-for-vacancy/{vacancy_id}', response_model=ScoringResponse)
async def calculate_score_for_vacancy(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Рассчитать финальный балл для вакансии на основе всех решенных задач
    
    Автоматически собирает метрики из решений задач пользователя для данной вакансии.
    """
    # Получаем заявку пользователя на вакансию
    application = await session.scalar(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.vacancy_id == vacancy_id
        )
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Application not found'
        )
    
    # Получаем все решения задач для этой вакансии
    solutions = await session.scalars(
        select(TaskSolution).where(
            TaskSolution.user_id == current_user.id,
            TaskSolution.vacancy_id == vacancy_id
        )
    )
    solutions_list = list(solutions.all())
    
    if not solutions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No solutions found for this vacancy'
        )
    
    # Собираем метрики из всех решений
    total_tests_passed = 0
    total_tests = 0
    total_time_seconds = 0.0
    code_quality_scores = []
    communication_scores = []
    all_hints_used = []
    difficulties = []
    
    for solution in solutions_list:
        # Получаем задачу для определения сложности
        task = await session.get(Task, solution.task_id)
        if task:
            difficulties.append(task.difficulty or 'medium')
        
        # Подсчитываем тесты
        test_results = solution.test_results or []
        if isinstance(test_results, list):
            for tr in test_results:
                if isinstance(tr, dict):
                    total_tests += 1
                    if tr.get('passed', False):
                        total_tests_passed += 1
        
        # Получаем время выполнения
        if solution.execution_id:
            execution = await session.get(Execution, solution.execution_id)
            if execution and execution.started_at and execution.completed_at:
                time_diff = (execution.completed_at - execution.started_at).total_seconds()
                total_time_seconds += time_diff
        
        # Получаем использованные подсказки
        hint_usages = await session.scalars(
            select(HintUsage).where(
                HintUsage.user_id == current_user.id,
                HintUsage.task_id == solution.task_id,
                HintUsage.vacancy_id == vacancy_id
            )
        )
        for hu in hint_usages:
            if hu.hint_level not in all_hints_used:
                all_hints_used.append(hu.hint_level)
        
        # TODO: Получить code_quality_score и communication_score через ML сервис
        # Пока используем значения по умолчанию
        code_quality_scores.append(75.0)  # Заменить на реальную оценку
        communication_scores.append(80.0)  # Заменить на реальную оценку
    
    # Усредняем оценки качества кода и коммуникации
    avg_code_quality = sum(code_quality_scores) / len(code_quality_scores) if code_quality_scores else 75.0
    avg_communication = sum(communication_scores) / len(communication_scores) if communication_scores else 80.0
    
    # Используем среднюю сложность задач
    avg_difficulty = 'medium'
    if difficulties:
        # Определяем преобладающую сложность
        easy_count = difficulties.count('easy')
        medium_count = difficulties.count('medium')
        hard_count = difficulties.count('hard')
        if hard_count >= medium_count and hard_count >= easy_count:
            avg_difficulty = 'hard'
        elif medium_count >= easy_count:
            avg_difficulty = 'medium'
        else:
            avg_difficulty = 'easy'
    
    # Рассчитываем финальный балл
    final_score = scoring_service.calculate_final_score(
        difficulty=avg_difficulty,
        tests_passed=total_tests_passed,
        total_tests=total_tests if total_tests > 0 else 1,
        time_taken_seconds=total_time_seconds,
        code_quality_score=avg_code_quality,
        communication_score=avg_communication,
        hints_used=all_hints_used
    )
    
    # Сохраняем балл в заявку
    application.ml_score = final_score
    await session.commit()
    
    # Формируем разбивку
    breakdown = {
        'total_tasks': len(solutions_list),
        'total_tests_passed': total_tests_passed,
        'total_tests': total_tests,
        'total_time_seconds': total_time_seconds,
        'avg_code_quality': avg_code_quality,
        'avg_communication': avg_communication,
        'avg_difficulty': avg_difficulty,
        'hints_used': all_hints_used,
        'final_score': final_score
    }
    
    return ScoringResponse(final_score=final_score, breakdown=breakdown)

