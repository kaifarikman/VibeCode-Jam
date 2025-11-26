"""Админские роуты - управление вопросами и просмотр ответов"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..dependencies.admin import get_admin_user
from ..models import Answer, Question, User
from ..schemas import AnswerWithQuestion, QuestionCreate, QuestionRead, QuestionUpdate
from ..services import crud

router = APIRouter(prefix='/admin', tags=['admin'])


# ========== Questions Management ==========


@router.get('/questions', response_model=list[QuestionRead])
async def list_questions(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить список всех вопросов (админ)"""
    questions = await crud.list_questions(session)
    return questions


@router.post('/questions', response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Создать новый вопрос"""
    # Проверка на уникальность текста
    existing = await session.scalar(
        select(Question).where(Question.text == question_data.text)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Question with this text already exists',
        )

    question = await crud.create_question(
        session, question_data.text, question_data.order
    )
    await session.commit()
    await session.refresh(question)
    return question


@router.get('/questions/{question_id}', response_model=QuestionRead)
async def get_question(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить вопрос по ID (админ)"""
    question = await crud.get_question(session, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Question not found'
        )
    return question


@router.put('/questions/{question_id}', response_model=QuestionRead)
async def update_question(
    question_id: UUID,
    question_data: QuestionUpdate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Обновить вопрос"""
    question = await crud.get_question(session, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Question not found'
        )

    # Проверка на уникальность текста, если текст изменяется
    if question_data.text is not None and question_data.text != question.text:
        existing = await session.scalar(
            select(Question).where(Question.text == question_data.text)
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Question with this text already exists',
            )

    question = await crud.update_question(
        session, question_id, question_data.text, question_data.order
    )
    await session.commit()
    await session.refresh(question)
    return question


@router.delete('/questions/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Удалить вопрос"""
    deleted = await crud.delete_question(session, question_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Question not found'
        )
    await session.commit()
    return None


# ========== Answers Viewing (Admin) ==========


@router.get('/answers', response_model=list[AnswerWithQuestion])
async def list_all_answers(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить все ответы всех пользователей (админ)"""
    # Загружаем ответы с вопросами
    stmt = select(Answer).options(selectinload(Answer.question)).order_by(Answer.created_at)
    result = await session.scalars(stmt)
    answers = list(result.all())
    return answers
