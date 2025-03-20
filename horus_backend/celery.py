# from celery.schedules import crontab
# from celery import Celery

# app = Celery("horus_backend")

# app.conf.beat_schedule = {
#     "fetch_twitter_engagement": {
#         "task": "twitter_tracker.tasks.fetch_twitter_engagement",
#         "schedule": crontab(minute="*/2"),  # Runs every 2 minutes
#     },
#     "check_followers": {
#         "task": "twitter_tracker.tasks.check_followers",
#         "schedule": crontab(minute="*/1"),  # Runs every 10 minutes
#     }, 
# }

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horus_backend.settings")

app = Celery("horus_backend")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed apps
app.autodiscover_tasks()

# Celery Beat: Run fetch_twitter_engagement every minute
app.conf.beat_schedule = {
    "fetch-twitter-engagement-every-minute": {
        "task": "twitter_tracker.tasks.fetch_twitter_engagement",
        "schedule": crontab(minute="*"),  # Runs every minute
    },
       "check_followers": {
        "task": "twitter_tracker.tasks.check_followers",
        "schedule": crontab(minute="*/1"),  # Runs every 10 minutes
    }, 
}

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
