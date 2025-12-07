"""
Administration pour l'application app_attendance.

Ce module contient les classes d'administration Django pour tous les modèles de présence.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    AttendanceRule, Attendance, Absence, Excuse
)


@admin.register(AttendanceRule)
class AttendanceRuleAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle AttendanceRule.
    """
    list_display = ['name', 'max_absences', 'alert_threshold', 'period_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Attendance.
    """
    list_display = ['student', 'class_section', 'date', 'status', 'time_in', 'is_active', 'created_at']
    list_filter = ['is_active', 'status', 'date', 'created_at']
    search_fields = ['student__profile__full_name', 'class_section__name']
    ordering = ['-date', 'student']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['student', 'class_section', 'created_by', 'updated_by']


@admin.register(Absence)
class AbsenceAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Absence.
    """
    list_display = ['student', 'start_date', 'end_date', 'is_justified', 'justified_by', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_justified', 'start_date', 'created_at']
    search_fields = ['student__profile__full_name', 'reason']
    ordering = ['-start_date', 'student']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['student', 'justified_by', 'created_by', 'updated_by']


@admin.register(Excuse)
class ExcuseAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Excuse.
    """
    list_display = ['absence', 'status', 'reviewed_by', 'reviewed_at', 'is_active', 'created_at']
    list_filter = ['is_active', 'status', 'created_at', 'reviewed_at']
    search_fields = ['absence__student__profile__full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    raw_id_fields = ['absence', 'reviewed_by', 'created_by', 'updated_by']
