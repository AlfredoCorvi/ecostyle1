"""
Configuración de Celery para tareas asíncronas (emails, notificaciones de stock).
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecostyle.settings.development")
app = Celery("ecostyle")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
