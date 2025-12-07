"""
Administration pour l'application app_academic.

Ce module contient les classes d'administration Django pour tous les modèles académiques.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    AcademicYear, Grade, ClassRoom, Class, Subject, Course, Schedule
)


@admin.register(AcademicYear)
class AcademicYearAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle AcademicYear.
    """
    list_display = ['name', 'start_date', 'end_date', 'is_current', 'is_active', 'created_at']
    list_filter = ['is_current', 'is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['name']
    ordering = ['-start_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'start_date', 'end_date', 'is_current')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Grade)
class GradeAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Grade.
    """
    list_display = ['name', 'code', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'code', 'order', 'description')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClassRoom)
class ClassRoomAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle ClassRoom.
    """
    list_display = ['name', 'capacity', 'floor', 'is_active', 'created_at']
    list_filter = ['is_active', 'floor', 'created_at']
    search_fields = ['name', 'equipment']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'capacity', 'floor', 'equipment')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Class)
class ClassAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Class.
    """
    list_display = ['name', 'code', 'grade', 'academic_year', 'capacity', 'teacher', 'is_active', 'created_at']
    list_filter = ['is_active', 'grade', 'academic_year', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['academic_year', 'grade__order', 'name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['grade', 'academic_year', 'classroom', 'teacher', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'code', 'grade', 'academic_year')
        }),
        ('Organisation', {
            'fields': ('classroom', 'capacity', 'teacher')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Subject.
    """
    list_display = ['name', 'code', 'coefficient', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'code', 'description', 'coefficient')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Course.
    """
    list_display = ['subject', 'class_section', 'teacher', 'academic_year', 'is_active', 'created_at']
    list_filter = ['is_active', 'academic_year', 'created_at']
    search_fields = ['subject__name', 'class_section__name', 'teacher__profile__full_name']
    ordering = ['academic_year', 'class_section', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['subject', 'class_section', 'teacher', 'academic_year', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('subject', 'class_section', 'teacher', 'academic_year')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Schedule.
    """
    list_display = ['course', 'get_day_display', 'start_time', 'end_time', 'classroom', 'is_active', 'created_at']
    list_filter = ['is_active', 'day_of_week', 'created_at']
    search_fields = ['course__subject__name', 'course__class_section__name', 'classroom__name']
    ordering = ['day_of_week', 'start_time']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['course', 'classroom', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('course', 'day_of_week', 'start_time', 'end_time', 'classroom')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_day_display(self, obj):
        """Affiche le jour de la semaine."""
        return dict(Schedule.DAY_CHOICES)[obj.day_of_week]
    get_day_display.short_description = 'Jour'
    get_day_display.admin_order_field = 'day_of_week'
