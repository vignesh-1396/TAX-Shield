"""
Celery Configuration for Async Task Processing
"""
from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "itc_shield",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.batch_tasks']
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='Asia/Kolkata',
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # Soft limit at 25 minutes
    
    # Worker optimization
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=True,
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},
    
    # Retry policy
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    
    # Monitoring
    task_send_sent_event=True,
    worker_send_task_events=True,
)

# Task routes (optional - for multiple queues)
celery_app.conf.task_routes = {
    'app.tasks.batch_tasks.*': {'queue': 'batch_processing'},
    'app.tasks.email_tasks.*': {'queue': 'notifications'},
}

logger.info("Celery app configured successfully")
