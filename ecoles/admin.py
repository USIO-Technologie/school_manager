from django.contrib import admin
from django.utils.html import format_html
from .models import CycleEtude, Ecole, Langue
from import_export.admin import ImportExportModelAdmin


@admin.register(Ecole)
class EcoleAdmin(ImportExportModelAdmin):
    """Interface d'admin pour le modèle Ecole."""

    # --- LISTE ---
    list_display  = (
        "logo_preview",
        "nom",
        "slogan",
        "langue_principale",
        "ville",
        "pays",
        "email_contact",
        "is_active",
        "created_at",
        
    )
    list_filter   = ("pays", "ville", "is_active", "langue_principale")
    search_fields = ("nom", "ville", "pays", "slogan", "description", "email_contact")
    ordering      = ("-created_at",)

    # --- FORM ---
    readonly_fields = ("created_at", "last_update", "logo_preview")
    prepopulated_fields = {"slug": ("nom",)}  # slug auto depuis nom
    filter_horizontal   = ("cycle", "langues")  # widget dual list

    fieldsets = (
        ("Identité de l'école", {
            "fields": (
                ("nom", "slug"),
                "slogan",
                "description",
                "logo",
                "logo_preview",
                ("theme_color", "is_active"),
            )
        }),
        ("Coordonnées", {
            "classes": ("collapse",),
            "fields": (
                ("adresse", "ville", "pays"),
                ("email_contact", "telephone_contact"),
                ("site_web", "map_link"),
            )
        }),
        ("Direction", {
            "classes": ("collapse",),
            "fields": (
                ("nom_directeur", "email_directeur", "telephone_directeur"),
            )
        }),
        ("Pédagogie & langues", {
            "classes": ("collapse",),
            "fields": (
                "cycle",
                ("langue_principale", "langues"),
                ("nombre_max_classes", "date_ouverture"),
            )
        }),
        ("Audit", {
            "classes": ("collapse",),
            "fields": (
                ("created_at", "last_update"),
                ("create_by", "update_by"),
            )
        }),
    )

    # --- APERÇU DU LOGO ---
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;" />', obj.logo.url)
        return "—"
    logo_preview.short_description = "Logo"

    # --- AUTO-RENSEIGNER create_by / update_by ---
    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)
    
@admin.register(CycleEtude)
class CycleEtudeAdmin(ImportExportModelAdmin):
    list_display   = ("nom", "niveau", "is_active", "created_at", "last_update")
    list_filter    = ("is_active",)
    search_fields  = ("nom", "description")
    readonly_fields = ("created_at", "last_update")
    fieldsets = (
        ("Informations principales", {
            "fields": ("nom", "description", "niveau", "is_active")
        }),
        ("Audit", {
            "classes": ("collapse",),
            "fields": (("created_at", "last_update"),
                       ("create_by", "update_by")),
        }),
    )
    def save_model(self, request, obj, form, change):
        """Renseigne l’utilisateur créateur / éditeur."""
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Langue)
class LangueAdmin(ImportExportModelAdmin):
    list_display   = ("code", "nom", "is_active", "created_at", "last_update")
    list_filter    = ("is_active",)
    search_fields  = ("code", "nom")
    readonly_fields = ("created_at", "last_update")
    fieldsets = (
        ("Détail", {
            "fields": ("code", "nom", "is_active")
        }),
        ("Audit", {
            "classes": ("collapse",),
            "fields": (("created_at", "last_update"),
                       ("create_by", "update_by")),
        }),
    )
    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_by = request.user
        obj.update_by = request.user
        super().save_model(request, obj, form, change)
