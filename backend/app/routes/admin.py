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
    TaskGenerateRequest,
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
    from sqlalchemy.orm import selectinload
    from ..schemas import ApplicationRead as AppRead
    
    stmt = (
        select(Application)
        .options(selectinload(Application.vacancy))
        .order_by(Application.created_at.desc())
    )
    result = await session.scalars(stmt)
    applications = list(result.all())
    
    # Создаем ApplicationRead без поля user (для админа тоже не нужно, модератор использует свой эндпоинт)
    result_list = []
    for app in applications:
        app_dict = {
            'id': app.id,
            'user_id': app.user_id,
            'vacancy_id': app.vacancy_id,
            'ml_score': app.ml_score,
            'status': app.status,
            'created_at': app.created_at,
            'updated_at': app.updated_at,
            'vacancy': app.vacancy,
            'user': None,
        }
        result_list.append(AppRead.model_validate(app_dict))
    
    return result_list


# ========== Tasks Management ==========


@router.get('/tasks', response_model=list[TaskReadWithHidden])
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Получить список всех задач (админ)"""
    tasks = await crud.list_tasks(session)
    return [TaskReadWithHidden.from_orm(task) for task in tasks]


@router.post('/tasks/generate', response_model=TaskReadWithHidden, status_code=status.HTTP_201_CREATED)
async def generate_task(
    request: TaskGenerateRequest,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Сгенерировать новую задачу через ML сервис"""
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем, что вакансия выбрана и существует
        if not request.vacancy_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='При генерации задачи необходимо выбрать вакансию'
            )
        vacancy = await session.get(Vacancy, request.vacancy_id)
        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Вакансия с ID {request.vacancy_id} не найдена'
            )
        vacancy_id = request.vacancy_id
        target_language = (request.language or vacancy.language or 'python').lower()
        if target_language not in {'python', 'go', 'java', 'typescript'}:
            target_language = 'python'
        
        # Генерируем задачу через ML сервис
        from ..services.ml_client import ml_client
        
        ml_task = await ml_client.generate_task(
            difficulty=request.difficulty,
            topic=request.topic,
            language=target_language,
        )
        
        # Преобразуем формат данных из ML в формат БД
        # 1. Объединяем description с input_format и output_format
        description_parts = [ml_task.get('description', '')]
        if ml_task.get('input_format'):
            description_parts.append(f"\n\n**Формат входных данных:**\n{ml_task['input_format']}")
        if ml_task.get('output_format'):
            description_parts.append(f"\n\n**Формат выходных данных:**\n{ml_task['output_format']}")
        if ml_task.get('constraints'):
            constraints_text = '\n'.join(f"- {c}" for c in ml_task['constraints'])
            description_parts.append(f"\n\n**Ограничения:**\n{constraints_text}")
        full_description = '\n'.join(description_parts)
        
        # 2. examples из ML → open_tests в БД (формат {input, output})
        open_tests_list = None
        if ml_task.get('examples'):
            open_tests_list = [
                {'input': ex.get('input', ''), 'output': ex.get('output', '')}
                for ex in ml_task['examples'][:3]
            ]
        
        # 3. hidden_tests из ML → формат {input, output}
        # ML теперь может возвращать hidden_tests_full с outputs, или только hidden_tests (inputs)
        hidden_tests_list = None
        if ml_task.get('hidden_tests_full'):
            # Используем полные тесты с outputs, если они есть
            hidden_tests_list = ml_task['hidden_tests_full'][:15]
        elif ml_task.get('hidden_tests'):
            # Если есть только inputs, создаем с пустыми outputs
            hidden_tests_list = [
                {'input': test_input, 'output': ''}
                for test_input in ml_task['hidden_tests'][:15]
            ]
        else:
            hidden_tests_list = None
        
        # Если открытые тесты отсутствуют или их меньше трех, заполняем из закрытых
        if hidden_tests_list:
            # Дополняем до 15 тестов при необходимости
            if hidden_tests_list:
                base_source = hidden_tests_list.copy()
                while len(hidden_tests_list) < 15:
                    seed = base_source[len(hidden_tests_list) % len(base_source)]
                    hidden_tests_list.append({'input': seed['input'], 'output': seed['output']})
            if not open_tests_list:
                open_tests_list = hidden_tests_list[:3]
            elif len(open_tests_list) < 3:
                open_tests_list += hidden_tests_list[: 3 - len(open_tests_list)]
            hidden_tests_list = hidden_tests_list[:15]
        else:
            # Используем fallback из открытых тестов или дефолтных значений
            logger.warning('ML не вернул закрытые тесты. Используем fallback.')
            fallback_source = open_tests_list or [{'input': '1', 'output': '1'}]
            hidden_tests_list = []
            while len(hidden_tests_list) < 15:
                base = fallback_source[len(hidden_tests_list) % len(fallback_source)]
                hidden_tests_list.append({'input': base['input'], 'output': base['output']})
            if not open_tests_list:
                open_tests_list = hidden_tests_list[:3]
        
        # Гарантируем, что у нас всегда есть минимум 3 открытых теста
        if not open_tests_list:
            open_tests_list = []
        if len(open_tests_list) < 3:
            source_pool = hidden_tests_list or open_tests_list
            # Если по какой-то причине и скрытых тестов нет — используем заглушки
            if not source_pool:
                source_pool = [{'input': '1', 'output': '1'}]
            # Берем копию источника, чтобы не зависеть от дальнейших изменений списка
            snapshot = [dict(seed) for seed in source_pool]
            idx = 0
            while len(open_tests_list) < 3 and snapshot:
                seed = snapshot[idx % len(snapshot)]
                open_tests_list.append({'input': seed.get('input', ''), 'output': seed.get('output', '')})
                idx += 1
        
        # 4. hints сохраняем как есть (уже dict/list)
        hints_data = ml_task.get('hints')
        
        if hidden_tests_list is None or len(hidden_tests_list) < 15:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Не удалось сгенерировать закрытые тесты. Попробуйте снова.'
            )
        
        # Создаем задачу в БД с привязкой к вакансии
        task = await crud.create_task(
            session=session,
            title=ml_task.get('title', 'Без названия'),
            description=full_description,
            difficulty=ml_task.get('difficulty', request.difficulty),
            topic=ml_task.get('topic') or request.topic,
            open_tests=open_tests_list,
            hidden_tests=hidden_tests_list,
            vacancy_id=vacancy_id,  # Используем проверенный vacancy_id
            hints=hints_data,  # hints уже в правильном формате (list[dict])
            canonical_solution=ml_task.get('canonical_solution'),
        )
        
        await session.commit()
        await session.refresh(task)
        return TaskReadWithHidden.from_orm(task)
        
    except Exception as e:
        logger.error(f'Error generating task via ML: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка генерации задачи через ML сервис: {str(e)}'
        )


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
        canonical_solution=task_data.canonical_solution,
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
        canonical_solution=task_data.canonical_solution,
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
