"""
main.py — FastAPI Application Entry Point

Concepts covered:
- FastAPI app setup with CORS middleware
- Router registration (modular architecture like TurboGears controllers)
- Database table auto-creation on startup
- Background scheduler startup with lifespan
- Interactive API docs at /docs (Swagger UI)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from . import models
from .routers import users, tasks
from .scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — runs startup and shutdown logic.
    
    On Startup:
    - Creates all DB tables (models → PostgreSQL tables)
    - Starts background scheduler
    
    On Shutdown:
    - Scheduler stops gracefully
    """
    # ── Startup ──────────────────────────────────────
    print("🚀 Starting Task Manager API...")
    
    # Auto-create tables from SQLAlchemy models
    # In production, use Alembic migrations instead
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")
    
    # Start background scheduler
    scheduler = start_scheduler()
    
    yield  # App is running here
    
    # ── Shutdown ─────────────────────────────────────
    scheduler.shutdown()
    print("👋 Shutting down...")


# ── FastAPI App Instance ──────────────────────────────
app = FastAPI(
    title="Task Manager Pro API",
    description="""
    ## Full-Stack Python Sample Project
    
    Demonstrates senior Python developer skills:
    - 🔐 JWT Authentication
    - 📋 CRUD Operations
    - 🗄️ PostgreSQL with SQLAlchemy ORM
    - ⏰ Background Jobs
    - 🐳 Docker-ready
    """,
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS Middleware ───────────────────────────────────
# Allows the React frontend (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins completely
    allow_credentials=False,  # We use Bearer tokens, so we don't need cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──────────────────────────────────
# Like TurboGears controllers — each router handles a domain
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint — useful for Docker/AWS load balancer probes."""
    return {
        "status": "healthy",
        "app": "Task Manager Pro",
        "version": "1.0.0",
        "docs": "/docs"
    }
