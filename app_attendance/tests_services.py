"""
Tests unitaires pour les services de app_attendance.

Ce module contient les tests pour les fonctions utilitaires de présence.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import AttendanceRule, Attendance, Absence
from app_academic.models import AcademicYear, Grade, Class
from app_profile.models import Profile, Student
from .services.utils import (
    calculate_attendance_rate,
    check_absence_threshold
)


class AttendanceServicesTestCase(TestCase):
    """Tests pour les services de calcul de présence."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.academic_year = AcademicYear.objects.create(
            name='2024-2025',
            start_date=date(2024, 9, 1),
            end_date=date(2025, 6, 30),
            is_current=True,
            is_active=True
        )
        self.grade = Grade.objects.create(name='6ème', code='6EME', order=6, is_active=True)
        self.class_section = Class.objects.create(
            name='6ème A',
            code='6A-2024',
            grade=self.grade,
            academic_year=self.academic_year,
            capacity=30,
            is_active=True
        )
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        student_user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=student_user)
        profile.full_name = 'Test Student'
        profile.role = 'student'
        profile.is_active = True
        profile.save()
        self.student = Student.objects.create(
            profile=profile,
            class_section=self.class_section,
            academic_year=self.academic_year,
            is_active=True
        )
        
        # Créer des présences pour les 10 derniers jours
        start_date = date.today() - timedelta(days=10)
        for i in range(10):
            current_date = start_date + timedelta(days=i)
            status = 'present' if i < 8 else 'absent'  # 8 présents, 2 absents
            Attendance.objects.create(
                student=self.student,
                class_section=self.class_section,
                date=current_date,
                status=status,
                is_active=True
            )
        
        # Créer une règle
        self.rule = AttendanceRule.objects.create(
            name='Règle standard',
            max_absences=5,
            alert_threshold=3,
            period_days=30,
            is_active=True
        )
    
    def test_calculate_attendance_rate(self):
        """Test le calcul du taux de présence."""
        start_date = date.today() - timedelta(days=10)
        end_date = date.today()
        
        rate = calculate_attendance_rate(self.student.id, start_date, end_date)
        self.assertIsNotNone(rate)
        # 8 présents sur 10 = 80%
        self.assertEqual(rate, Decimal('80.00'))
    
    def test_check_absence_threshold(self):
        """Test la vérification du seuil d'absences."""
        # Créer 6 absences non justifiées (dépassant le seuil de 5)
        for i in range(6):
            Absence.objects.create(
                student=self.student,
                start_date=date.today() - timedelta(days=30-i),
                reason=f'Absence {i+1}',
                is_justified=False,
                is_active=True
            )
        
        # Vérifier que le seuil est dépassé
        threshold_exceeded = check_absence_threshold(self.student.id, self.rule.id)
        self.assertTrue(threshold_exceeded)
        
        # Créer seulement 3 absences (sous le seuil)
        Absence.objects.filter(student=self.student).delete()
        for i in range(3):
            Absence.objects.create(
                student=self.student,
                start_date=date.today() - timedelta(days=30-i),
                reason=f'Absence {i+1}',
                is_justified=False,
                is_active=True
            )
        
        threshold_exceeded = check_absence_threshold(self.student.id, self.rule.id)
        self.assertFalse(threshold_exceeded)

