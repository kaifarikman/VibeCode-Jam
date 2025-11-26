# Архитектура проекта VibeCode Jam IDE

## 📐 Общая архитектура

Проект построен по принципу **клиент-серверной архитектуры** с разделением на frontend и backend компоненты.

```
┌─────────────────┐         HTTP/REST API         ┌─────────────────┐
│                 │ ◄─────────────────────────────► │                 │
│   Frontend      │         JWT Authentication      │    Backend      │
│   (React)       │                                 │   (FastAPI)     │
│   Port: 5173    │                                 │   Port: 8000    │
└─────────────────┘                                 └─────────────────┘
                                                             │
                                                             │
                    ┌────────────────────────────────────────┼────────────┐
                    │                                        │            │
                    ▼                                        ▼            ▼
            ┌──────────────┐                      ┌──────────────┐  ┌──────────────┐
            │  PostgreSQL  │                      │   Mailhog    │  │   Alembic    │
            │  Port: 5432  │                      │  Port: 8025   │  │  Migrations  │
            └──────────────┘                      └──────────────┘  └──────────────┘
```

### Тип архитектуры

- **Монолитная архитектура** (backend) с четким разделением слоев
- **SPA (Single Page Application)** на frontend
- **RESTful API** для взаимодействия между компонентами

---

## 🛠️ Технологический стек

### Backend

| Категория | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| **Framework** | FastAPI | 0.115.5 | Асинхронный веб-фреймворк |
| **ASGI Server** | Uvicorn | 0.32.1 | Высокопроизводительный ASGI сервер |
| **ORM** | SQLAlchemy | 2.0.44 | Асинхронный ORM для работы с БД |
| **Database Driver** | asyncpg | 0.30.0 | Асинхронный драйвер для PostgreSQL |
| **Database** | PostgreSQL | 16-alpine | Реляционная БД |
| **Migrations** | Alembic | 1.14.0 | Управление миграциями БД |
| **Validation** | Pydantic | 2.12.4 | Валидация данных и настройки |
| **Authentication** | python-jose | 3.3.0 | JWT токены |
| **Email** | aiosmtplib | 3.0.1 | Асинхронная отправка email |
| **Language** | Python | 3.11+ | Основной язык программирования |

### Frontend

| Категория | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| **Framework** | React | 19.2.0 | UI библиотека |
| **Language** | TypeScript | 5.9.3 | Типизированный JavaScript |
| **Build Tool** | Vite | 7.2.4 | Быстрый сборщик и dev-сервер |
| **Editor** | Monaco Editor | 0.52.2 | Код-редактор (VS Code в браузере) |
| **State Management** | React Hooks | - | Встроенное управление состоянием |

### Инфраструктура

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| **Containerization** | Docker & Docker Compose | Оркестрация сервисов |
| **Database** | PostgreSQL 16 | Хранение данных |
| **Email Testing** | Mailhog | Тестовая SMTP-служба |
| **Migrations** | Alembic | Версионирование схемы БД |

---

## 📁 Структура проекта

### Backend (FastAPI)

```
backend/
├── app/
│   ├── alembic/              # Миграции базы данных
│   │   ├── versions/         # Файлы миграций
│   │   └── env.py            # Конфигурация Alembic
│   ├── core/                 # Ядро приложения
│   │   ├── config.py         # Настройки (Pydantic Settings)
│   │   └── security.py       # JWT, хеширование
│   ├── dependencies/         # FastAPI зависимости
│   │   ├── auth.py           # get_current_user
│   │   └── admin.py          # get_admin_user
│   ├── models/               # SQLAlchemy модели
│   │   ├── base.py           # Базовый класс
│   │   ├── user.py           # User модель
│   │   ├── login_code.py     # LoginCode модель
│   │   └── question.py        # Question, Answer модели
│   ├── routes/               # API эндпоинты
│   │   ├── auth.py           # /api/auth/*
│   │   ├── users.py          # /api/users/*
│   │   ├── questions.py      # /api/questions/*
│   │   └── admin.py          # /api/admin/*
│   ├── schemas/              # Pydantic схемы
│   │   ├── auth.py           # Схемы авторизации
│   │   ├── user.py           # Схемы пользователя
│   │   ├── question.py       # Схемы вопросов
│   │   └── answer.py         # Схемы ответов
│   ├── services/             # Бизнес-логика
│   │   ├── auth.py           # Логика авторизации
│   │   ├── email.py          # Отправка email
│   │   └── crud.py           # CRUD операции
│   ├── database.py           # Подключение к БД
│   └── main.py               # Точка входа FastAPI
├── requirements.txt          # Python зависимости
├── env.example               # Пример конфигурации
└── pyproject.toml           # Метаданные проекта
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/           # React компоненты
│   │   └── AdminPanel.tsx   # Админ-панель
│   ├── modules/             # Модули приложения
│   │   ├── auth/            # Авторизация
│   │   │   ├── api.ts       # API функции
│   │   │   └── types.ts     # TypeScript типы
│   │   ├── questions/       # Вопросы и ответы
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── admin/           # Админ-функции
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── ide/             # IDE функционал
│   │       └── sampleWorkspace.ts
│   ├── App.tsx              # Главный компонент
│   ├── App.css              # Стили
│   └── main.tsx             # Точка входа
├── package.json             # Node.js зависимости
└── env.example              # Пример конфигурации
```

---

## 🏗️ Архитектурные паттерны

### 1. Layered Architecture (Слоистая архитектура)

Backend организован в четкие слои:

```
┌─────────────────────────────────────┐
│         Routes Layer                │  ← API эндпоинты (тонкий слой)
├─────────────────────────────────────┤
│         Services Layer              │  ← Бизнес-логика, CRUD
├─────────────────────────────────────┤
│         Models Layer                │  ← SQLAlchemy модели
├─────────────────────────────────────┤
│         Database Layer              │  ← PostgreSQL
└─────────────────────────────────────┘
```

**Принципы:**
- **Routes** — тонкий слой, только валидация и маршрутизация
- **Services** — вся бизнес-логика и CRUD операции
- **Models** — только структура данных, без логики
- **Dependencies** — переиспользуемые зависимости (auth, admin)

### 2. Dependency Injection

FastAPI использует встроенную систему dependency injection:

```python
# Пример из routes/questions.py
async def create_answer(
    question_id: UUID,
    answer_data: AnswerCreate,
    session: AsyncSession = Depends(get_session),      # DI
    current_user: User = Depends(get_current_user),    # DI
):
    # Логика обработки
```

**Преимущества:**
- Легкое тестирование (можно мокировать зависимости)
- Переиспользование кода
- Четкое разделение ответственности

### 3. Repository Pattern (через Services)

CRUD операции вынесены в отдельный сервис `services/crud.py`:

```python
# Тривиальные CRUD операции
async def list_questions(session: AsyncSession) -> list[Question]:
    """Получить все вопросы"""
    result = await session.scalars(
        select(Question).order_by(Question.order, Question.created_at)
    )
    return list(result.all())
```

**Преимущества:**
- Централизация доступа к данным
- Легкая замена реализации
- Упрощение тестирования

### 4. Schema Validation (Pydantic)

Двухуровневая валидация:
1. **Request validation** — на уровне FastAPI (Pydantic schemas)
2. **Database constraints** — на уровне PostgreSQL

```python
# Пример схемы
class AnswerCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    question_id: uuid.UUID | None = None
```

---

## 🔄 Потоки данных

### Авторизация пользователя

```
┌──────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│          │ 1.POST │          │ 2.Save │          │ 3.Code │          │
│ Frontend │ /auth/ │ Backend  │ user + │ Database │ stored │ Mailhog   │
│          │ register──────────►        │──────────►        │──────────►│
│          │ (email+password)  │        │        ▲         │ sends     │
│          │                   │        │        │         │ e-mail    │
│          │◄──── 4.202 Accepted        │        │         │           │
│          │                           │        │         │           │
│          │ 5.POST /auth/verify       │        │         │           │
│          │ ──────────────────────────►        │ updates │           │
│          │ (code)                     │        │ is_verified       │
│          │◄───── 6.OK                │        │         │           │
│          │                           │        │         │           │
│          │ 7.POST /auth/login        │        │         │           │
│          │ (email+password)─────────►│        │         │           │
│          │◄── 8.JWT Token            │        │         │           │
└──────────┘        └──────────┘        └──────────┘        └──────────┘
```

> Код подтверждает только email при регистрации. Все последующие входы выполняются по e-mail + пароль, JWT выдаётся только после успешного логина.

### Создание ответа на вопрос

```
Frontend → POST /api/questions/{id}/answers
         ↓
    [JWT Auth] → get_current_user dependency
         ↓
    [Validation] → AnswerCreate schema
         ↓
    [Service] → crud.create_or_update_answer
         ↓
    [Database] → INSERT/UPDATE answers
         ↓
    [Response] → AnswerRead schema
         ↓
Frontend ← 201 Created
```

---

## 🔐 Безопасность

### 1. Аутентификация

- **JWT токены** (JSON Web Tokens)
- **OAuth2 Password Bearer** схема
- Токены хранятся в `localStorage` на клиенте
- Срок действия: 60 минут (настраивается)

### 2. Авторизация

- **Role-based access control (RBAC)**
- Поле `is_admin` в модели User
- Dependency `get_admin_user` для защищенных эндпоинтов

### 3. Валидация данных

- **Pydantic** на уровне API
- **SQL constraints** на уровне БД
- **Email validation** через `email-validator`

### 4. Защита от SQL Injection

- **SQLAlchemy ORM** — параметризованные запросы
- **AsyncPG** — безопасные prepared statements

### 5. CORS

Настроен только для development:
```python
allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173']
```

---

## 📊 Модель данных

### ER-диаграмма

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    User      │         │   Question   │         │    Answer    │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ email (UQ)   │         │ text (UQ)    │         │ user_id (FK) │
│ full_name    │         │ order        │         │ question_id   │
│ is_admin     │         │ created_at   │         │   (FK)       │
│ created_at   │         │ updated_at   │         │ text         │
│ last_login_at│         └──────────────┘         │ created_at   │
└──────────────┘                 │               │ updated_at   │
       │                          │               └──────────────┘
       │                          │                      │
       │                          └──────────────────────┘
       │
       │
┌──────────────┐
│  LoginCode   │
├──────────────┤
│ id (PK)      │
│ user_id (FK) │
│ code_hash    │
│ expires_at   │
│ consumed_at  │
│ created_at   │
└──────────────┘
```

### Связи

- `User` 1:N `LoginCode` (cascade delete)
- `User` 1:N `Answer` (cascade delete)
- `Question` 1:N `Answer` (cascade delete)

---

## 🚀 Производительность и масштабируемость

### Backend оптимизации

1. **Асинхронность**
   - Async SQLAlchemy
   - AsyncPG драйвер
   - Async FastAPI endpoints

2. **Connection Pooling**
   ```python
   pool_size=10
   max_overflow=20
   pool_recycle=3600
   pool_pre_ping=True
   ```

3. **Lazy Loading**
   - Использование `selectinload` для eager loading где нужно
   - Избежание N+1 проблем

### Frontend оптимизации

1. **Code Splitting** (Vite автоматически)
2. **React 19 Compiler** — оптимизация рендеринга
3. **Monaco Editor** — загрузка только нужных языков

### Масштабируемость

**Горизонтальное масштабирование:**
- Stateless backend (JWT токены)
- Можно запускать несколько инстансов FastAPI
- Load balancer перед инстансами

**Вертикальное масштабирование:**
- Увеличение connection pool
- Оптимизация запросов к БД
- Кэширование (Redis) для частых запросов

---

## 🔧 Развертывание

### Development

```
docker compose up -d          # PostgreSQL + Mailhog
uvicorn app.main:app --reload # Backend (hot reload)
npm run dev                    # Frontend (hot reload)
```

### Production (рекомендации)

1. **Backend:**
   - Gunicorn + Uvicorn workers
   - Nginx как reverse proxy
   - HTTPS через Let's Encrypt

2. **Frontend:**
   - `npm run build` → статические файлы
   - Раздача через Nginx или CDN

3. **Database:**
   - Репликация для высокой доступности
   - Регулярные бэкапы

4. **Monitoring:**
   - Логирование (структурированные логи)
   - Метрики (Prometheus)
   - Трейсинг (OpenTelemetry)

---

## 📈 Метрики и мониторинг

### Рекомендуемые метрики

- **API Response Time** — время ответа эндпоинтов
- **Database Query Time** — время выполнения запросов
- **Error Rate** — процент ошибок
- **Active Users** — количество активных пользователей
- **Email Delivery Rate** — процент доставленных писем

---

## 🎯 Ключевые решения

### Почему FastAPI?

- ✅ Высокая производительность (асинхронность)
- ✅ Автоматическая документация (OpenAPI/Swagger)
- ✅ Type hints и валидация (Pydantic)
- ✅ Современный Python (3.11+)

### Почему React 19?

- ✅ React Compiler — автоматическая оптимизация
- ✅ Современные хуки и паттерны
- ✅ Большое сообщество и экосистема

### Почему PostgreSQL?

- ✅ Надежность и ACID
- ✅ Богатые возможности (JSON, Full-text search)
- ✅ Отличная производительность
- ✅ Open source

### Почему Alembic?

- ✅ Версионирование схемы БД
- ✅ Откат миграций
- ✅ Автогенерация миграций
- ✅ Стандарт для SQLAlchemy

---

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [React 19 Documentation](https://react.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Версия документа:** 1.0  
**Последнее обновление:** 2025-11-26

