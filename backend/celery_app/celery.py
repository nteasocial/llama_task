
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

#
app.conf.beat_schedule = {
    'update-crypto-prices': {
        'task': 'api.tasks.update_crypto_prices',
        'schedule': 10.0, 
    }
}

app.autodiscover_tasks()
