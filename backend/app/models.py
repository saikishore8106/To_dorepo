"""
models.py — SQLAlchemy ORM Models (maps Python classes → PostgreSQL tables)

Concepts covered:
- OOP: Classes represent database tables
- Relationships: One user has many tasks (one-to-many)
- PostgreSQL data types in SQLAlchemy
- Enum type for task priority/status
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from .database import Base


class TaskPriority(str, enum.Enum):
    """Enum for task priority levels — Python enum + PostgreSQL ENUM type"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, enum.Enum):
    """Enum for task lifecycle status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class User(Base):
    """
    User model — maps to 'users' table in PostgreSQL.
    
    OOP Concepts:
    - Class attributes = table columns
    - `relationship` = SQLAlchemy join shortcut (no manual JOINs needed)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many: One user → many tasks
    # `back_populates` creates a reverse link on Task.owner
    tasks = relationship("Task", back_populates="owner", cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Task(Base):
    """
    Task model — maps to 'tasks' table in PostgreSQL.
    
    Database Design:
    - ForeignKey creates a DB-level constraint (ensures referential integrity)
    - Index on user_id speeds up "get all tasks for user" queries
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    # Many-to-one: many tasks → one user
    owner = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
