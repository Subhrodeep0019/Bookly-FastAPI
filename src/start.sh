
celery -A celery_task.c_app worker --loglevel=info --concurrency=1 &

uvicorn src:app --host 0.0.0.0 --port $PORT