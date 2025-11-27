"""Роуты для работы с вакансиями"""

import random
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Application, Question, User, Vacancy
from ..schemas import ApplicationCreate, ApplicationRead, ApplicationStatusUpdate, QuestionRead, VacancyRead

router = APIRouter(prefix='/vacancies', tags=['vacancies'])


@router.get('', response_model=list[VacancyRead])
async def list_vacancies(
    language: str | None = None,
    grade: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Получить список вакансий с фильтрацией по языку и грейду"""
    query = select(Vacancy)
    
    if language:
        query = query.where(Vacancy.language == language)
    if grade:
        query = query.where(Vacancy.grade == grade)
    
    result = await session.scalars(query.order_by(Vacancy.created_at.desc()))
    return list(result.all())


@router.get('/{vacancy_id}', response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Получить вакансию по ID"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    return vacancy


@router.post('/{vacancy_id}/apply', response_model=ApplicationRead)
async def apply_to_vacancy(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Подать заявку на вакансию. Если заявка уже существует, возвращает существующую."""
    from fastapi import Response
    
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    
    # Проверяем, нет ли уже заявки
    existing = await session.scalar(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.vacancy_id == vacancy_id
        )
    )
    if existing:
        # Если заявка уже существует и тест пройден, запрещаем повторную подачу
        if existing.status in ['survey_completed', 'algo_test_completed', 'final_verdict']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Вы уже прошли тест по этой вакансии. Повторная подача заявки невозможна.'
            )
        # Если заявка существует, но тест не пройден, возвращаем её с кодом 200
        await session.refresh(existing)
        from ..schemas import ApplicationRead
        app_read = ApplicationRead.model_validate(existing)
        return Response(
            content=app_read.model_dump_json(),
            media_type='application/json',
            status_code=status.HTTP_200_OK
        )
    
    # Создаём новую заявку
    application = Application(
        user_id=current_user.id,
        vacancy_id=vacancy_id,
        status='pending',
    )
    session.add(application)
    await session.commit()
    await session.refresh(application)
    
    # Возвращаем новую заявку с кодом 201
    from ..schemas import ApplicationRead
    app_read = ApplicationRead.model_validate(application)
    return Response(
        content=app_read.model_dump_json(),
        media_type='application/json',
        status_code=status.HTTP_201_CREATED
    )


@router.patch('/applications/{application_id}/status', response_model=ApplicationRead)
async def update_application_status(
    application_id: uuid.UUID,
    status_data: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Обновить статус заявки"""
    try:
        from sqlalchemy.orm import selectinload
        
        # Загружаем заявку с вакансией
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(selectinload(Application.vacancy))
        )
        application = await session.scalar(stmt)
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Application not found'
            )
        
        # Проверяем, что заявка принадлежит текущему пользователю
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Access denied'
            )
        
        # Валидация статуса
        valid_statuses = ['pending', 'survey_completed', 'algo_test_completed', 'final_verdict']
        if status_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            )
        
        application.status = status_data.status
        await session.commit()
        await session.refresh(application)
        
        return application
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error updating application status: {str(e)}'
        )


@router.get('/my/applications', response_model=list[ApplicationRead])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить список заявок текущего пользователя с информацией о вакансиях"""
    from sqlalchemy.orm import selectinload
    
    stmt = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .options(selectinload(Application.vacancy))
        .order_by(Application.created_at.desc())
    )
    result = await session.scalars(stmt)
    applications = list(result.all())
    return applications


@router.get('/{vacancy_id}/survey-questions', response_model=list[QuestionRead])
async def get_survey_questions(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить до 10 случайных вопросов для опроса по вакансии"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    
    # Получаем вопросы, привязанные к этой вакансии, или все вопросы, если нет привязки
    stmt = select(Question).where(
        (Question.vacancy_id == vacancy_id) | (Question.vacancy_id.is_(None))
    )
    all_questions = await session.scalars(stmt)
    questions_list = list(all_questions.all())
    
    if len(questions_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет вопросов в базе для этой вакансии'
        )
    
    # Выбираем случайные вопросы (до 10)
    random.shuffle(questions_list)
    selected_questions = questions_list[:10]
    
    return selected_questions


@router.get('/{vacancy_id}/tasks', response_model=list[QuestionRead])
async def get_random_tasks(
    vacancy_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Получить 3 случайные задачи разной сложности для вакансии"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    
    # Получаем задачи, привязанные к этой вакансии, или все задачи, если нет привязки
    stmt = select(Question).where(
        (Question.vacancy_id == vacancy_id) | (Question.vacancy_id.is_(None))
    )
    all_questions = await session.scalars(stmt)
    questions_list = list(all_questions.all())
    
    # Убрана проверка на минимум 3 задачи - можно работать с любым количеством
    if len(questions_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нет задач в базе для этой вакансии'
        )
    
    # Группируем задачи по сложности
    by_difficulty: dict[str, list[Question]] = {'easy': [], 'medium': [], 'hard': []}
    for q in questions_list:
        difficulty = q.difficulty or 'medium'
        if difficulty in by_difficulty:
            by_difficulty[difficulty].append(q)
    
    # Выбираем по одной задаче каждого уровня сложности
    selected_tasks: list[Question] = []
    for difficulty in ['easy', 'medium', 'hard']:
        if by_difficulty[difficulty]:
            selected_tasks.append(random.choice(by_difficulty[difficulty]))
    
    # Если не хватает задач, дополняем случайными
    while len(selected_tasks) < 3:
        remaining = [q for q in questions_list if q not in selected_tasks]
        if not remaining:
            break
        selected_tasks.append(random.choice(remaining))
    
    # Перемешиваем порядок
    random.shuffle(selected_tasks)
    
    return selected_tasks[:3]

