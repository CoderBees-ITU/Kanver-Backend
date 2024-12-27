# tasks/__init__.py
from celery import Celery

# 1) Celery uygulamasını burada tanımlayın:
app = Celery('tasks')

# 2) Konfigürasyonu ayrı bir dosyadan yükleyin:
app.config_from_object('tasks.celeryconfig')

from .tasks import *

from .beat_scheduler import *