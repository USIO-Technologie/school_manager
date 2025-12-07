"""
Configuration d'initialisation pour le projet school_manager.

Ce module garantit que l'application Celery est chargée lorsque Django démarre.
"""

# Import de l'application Celery pour s'assurer qu'elle est chargée au démarrage
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery n'est pas installé, on continue sans
    __all__ = ()

