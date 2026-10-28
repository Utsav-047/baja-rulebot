# ==============================================================================
# BAJA RuleBot - Production Multi-Stage Dockerfile
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for optimized Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY backend/ /app/backend/

# Copy frontend static files
COPY frontend/ /app/frontend/

# Ensure runtime directories exist
RUN mkdir -p /app/backend/uploads /app/backend/chroma_db

# Expose FastAPI application port
EXPOSE 8000

# Set working directory to backend for seamless relative path resolution
WORKDIR /app/backend

# Default execution command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
