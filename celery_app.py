from celery import Celery
from settings import settings

celery = Celery(
    "air_guardian_worker",
    broker=settings.CELERY_BROKER_URL,
    include=["tasks"]
)

celery.conf.beat_schedule = {
    'checkV': {
        'task': 'tasks.check_for_violations',
        'schedule': 10,
    },
}
celery.conf.timezone = 'UTC'