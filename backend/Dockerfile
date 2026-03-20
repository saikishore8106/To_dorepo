# ── Backend Dockerfile ────────────────────────────────
# Multi-stage build concept:
# Stage 1: Install dependencies
# Stage 2: Copy app code (keeps image lean)

FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy and install dependencies first (Docker layer caching optimization)
# If requirements.txt hasn't changed, Docker reuses cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose port 8001 for the FastAPI server
EXPOSE 8001

# Start the FastAPI app with uvicorn
# --host 0.0.0.0 makes it accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
