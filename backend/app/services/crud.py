"""Тривиальные CRUD операции для вопросов, ответов и задач"""

import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Answer, Question, Task


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


# ========== Tasks CRUD ==========


async def get_task(session: AsyncSession, task_id: UUID) -> Task | None:
    """Получить задачу по ID"""
    return await session.get(Task, task_id)


async def list_tasks(session: AsyncSession, vacancy_id: UUID | None = None) -> list[Task]:
    """Получить все задачи, опционально отфильтрованные по вакансии"""
    query = select(Task)
    if vacancy_id:
        query = query.where((Task.vacancy_id == vacancy_id) | (Task.vacancy_id.is_(None)))
    result = await session.scalars(query.order_by(Task.difficulty, Task.created_at))
    return list(result.all())


async def create_task(
    session: AsyncSession,
    title: str,
    description: str,
    difficulty: str = 'medium',
    topic: str | None = None,
    open_tests: list[dict] | None = None,
    hidden_tests: list[dict] | None = None,
    vacancy_id: UUID | None = None,
) -> Task:
    """Создать новую задачу"""
    task = Task(
        title=title,
        description=description,
        difficulty=difficulty,
        topic=topic,
        open_tests=json.dumps(open_tests) if open_tests else None,
        hidden_tests=json.dumps(hidden_tests) if hidden_tests else None,
        vacancy_id=vacancy_id,
    )
    session.add(task)
    await session.flush()
    return task


async def update_task(
    session: AsyncSession,
    task_id: UUID,
    title: str | None = None,
    description: str | None = None,
    difficulty: str | None = None,
    topic: str | None = None,
    open_tests: list[dict] | None = None,
    hidden_tests: list[dict] | None = None,
    vacancy_id: UUID | None = None,
) -> Task | None:
    """Обновить задачу"""
    task = await session.get(Task, task_id)
    if not task:
        return None

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if difficulty is not None:
        task.difficulty = difficulty
    if topic is not None:
        task.topic = topic
    if open_tests is not None:
        task.open_tests = json.dumps(open_tests) if open_tests else None
    if hidden_tests is not None:
        task.hidden_tests = json.dumps(hidden_tests) if hidden_tests else None
    if vacancy_id is not None:
        task.vacancy_id = vacancy_id

    await session.flush()
    return task


async def delete_task(session: AsyncSession, task_id: UUID) -> bool:
    """Удалить задачу"""
    task = await session.get(Task, task_id)
    if not task:
        return False

    await session.delete(task)
    await session.flush()
    return True

