"""
Configuration des URLs pour l'application app_attendance.

Ce module contient les routes pour la gestion des présences.
"""

from django.urls import path
from . import views

app_name = 'app_attendance'

urlpatterns = [
    # Attendance Rule
    path('attendance-rules/', views.AttendanceRuleListView.as_view(), name='attendance_rule_list'),
    path('attendance-rules/<int:pk>/', views.AttendanceRuleDetailView.as_view(), name='attendance_rule_detail'),
    path('attendance-rules/create/', views.AttendanceRuleCreateView.as_view(), name='attendance_rule_create'),
    path('attendance-rules/<int:pk>/update/', views.AttendanceRuleUpdateView.as_view(), name='attendance_rule_update'),
    
    # Attendance
    path('attendances/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendances/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendances/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendances/<int:pk>/update/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    
    # Absence
    path('absences/', views.AbsenceListView.as_view(), name='absence_list'),
    path('absences/<int:pk>/', views.AbsenceDetailView.as_view(), name='absence_detail'),
    path('absences/create/', views.AbsenceCreateView.as_view(), name='absence_create'),
    path('absences/<int:pk>/update/', views.AbsenceUpdateView.as_view(), name='absence_update'),
    
    # Excuse
    path('excuses/', views.ExcuseListView.as_view(), name='excuse_list'),
    path('excuses/<int:pk>/', views.ExcuseDetailView.as_view(), name='excuse_detail'),
    path('excuses/create/', views.ExcuseCreateView.as_view(), name='excuse_create'),
    path('excuses/<int:pk>/update/', views.ExcuseUpdateView.as_view(), name='excuse_update'),
]
