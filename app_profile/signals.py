"""
Signals pour l'application app_profile.

Ce module contient les signaux Django pour la gestion automatique
des profils utilisateurs lors de la création d'un User.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil lorsqu'un utilisateur est créé.
    
    Args:
        sender: Le modèle qui a envoyé le signal (User)
        instance: L'instance de User qui vient d'être créée
        created: Booléen indiquant si l'instance vient d'être créée
        **kwargs: Arguments supplémentaires
    """
    if created:
        # Créer le profil uniquement s'il n'existe pas déjà
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.username,
                'firstname': instance.first_name or '',
                'name': instance.last_name or '',
            }
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Met à jour automatiquement le profil lorsqu'un utilisateur est sauvegardé.
    
    Args:
        sender: Le modèle qui a envoyé le signal (User)
        instance: L'instance de User qui vient d'être sauvegardée
        **kwargs: Arguments supplémentaires
    """
    # Mettre à jour le profil si l'utilisateur a un profil
    if hasattr(instance, 'profile'):
        profile = instance.profile
        # Mettre à jour le nom complet si nécessaire
        if not profile.full_name or profile.full_name == instance.username:
            full_name = instance.get_full_name() or instance.username
            profile.full_name = full_name
        # Mettre à jour le prénom et nom si nécessaire
        if instance.first_name and not profile.firstname:
            profile.firstname = instance.first_name
        if instance.last_name and not profile.name:
            profile.name = instance.last_name
        profile.save()

