# tasks/celeryconfig.py
# SAKIN: from tasks import app  # diye bir import yapmayın!

broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"

# Opsiyonel ek ayarlar:
# beat_scheduler_max_interval = 10
# result_expires = 3600

# beat_schedule vb. gibi zamanlama ayarlarını da isterseniz buraya koyabilirsiniz.
# Ama eğer beat_schedule'ı ayrı bir dosyada yönetmek istiyorsanız,
# best_scheduler.py (veya beat_scheduler.py) içinde tanımlayabilirsiniz.
