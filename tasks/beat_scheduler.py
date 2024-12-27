# tasks/beat_scheduler.py
from . import app
from celery.schedules import crontab

app.conf.beat_schedule = {
    'print-every-10-seconds': {
        'task': 'tasks.print_message',
        'schedule': 10.0,
    },
    'add-numbers-every-minute': {
        'task': 'tasks.add_numbers',
        'schedule': crontab(minute='*'),
        'args': (15, 25),
    },
}
