from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Classe, Eleve, Cours


@admin.register(Classe)
class ClasseAdmin(ImportExportModelAdmin):
    list_display = ("nom", "cycle", "annee_scolaire", "ecole", "is_active", "created_at")
    list_filter = ("cycle", "ecole", "annee_scolaire", "is_active")
    search_fields = ("nom",)
    readonly_fields = ("created_at", "last_update")

    def save_model(self, request, obj, form, change):  # pragma: no cover - admin
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Eleve)
class EleveAdmin(ImportExportModelAdmin):
    list_display = ("nom", "prenom", "genre", "classe", "ecole", "is_active", "created_at")
    list_filter = ("genre", "classe", "ecole", "is_active")
    search_fields = ("nom", "prenom")
    readonly_fields = ("created_at", "last_update")

    def save_model(self, request, obj, form, change):  # pragma: no cover - admin
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Cours)
class CoursAdmin(ImportExportModelAdmin):
    list_display = ("nom", "classe", "ecole", "is_active", "created_at")
    list_filter = ("classe", "ecole", "is_active")
    search_fields = ("nom", "description")
    readonly_fields = ("created_at", "last_update")

    def save_model(self, request, obj, form, change):  # pragma: no cover - admin
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)
