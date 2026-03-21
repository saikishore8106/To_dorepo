"""
routers/tasks.py — Task CRUD endpoints (Create, Read, Update, Delete)

Concepts covered:
- Full CRUD with RESTful HTTP methods (GET, POST, PUT, DELETE)
- Protected routes using JWT (Depends(get_current_user))
- Query filtering and pagination (SQL concepts)
- Proper HTTP status codes
- Error handling (404 Not Found, 403 Forbidden)
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("/", response_model=schemas.TaskListResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status_filter: Optional[models.TaskStatus] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/tasks/?page=1&page_size=10&status_filter=todo
    
    List all tasks for the current user with pagination and filtering.
    
    SQL equivalent:
        SELECT * FROM tasks WHERE user_id = :id AND status = :status
        LIMIT :page_size OFFSET :offset
    """
    query = db.query(models.Task).filter(models.Task.user_id == current_user.id)

    # Optional filtering by status
    if status_filter:
        query = query.filter(models.Task.status == status_filter)

    total = query.count()
    tasks = query.order_by(models.Task.created_at.desc()) \
                 .offset((page - 1) * page_size) \
                 .limit(page_size) \
                 .all()

    return {
        "tasks": tasks,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/", response_model=schemas.TaskResponse, status_code=201)
def create_task(
    task_data: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /api/tasks/
    
    Create a new task for the current user.
    """
    new_task = models.Task(
        **task_data.model_dump(),
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/tasks/{task_id}
    
    Get a specific task by ID.
    - 404 if task not found
    - 403 if task belongs to another user (authorization check)
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return task


@router.put("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT /api/tasks/{task_id}
    
    Update a task. Supports partial updates (only provided fields are changed).
    Auto-sets completed_at when status changes to DONE.
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    # Apply only the fields that were provided (partial update)
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Auto-timestamp when a task is completed
    if task_data.status == models.TaskStatus.DONE and not task.completed_at:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE /api/tasks/{task_id}
    
    Delete a task. Returns 204 No Content on success.
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or access denied")

    db.delete(task)
    db.commit()


@router.get("/stats/summary")
def task_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/tasks/stats/summary
    
    Aggregated task stats using SQL GROUP BY.
    
    SQL equivalent:
        SELECT status, COUNT(*) FROM tasks WHERE user_id = :id GROUP BY status
    """
    results = db.query(
        models.Task.status,
        func.count(models.Task.id).label("count")
    ).filter(
        models.Task.user_id == current_user.id
    ).group_by(models.Task.status).all()

    stats = {row.status.value: row.count for row in results}
    return {
        "todo": stats.get("todo", 0),
        "in_progress": stats.get("in_progress", 0),
        "done": stats.get("done", 0),
        "total": sum(stats.values())
    }
