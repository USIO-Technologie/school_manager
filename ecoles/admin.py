from django.contrib import admin

from .models import Ecole


@admin.register(Ecole)
class EcoleAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "pays", "est_active")
    prepopulated_fields = {"slug": ("nom",)}
