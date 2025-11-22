#!/bin/sh
# Railway startup script - uses dynamic PORT from environment

# Use Railway's PORT or default to 8000
PORT=${PORT:-8000}

echo "Starting API on port $PORT..."

exec gunicorn api_joyo_core:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind "0.0.0.0:$PORT" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
