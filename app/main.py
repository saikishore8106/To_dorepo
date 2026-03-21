"""Compatibility wrapper for tests.

Imports the FastAPI ``app`` instance from the real location so that
``from app.main import app`` works as expected.
"""

from backend.app.main import app  # noqa: F401

__all__ = ["app"]
