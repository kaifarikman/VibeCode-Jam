# Backend (FastAPI)

> 📖 **Полная документация:** см. [главный README.md](../README.md)

## Быстрый старт

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env
cd app
python -m alembic upgrade head
cd ..
uvicorn app.main:app --reload

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
cd app
python -m alembic upgrade head
cd ..
uvicorn app.main:app --reload
```

## Структура

```
app/
  alembic/     # Миграции базы данных
  core/        # Конфигурация, безопасность
  models/      # SQLAlchemy модели
  routes/      # API роуты
  services/    # Бизнес-логика, CRUD
  schemas/     # Pydantic схемы
```

## Технологии

- FastAPI + Pydantic Settings
- SQLAlchemy (async) + PostgreSQL
- Alembic (миграции)
- aiosmtplib (Mailhog)
- JWT токены (python-jose)
