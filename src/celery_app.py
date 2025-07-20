from celery import Celery
from src.settings import settings

"""
This module configures and initializes a Celery application instance for the Air Guardian app.

- Imports the Celery class and project settings.
- Creates a Celery app named "air_guardian_worker" using the broker URL from settings.
- Includes the "src.tasks" module for task discovery.
- Configures a periodic task schedule (beat) to run 'src.tasks.check_for_violations' every 10 seconds.
- Sets the Celery timezone to UTC.
"""

celery = Celery(
    "air_guardian_worker",
    broker=settings.CELERY_BROKER_URL,
    include=["src.tasks"]
)

celery.conf.beat_schedule = {
    'checkV': {
        'task': 'src.tasks.check_for_violations',
        'schedule': 10,
    },
}
celery.conf.timezone = 'UTC'