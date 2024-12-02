from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# Create app
app = Celery('app')

# Configure Celery directly
app.conf.update(
    broker_url='redis://localhost:6389/0',
    result_backend='redis://localhost:6389/0',
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

# Auto-discover tasks
app.autodiscover_tasks()
