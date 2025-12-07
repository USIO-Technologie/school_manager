"""
Utilitaires pour la gestion des permissions.

Ce module contient les fonctions et classes pour vérifier
et gérer les permissions des utilisateurs.
"""

from django.core.exceptions import PermissionDenied
from .models import Permission, Role, UserPermission, UserRole


def has_permission(profile, permission_codename, resource=None):
    """
    Vérifie si un profil a une permission spécifique.
    
    Args:
        profile: Instance du modèle Profile
        permission_codename: Code de la permission (ex: 'view_profile')
        resource: Ressource concernée (optionnel, pour filtrage)
    
    Returns:
        bool: True si le profil a la permission, False sinon
    """
    if not profile or not profile.is_active:
        return False
    
    # Vérifier les permissions directes de l'utilisateur
    user_permissions = UserPermission.objects.filter(
        profile=profile,
        permissions__codename=permission_codename,
        granted=True,
        is_active=True
    )
    
    if resource:
        user_permissions = user_permissions.filter(permissions__resource=resource)
    
    # Si une permission est explicitement refusée, retourner False
    denied_permissions = UserPermission.objects.filter(
        profile=profile,
        permissions__codename=permission_codename,
        granted=False,
        is_active=True
    )
    if resource:
        denied_permissions = denied_permissions.filter(permissions__resource=resource)
    
    if denied_permissions.exists():
        return False
    
    # Si une permission est explicitement accordée, retourner True
    if user_permissions.exists():
        return True
    
    # Vérifier les permissions via les rôles
    user_roles = UserRole.objects.filter(
        profile=profile,
        is_active=True,
        role__is_active=True
    ).select_related('role').prefetch_related('role__permissions')
    
    for user_role in user_roles:
        role_permissions = user_role.role.permissions.filter(
            codename=permission_codename,
            is_active=True
        )
        if resource:
            role_permissions = role_permissions.filter(resource=resource)
        
        if role_permissions.exists():
            return True
    
    return False


def has_role(profile, role_codename):
    """
    Vérifie si un profil a un rôle spécifique.
    
    Args:
        profile: Instance du modèle Profile
        role_codename: Code du rôle (ex: 'admin')
    
    Returns:
        bool: True si le profil a le rôle, False sinon
    """
    if not profile or not profile.is_active:
        return False
    
    return UserRole.objects.filter(
        profile=profile,
        role__codename=role_codename,
        role__is_active=True,
        is_active=True
    ).exists()


def is_admin(profile):
    """
    Vérifie si un profil est administrateur.
    
    Args:
        profile: Instance du modèle Profile
    
    Returns:
        bool: True si le profil est admin, False sinon
    """
    return has_role(profile, 'admin')


def get_user_permissions(profile):
    """
    Récupère toutes les permissions d'un profil (via rôles et permissions directes).
    
    Args:
        profile: Instance du modèle Profile
    
    Returns:
        QuerySet: Permissions du profil
    """
    if not profile or not profile.is_active:
        return Permission.objects.none()
    
    # Permissions via rôles
    role_permissions = Permission.objects.filter(
        roles__user_roles__profile=profile,
        roles__user_roles__is_active=True,
        roles__user_roles__role__is_active=True,
        is_active=True
    ).distinct()
    
    # Permissions directes accordées
    direct_permissions = Permission.objects.filter(
        user_permissions__profile=profile,
        user_permissions__granted=True,
        user_permissions__is_active=True,
        is_active=True
    ).distinct()
    
    # Combiner les deux
    all_permissions = (role_permissions | direct_permissions).distinct()
    
    # Exclure les permissions explicitement refusées
    denied_permissions = Permission.objects.filter(
        user_permissions__profile=profile,
        user_permissions__granted=False,
        user_permissions__is_active=True,
        is_active=True
    ).values_list('id', flat=True)
    
    return all_permissions.exclude(id__in=denied_permissions)


def assign_permission(profile, permission_codename, granted=True, granted_by=None):
    """
    Assigne une permission à un profil.
    
    Args:
        profile: Instance du modèle Profile
        permission_codename: Code de la permission
        granted: True pour accorder, False pour refuser
        granted_by: Utilisateur qui accorde la permission
    
    Returns:
        UserPermission: Instance créée ou mise à jour
    """
    try:
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
    except Permission.DoesNotExist:
        raise ValueError(f"Permission '{permission_codename}' not found")
    
    # Chercher un UserPermission existant actif avec le même statut (granted) pour ce profil
    user_permission = UserPermission.objects.filter(
        profile=profile,
        granted=granted,
        is_active=True
    ).first()
    
    if user_permission:
        # Ajouter la permission au ManyToMany si elle n'est pas déjà présente
        if permission not in user_permission.permissions.all():
            user_permission.permissions.add(permission)
            if granted_by:
                user_permission.granted_by = granted_by
            user_permission.is_active = True
            user_permission.save()
    else:
        # Créer un nouveau UserPermission
        user_permission = UserPermission.objects.create(
            profile=profile,
            granted=granted,
            is_active=True,
            granted_by=granted_by
        )
        user_permission.permissions.add(permission)
    
    return user_permission


def assign_role(profile, role_codename, assigned_by=None):
    """
    Assigne un rôle à un profil.
    
    Args:
        profile: Instance du modèle Profile
        role_codename: Code du rôle
        assigned_by: Utilisateur qui assigne le rôle
    
    Returns:
        UserRole: Instance créée ou mise à jour
    """
    try:
        role = Role.objects.get(codename=role_codename, is_active=True)
    except Role.DoesNotExist:
        raise ValueError(f"Role '{role_codename}' not found")
    
    user_role, created = UserRole.objects.update_or_create(
        profile=profile,
        role=role,
        defaults={
            'is_active': True,
            'assigned_by': assigned_by
        }
    )
    
    return user_role


def remove_role(profile, role_codename):
    """
    Retire un rôle d'un profil.
    
    Args:
        profile: Instance du modèle Profile
        role_codename: Code du rôle
    
    Returns:
        bool: True si le rôle a été retiré, False sinon
    """
    try:
        user_role = UserRole.objects.get(
            profile=profile,
            role__codename=role_codename,
            is_active=True
        )
        user_role.is_active = False
        user_role.save()
        return True
    except UserRole.DoesNotExist:
        return False


class PermissionRequiredMixin:
    """
    Mixin pour vérifier les permissions dans les vues.
    
    Usage:
        class MyView(PermissionRequiredMixin, View):
            required_permission = 'view_profile'
            required_resource = 'app_profile'
    """
    
    required_permission = None
    required_resource = None
    raise_exception = True
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if self.raise_exception:
                raise PermissionDenied("Authentication required")
            return self.handle_no_permission()
        
        if not hasattr(request.user, 'profile'):
            if self.raise_exception:
                raise PermissionDenied("Profile not found")
            return self.handle_no_permission()
        
        if self.required_permission:
            has_perm = has_permission(
                request.user.profile,
                self.required_permission,
                self.required_resource
            )
            
            if not has_perm:
                if self.raise_exception:
                    raise PermissionDenied(
                        f"You don't have permission to {self.required_permission}"
                    )
                return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        """
        Gère le cas où l'utilisateur n'a pas la permission.
        Peut être surchargé dans les classes dérivées.
        """
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You don't have permission to access this resource.")


def require_permission(permission_codename, resource=None):
    """
    Décorateur pour vérifier les permissions.
    
    Usage:
        @require_permission('view_profile', 'app_profile')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            if not hasattr(request.user, 'profile'):
                raise PermissionDenied("Profile not found")
            
            if not has_permission(request.user.profile, permission_codename, resource):
                raise PermissionDenied(
                    f"You don't have permission to {permission_codename}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

