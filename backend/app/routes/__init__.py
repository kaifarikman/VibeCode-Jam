from .admin import router as admin_router
from .auth import router as auth_router
from .executions import router as executions_router
from .questions import router as questions_router
from .tasks import router as tasks_router
from .users import router as users_router
from .vacancies import router as vacancies_router
from .hints import router as hints_router

__all__ = ['auth_router', 'users_router', 'admin_router', 'questions_router', 'tasks_router', 'executions_router', 'vacancies_router', 'hints_router']
