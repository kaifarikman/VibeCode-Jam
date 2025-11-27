"""Роуты для модератора - просмотр и решение по заявкам"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.config import get_settings
from ..database import get_session
from ..dependencies.moderator import get_current_moderator
from ..models import Application, Answer, Question, Task, TaskSolution, TaskMetric, User, Vacancy, Moderator
from ..schemas import ApplicationRead, VacancyRead
from ..services.email import EmailService

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/moderator', tags=['moderator'])
settings = get_settings()


@router.get('/applications')
async def list_applications_for_moderation(
    _moderator: Moderator = Depends(get_current_moderator),
    session: AsyncSession = Depends(get_session),
):
    """Получить список заявок для модерации (опрос завершен или алгоритмы выполнены)"""
    from sqlalchemy import or_
    stmt = (
        select(Application)
        .where(
            or_(
                Application.status == 'survey_completed',
                Application.status == 'algo_test_completed',
                Application.status == 'under_review',
            )
        )
        .options(selectinload(Application.vacancy), selectinload(Application.user))
        .order_by(Application.updated_at.desc())
    )
    result = await session.scalars(stmt)
    applications = list(result.all())
    
    # Преобразуем в dict с данными пользователя
    applications_data = []
    for app in applications:
        app_dict = {
            'id': str(app.id),
            'user_id': str(app.user_id),
            'vacancy_id': str(app.vacancy_id),
            'ml_score': app.ml_score,
            'status': app.status,
            'created_at': app.created_at.isoformat(),
            'updated_at': app.updated_at.isoformat(),
            'vacancy': {
                'id': str(app.vacancy.id),
                'title': app.vacancy.title,
                'position': app.vacancy.position,
                'language': app.vacancy.language,
                'grade': app.vacancy.grade,
                'ideal_resume': app.vacancy.ideal_resume,
                'created_at': app.vacancy.created_at.isoformat(),
                'updated_at': app.vacancy.updated_at.isoformat(),
            } if app.vacancy else None,
            'user': {
                'id': str(app.user.id),
                'email': app.user.email,
                'full_name': app.user.full_name,
            } if app.user else None,
        }
        applications_data.append(app_dict)
    
    return applications_data


@router.get('/applications/{application_id}')
async def get_application_details(
    application_id: uuid.UUID,
    _moderator: Moderator = Depends(get_current_moderator),
    session: AsyncSession = Depends(get_session),
):
    """Получить детальную информацию о заявке: решения задач, ответы на вопросы"""
    # Загружаем заявку с вакансией и пользователем
    stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.vacancy), selectinload(Application.user))
    )
    application = await session.scalar(stmt)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Application not found'
        )
    
    # Получаем решения задач
    task_solutions = await session.scalars(
        select(TaskSolution)
        .where(
            TaskSolution.user_id == application.user_id,
            TaskSolution.vacancy_id == application.vacancy_id
        )
        .options(selectinload(TaskSolution.task))
    )
    solutions_list = list(task_solutions.all())

    solution_ids = [sol.id for sol in solutions_list]
    metrics_map: dict[uuid.UUID, TaskMetric] = {}
    if solution_ids:
        metrics = await session.scalars(
            select(TaskMetric).where(TaskMetric.task_solution_id.in_(solution_ids))
        )
        metrics_map = {metric.task_solution_id: metric for metric in metrics}
    
    # Получаем ответы на вопросы опроса для этой вакансии
    # Фильтруем по вопросам, связанным с вакансией
    answers = await session.scalars(
        select(Answer)
        .join(Question, Answer.question_id == Question.id)
        .where(
            Answer.user_id == application.user_id,
            or_(Question.vacancy_id == application.vacancy_id, Question.vacancy_id.is_(None))
        )
        .options(selectinload(Answer.question))
    )
    answers_list = list(answers.all())
    
    # Формируем ответ
    return {
        'application': {
            'id': str(application.id),
            'user_id': str(application.user_id),
            'user_email': application.user.email,
            'user_full_name': application.user.full_name,
            'vacancy_id': str(application.vacancy_id),
            'vacancy_title': application.vacancy.title,
            'vacancy_position': application.vacancy.position,
            'status': application.status,
            'ml_score': application.ml_score,
            'created_at': application.created_at.isoformat(),
            'updated_at': application.updated_at.isoformat(),
        },
        'task_solutions': [
            {
                'task_id': str(sol.task_id),
                'task_title': sol.task.title if sol.task else 'Unknown',
                'task_description': sol.task.description if sol.task else '',
                'solution_code': sol.solution_code,
                'language': sol.language,
                'status': sol.status,
                'verdict': sol.verdict,
                'test_results': sol.test_results,
                'created_at': sol.created_at.isoformat(),
                'metric': (
                    {
                        'tests_total': metrics_map[sol.id].tests_total,
                        'tests_passed': metrics_map[sol.id].tests_passed,
                        'total_duration_ms': metrics_map[sol.id].total_duration_ms,
                        'average_duration_ms': metrics_map[sol.id].average_duration_ms,
                        'verdict': metrics_map[sol.id].verdict,
                        'language': metrics_map[sol.id].language,
                    }
                    if sol.id in metrics_map
                    else None
                ),
            }
            for sol in solutions_list
        ],
        'survey_answers': [
            {
                'question_id': str(ans.question_id),
                'question_text': ans.question.text if ans.question else 'Unknown',
                'answer_text': ans.answer_text,
                'created_at': ans.created_at.isoformat(),
            }
            for ans in answers_list
        ],
    }


@router.post('/applications/{application_id}/decide')
async def decide_application(
    application_id: uuid.UUID,
    decision_data: dict[str, Any],
    _moderator: Moderator = Depends(get_current_moderator),
    session: AsyncSession = Depends(get_session),
):
    """Принять или отклонить заявку"""
    decision = decision_data.get('decision')
    comment = decision_data.get('comment')
    
    if decision not in ['accepted', 'rejected']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Decision must be "accepted" or "rejected"'
        )
    
    # Загружаем заявку с пользователем и вакансией
    stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.user), selectinload(Application.vacancy))
    )
    application = await session.scalar(stmt)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Application not found'
        )
    
    # Разрешаем принимать решение для заявок со статусом survey_completed, algo_test_completed или under_review
    if application.status not in ['survey_completed', 'algo_test_completed', 'under_review']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Application status is {application.status}, expected survey_completed, algo_test_completed или under_review'
        )
    
    # Обновляем статус заявки
    # Если принято - статус accepted, если отклонено - rejected
    new_status = 'accepted' if decision == 'accepted' else 'rejected'
    application.status = new_status
    await session.commit()
    await session.refresh(application)
    
    # Отправляем письмо пользователю
    try:
        email_service = EmailService(settings)
        if decision == 'accepted':
            subject = f'Поздравляем! Ваша заявка на {application.vacancy.title} принята'
            body = f"""Здравствуйте, {application.user.full_name or 'Кандидат'}!

Поздравляем! Ваша заявка на вакансию "{application.vacancy.title}" ({application.vacancy.position}) была принята.

Мы рассмотрели ваше резюме и результаты тестирования, и готовы предложить вам следующий этап собеседования.

{f'Комментарий: {comment}' if comment else ''}

С уважением,
Команда FutureCareer"""
        else:
            subject = f'Результат рассмотрения заявки на {application.vacancy.title}'
            body = f"""Здравствуйте, {application.user.full_name or 'Кандидат'}!

К сожалению, ваша заявка на вакансию "{application.vacancy.title}" ({application.vacancy.position}) была отклонена.

{f'Комментарий: {comment}' if comment else 'Мы рассмотрели ваше резюме и результаты тестирования, но на данный момент не можем предложить вам дальнейшее участие в отборе.'}

Благодарим за интерес к нашей компании и желаем успехов в поиске работы!

С уважением,
Команда FutureCareer"""
        
        await email_service.send_email(
            to_email=application.user.email,
            subject=subject,
            body=body
        )
        logger.info(f"Email sent to {application.user.email} for application {application_id}")
    except Exception as e:
        logger.error(f"Failed to send email for application {application_id}: {e}", exc_info=True)
        # Не прерываем выполнение, если письмо не отправилось
    
    return {
        'success': True,
        'application_id': str(application_id),
        'new_status': new_status,
        'decision': decision
    }

