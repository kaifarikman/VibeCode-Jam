"""Публичные роуты для вопросов и ответов"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..dependencies.auth import get_current_user
from ..models import Answer, Question, User
from ..schemas import AnswerCreate, AnswerRead, AnswerWithQuestion, QuestionRead
from ..services import crud

router = APIRouter(prefix='/questions', tags=['questions'])


@router.get('', response_model=list[QuestionRead])
async def list_questions(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Получить список всех вопросов (требует авторизации)"""
    questions = await crud.list_questions(session)
    return questions


@router.get('/{question_id}', response_model=QuestionRead)
async def get_question(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Получить вопрос по ID (требует авторизации)"""
    question = await crud.get_question(session, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Question not found'
        )
    return question


@router.post('/{question_id}/answers', response_model=AnswerRead, status_code=status.HTTP_201_CREATED)
async def create_answer(
    question_id: UUID,
    answer_data: AnswerCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Создать или обновить ответ на вопрос"""
    # Проверяем существование вопроса
    question = await crud.get_question(session, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Question not found'
        )

    # Используем question_id из URL, игнорируем из body для безопасности
    answer = await crud.create_or_update_answer(
        session, current_user.id, question_id, answer_data.text
    )
    await session.commit()
    await session.refresh(answer)
    return answer


@router.get('/me/answers', response_model=list[AnswerWithQuestion])
async def get_my_answers(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Получить все свои ответы"""
    # Загружаем ответы с вопросами
    stmt = (
        select(Answer)
        .where(Answer.user_id == current_user.id)
        .options(selectinload(Answer.question))
        .order_by(Answer.created_at)
    )
    result = await session.scalars(stmt)
    answers = list(result.all())
    return answers

