"""Скрипт для сброса БД с сохранением данных из tasks, questions, vacancies"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Добавляем путь к backend
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

# Устанавливаем переменную окружения для поиска .env
env_file = backend_path / '.env'
if env_file.exists():
    os.environ['ENV_FILE'] = str(env_file)

from app.core.config import get_settings

settings = get_settings()


async def export_data(session: AsyncSession) -> dict:
    """Экспортировать данные из tasks, questions, vacancies"""
    print("Экспортирую данные из tasks, questions, vacancies...")
    
    data = {
        'tasks': [],
        'questions': [],
        'vacancies': [],
    }
    
    # Экспортируем tasks
    try:
        await session.rollback()  # Сбрасываем транзакцию
        result = await session.execute(text("SELECT * FROM tasks"))
        for row in result:
            task_dict = {}
            for key, value in row._mapping.items():
                if isinstance(value, UUID):
                    task_dict[key] = str(value)
                elif isinstance(value, datetime):
                    task_dict[key] = value.isoformat()
                elif value is None:
                    task_dict[key] = None
                else:
                    task_dict[key] = value
            data['tasks'].append(task_dict)
        print(f"  Экспортировано {len(data['tasks'])} задач")
    except Exception as e:
        print(f"  Таблица tasks не найдена или ошибка: {e}")
        await session.rollback()
    
    # Экспортируем questions
    try:
        await session.rollback()  # Сбрасываем транзакцию
        result = await session.execute(text("SELECT * FROM questions"))
        for row in result:
            question_dict = {}
            for key, value in row._mapping.items():
                if isinstance(value, UUID):
                    question_dict[key] = str(value)
                elif isinstance(value, datetime):
                    question_dict[key] = value.isoformat()
                elif value is None:
                    question_dict[key] = None
                else:
                    question_dict[key] = value
            data['questions'].append(question_dict)
        print(f"  Экспортировано {len(data['questions'])} вопросов")
    except Exception as e:
        print(f"  Таблица questions не найдена или ошибка: {e}")
        await session.rollback()
    
    # Экспортируем vacancies
    try:
        await session.rollback()  # Сбрасываем транзакцию
        result = await session.execute(text("SELECT * FROM vacancies"))
        for row in result:
            vacancy_dict = {}
            for key, value in row._mapping.items():
                if isinstance(value, UUID):
                    vacancy_dict[key] = str(value)
                elif isinstance(value, datetime):
                    vacancy_dict[key] = value.isoformat()
                elif value is None:
                    vacancy_dict[key] = None
                else:
                    vacancy_dict[key] = value
            data['vacancies'].append(vacancy_dict)
        print(f"  Экспортировано {len(data['vacancies'])} вакансий")
    except Exception as e:
        print(f"  Таблица vacancies не найдена или ошибка: {e}")
        await session.rollback()
    
    return data


async def drop_all_tables(engine):
    """Удалить все таблицы из БД, кроме tasks, questions, vacancies"""
    print("\nУдаляю все таблицы кроме tasks, questions, vacancies...")
    async with engine.begin() as conn:
        # Получаем список всех таблиц
        result = await conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result]
        
        # Таблицы, которые нужно сохранить
        keep_tables = {'tasks', 'questions', 'vacancies'}
        
        if tables:
            # Отключаем проверку внешних ключей временно
            await conn.execute(text("SET session_replication_role = 'replica'"))
            
            # Удаляем все таблицы кроме нужных
            for table in tables:
                if table not in keep_tables:
                    await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
                    print(f"  Удалена таблица: {table}")
                else:
                    print(f"  Сохранена таблица: {table}")
            
            await conn.execute(text("SET session_replication_role = 'origin'"))
        else:
            print("  Таблицы не найдены")
        
        # Удаляем версию Alembic, чтобы миграции применялись с начала
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        print("  Версия Alembic сброшена")
    
    print("Таблицы удалены\n")


async def apply_migrations(engine):
    """Применить миграции Alembic"""
    print("Применяю миграции...")
    import subprocess
    import sys
    
    app_dir = backend_path / 'app'
    
    # Сначала устанавливаем версию на первую миграцию, если таблицы не существуют
    async with engine.begin() as conn:
        # Проверяем, существует ли таблица users
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            )
        """))
        users_exists = result.scalar()
        
        if not users_exists:
            print("  Таблица users не существует, пропускаем первую миграцию...")
            # Создаем таблицу версий Alembic и устанавливаем версию на первую миграцию
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
            await conn.execute(text("""
                INSERT INTO alembic_version (version_num) 
                VALUES ('6a7c625306ad')
                ON CONFLICT DO NOTHING
            """))
    
    # Применяем миграции
    result = subprocess.run(
        [sys.executable, '-m', 'alembic', 'upgrade', 'head'],
        cwd=str(app_dir),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  Миграции применены успешно\n")
    else:
        print(f"  Ошибка при применении миграций:\n{result.stderr}")
        if result.stdout:
            print(f"  stdout: {result.stdout}")
        raise Exception("Не удалось применить миграции")


async def import_data(session: AsyncSession, data: dict):
    """Импортировать данные обратно в БД"""
    print("Импортирую данные обратно...")
    
    # Импортируем vacancies первыми (они могут быть нужны для foreign keys)
    if data['vacancies']:
        print(f"  Импортирую {len(data['vacancies'])} вакансий...")
        for vacancy_data in data['vacancies']:
            # Используем raw SQL для вставки
            await session.execute(text("""
                INSERT INTO vacancies (id, title, position, language, grade, ideal_resume, created_at, updated_at)
                VALUES (
                    :id::uuid, :title, :position, :language, :grade, :ideal_resume, 
                    :created_at::timestamptz, :updated_at::timestamptz
                )
                ON CONFLICT (id) DO NOTHING
            """), {
                'id': vacancy_data['id'],
                'title': vacancy_data['title'],
                'position': vacancy_data['position'],
                'language': vacancy_data['language'],
                'grade': vacancy_data['grade'],
                'ideal_resume': vacancy_data['ideal_resume'],
                'created_at': vacancy_data['created_at'],
                'updated_at': vacancy_data['updated_at'],
            })
        await session.commit()
        print("  Вакансии импортированы")
    
    # Импортируем questions
    if data['questions']:
        print(f"  Импортирую {len(data['questions'])} вопросов...")
        for question_data in data['questions']:
            options = question_data.get('options')
            if isinstance(options, str):
                options_json = options
            elif options is not None:
                options_json = json.dumps(options)
            else:
                options_json = None
            
            await session.execute(text("""
                INSERT INTO questions (id, text, type, options, "order", difficulty, vacancy_id, created_at, updated_at)
                VALUES (
                    :id::uuid, :text, :type, :options::jsonb, :order, :difficulty, 
                    :vacancy_id::uuid, :created_at::timestamptz, :updated_at::timestamptz
                )
                ON CONFLICT (id) DO NOTHING
            """), {
                'id': question_data['id'],
                'text': question_data['text'],
                'type': question_data.get('type', 'text'),
                'options': options_json,
                'order': question_data.get('order', 0),
                'difficulty': question_data.get('difficulty'),
                'vacancy_id': question_data.get('vacancy_id'),
                'created_at': question_data['created_at'],
                'updated_at': question_data.get('updated_at', question_data['created_at']),
            })
        await session.commit()
        print("  Вопросы импортированы")
    
    # Импортируем tasks
    if data['tasks']:
        print(f"  Импортирую {len(data['tasks'])} задач...")
        for task_data in data['tasks']:
            hints = task_data.get('hints')
            if isinstance(hints, str):
                hints_json = hints
            elif hints is not None:
                hints_json = json.dumps(hints)
            else:
                hints_json = None
            
            await session.execute(text("""
                INSERT INTO tasks (
                    id, title, description, topic, difficulty, 
                    open_tests, hidden_tests, hints, vacancy_id, 
                    created_at, updated_at
                )
                VALUES (
                    :id::uuid, :title, :description, :topic, :difficulty,
                    :open_tests, :hidden_tests, :hints::jsonb, :vacancy_id::uuid,
                    :created_at::timestamptz, :updated_at::timestamptz
                )
                ON CONFLICT (id) DO NOTHING
            """), {
                'id': task_data['id'],
                'title': task_data['title'],
                'description': task_data['description'],
                'topic': task_data.get('topic'),
                'difficulty': task_data.get('difficulty', 'medium'),
                'open_tests': task_data.get('open_tests'),
                'hidden_tests': task_data.get('hidden_tests'),
                'hints': hints_json,
                'vacancy_id': task_data.get('vacancy_id'),
                'created_at': task_data['created_at'],
                'updated_at': task_data.get('updated_at', task_data['created_at']),
            })
        await session.commit()
        print("  Задачи импортированы")
    
    print("\nИмпорт завершен")


async def main():
    """Основная функция"""
    print("=" * 60)
    print("Сброс БД с сохранением tasks, questions, vacancies")
    print("=" * 60)
    
    # Создаем engine
    database_url = settings.database_url
    engine = create_async_engine(database_url, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # 1. Экспортируем данные
        async with async_session() as session:
            data = await export_data(session)
        
        # 2. Удаляем все таблицы кроме нужных трех
        await drop_all_tables(engine)
        
        # 3. Применяем миграции (создадут недостающие таблицы)
        # Если миграции не могут быть применены, пропускаем их
        try:
            await apply_migrations(engine)
        except Exception as e:
            print(f"  Предупреждение: не удалось применить некоторые миграции: {e}")
            print("  Продолжаем импорт данных...")
        
        # 4. Импортируем данные обратно (если они были экспортированы)
        if data['tasks'] or data['questions'] or data['vacancies']:
            async with async_session() as session:
                await import_data(session, data)
        else:
            print("Нет данных для импорта (таблицы были пусты или не существовали)")
        
        print("=" * 60)
        print("Сброс БД завершен успешно!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())

