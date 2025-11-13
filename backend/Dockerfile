# backend/Dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and setup files
COPY pyproject.toml .
# Optional: copy README if referenced
# COPY README.md .

# Install the package (this pulls all deps from pyproject.toml)
RUN pip install --no-cache-dir -e .

# Create uploads dir
RUN mkdir -p uploads

# Copy backend code
COPY backend/app ./backend/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Pre-download BLIP model on first container start
COPY backend/download_model.py ./download_model.py
RUN python download_model.py

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]