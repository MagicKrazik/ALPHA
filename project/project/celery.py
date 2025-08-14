import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('alpha_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-alerts': {
        'task': 'website.tasks.cleanup_old_alerts',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'update-risk-profiles': {
        'task': 'website.tasks.update_risk_profiles',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Weekly on Monday at 3 AM
    },
}

app.conf.timezone = 'America/Mexico_City'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')