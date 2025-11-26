import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_admin: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True


class DashboardSnapshot(BaseModel):
    last_executor_status: str
    pending_jobs: int
    last_language: str
    recent_actions: list[str]


