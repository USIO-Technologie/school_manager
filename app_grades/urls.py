"""
Configuration des URLs pour l'application app_grades.

Ce module contient les routes pour la gestion des notes.
"""

from django.urls import path
from . import views

app_name = 'app_grades'

urlpatterns = [
    # Grade Scale
    path('grade-scales/', views.GradeScaleListView.as_view(), name='grade_scale_list'),
    path('grade-scales/<int:pk>/', views.GradeScaleDetailView.as_view(), name='grade_scale_detail'),
    path('grade-scales/create/', views.GradeScaleCreateView.as_view(), name='grade_scale_create'),
    path('grade-scales/<int:pk>/update/', views.GradeScaleUpdateView.as_view(), name='grade_scale_update'),
    
    # Grade Category
    path('grade-categories/', views.GradeCategoryListView.as_view(), name='grade_category_list'),
    path('grade-categories/<int:pk>/', views.GradeCategoryDetailView.as_view(), name='grade_category_detail'),
    path('grade-categories/create/', views.GradeCategoryCreateView.as_view(), name='grade_category_create'),
    path('grade-categories/<int:pk>/update/', views.GradeCategoryUpdateView.as_view(), name='grade_category_update'),
    
    # Assessment
    path('assessments/', views.AssessmentListView.as_view(), name='assessment_list'),
    path('assessments/<int:pk>/', views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path('assessments/create/', views.AssessmentCreateView.as_view(), name='assessment_create'),
    path('assessments/<int:pk>/update/', views.AssessmentUpdateView.as_view(), name='assessment_update'),
    
    # Student Grade
    path('grades/', views.StudentGradeListView.as_view(), name='grade_list'),
    path('grades/<int:pk>/', views.StudentGradeDetailView.as_view(), name='student_grade_detail'),
    path('grades/create/', views.StudentGradeCreateView.as_view(), name='student_grade_create'),
    path('grades/<int:pk>/update/', views.StudentGradeUpdateView.as_view(), name='student_grade_update'),
    
    # Report Card
    path('report-cards/', views.ReportCardListView.as_view(), name='report_card_list'),
    path('report-cards/<int:pk>/', views.ReportCardDetailView.as_view(), name='report_card_detail'),
    path('report-cards/create/', views.ReportCardCreateView.as_view(), name='report_card_create'),
    path('report-cards/<int:pk>/update/', views.ReportCardUpdateView.as_view(), name='report_card_update'),
]
