"""
Vues pour la gestion des configurations et permissions.

Ce module contient les vues pour gérer les permissions,
rôles et configurations de l'application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
import json

from .models import Permission, Role, UserPermission, UserRole
from app_profile.models import Profile
from django.contrib.auth.models import User
from .permissions import (
    has_permission, is_admin, assign_permission, 
    assign_role, remove_role, get_user_permissions, PermissionRequiredMixin
)


class AllUsersView(PermissionRequiredMixin, View):
    """
    Vue pour afficher tous les utilisateurs du système.
    
    Requiert la permission: view_all_users
    """
    
    required_permission = 'view_all_users'
    required_resource = 'app_config'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche la liste de tous les utilisateurs.
        """
        # Récupérer tous les profils avec leurs informations
        profiles = Profile.objects.filter(is_active=True).select_related('user').prefetch_related(
            'user_roles__role',
            'user_permissions__permissions'
        ).annotate(
            roles_count=Count('user_roles', filter=Q(user_roles__is_active=True)),
            permissions_count=Count('user_permissions__permissions', filter=Q(user_permissions__granted=True, user_permissions__is_active=True), distinct=True)
        ).order_by('-created_at')
        
        # Recherche et filtrage
        search_query = request.GET.get('search', '')
        if search_query:
            profiles = profiles.filter(
                Q(full_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        context = {
            'profiles': profiles,
            'search_query': search_query,
        }
        
        return render(request, 'app_config/all_users.html', context)


class PermissionManagementView(PermissionRequiredMixin, View):
    """
    Vue principale pour la gestion des permissions.
    
    Affiche la liste des utilisateurs avec leurs permissions et rôles.
    Requiert la permission: assign_role_permissions ou manage_permissions
    """
    
    required_permission = 'assign_role_permissions'
    required_resource = 'app_config'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Vérifier si l'utilisateur a assign_role_permissions ou manage_permissions
        if hasattr(request.user, 'profile'):
            has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
            has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
            if not (has_assign or has_manage):
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('app_profile:dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        Affiche la page de gestion des permissions.
        """
        
        # Récupérer tous les profils avec leurs permissions et rôles
        profiles = Profile.objects.filter(is_active=True).select_related('user').prefetch_related(
            'user_roles__role',
            'user_permissions__permissions'
        ).annotate(
            roles_count=Count('user_roles', filter=Q(user_roles__is_active=True)),
            permissions_count=Count('user_permissions__permissions', filter=Q(user_permissions__granted=True, user_permissions__is_active=True), distinct=True)
        ).order_by('-created_at')
        
        # Récupérer tous les rôles et permissions disponibles
        roles = Role.objects.filter(is_active=True).order_by('name')
        permissions = Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name')
        
        # Grouper les permissions par ressource
        permissions_by_resource = {}
        for perm in permissions:
            if perm.resource not in permissions_by_resource:
                permissions_by_resource[perm.resource] = []
            permissions_by_resource[perm.resource].append(perm)
        
        context = {
            'profiles': profiles,
            'roles': roles,
            'permissions': permissions,
            'permissions_by_resource': permissions_by_resource,
        }
        
        return render(request, 'app_config/permission_management.html', context)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AssignPermissionView(View):
    """
    Vue pour assigner une permission à un utilisateur.
    """
    
    def post(self, request):
        """
        Assigne une permission à un profil.
        
        Body JSON attendu:
        {
            "profile_id": 1,
            "permission_id": 2,
            "granted": true
        }
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
            permission_id = data.get('permission_id')
            granted = data.get('granted', True)
            
            if not profile_id or not permission_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Profile ID and Permission ID are required.'
                }, status=400)
            
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            permission = get_object_or_404(Permission, id=permission_id, is_active=True)
            
            user_permission = assign_permission(
                profile=profile,
                permission_codename=permission.codename,
                granted=granted,
                granted_by=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Permission {"granted" if granted else "denied"} successfully.',
                'user_permission': {
                    'id': user_permission.id,
                    'permission_name': permission.name,
                    'granted': user_permission.granted
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RemovePermissionView(View):
    """
    Vue pour retirer une permission d'un utilisateur.
    """
    
    def post(self, request):
        """
        Retire une permission d'un profil.
        
        Body JSON attendu:
        {
            "profile_id": 1,
            "permission_id": 2
        }
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
            permission_id = data.get('permission_id')
            
            if not profile_id or not permission_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Profile ID and Permission ID are required.'
                }, status=400)
            
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            permission = get_object_or_404(Permission, id=permission_id, is_active=True)
            
            # Chercher tous les UserPermission actifs pour ce profil qui contiennent cette permission
            user_permissions = UserPermission.objects.filter(
                profile=profile,
                permissions=permission,
                is_active=True
            )
            
            if user_permissions.exists():
                # Retirer la permission du ManyToManyField pour chaque UserPermission
                for user_permission in user_permissions:
                    user_permission.permissions.remove(permission)
                    # Si plus aucune permission, désactiver l'enregistrement au lieu de le supprimer
                    if user_permission.permissions.count() == 0:
                        user_permission.is_active = False
                        user_permission.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Permission removed successfully.'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Permission not found for this user.'
                }, status=404)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AssignRoleView(View):
    """
    Vue pour assigner un rôle à un utilisateur.
    """
    
    def post(self, request):
        """
        Assigne un rôle à un profil.
        
        Body JSON attendu:
        {
            "profile_id": 1,
            "role_id": 2
        }
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
            role_id = data.get('role_id')
            
            if not profile_id or not role_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Profile ID and Role ID are required.'
                }, status=400)
            
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            role = get_object_or_404(Role, id=role_id, is_active=True)
            
            user_role = assign_role(
                profile=profile,
                role_codename=role.codename,
                assigned_by=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Role assigned successfully.',
                'user_role': {
                    'id': user_role.id,
                    'role_name': role.name,
                    'is_active': user_role.is_active
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RemoveRoleView(View):
    """
    Vue pour retirer un rôle d'un utilisateur.
    """
    
    def post(self, request):
        """
        Retire un rôle d'un profil.
        
        Body JSON attendu:
        {
            "profile_id": 1,
            "role_id": 2
        }
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            profile_id = data.get('profile_id')
            role_id = data.get('role_id')
            
            if not profile_id or not role_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Profile ID and Role ID are required.'
                }, status=400)
            
            profile = get_object_or_404(Profile, id=profile_id, is_active=True)
            role = get_object_or_404(Role, id=role_id, is_active=True)
            
            success = remove_role(profile, role.codename)
            
            if success:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Role removed successfully.'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Role not found for this user.'
                }, status=404)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class UserPermissionsView(View):
    """
    Vue pour afficher les permissions d'un utilisateur spécifique.
    """
    
    def get(self, request, profile_id):
        """
        Affiche les permissions et rôles d'un utilisateur.
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('app_profile:dashboard_redirect')
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('app_profile:dashboard_redirect')
        
        profile = get_object_or_404(Profile, id=profile_id, is_active=True)
        
        # Récupérer les rôles de l'utilisateur
        user_roles = UserRole.objects.filter(
            profile=profile,
            is_active=True
        ).select_related('role', 'assigned_by')
        
        # Récupérer les permissions directes (actives uniquement)
        user_permissions = UserPermission.objects.filter(
            profile=profile,
            is_active=True
        ).prefetch_related('permissions', 'granted_by')
        
        # Récupérer toutes les permissions (via rôles et directes)
        all_permissions = get_user_permissions(profile)
        
        # Récupérer tous les rôles et permissions disponibles
        all_roles = Role.objects.filter(is_active=True).order_by('name')
        all_permissions_list = Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name')
        
        # Grouper les permissions par ressource
        permissions_by_resource = {}
        for perm in all_permissions_list:
            if perm.resource not in permissions_by_resource:
                permissions_by_resource[perm.resource] = []
            permissions_by_resource[perm.resource].append(perm)
        
        context = {
            'profile': profile,
            'user_roles': user_roles,
            'user_permissions': user_permissions,
            'all_permissions': all_permissions,
            'all_roles': all_roles,
            'permissions_by_resource': permissions_by_resource,
        }
        
        return render(request, 'app_config/user_permissions.html', context)


class RolePermissionsManagementView(PermissionRequiredMixin, View):
    """
    Vue pour gérer les permissions par rôle.
    
    Permet d'assigner ou retirer des permissions à un rôle spécifique.
    Requiert la permission: assign_role_permissions
    """
    
    required_permission = 'assign_role_permissions'
    required_resource = 'app_config'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Affiche la page de gestion des permissions par rôle.
        """
        from django.db.models import Prefetch
        
        # Précharger uniquement les permissions actives avec to_attr pour un accès direct
        active_permissions_prefetch = Prefetch(
            'permissions',
            queryset=Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name'),
            to_attr='active_permissions_list'
        )
        
        # Récupérer tous les rôles avec leurs permissions actives
        roles = Role.objects.filter(is_active=True).prefetch_related(
            active_permissions_prefetch
        ).annotate(
            permissions_count=Count('permissions', filter=Q(permissions__is_active=True))
        ).order_by('name')
        
        # Récupérer toutes les permissions disponibles
        all_permissions = Permission.objects.filter(is_active=True).order_by('resource', 'action', 'name')
        
        # Grouper les permissions par ressource
        permissions_by_resource = {}
        for perm in all_permissions:
            if perm.resource not in permissions_by_resource:
                permissions_by_resource[perm.resource] = []
            permissions_by_resource[perm.resource].append(perm)
        
        context = {
            'roles': roles,
            'all_permissions': all_permissions,
            'permissions_by_resource': permissions_by_resource,
        }
        
        return render(request, 'app_config/role_permissions_management.html', context)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RolePermissionsUpdateView(View):
    """
    Vue API pour mettre à jour les permissions d'un rôle.
    """
    
    def post(self, request):
        """
        Met à jour les permissions d'un rôle.
        
        Body JSON attendu:
        {
            "role_id": 1,
            "permission_ids": [1, 2, 3]
        }
        """
        # Vérifier la permission assign_role_permissions ou manage_permissions
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        has_assign = has_permission(request.user.profile, 'assign_role_permissions', 'app_config')
        has_manage = has_permission(request.user.profile, 'manage_permissions', 'app_config')
        
        if not (has_assign or has_manage):
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to perform this action.'
            }, status=403)
        
        try:
            data = json.loads(request.body)
            role_id = data.get('role_id')
            permission_ids = data.get('permission_ids', [])
            
            if not role_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Role ID is required.'
                }, status=400)
            
            role = get_object_or_404(Role, id=role_id, is_active=True)
            
            # Récupérer les permissions
            permissions = Permission.objects.filter(id__in=permission_ids, is_active=True)
            
            # Mettre à jour les permissions du rôle
            role.permissions.set(permissions)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Permissions updated successfully for {role.name}.',
                'role': {
                    'id': role.id,
                    'name': role.name,
                    'permissions_count': permissions.count()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
