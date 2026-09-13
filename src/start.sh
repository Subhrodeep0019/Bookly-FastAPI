#!/usr/bin/env bash

# Ensure the current directory is in the Python path
export PYTHONPATH=.

# Run Celery pointing to src.celery_task:c_app (no .py)
celery -A src.celery_task:c_app worker --loglevel=info --concurrency=1 &

# Run Uvicorn pointing to the file inside src containing your FastAPI app
# Replace 'main' with your actual filename if it is not main.py (e.g., src.app:app)
uvicorn src.main:app --host 0.0.0.0 --port $PORT
