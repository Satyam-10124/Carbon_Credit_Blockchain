# Optimized Dockerfile for Railway - API only, no heavy packages
FROM python:3.12-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt requirements_postgres.txt ./

# Install minimal Python packages (API only, no MediaPipe/OpenCV)
RUN pip install --no-cache-dir \
    fastapi==0.115.6 \
    uvicorn[standard]==0.30.0 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.9 \
    openai \
    py-algorand-sdk \
    python-dotenv \
    requests \
    python-multipart \
    && pip install --no-cache-dir -r requirements_postgres.txt || true

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /tmp/joyo_uploads && chmod 777 /tmp/joyo_uploads

# Expose port
EXPOSE 8000

# Use startup script
CMD ["/app/start.sh"]
