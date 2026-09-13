
celery -A your_project_name.celery worker --loglevel=info --concurrency=1 &

uvicorn your_project_name.main:app --host 0.0.0.0 --port $PORT