"""
Tests unitaires pour les services de app_grades.

Ce module contient les tests pour les fonctions utilitaires de calcul.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
from .models import (
    Assessment, StudentGrade, GradeCategory
)
from app_academic.models import AcademicYear, Grade, Class, Subject
from app_profile.models import Profile, Student
from .services.utils import (
    calculate_student_average,
    calculate_class_average,
    calculate_overall_average
)


class GradesServicesTestCase(TestCase):
    """Tests pour les services de calcul de notes."""
    
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
        self.subject = Subject.objects.create(
            name='Mathématiques',
            code='MATH',
            coefficient=Decimal('3.0'),
            is_active=True
        )
        self.category = GradeCategory.objects.create(
            name='Contrôle',
            code='CTRL',
            weight=Decimal('1.0'),
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
        
        # Créer des évaluations et notes
        self.assessment1 = Assessment.objects.create(
            name='Contrôle 1',
            subject=self.subject,
            class_section=self.class_section,
            category=self.category,
            date=date.today(),
            coefficient=Decimal('1.0'),
            max_score=Decimal('20.00'),
            academic_year=self.academic_year,
            is_active=True
        )
        self.assessment2 = Assessment.objects.create(
            name='Contrôle 2',
            subject=self.subject,
            class_section=self.class_section,
            category=self.category,
            date=date.today(),
            coefficient=Decimal('2.0'),
            max_score=Decimal('20.00'),
            academic_year=self.academic_year,
            is_active=True
        )
        
        StudentGrade.objects.create(
            student=self.student,
            assessment=self.assessment1,
            score=Decimal('15.00'),
            is_absent=False,
            is_active=True
        )
        StudentGrade.objects.create(
            student=self.student,
            assessment=self.assessment2,
            score=Decimal('18.00'),
            is_absent=False,
            is_active=True
        )
    
    def test_calculate_student_average(self):
        """Test le calcul de moyenne d'un élève pour une matière."""
        # Moyenne attendue : (15.00 * 1.0 + 18.00 * 2.0) / (1.0 + 2.0) = 17.00
        average = calculate_student_average(
            self.student.id,
            self.subject.id,
            self.academic_year.id
        )
        self.assertIsNotNone(average)
        self.assertEqual(average, Decimal('17.00'))
    
    def test_calculate_class_average(self):
        """Test le calcul de moyenne de classe pour une évaluation."""
        # Créer un autre élève avec une note
        user2 = User.objects.create_user(username='student2', password='test')
        profile2 = Profile.objects.get(user=user2)
        profile2.full_name = 'Student 2'
        profile2.role = 'student'
        profile2.is_active = True
        profile2.save()
        student2 = Student.objects.create(
            profile=profile2,
            class_section=self.class_section,
            academic_year=self.academic_year,
            is_active=True
        )
        StudentGrade.objects.create(
            student=student2,
            assessment=self.assessment1,
            score=Decimal('12.00'),
            is_absent=False,
            is_active=True
        )
        
        # Moyenne de classe : (15.00 + 12.00) / 2 = 13.50
        average = calculate_class_average(self.class_section.id, self.assessment1.id)
        self.assertIsNotNone(average)
        self.assertEqual(average, Decimal('13.50'))
    
    def test_calculate_overall_average(self):
        """Test le calcul de moyenne générale."""
        # Créer une autre matière avec notes
        subject2 = Subject.objects.create(
            name='Français',
            code='FR',
            coefficient=Decimal('3.0'),
            is_active=True
        )
        assessment3 = Assessment.objects.create(
            name='Contrôle Français',
            subject=subject2,
            class_section=self.class_section,
            category=self.category,
            date=date.today(),
            coefficient=Decimal('1.0'),
            max_score=Decimal('20.00'),
            academic_year=self.academic_year,
            is_active=True
        )
        StudentGrade.objects.create(
            student=self.student,
            assessment=assessment3,
            score=Decimal('16.00'),
            is_absent=False,
            is_active=True
        )
        
        # Moyenne générale : (17.00 * 3.0 + 16.00 * 3.0) / (3.0 + 3.0) = 16.50
        average = calculate_overall_average(self.student.id, self.academic_year.id)
        self.assertIsNotNone(average)
        self.assertEqual(average, Decimal('16.50'))

