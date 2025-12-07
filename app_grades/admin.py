"""
Administration pour l'application app_grades.

Ce module contient les classes d'administration Django pour tous les modèles de notes.
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    GradeScale, GradeCategory, Assessment, StudentGrade, ReportCard
)


@admin.register(GradeScale)
class GradeScaleAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle GradeScale.
    """
    list_display = ['name', 'min_score', 'max_score', 'passing_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GradeCategory)
class GradeCategoryAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle GradeCategory.
    """
    list_display = ['name', 'code', 'weight', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle Assessment.
    """
    list_display = ['name', 'subject', 'class_section', 'category', 'date', 'max_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'date', 'academic_year', 'created_at']
    search_fields = ['name', 'subject__name', 'class_section__name']
    ordering = ['-date', 'subject', 'class_section']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['subject', 'class_section', 'category', 'academic_year', 'created_by', 'updated_by']


@admin.register(StudentGrade)
class StudentGradeAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle StudentGrade.
    """
    list_display = ['student', 'assessment', 'score', 'is_absent', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_absent', 'created_at']
    search_fields = ['student__profile__full_name', 'assessment__name']
    ordering = ['-assessment__date', 'student']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['student', 'assessment', 'created_by', 'updated_by']


@admin.register(ReportCard)
class ReportCardAdmin(ImportExportModelAdmin):
    """
    Administration pour le modèle ReportCard.
    """
    list_display = ['student', 'academic_year', 'term', 'overall_average', 'rank', 'is_active', 'created_at']
    list_filter = ['is_active', 'academic_year', 'term', 'created_at']
    search_fields = ['student__profile__full_name', 'term']
    ordering = ['-academic_year', 'student', '-term']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['student', 'academic_year', 'created_by', 'updated_by']
