"""
EcoStyle - Configuración de desarrollo.
Activa DEBUG, usa consola para email y agrega herramientas de desarrollo.
"""
from .base import *  # noqa

DEBUG = True

# En desarrollo mostramos emails en la consola, sin necesidad de SMTP
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# django-debug-toolbar - solo en desarrollo
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Cache en memoria para desarrollo (sin Redis)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Logs detallados en desarrollo
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Muestra todas las queries SQL
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
