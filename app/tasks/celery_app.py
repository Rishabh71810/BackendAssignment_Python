from celery import Celery
from app.config import settings

celery_app = Celery(
    "subscription_service",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.subscription_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "expire-subscriptions": {
            "task": "app.tasks.subscription_tasks.expire_subscriptions_task",
            "schedule": 3600.0,  # Run every hour
        },
    },
) 