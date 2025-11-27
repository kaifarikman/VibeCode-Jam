"""Админские роуты - управление вопросами и просмотр ответов"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_session
from ..dependencies.admin import get_admin_user
from ..models import Answer, Application, Question, Task, User, Vacancy
from ..schemas import (
    AnswerWithQuestion,
    ApplicationRead,
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
    TaskCreate,
    TaskReadWithHidden,
    TaskUpdate,
    VacancyCreate,
    VacancyRead,
    VacancyUpdate,
)
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
    # Обновляем тип вопроса, опции, сложность и вакансию, если они указаны
    if question_data.question_type:
        question.question_type = question_data.question_type
    if question_data.options is not None:
        question.options = question_data.options
    if question_data.difficulty:
        question.difficulty = question_data.difficulty
    if question_data.vacancy_id:
        question.vacancy_id = question_data.vacancy_id
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
    # Обновляем тип вопроса, опции и сложность, если они указаны
    if question_data.question_type is not None:
        question.question_type = question_data.question_type
    if question_data.options is not None:
        question.options = question_data.options
    if question_data.difficulty is not None:
        question.difficulty = question_data.difficulty
    if question_data.vacancy_id is not None:
        question.vacancy_id = question_data.vacancy_id
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


# ========== Vacancies Management ==========


@router.get('/vacancies', response_model=list[VacancyRead])
async def list_vacancies(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить список всех вакансий (админ)"""
    result = await session.scalars(select(Vacancy).order_by(Vacancy.created_at.desc()))
    return list(result.all())


@router.post('/vacancies', response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Создать новую вакансию"""
    vacancy = Vacancy(
        title=vacancy_data.title,
        position=vacancy_data.position,
        language=vacancy_data.language,
        grade=vacancy_data.grade,
        ideal_resume=vacancy_data.ideal_resume,
    )
    session.add(vacancy)
    await session.commit()
    await session.refresh(vacancy)
    return vacancy


@router.get('/vacancies/{vacancy_id}', response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить вакансию по ID (админ)"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    return vacancy


@router.put('/vacancies/{vacancy_id}', response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: UUID,
    vacancy_data: VacancyUpdate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Обновить вакансию"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )

    if vacancy_data.title is not None:
        vacancy.title = vacancy_data.title
    if vacancy_data.position is not None:
        vacancy.position = vacancy_data.position
    if vacancy_data.language is not None:
        vacancy.language = vacancy_data.language
    if vacancy_data.grade is not None:
        vacancy.grade = vacancy_data.grade
    if vacancy_data.ideal_resume is not None:
        vacancy.ideal_resume = vacancy_data.ideal_resume

    await session.commit()
    await session.refresh(vacancy)
    return vacancy


@router.delete('/vacancies/{vacancy_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Удалить вакансию"""
    vacancy = await session.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Vacancy not found'
        )
    await session.delete(vacancy)
    await session.commit()
    return None


@router.get('/applications', response_model=list[ApplicationRead])
async def list_applications(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить все заявки (админ)"""
    result = await session.scalars(select(Application).order_by(Application.created_at.desc()))
    return list(result.all())


# ========== Tasks Management ==========


@router.get('/tasks', response_model=list[TaskReadWithHidden])
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить список всех задач (админ)"""
    tasks = await crud.list_tasks(session)
    return [TaskReadWithHidden.from_orm(task) for task in tasks]


@router.post('/tasks', response_model=TaskReadWithHidden, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Создать новую задачу"""
    import json
    
    # Конвертируем тесты в JSON
    open_tests_json = None
    if task_data.open_tests:
        open_tests_json = json.dumps([test.model_dump() for test in task_data.open_tests])
    
    hidden_tests_json = None
    if task_data.hidden_tests:
        hidden_tests_json = json.dumps([test.model_dump() for test in task_data.hidden_tests])
    
    task = await crud.create_task(
        session=session,
        title=task_data.title,
        description=task_data.description,
        difficulty=task_data.difficulty,
        topic=task_data.topic,
        open_tests=json.loads(open_tests_json) if open_tests_json else None,
        hidden_tests=json.loads(hidden_tests_json) if hidden_tests_json else None,
        vacancy_id=task_data.vacancy_id,
    )
    await session.commit()
    await session.refresh(task)
    return TaskReadWithHidden.from_orm(task)


@router.get('/tasks/{task_id}', response_model=TaskReadWithHidden)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить задачу по ID (админ)"""
    task = await crud.get_task(session, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    return TaskReadWithHidden.from_orm(task)


@router.put('/tasks/{task_id}', response_model=TaskReadWithHidden)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Обновить задачу"""
    import json
    
    # Конвертируем тесты в JSON, если они указаны
    open_tests_list = None
    if task_data.open_tests is not None:
        open_tests_list = [test.model_dump() for test in task_data.open_tests]
    
    hidden_tests_list = None
    if task_data.hidden_tests is not None:
        hidden_tests_list = [test.model_dump() for test in task_data.hidden_tests]
    
    task = await crud.update_task(
        session=session,
        task_id=task_id,
        title=task_data.title,
        description=task_data.description,
        difficulty=task_data.difficulty,
        topic=task_data.topic,
        open_tests=open_tests_list,
        hidden_tests=hidden_tests_list,
        vacancy_id=task_data.vacancy_id,
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    await session.commit()
    await session.refresh(task)
    return TaskReadWithHidden.from_orm(task)


@router.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Удалить задачу"""
    deleted = await crud.delete_task(session, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Task not found'
        )
    await session.commit()
    return None
