from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(ImportExportModelAdmin):
    list_display = ("eleve", "montant", "date_paiement", "ecole", "created_at")
    list_filter = ("ecole", "date_paiement")
    search_fields = ("eleve__nom", "eleve__prenom")
    readonly_fields = ("created_at", "last_update")

    def save_model(self, request, obj, form, change):  # pragma: no cover - admin
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)
