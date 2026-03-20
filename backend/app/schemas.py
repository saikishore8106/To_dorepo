"""
schemas.py — Pydantic models for request/response validation

Concepts covered:
- Data validation with Pydantic v2
- Separation of input (Create) vs output (Response) schemas
- ORM mode for serializing SQLAlchemy objects
- Email validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from .models import TaskStatus, TaskPriority


# ─────────────────────────────────────────────
# Auth Schemas
# ─────────────────────────────────────────────

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload extracted from the JWT token"""
    username: Optional[str] = None


# ─────────────────────────────────────────────
# User Schemas
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for registering a new user — input validation"""
    email: EmailStr           # Validates email format automatically
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Custom validator: username must be alphanumeric"""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.lower()


class UserResponse(BaseModel):
    """Schema for user data returned in API responses (no password!)"""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # ORM mode: read from SQLAlchemy model


# ─────────────────────────────────────────────
# Task Schemas
# ─────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()


class TaskUpdate(BaseModel):
    """Schema for updating a task — all fields are optional (PATCH semantics)"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task data returned in API responses"""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Paginated task list response"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
