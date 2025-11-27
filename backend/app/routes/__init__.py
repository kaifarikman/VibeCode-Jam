from .admin import router as admin_router
from .auth import router as auth_router
from .executions import router as executions_router
from .questions import router as questions_router
from .tasks import router as tasks_router
from .users import router as users_router
from .vacancies import router as vacancies_router
from .hints import router as hints_router
from .scoring import router as scoring_router
from .moderator import router as moderator_router
from .moderator_auth import router as moderator_auth_router

__all__ = ['auth_router', 'users_router', 'admin_router', 'questions_router', 'tasks_router', 'executions_router', 'vacancies_router', 'hints_router', 'scoring_router', 'moderator_router', 'moderator_auth_router']
