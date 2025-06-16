from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from comptes.models import Profil, Role

@admin.register(Role)
class RoleAdmin(ImportExportModelAdmin):
    
    list_display = (
        "nom",
        "description",
        "is_active",
        "created_at",
        "create_by",
    )
    list_filter = ("is_active",)
    search_fields = ("nom",)

@admin.register(Profil)
class ProfilAdmin(ImportExportModelAdmin):
    
    list_display = (
        "user",
        "display_ecoles",  # Custom method
        "display_roles",   # Custom method
        "nom",
        "matricule",
        "date_naissance",
        "telephone",
        "is_active",
        "created_at",
        "create_by",
    )
    list_filter = ("nom", "matricule","is_active",)
    search_fields = ("user__username", "created_at", "matricule")
    filter_horizontal = ("roles",)
    
    def display_ecoles(self, obj):
        return ", ".join([ecole.nom for ecole in obj.ecoles.all()])
    display_ecoles.short_description = "Ecoles"
    
    def display_roles(self, obj):
        return ", ".join([role.nom for role in obj.roles.all()])
    display_roles.short_description = "Roles"