"""
Configuration de l'administration Django pour app_config.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Country, CountryPrefix, PhoneOTP, Language,
    Permission, Role, UserPermission, UserRole
)
from .resources import PermissionResource


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'code', 'prefix', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'prefix']
    ordering = ['name']


@admin.register(CountryPrefix)
class CountryPrefixAdmin(ImportExportModelAdmin):
    list_display = ['name', 'prefix', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'prefix']
    ordering = ['name']


@admin.register(PhoneOTP)
class PhoneOTPAdmin(ImportExportModelAdmin):
    list_display = ['phone_number', 'code', 'attempts', 'isActif', 'create']
    list_filter = ['isActif', 'create']
    search_fields = ['phone_number', 'code']
    ordering = ['-create']


@admin.register(Language)
class LanguageAdmin(ImportExportModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(Permission)
class PermissionAdmin(ImportExportModelAdmin):
    resource_class = PermissionResource
    list_display = ['name', 'codename', 'resource', 'action', 'is_active', 'created_at']
    list_filter = ['resource', 'action', 'is_active', 'created_at']
    search_fields = ['name', 'codename', 'description']
    ordering = ['resource', 'action', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    list_display = ['name', 'codename', 'role_type', 'is_active', 'created_at']
    list_filter = ['role_type', 'is_active', 'created_at']
    search_fields = ['name', 'codename', 'description']
    ordering = ['name']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPermission)
class UserPermissionAdmin(ImportExportModelAdmin):
    list_display = ['profile', 'get_permissions_count', 'granted', 'is_active', 'granted_by', 'created_at']
    list_filter = ['granted', 'is_active', 'permissions__resource', 'created_at']
    filter_horizontal = ['permissions']
    
    def get_permissions_count(self, obj):
        """Affiche le nombre de permissions."""
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissions'
    search_fields = ['profile__full_name', 'permissions__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """
        Surcharge pour stocker les permissions existantes avant la sauvegarde.
        """
        if change and obj.pk:
            # Stocker les permissions existantes dans l'objet pour les récupérer plus tard
            obj._existing_permissions = list(obj.permissions.all())
        
        # Sauvegarder l'objet
        super().save_model(request, obj, form, change)
    
    def save_related(self, request, form, formsets, change):
        """
        Surcharge pour préserver les permissions existantes lors de l'édition.
        Django appelle save_related pour gérer les relations ManyToMany.
        """
        # Appeler save_related normalement (cela remplace les permissions)
        super().save_related(request, form, formsets, change)
        
        # Si on édite un objet existant, fusionner les permissions
        if change and hasattr(form.instance, '_existing_permissions'):
            instance = form.instance
            existing_permissions = set(instance._existing_permissions)
            new_permissions = set(instance.permissions.all())
            
            # Fusionner : garder les existantes + ajouter les nouvelles
            all_permissions = existing_permissions | new_permissions
            instance.permissions.set(all_permissions)
            
            # Nettoyer l'attribut temporaire
            delattr(instance, '_existing_permissions')


@admin.register(UserRole)
class UserRoleAdmin(ImportExportModelAdmin):
    list_display = ['profile', 'role', 'is_active', 'assigned_by', 'created_at']
    list_filter = ['is_active', 'role__role_type', 'created_at']
    search_fields = ['profile__full_name', 'role__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    # raw_id_fields = ['profile', 'role', 'assigned_by']
