from celery import Celery

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "ecommerce_operation",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_default_queue=settings.celery_task_default_queue,
    task_routes={
        "generation.*": {"queue": settings.celery_task_default_queue},
    },
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)