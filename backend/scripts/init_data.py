"""Скрипт для инициализации данных: создание админа и заполнение вакансиями"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к backend
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

import json

from app.database import async_session_factory
from app.models import Question, Task, User, Vacancy
from app.services.auth import hash_password
from sqlalchemy import select


VACANCIES_DATA = [
    # Python
    {
        'title': 'Python Backend Developer (Junior)',
        'position': 'Backend Developer',
        'language': 'python',
        'grade': 'junior',
        'ideal_resume': 'Опыт работы с Python от 6 месяцев. Знание основ Django/FastAPI. Понимание REST API. Базовые знания SQL и Git. Готовность к обучению и работе в команде.',
    },
    {
        'title': 'Python Backend Developer (Middle)',
        'position': 'Backend Developer',
        'language': 'python',
        'grade': 'middle',
        'ideal_resume': 'Опыт работы с Python от 2 лет. Глубокое знание Django/FastAPI. Опыт работы с базами данных (PostgreSQL, Redis). Понимание микросервисной архитектуры. Опыт работы с Docker, CI/CD. Знание асинхронного программирования.',
    },
    {
        'title': 'Python Backend Developer (Senior)',
        'position': 'Backend Developer',
        'language': 'python',
        'grade': 'senior',
        'ideal_resume': 'Опыт работы с Python от 5 лет. Экспертные знания архитектуры высоконагруженных систем. Опыт проектирования и масштабирования систем. Лидерские качества, опыт менторинга. Знание различных паттернов проектирования. Опыт работы с Kubernetes, мониторингом и логированием.',
    },
    # TypeScript
    {
        'title': 'TypeScript Full-Stack Developer (Junior)',
        'position': 'Full-Stack Developer',
        'language': 'typescript',
        'grade': 'junior',
        'ideal_resume': 'Опыт работы с TypeScript от 6 месяцев. Знание React/Next.js или Node.js. Понимание основ веб-разработки. Базовые знания HTML, CSS, JavaScript. Готовность к обучению и работе в команде.',
    },
    {
        'title': 'TypeScript Full-Stack Developer (Middle)',
        'position': 'Full-Stack Developer',
        'language': 'typescript',
        'grade': 'middle',
        'ideal_resume': 'Опыт работы с TypeScript от 2 лет. Глубокое знание React/Next.js и Node.js. Опыт работы с базами данных. Понимание архитектуры фронтенд и бэкенд приложений. Опыт работы с Docker, CI/CD. Знание современных инструментов разработки.',
    },
    {
        'title': 'TypeScript Full-Stack Developer (Senior)',
        'position': 'Full-Stack Developer',
        'language': 'typescript',
        'grade': 'senior',
        'ideal_resume': 'Опыт работы с TypeScript от 5 лет. Экспертные знания в области веб-разработки. Опыт проектирования и разработки сложных приложений. Лидерские качества, опыт менторинга. Знание различных фреймворков и библиотек. Опыт работы с микросервисной архитектурой.',
    },
    # Go
    {
        'title': 'Go Backend Developer (Junior)',
        'position': 'Backend Developer',
        'language': 'go',
        'grade': 'junior',
        'ideal_resume': 'Опыт работы с Go от 6 месяцев. Знание основ языка и стандартной библиотеки. Понимание принципов конкурентного программирования. Базовые знания SQL и Git. Готовность к обучению и работе в команде.',
    },
    {
        'title': 'Go Backend Developer (Middle)',
        'position': 'Backend Developer',
        'language': 'go',
        'grade': 'middle',
        'ideal_resume': 'Опыт работы с Go от 2 лет. Глубокое знание языка и его экосистемы. Опыт работы с базами данных и кэшированием. Понимание микросервисной архитектуры. Опыт работы с Docker, CI/CD. Знание goroutines и каналов.',
    },
    {
        'title': 'Go Backend Developer (Senior)',
        'position': 'Backend Developer',
        'language': 'go',
        'grade': 'senior',
        'ideal_resume': 'Опыт работы с Go от 5 лет. Экспертные знания языка и его внутренностей. Опыт проектирования и масштабирования высоконагруженных систем. Лидерские качества, опыт менторинга. Знание различных паттернов и best practices. Опыт работы с Kubernetes, мониторингом и логированием.',
    },
    # Java
    {
        'title': 'Java Backend Developer (Junior)',
        'position': 'Backend Developer',
        'language': 'java',
        'grade': 'junior',
        'ideal_resume': 'Опыт работы с Java от 6 месяцев. Знание основ Java и Spring Framework. Понимание REST API. Базовые знания SQL и Git. Готовность к обучению и работе в команде.',
    },
    {
        'title': 'Java Backend Developer (Middle)',
        'position': 'Backend Developer',
        'language': 'java',
        'grade': 'middle',
        'ideal_resume': 'Опыт работы с Java от 2 лет. Глубокое знание Spring Boot, Spring Data, Spring Security. Опыт работы с базами данных (PostgreSQL, MySQL). Понимание микросервисной архитектуры. Опыт работы с Docker, CI/CD. Знание Maven/Gradle.',
    },
    {
        'title': 'Java Backend Developer (Senior)',
        'position': 'Backend Developer',
        'language': 'java',
        'grade': 'senior',
        'ideal_resume': 'Опыт работы с Java от 5 лет. Экспертные знания Spring экосистемы и JVM. Опыт проектирования и масштабирования высоконагруженных систем. Лидерские качества, опыт менторинга. Знание различных паттернов проектирования. Опыт работы с Kubernetes, мониторингом и логированием.',
    },
]


async def create_admin_user():
    """Создает админского пользователя"""
    async with async_session_factory() as session:
        # Используем валидный email и пароль длиной минимум 8 символов
        admin_email = 'admin@example.com'
        admin_password = 'admin123'  # Минимум 8 символов
        
        # Проверяем, существует ли уже админ
        admin = await session.scalar(select(User).where(User.email == admin_email))
        
        if admin:
            print('Админский пользователь уже существует. Обновляем пароль...')
            admin.password_hash = hash_password(admin_password)
            admin.is_admin = True
            admin.is_verified = True
            admin.full_name = 'Администратор'
        else:
            print('Создаем админского пользователя...')
            admin = User(
                email=admin_email,
                password_hash=hash_password(admin_password),
                full_name='Администратор',
                is_admin=True,
                is_verified=True,
            )
            session.add(admin)
        
        await session.commit()
        print('✅ Админский пользователь создан/обновлен:')
        print(f'   Email: {admin_email}')
        print(f'   Password: {admin_password}')


async def create_vacancies():
    """Создает вакансии в базе данных"""
    async with async_session_factory() as session:
        created_count = 0
        updated_count = 0
        
        for vacancy_data in VACANCIES_DATA:
            # Проверяем, существует ли уже такая вакансия
            existing = await session.scalar(
                select(Vacancy).where(
                    Vacancy.title == vacancy_data['title']
                )
            )
            
            if existing:
                # Обновляем существующую вакансию
                existing.position = vacancy_data['position']
                existing.language = vacancy_data['language']
                existing.grade = vacancy_data['grade']
                existing.ideal_resume = vacancy_data['ideal_resume']
                updated_count += 1
                print(f'   Обновлена: {vacancy_data["title"]}')
            else:
                # Создаем новую вакансию
                vacancy = Vacancy(**vacancy_data)
                session.add(vacancy)
                created_count += 1
                print(f'   Создана: {vacancy_data["title"]}')
        
        await session.commit()
        print(f'\n✅ Вакансии обработаны:')
        print(f'   Создано: {created_count}')
        print(f'   Обновлено: {updated_count}')
        print(f'   Всего: {len(VACANCIES_DATA)}')


QUESTIONS_DATA = [
    # Общие вопросы для опроса
    {
        'text': 'Расскажите о своем опыте работы с базами данных. Какие СУБД вы использовали?',
        'question_type': 'text',
        'order': 1,
        'difficulty': 'medium',
        'vacancy_id': None,  # Общий вопрос для всех вакансий
    },
    {
        'text': 'Опишите ваш опыт работы с системами контроля версий (Git).',
        'question_type': 'text',
        'order': 2,
        'difficulty': 'easy',
        'vacancy_id': None,
    },
    {
        'text': 'Какой у вас опыт работы с Docker и контейнеризацией?',
        'question_type': 'text',
        'order': 3,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с REST API. Какие подходы к проектированию API вы используете?',
        'question_type': 'text',
        'order': 4,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Какой у вас опыт работы в команде? Опишите ваш подход к совместной разработке.',
        'question_type': 'text',
        'order': 5,
        'difficulty': 'easy',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с тестированием кода. Какие виды тестов вы писали?',
        'question_type': 'text',
        'order': 6,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Как вы подходите к решению сложных технических задач? Опишите ваш процесс.',
        'question_type': 'text',
        'order': 7,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с CI/CD системами.',
        'question_type': 'text',
        'order': 8,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Какой у вас опыт работы с мониторингом и логированием приложений?',
        'question_type': 'text',
        'order': 9,
        'difficulty': 'hard',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с микросервисной архитектурой.',
        'question_type': 'text',
        'order': 10,
        'difficulty': 'hard',
        'vacancy_id': None,
    },
    # Python-специфичные вопросы
    {
        'text': 'Опишите ваш опыт работы с Python. Какие фреймворки и библиотеки вы использовали?',
        'question_type': 'text',
        'order': 1,
        'difficulty': 'easy',
        'vacancy_id': None,  # Будет привязано к Python вакансиям
    },
    {
        'text': 'Какой у вас опыт работы с асинхронным программированием в Python (asyncio)?',
        'question_type': 'text',
        'order': 2,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с Django или FastAPI. Какие проекты вы разрабатывали?',
        'question_type': 'text',
        'order': 3,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    # TypeScript-специфичные вопросы
    {
        'text': 'Опишите ваш опыт работы с TypeScript. Какие проекты вы разрабатывали?',
        'question_type': 'text',
        'order': 1,
        'difficulty': 'easy',
        'vacancy_id': None,
    },
    {
        'text': 'Какой у вас опыт работы с React или Next.js?',
        'question_type': 'text',
        'order': 2,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    {
        'text': 'Опишите ваш опыт работы с Node.js и серверной разработкой на TypeScript.',
        'question_type': 'text',
        'order': 3,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    # Go-специфичные вопросы
    {
        'text': 'Опишите ваш опыт работы с Go. Какие проекты вы разрабатывали?',
        'question_type': 'text',
        'order': 1,
        'difficulty': 'easy',
        'vacancy_id': None,
    },
    {
        'text': 'Как вы используете goroutines и каналы в Go? Приведите примеры.',
        'question_type': 'text',
        'order': 2,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
    # Java-специфичные вопросы
    {
        'text': 'Опишите ваш опыт работы с Java. Какие фреймворки вы использовали?',
        'question_type': 'text',
        'order': 1,
        'difficulty': 'easy',
        'vacancy_id': None,
    },
    {
        'text': 'Какой у вас опыт работы со Spring Framework? Какие модули вы использовали?',
        'question_type': 'text',
        'order': 2,
        'difficulty': 'medium',
        'vacancy_id': None,
    },
]


async def create_questions():
    """Создает вопросы в базе данных"""
    async with async_session_factory() as session:
        created_count = 0
        updated_count = 0
        
        for question_data in QUESTIONS_DATA:
            # Проверяем, существует ли уже такой вопрос
            existing = await session.scalar(
                select(Question).where(
                    Question.text == question_data['text']
                )
            )
            
            if existing:
                # Обновляем существующий вопрос
                existing.question_type = question_data['question_type']
                existing.order = question_data['order']
                existing.difficulty = question_data['difficulty']
                existing.vacancy_id = question_data.get('vacancy_id')
                updated_count += 1
                print(f'   Обновлен: {question_data["text"][:50]}...')
            else:
                # Создаем новый вопрос
                question = Question(**question_data)
                session.add(question)
                created_count += 1
                print(f'   Создан: {question_data["text"][:50]}...')
        
        await session.commit()
        print(f'\n✅ Вопросы обработаны:')
        print(f'   Создано: {created_count}')
        print(f'   Обновлено: {updated_count}')
        print(f'   Всего: {len(QUESTIONS_DATA)}')


TASKS_DATA = [
    {
        'title': 'Сумма двух чисел',
        'description': '''Напишите функцию, которая принимает два целых числа и возвращает их сумму.

Входные данные:
- Два целых числа a и b (|a|, |b| <= 1000)

Выходные данные:
- Одно целое число - сумма a и b

Пример:
Вход: 5 3
Выход: 8''',
        'topic': 'Математика',
        'difficulty': 'easy',
        'open_tests': [
            {'input': '5 3', 'output': '8'},
            {'input': '-10 20', 'output': '10'},
            {'input': '0 0', 'output': '0'},
        ],
        'hidden_tests': [
            {'input': '1000 1000', 'output': '2000'},
            {'input': '-1000 -1000', 'output': '-2000'},
            {'input': '999 -999', 'output': '0'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Максимальный элемент массива',
        'description': '''Найдите максимальный элемент в массиве целых чисел.

Входные данные:
- Первая строка: целое число n (1 <= n <= 1000) - размер массива
- Вторая строка: n целых чисел через пробел (каждое число по модулю <= 10^6)

Выходные данные:
- Одно целое число - максимальный элемент массива

Пример:
Вход:
5
1 5 3 9 2
Выход: 9''',
        'topic': 'Массивы',
        'difficulty': 'easy',
        'open_tests': [
            {'input': '5\n1 5 3 9 2', 'output': '9'},
            {'input': '3\n-1 -5 -3', 'output': '-1'},
            {'input': '1\n42', 'output': '42'},
        ],
        'hidden_tests': [
            {'input': '1000\n' + ' '.join(str(i) for i in range(1000)), 'output': '999'},
            {'input': '10\n-1000000 1000000 -500000 0 500000', 'output': '1000000'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Проверка палиндрома',
        'description': '''Определите, является ли строка палиндромом (читается одинаково слева направо и справа налево).

Входные данные:
- Одна строка s (1 <= len(s) <= 1000), состоящая из строчных латинских букв

Выходные данные:
- Выведите "YES", если строка является палиндромом, и "NO" в противном случае

Пример:
Вход: radar
Выход: YES

Вход: hello
Выход: NO''',
        'topic': 'Строки',
        'difficulty': 'easy',
        'open_tests': [
            {'input': 'radar', 'output': 'YES'},
            {'input': 'hello', 'output': 'NO'},
            {'input': 'a', 'output': 'YES'},
        ],
        'hidden_tests': [
            {'input': 'racecar', 'output': 'YES'},
            {'input': 'python', 'output': 'NO'},
            {'input': 'a' * 1000, 'output': 'YES'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Поиск в отсортированном массиве',
        'description': '''Реализуйте бинарный поиск в отсортированном массиве.

Входные данные:
- Первая строка: целое число n (1 <= n <= 10^5) - размер массива
- Вторая строка: n целых чисел в порядке возрастания
- Третья строка: целое число target - искомое значение

Выходные данные:
- Индекс элемента target в массиве (0-indexed), или -1, если элемент не найден

Пример:
Вход:
5
1 3 5 7 9
5
Выход: 2''',
        'topic': 'Бинарный поиск',
        'difficulty': 'medium',
        'open_tests': [
            {'input': '5\n1 3 5 7 9\n5', 'output': '2'},
            {'input': '5\n1 3 5 7 9\n10', 'output': '-1'},
            {'input': '1\n5\n5', 'output': '0'},
        ],
        'hidden_tests': [
            {'input': '100000\n' + ' '.join(str(i) for i in range(100000)) + '\n50000', 'output': '50000'},
            {'input': '10\n1 2 3 4 5 6 7 8 9 10\n1', 'output': '0'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Две суммы',
        'description': '''Найдите два числа в массиве, сумма которых равна заданному значению.

Входные данные:
- Первая строка: целое число n (2 <= n <= 10^4) - размер массива
- Вторая строка: n целых чисел через пробел
- Третья строка: целое число target - целевая сумма

Выходные данные:
- Два индекса (0-indexed) через пробел, или "-1 -1", если таких чисел нет

Пример:
Вход:
4
2 7 11 15
9
Выход: 0 1''',
        'topic': 'Хеш-таблицы',
        'difficulty': 'medium',
        'open_tests': [
            {'input': '4\n2 7 11 15\n9', 'output': '0 1'},
            {'input': '3\n3 2 4\n6', 'output': '1 2'},
            {'input': '2\n3 3\n6', 'output': '0 1'},
        ],
        'hidden_tests': [
            {'input': '10000\n' + ' '.join(str(i) for i in range(10000)) + '\n19999', 'output': '9999 10000'},
            {'input': '5\n1 2 3 4 5\n10', 'output': '-1 -1'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Объединение интервалов',
        'description': '''Объедините перекрывающиеся интервалы.

Входные данные:
- Первая строка: целое число n (1 <= n <= 10^4) - количество интервалов
- Следующие n строк: по два целых числа через пробел - начало и конец интервала

Выходные данные:
- Объединенные интервалы, по одному на строку (начало и конец через пробел), отсортированные по началу

Пример:
Вход:
4
1 3
2 6
8 10
15 18
Выход:
1 6
8 10
15 18''',
        'topic': 'Интервалы',
        'difficulty': 'medium',
        'open_tests': [
            {'input': '4\n1 3\n2 6\n8 10\n15 18', 'output': '1 6\n8 10\n15 18'},
            {'input': '2\n1 4\n4 5', 'output': '1 5'},
            {'input': '1\n1 1', 'output': '1 1'},
        ],
        'hidden_tests': [
            {'input': '10000\n' + '\n'.join(f'{i} {i+1}' for i in range(10000)), 'output': '0 10001'},
            {'input': '3\n1 2\n3 4\n5 6', 'output': '1 2\n3 4\n5 6'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Медиана двух отсортированных массивов',
        'description': '''Найдите медиану двух отсортированных массивов.

Входные данные:
- Первая строка: целое число n (1 <= n <= 10^5) - размер первого массива
- Вторая строка: n целых чисел через пробел (отсортированы)
- Третья строка: целое число m (1 <= m <= 10^5) - размер второго массива
- Четвертая строка: m целых чисел через пробел (отсортированы)

Выходные данные:
- Медиана объединенных массивов (одно число с точностью до 1 знака после запятой, если нужно)

Пример:
Вход:
2
1 3
2
2 4
Выход: 2.5''',
        'topic': 'Бинарный поиск',
        'difficulty': 'hard',
        'open_tests': [
            {'input': '2\n1 3\n2\n2 4', 'output': '2.5'},
            {'input': '2\n1 2\n2\n3 4', 'output': '2.5'},
            {'input': '1\n1\n1\n2', 'output': '1.5'},
        ],
        'hidden_tests': [
            {'input': '100000\n' + ' '.join(str(i*2) for i in range(100000)) + '\n100000\n' + ' '.join(str(i*2+1) for i in range(100000)), 'output': '99999.5'},
            {'input': '1\n1\n1\n1', 'output': '1.0'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Наибольшая общая подпоследовательность',
        'description': '''Найдите длину наибольшей общей подпоследовательности (LCS) двух строк.

Входные данные:
- Первая строка: строка s1 (1 <= len(s1) <= 1000)
- Вторая строка: строка s2 (1 <= len(s2) <= 1000)

Выходные данные:
- Одно целое число - длина LCS

Пример:
Вход:
ABCDGH
AEDFHR
Выход: 3''',
        'topic': 'Динамическое программирование',
        'difficulty': 'hard',
        'open_tests': [
            {'input': 'ABCDGH\nAEDFHR', 'output': '3'},
            {'input': 'AGGTAB\nGXTXAYB', 'output': '4'},
            {'input': 'abc\nabc', 'output': '3'},
        ],
        'hidden_tests': [
            {'input': 'A' * 1000 + '\n' + 'A' * 1000, 'output': '1000'},
            {'input': 'ABCDEF\nGHIJKL', 'output': '0'},
        ],
        'vacancy_id': None,
    },
    {
        'title': 'Валидация скобок',
        'description': '''Проверьте, правильно ли расставлены скобки в строке.

Входные данные:
- Одна строка s (1 <= len(s) <= 10^4), содержащая только символы '(', ')', '[', ']', '{', '}'

Выходные данные:
- Выведите "YES", если скобки расставлены правильно, и "NO" в противном случае

Пример:
Вход: ()[]{}
Выход: YES

Вход: ([)]
Выход: NO''',
        'topic': 'Стеки',
        'difficulty': 'medium',
        'open_tests': [
            {'input': '()[]{}', 'output': 'YES'},
            {'input': '([)]', 'output': 'NO'},
            {'input': '({[]})', 'output': 'YES'},
        ],
        'hidden_tests': [
            {'input': '(' * 5000 + ')' * 5000, 'output': 'YES'},
            {'input': '([{', 'output': 'NO'},
            {'input': '', 'output': 'YES'},
        ],
        'vacancy_id': None,
    },
]


async def create_tasks():
    """Создает задачи в базе данных"""
    async with async_session_factory() as session:
        created_count = 0
        updated_count = 0
        
        for task_data in TASKS_DATA:
            # Проверяем, существует ли уже такая задача
            existing = await session.scalar(
                select(Task).where(Task.title == task_data['title'])
            )
            
            if existing:
                # Обновляем существующую задачу
                existing.description = task_data['description']
                existing.topic = task_data['topic']
                existing.difficulty = task_data['difficulty']
                existing.open_tests = json.dumps(task_data['open_tests'])
                existing.hidden_tests = json.dumps(task_data['hidden_tests'])
                existing.vacancy_id = task_data.get('vacancy_id')
                updated_count += 1
                print(f'   Обновлена: {task_data["title"]}')
            else:
                # Создаем новую задачу
                task = Task(
                    title=task_data['title'],
                    description=task_data['description'],
                    topic=task_data['topic'],
                    difficulty=task_data['difficulty'],
                    open_tests=json.dumps(task_data['open_tests']),
                    hidden_tests=json.dumps(task_data['hidden_tests']),
                    vacancy_id=task_data.get('vacancy_id'),
                )
                session.add(task)
                created_count += 1
                print(f'   Создана: {task_data["title"]}')
        
        await session.commit()
        print(f'\n✅ Задачи обработаны:')
        print(f'   Создано: {created_count}')
        print(f'   Обновлено: {updated_count}')
        print(f'   Всего: {len(TASKS_DATA)}')


async def main():
    """Основная функция"""
    print('🚀 Инициализация данных...\n')
    
    try:
        await create_admin_user()
        print()
        await create_vacancies()
        print()
        await create_questions()
        print()
        await create_tasks()
        print('\n✅ Инициализация завершена успешно!')
    except Exception as e:
        print(f'\n❌ Ошибка при инициализации: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

