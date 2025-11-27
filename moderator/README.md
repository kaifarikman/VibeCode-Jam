# Moderator Service

Микросервис для модерации заявок кандидатов.

## Запуск

```bash
cd moderator
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

## Переменные окружения

Создайте файл `.env`:

```env
BACKEND_URL=http://localhost:8000/api
MODERATOR_TOKEN=your_secret_token_here
```

## API

- `POST /auth` - Авторизация модератора
- `GET /applications?moderator_token=...` - Список заявок для модерации
- `GET /applications/{application_id}?moderator_token=...` - Детали заявки
- `POST /applications/{application_id}/decide?moderator_token=...` - Принять/отклонить заявку

