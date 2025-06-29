from celery import Celery

from my_service.core.config import CELERY_BROKER_URL

celery_app = Celery("worker", broker=CELERY_BROKER_URL)
celery_app.autodiscover_tasks(["my_service.tasks"])
