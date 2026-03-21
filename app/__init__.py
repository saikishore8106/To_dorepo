"""Top-level package shim for the FastAPI app.

The test suite expects to import ``app.main`` directly from the project root.
In the source layout the actual application lives under ``backend/app``.
This shim makes ``import app`` resolve correctly without altering the existing package structure.
"""

# Re-export the FastAPI ``app`` instance for compatibility with tests.
from backend.app.main import app  # noqa: F401

__all__ = ["app"]
