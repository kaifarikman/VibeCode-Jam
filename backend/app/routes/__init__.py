from .admin import router as admin_router
from .auth import router as auth_router
from .questions import router as questions_router
from .users import router as users_router

__all__ = ['auth_router', 'users_router', 'admin_router', 'questions_router']
