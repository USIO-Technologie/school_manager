"""
Django production settings for jiwe_saas_project
"""

from .settings import *  # Importer les paramètres de base
import os

# ===================== DEBUG & ALLOWED HOSTS =====================
DEBUG = False
ALLOWED_HOSTS = [
        "jiwe-holding.online",
        "www.jiwe-holding.online",  # au cas où tu utilises www
        "161.97.159.227",  # ton IP publique
        "localhost",       # utile en local/Docker
    ]
# Django est derrière Caddy (proxy HTTPS)
# SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOWED_ORIGINS = [
    "https://jiwe-holding.online",
]
# Si tu envoies Authorization: Bearer ...
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "accept",
    "origin",
    "x-csrftoken",
]
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
CORS_PREFLIGHT_MAX_AGE = 81000  # 24h de cache du preflight par le navigateur
# Si tu utilises des cookies (pas le cas avec JWT) :
# CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [

]

# ===================== DATABASE =====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME", "school_db"),
        'HOST': os.getenv("DB_HOST", "db"),
        'PORT': os.getenv("DB_PORT", "5432"),
        'USER': os.getenv("DB_USER", "school_user"),
        'PASSWORD': os.getenv("DB_PASSWORD", "blinding_school@"),
    }
}

# ===================== STATIC & MEDIA =====================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ===================== SECURITY =====================
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 600  # 10 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

# ===================== CELERY =====================
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_ALWAYS_EAGER = False  # False pour la production, True pour les tests

# ===================== Secret Key =====================
FERNET_KEY="x4S7qqSYAS0ZsDL-JIWE-ABhEC_9AJbhp2rNdnEwqU8="

# ===================== SENTRY =====================
# import sentry_sdk
#
# sentry_sdk.init(
#     dsn="https://56219ab85f613404ad1f3adea04f87b6@o4505668669538304.ingest.us.sentry.io/4509937398841344",
#     send_default_pii=True,
#     traces_sample_rate=0.2,  # ajuste selon besoin
#     profiles_sample_rate=0.2,
# )
