"""
test_tasks.py — Unit & Integration Tests with pytest

Concepts covered:
- pytest fixtures for setup/teardown
- FastAPI TestClient for API testing
- In-memory SQLite DB for isolated tests
- Testing auth flows (register → login → use token)
- Asserting HTTP status codes and response bodies
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use SQLite in-memory DB for tests (no PostgreSQL needed)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the real DB dependency with the test DB."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override FastAPI's get_db with test db
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Registers a user and returns their JWT token."""
    client.post("/api/users/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "secret123"
    })
    response = client.post("/api/users/login", data={
        "username": "testuser",
        "password": "secret123"
    })
    return response.json()["access_token"]


# ── Tests ─────────────────────────────────────────────

def test_health_check(client):
    """Health check returns 200 and healthy status."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_register_user(client):
    """User registration returns 201 with user data."""
    res = client.post("/api/users/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "password123"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "newuser"
    assert "hashed_password" not in data  # password must never be returned!


def test_register_duplicate_email(client):
    """Duplicate email registration should return 400."""
    payload = {"email": "dup@example.com", "username": "user1", "password": "pass"}
    client.post("/api/users/register", json=payload)
    payload["username"] = "user2"
    res = client.post("/api/users/register", json=payload)
    assert res.status_code == 400


def test_login_success(client):
    """Valid credentials return a JWT token."""
    client.post("/api/users/register", json={
        "email": "u@test.com", "username": "loginuser", "password": "mypass"
    })
    res = client.post("/api/users/login", data={
        "username": "loginuser", "password": "mypass"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    """Wrong password returns 401."""
    client.post("/api/users/register", json={
        "email": "u@test.com", "username": "myuser", "password": "correct"
    })
    res = client.post("/api/users/login", data={
        "username": "myuser", "password": "wrong"
    })
    assert res.status_code == 401


def test_create_task(client, auth_token):
    """Authenticated user can create a task."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = client.post("/api/tasks/", json={
        "title": "Write unit tests",
        "description": "Cover all endpoints",
        "priority": "high"
    }, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Write unit tests"
    assert data["status"] == "todo"


def test_list_tasks(client, auth_token):
    """Authenticated user can list their tasks."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/api/tasks/", json={"title": "Task 1"}, headers=headers)
    client.post("/api/tasks/", json={"title": "Task 2"}, headers=headers)

    res = client.get("/api/tasks/", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2


def test_update_task_status(client, auth_token):
    """Updating a task to DONE sets completed_at."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    task = client.post("/api/tasks/", json={"title": "Finish me"}, headers=headers).json()

    res = client.put(f"/api/tasks/{task['id']}", json={"status": "done"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "done"
    assert res.json()["completed_at"] is not None


def test_unauthorized_access(client):
    """Accessing protected endpoint without token returns 401."""
    res = client.get("/api/tasks/")
    assert res.status_code == 401


def test_task_stats(client, auth_token):
    """Stats endpoint returns correct counts per status."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    client.post("/api/tasks/", json={"title": "T1"}, headers=headers)
    task = client.post("/api/tasks/", json={"title": "T2"}, headers=headers).json()
    client.put(f"/api/tasks/{task['id']}", json={"status": "done"}, headers=headers)

    res = client.get("/api/tasks/stats/summary", headers=headers)
    assert res.status_code == 200
    stats = res.json()
    assert stats["todo"] == 1
    assert stats["done"] == 1
    assert stats["total"] == 2
