"""
database.py — PostgreSQL connection using SQLAlchemy ORM

Concepts covered:
- Environment-based configuration (12-factor app pattern)
- SQLAlchemy engine + session management
- Dependency injection pattern for FastAPI (get_db)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings loaded from environment variables / .env file.
    
    Cloud Deployment Note:
    - On AWS: set these as RDS connection strings in ECS Task Definitions
    - On Azure: set them in App Service Configuration > Application Settings
    """
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/taskdb"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()

# Create the DB engine — psycopg2 driver connects to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Each request gets its own DB session (thread-safe)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, then closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
