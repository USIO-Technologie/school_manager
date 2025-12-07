"""
Vues pour la landing page du projet.

Ce module contient les vues pour la page d'accueil publique.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q
from app_profile.models import Profile, Student, Teacher, Parent
from app_academic.models import AcademicYear, Class, Subject
from app_grades.models import Assessment, StudentGrade
from app_attendance.models import Attendance


class LandingPageView(TemplateView):
    """
    Vue pour la landing page du système de gestion scolaire.
    """
    template_name = 'app_profile/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques pour la landing page
        try:
            context['total_students'] = Student.objects.filter(is_active=True).count()
            context['total_teachers'] = Teacher.objects.filter(is_active=True).count()
            context['total_parents'] = Parent.objects.filter(is_active=True).count()
            context['total_classes'] = Class.objects.filter(is_active=True).count()
            context['total_subjects'] = Subject.objects.filter(is_active=True).count()
            context['total_academic_years'] = AcademicYear.objects.filter(is_active=True).count()
        except Exception:
            # Si les tables n'existent pas encore, utiliser des valeurs par défaut
            context['total_students'] = 0
            context['total_teachers'] = 0
            context['total_parents'] = 0
            context['total_classes'] = 0
            context['total_subjects'] = 0
            context['total_academic_years'] = 0
        
        return context

