import os
from celery import Celery

celery_app = Celery(
    "omnicrew",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_track_started=True
)

# CRITICAL: Import the tasks module so Celery registers the @celery_app.task functions
import tasks