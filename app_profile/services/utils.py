"""
Utilitaires pour l'application app_profile.

Ce module contient les fonctions utilitaires pour la logique métier.
"""

from django.contrib.auth.models import User
from django.db import transaction
from ..models import Profile, Student, Teacher, Parent


def create_profile_with_role(user, role, **profile_data):
    """
    Crée un profil avec un rôle spécifique.
    
    Args:
        user: Instance de User Django
        role: Rôle du profil ('student', 'teacher', 'parent')
        **profile_data: Données supplémentaires pour le profil
        
    Returns:
        tuple: (Profile, Student/Teacher/Parent) selon le rôle
    """
    with transaction.atomic():
        # Créer ou récupérer le profil
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': user.get_full_name() or user.username,
                'firstname': user.first_name or '',
                'name': user.last_name or '',
                'role': role,
                **profile_data
            }
        )
        
        # Mettre à jour le rôle si nécessaire
        if not created:
            profile.role = role
            profile.save()
        
        # Créer l'entité spécifique selon le rôle
        entity = None
        if role == 'student':
            entity, _ = Student.objects.get_or_create(profile=profile)
        elif role == 'teacher':
            entity, _ = Teacher.objects.get_or_create(profile=profile)
        elif role == 'parent':
            entity, _ = Parent.objects.get_or_create(profile=profile)
        
        return profile, entity


def generate_student_number():
    """
    Génère un numéro d'élève unique.
    
    Returns:
        str: Numéro d'élève unique
    """
    from datetime import datetime
    import random
    
    # Format: STU-YYYYMMDD-XXXX
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = str(random.randint(1000, 9999))
    
    student_number = f"STU-{date_part}-{random_part}"
    
    # Vérifier l'unicité
    while Student.objects.filter(student_number=student_number).exists():
        random_part = str(random.randint(1000, 9999))
        student_number = f"STU-{date_part}-{random_part}"
    
    return student_number


def generate_teacher_number():
    """
    Génère un numéro d'enseignant unique.
    
    Returns:
        str: Numéro d'enseignant unique
    """
    from datetime import datetime
    import random
    
    # Format: TCH-YYYYMMDD-XXXX
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = str(random.randint(1000, 9999))
    
    teacher_number = f"TCH-{date_part}-{random_part}"
    
    # Vérifier l'unicité
    while Teacher.objects.filter(teacher_number=teacher_number).exists():
        random_part = str(random.randint(1000, 9999))
        teacher_number = f"TCH-{date_part}-{random_part}"
    
    return teacher_number


def generate_parent_number():
    """
    Génère un numéro de parent unique.
    
    Returns:
        str: Numéro de parent unique
    """
    from datetime import datetime
    import random
    
    # Format: PRT-YYYYMMDD-XXXX
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = str(random.randint(1000, 9999))
    
    parent_number = f"PRT-{date_part}-{random_part}"
    
    # Vérifier l'unicité
    while Parent.objects.filter(parent_number=parent_number).exists():
        random_part = str(random.randint(1000, 9999))
        parent_number = f"PRT-{date_part}-{random_part}"
    
    return parent_number


def get_profile_statistics(profile):
    """
    Récupère les statistiques d'un profil.
    
    Args:
        profile: Instance de Profile
        
    Returns:
        dict: Dictionnaire contenant les statistiques
    """
    stats = {
        'completion_rate': profile.completion_rate,
        'is_verified': profile.is_verified,
        'has_photo': bool(profile.photo),
    }
    
    # Ajouter des statistiques spécifiques selon le rôle
    if hasattr(profile, 'student'):
        stats['type'] = 'student'
        stats['student_number'] = profile.student.student_number
    elif hasattr(profile, 'teacher'):
        stats['type'] = 'teacher'
        stats['teacher_number'] = profile.teacher.teacher_number
    elif hasattr(profile, 'parent'):
        stats['type'] = 'parent'
        stats['parent_number'] = profile.parent.parent_number
    else:
        stats['type'] = 'profile'
    
    return stats


def validate_phone_number(phone):
    """
    Valide un numéro de téléphone.
    
    Args:
        phone: Numéro de téléphone à valider
        
    Returns:
        tuple: (is_valid, cleaned_phone)
    """
    if not phone:
        return False, None
    
    # Nettoyer le numéro (supprimer les espaces, tirets, etc.)
    cleaned = ''.join(filter(str.isdigit, phone))
    
    # Vérifier la longueur (au moins 8 chiffres)
    if len(cleaned) < 8:
        return False, None
    
    return True, cleaned

