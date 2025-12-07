"""
Configuration des URLs pour l'application app_academic.

Ce module contient les routes pour la gestion académique.
"""

from django.urls import path
from . import views

app_name = 'app_academic'

urlpatterns = [
    # Academic Year
    path('academic-years/', views.AcademicYearListView.as_view(), name='academic_year_list'),
    path('academic-years/<int:pk>/', views.AcademicYearDetailView.as_view(), name='academic_year_detail'),
    path('academic-years/create/', views.AcademicYearCreateView.as_view(), name='academic_year_create'),
    path('academic-years/<int:pk>/update/', views.AcademicYearUpdateView.as_view(), name='academic_year_update'),
    
    # Grade
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    path('grades/<int:pk>/', views.GradeDetailView.as_view(), name='grade_detail'),
    path('grades/create/', views.GradeCreateView.as_view(), name='grade_create'),
    path('grades/<int:pk>/update/', views.GradeUpdateView.as_view(), name='grade_update'),
    
    # Classroom
    path('classrooms/', views.ClassroomListView.as_view(), name='classroom_list'),
    path('classrooms/<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    path('classrooms/create/', views.ClassroomCreateView.as_view(), name='classroom_create'),
    path('classrooms/<int:pk>/update/', views.ClassroomUpdateView.as_view(), name='classroom_update'),
    
    # Class
    path('classes/', views.ClassListView.as_view(), name='class_list'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class_detail'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class_create'),
    path('classes/<int:pk>/update/', views.ClassUpdateView.as_view(), name='class_update'),
    
    # Subject
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/update/', views.SubjectUpdateView.as_view(), name='subject_update'),
    
    # Course
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),
    
    # Schedule
    path('schedules/', views.ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/<int:pk>/', views.ScheduleDetailView.as_view(), name='schedule_detail'),
    path('schedules/create/', views.ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/<int:pk>/update/', views.ScheduleUpdateView.as_view(), name='schedule_update'),
]
