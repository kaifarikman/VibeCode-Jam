"""Тривиальные CRUD операции для вопросов и ответов"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Answer, Question


# ========== Questions CRUD ==========


async def get_question(session: AsyncSession, question_id: UUID) -> Question | None:
    """Получить вопрос по ID"""
    return await session.get(Question, question_id)


async def list_questions(session: AsyncSession) -> list[Question]:
    """Получить все вопросы, отсортированные по порядку"""
    result = await session.scalars(
        select(Question).order_by(Question.order, Question.created_at)
    )
    return list(result.all())


async def create_question(session: AsyncSession, text: str, order: int = 0) -> Question:
    """Создать новый вопрос"""
    question = Question(text=text, order=order)
    session.add(question)
    await session.flush()
    return question


async def update_question(
    session: AsyncSession, question_id: UUID, text: str | None = None, order: int | None = None
) -> Question | None:
    """Обновить вопрос"""
    question = await session.get(Question, question_id)
    if not question:
        return None

    if text is not None:
        question.text = text
    if order is not None:
        question.order = order

    await session.flush()
    return question


async def delete_question(session: AsyncSession, question_id: UUID) -> bool:
    """Удалить вопрос"""
    question = await session.get(Question, question_id)
    if not question:
        return False

    await session.delete(question)
    await session.flush()
    return True


# ========== Answers CRUD ==========


async def get_answer(session: AsyncSession, answer_id: UUID) -> Answer | None:
    """Получить ответ по ID"""
    return await session.get(Answer, answer_id)


async def get_user_answer_for_question(
    session: AsyncSession, user_id: UUID, question_id: UUID
) -> Answer | None:
    """Получить ответ пользователя на конкретный вопрос"""
    result = await session.scalar(
        select(Answer).where(Answer.user_id == user_id, Answer.question_id == question_id)
    )
    return result


async def list_user_answers(session: AsyncSession, user_id: UUID) -> list[Answer]:
    """Получить все ответы пользователя"""
    result = await session.scalars(
        select(Answer)
        .where(Answer.user_id == user_id)
        .order_by(Answer.created_at)
    )
    return list(result.all())


async def list_all_answers(session: AsyncSession) -> list[Answer]:
    """Получить все ответы (для админа)"""
    result = await session.scalars(select(Answer).order_by(Answer.created_at))
    return list(result.all())


async def create_or_update_answer(
    session: AsyncSession, user_id: UUID, question_id: UUID, text: str
) -> Answer:
    """Создать или обновить ответ пользователя на вопрос"""
    existing = await get_user_answer_for_question(session, user_id, question_id)
    if existing:
        existing.text = text
        await session.flush()
        return existing

    answer = Answer(user_id=user_id, question_id=question_id, text=text)
    session.add(answer)
    await session.flush()
    return answer


async def delete_answer(session: AsyncSession, answer_id: UUID) -> bool:
    """Удалить ответ"""
    answer = await session.get(Answer, answer_id)
    if not answer:
        return False

    await session.delete(answer)
    await session.flush()
    return True

