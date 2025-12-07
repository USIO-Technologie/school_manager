"""
Configuration Celery pour le projet school_manager.

Ce module configure l'application Celery pour gérer les tâches asynchrones.
"""

import os
from celery import Celery
from django.conf import settings

# Définir le module de settings par défaut pour la ligne de commande 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')

# Créer l'instance de l'application Celery
app = Celery('school_manager')

# Inclure les modules de tâches des apps
app.conf.include = ['app_profile.tasks']

# Charger la configuration depuis les settings Django avec le namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans toutes les apps installées
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Définir le timezone selon les settings Django
app.conf.timezone = settings.TIME_ZONE


@app.task(bind=True)
def debug_task(self):
    """
    Tâche de debug pour tester la configuration Celery.
    
    Args:
        self: Instance de la tâche (bind=True)
    
    Returns:
        str: Message de confirmation avec les informations de la requête
    """
    print(f'Request: {self.request!r}')
    return f'Debug task executed: {self.request.id}'

