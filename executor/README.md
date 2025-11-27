# Executor Service

Микросервис для выполнения пользовательского кода в изолированных Docker контейнерах.

## Запуск

```bash
cd executor
python3 -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate на Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Переменные окружения

- `BACKEND_URL` - URL основного backend API (по умолчанию: http://localhost:8000/api)

## API

- `POST /execute` - Принять задачу на выполнение (асинхронно)
- `GET /health` - Проверка здоровья сервиса

## Поддерживаемые языки

- Python 3.12
- TypeScript (Node.js 20)
- Go 1.23
- Java 21

