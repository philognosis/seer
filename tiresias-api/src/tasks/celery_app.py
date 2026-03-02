"""
Celery application configuration
"""
from celery import Celery

from src.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "tiresias",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.PROCESSING_TIMEOUT,
    worker_max_tasks_per_child=50,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

celery_app.autodiscover_tasks(["src.tasks"])
