import os
from celery import Celery


app = Celery('MamuraParfume')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MamuraParfume.settings')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
