"""
Permissions pour l'application app_profile.

Ce module contient les fonctions et classes pour la gestion
des permissions spécifiques à app_profile.
"""

from django.core.exceptions import PermissionDenied
from .models import Profile, Student, Teacher, Parent


def can_view_profile(user, profile):
    """
    Vérifie si un utilisateur peut voir un profil.
    
    Args:
        user: Utilisateur Django
        profile: Instance de Profile
        
    Returns:
        bool: True si l'utilisateur peut voir le profil
    """
    # L'utilisateur peut toujours voir son propre profil
    if hasattr(user, 'profile') and user.profile == profile:
        return True
    
    # Vérifier les permissions via app_config
    try:
        from app_config.permissions import has_permission, is_admin
        if hasattr(user, 'profile'):
            user_profile = user.profile
            # Admin peut tout voir
            if is_admin(user_profile):
                return True
            # Vérifier la permission view_profile
            return has_permission(user_profile, 'view_profile', 'app_profile')
    except Exception:
        pass
    
    return False


def can_edit_profile(user, profile):
    """
    Vérifie si un utilisateur peut modifier un profil.
    
    Args:
        user: Utilisateur Django
        profile: Instance de Profile
        
    Returns:
        bool: True si l'utilisateur peut modifier le profil
    """
    # L'utilisateur peut toujours modifier son propre profil
    if hasattr(user, 'profile') and user.profile == profile:
        return True
    
    # Vérifier les permissions via app_config
    try:
        from app_config.permissions import has_permission, is_admin
        if hasattr(user, 'profile'):
            user_profile = user.profile
            # Admin peut tout modifier
            if is_admin(user_profile):
                return True
            # Vérifier la permission edit_profile
            return has_permission(user_profile, 'edit_profile', 'app_profile')
    except Exception:
        pass
    
    return False


def can_view_student(user, student):
    """
    Vérifie si un utilisateur peut voir un élève.
    
    Args:
        user: Utilisateur Django
        student: Instance de Student
        
    Returns:
        bool: True si l'utilisateur peut voir l'élève
    """
    # L'élève peut voir son propre profil
    if hasattr(user, 'profile') and user.profile == student.profile:
        return True
    
    # Vérifier les permissions via app_config
    try:
        from app_config.permissions import has_permission, is_admin
        if hasattr(user, 'profile'):
            user_profile = user.profile
            # Admin peut tout voir
            if is_admin(user_profile):
                return True
            # Vérifier la permission view_student
            return has_permission(user_profile, 'view_student', 'app_profile')
    except Exception:
        pass
    
    return False


def can_view_teacher(user, teacher):
    """
    Vérifie si un utilisateur peut voir un enseignant.
    
    Args:
        user: Utilisateur Django
        teacher: Instance de Teacher
        
    Returns:
        bool: True si l'utilisateur peut voir l'enseignant
    """
    # L'enseignant peut voir son propre profil
    if hasattr(user, 'profile') and user.profile == teacher.profile:
        return True
    
    # Vérifier les permissions via app_config
    try:
        from app_config.permissions import has_permission, is_admin
        if hasattr(user, 'profile'):
            user_profile = user.profile
            # Admin peut tout voir
            if is_admin(user_profile):
                return True
            # Vérifier la permission view_teacher
            return has_permission(user_profile, 'view_teacher', 'app_profile')
    except Exception:
        pass
    
    return False


def can_view_parent(user, parent):
    """
    Vérifie si un utilisateur peut voir un parent.
    
    Args:
        user: Utilisateur Django
        parent: Instance de Parent
        
    Returns:
        bool: True si l'utilisateur peut voir le parent
    """
    # Le parent peut voir son propre profil
    if hasattr(user, 'profile') and user.profile == parent.profile:
        return True
    
    # Vérifier les permissions via app_config
    try:
        from app_config.permissions import has_permission, is_admin
        if hasattr(user, 'profile'):
            user_profile = user.profile
            # Admin peut tout voir
            if is_admin(user_profile):
                return True
            # Vérifier la permission view_parent
            return has_permission(user_profile, 'view_parent', 'app_profile')
    except Exception:
        pass
    
    return False


class ProfilePermissionMixin:
    """
    Mixin pour vérifier les permissions sur les profils.
    """
    
    def check_permission(self, user, profile, permission_type='view'):
        """
        Vérifie une permission sur un profil.
        
        Args:
            user: Utilisateur Django
            profile: Instance de Profile
            permission_type: Type de permission ('view' ou 'edit')
            
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas la permission
        """
        if permission_type == 'view':
            if not can_view_profile(user, profile):
                raise PermissionDenied("Vous n'avez pas la permission de voir ce profil.")
        elif permission_type == 'edit':
            if not can_edit_profile(user, profile):
                raise PermissionDenied("Vous n'avez pas la permission de modifier ce profil.")
        else:
            raise ValueError(f"Type de permission inconnu: {permission_type}")

