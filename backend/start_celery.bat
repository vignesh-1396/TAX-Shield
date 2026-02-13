# Celery Worker Startup Script
# Run this to start the Celery worker for background task processing

celery -A app.core.celery_app worker --loglevel=info --concurrency=4 --pool=solo
