from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .database import engine
from .models import Base
from .routes import admin_router, auth_router, executions_router, questions_router, tasks_router, users_router, vacancies_router


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
    expose_headers=['*'],
)


# Миграции выполняются через Alembic
# Для разработки можно раскомментировать строки ниже для автоматического создания таблиц
# @app.on_event('startup')
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


@app.get('/health', tags=['health'])
async def health():
    return {'status': 'ok'}


api_router = APIRouter(prefix=settings.api_v1_str)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(questions_router)
api_router.include_router(tasks_router)
api_router.include_router(admin_router)
api_router.include_router(executions_router)
api_router.include_router(vacancies_router)

app.include_router(api_router)

