"""
Tâches Celery pour l'application app_profile.

Ce module contient les tâches asynchrones pour la gestion des profils utilisateurs.
"""

from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User


@shared_task(name='app_profile.send_welcome_email')
def send_welcome_email(user_id):
    """
    Envoie un email de bienvenue à un nouvel utilisateur.
    
    Cette tâche est exécutée de manière asynchrone pour ne pas bloquer
    la réponse HTTP lors de la création d'un compte.
    
    Args:
        user_id (int): ID de l'utilisateur à qui envoyer l'email
    
    Returns:
        str: Message de confirmation
    """
    try:
        user = User.objects.get(id=user_id)
        # TODO: Implémenter l'envoi d'email réel
        # from django.core.mail import send_mail
        # send_mail(
        #     subject='Bienvenue sur School Manager',
        #     message=f'Bonjour {user.get_full_name() or user.username}, bienvenue !',
        #     from_email=None,
        #     recipient_list=[user.email],
        #     fail_silently=False,
        # )
        print(f"Email de bienvenue envoyé à {user.username} ({user.email})")
        return f"Email de bienvenue envoyé avec succès à {user.username}"
    except User.DoesNotExist:
        return f"Utilisateur avec l'ID {user_id} introuvable"


@shared_task(name='app_profile.cleanup_old_sessions')
def cleanup_old_sessions(days=30):
    """
    Nettoie les sessions utilisateur expirées.
    
    Supprime les sessions qui sont plus anciennes que le nombre de jours spécifié.
    
    Args:
        days (int): Nombre de jours après lesquels une session est considérée comme expirée (défaut: 30)
    
    Returns:
        dict: Statistiques du nettoyage
    """
    from .models import UserSession
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = UserSession.objects.filter(
        last_activity__lt=cutoff_date
    ).delete()
    
    return {
        'deleted_sessions': deleted_count,
        'cutoff_date': cutoff_date.isoformat(),
        'status': 'success'
    }


@shared_task(name='app_profile.update_profile_statistics')
def update_profile_statistics():
    """
    Met à jour les statistiques globales des profils.
    
    Calcule et met à jour les statistiques agrégées pour tous les profils.
    Cette tâche peut être exécutée périodiquement via Celery Beat.
    
    Returns:
        dict: Statistiques mises à jour
    """
    from .models import Profile, Student, Teacher, Parent
    
    stats = {
        'total_profiles': Profile.objects.count(),
        'active_profiles': Profile.objects.filter(is_active=True).count(),
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_teachers': Teacher.objects.filter(is_active=True).count(),
        'total_parents': Parent.objects.filter(is_active=True).count(),
        'updated_at': timezone.now().isoformat(),
    }
    
    print(f"Statistiques mises à jour: {stats}")
    return stats

