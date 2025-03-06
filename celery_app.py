from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Create Celery app
celery_app = Celery(
    'image_processor',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.tasks.worker']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max task time
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    task_acks_late=True,  # Acknowledge tasks after execution
    task_reject_on_worker_lost=True  # Reject tasks if worker dies
)

if __name__ == '__main__':
    celery_app.start()