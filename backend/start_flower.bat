# Flower Monitoring UI Startup Script
# Run this to start the Flower web interface for monitoring Celery tasks
# Access at: http://localhost:5555

celery -A app.core.celery_app flower --port=5555
