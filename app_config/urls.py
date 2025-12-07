"""
Configuration des URLs pour l'application app_config.
"""

from django.urls import path
from .views import (
    AllUsersView,
    PermissionManagementView,
    RolePermissionsManagementView,
    RolePermissionsUpdateView,
    AssignPermissionView,
    RemovePermissionView,
    AssignRoleView,
    RemoveRoleView,
    UserPermissionsView
)

app_name = 'app_config'

urlpatterns = [
    # Liste de tous les utilisateurs
    path('users/', AllUsersView.as_view(), name='all_users'),
    
    # Gestion des permissions
    path('permissions/', PermissionManagementView.as_view(), name='permission_management'),
    path('permissions/roles/', RolePermissionsManagementView.as_view(), name='role_permissions_management'),
    path('permissions/user/<int:profile_id>/', UserPermissionsView.as_view(), name='user_permissions'),
    
    # API pour assigner/retirer permissions
    path('api/permissions/assign/', AssignPermissionView.as_view(), name='assign_permission'),
    path('api/permissions/remove/', RemovePermissionView.as_view(), name='remove_permission'),
    path('api/roles/assign/', AssignRoleView.as_view(), name='assign_role'),
    path('api/roles/remove/', RemoveRoleView.as_view(), name='remove_role'),
    path('api/roles/permissions/update/', RolePermissionsUpdateView.as_view(), name='update_role_permissions'),
]

