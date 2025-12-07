"""
Tests unitaires pour l'application app_grades.

Ce module contient les tests pour tous les modèles de notes.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import (
    GradeScale, GradeCategory, Assessment, StudentGrade, ReportCard
)
from app_academic.models import AcademicYear, Grade, Class, Subject
from app_profile.models import Profile, Student, Teacher


class GradeScaleTestCase(TestCase):
    """Tests pour le modèle GradeScale."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.grade_scale = GradeScale.objects.create(
            name='0-20',
            min_score=Decimal('0.00'),
            max_score=Decimal('20.00'),
            passing_score=Decimal('10.00'),
            is_active=True,
            created_by=self.user
        )
    
    def test_grade_scale_creation(self):
        """Test la création d'un barème."""
        self.assertIsNotNone(self.grade_scale)
        self.assertEqual(self.grade_scale.name, '0-20')
        self.assertEqual(self.grade_scale.max_score, Decimal('20.00'))
    
    def test_get_grade_scale(self):
        """Test la méthode get_grade_scale()."""
        scale = GradeScale.get_grade_scale(self.grade_scale.id)
        self.assertIsNotNone(scale)
        self.assertEqual(scale.name, '0-20')
        
        # Test avec ID invalide
        scale = GradeScale.get_grade_scale(99999)
        self.assertIsNone(scale)


class GradeCategoryTestCase(TestCase):
    """Tests pour le modèle GradeCategory."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = GradeCategory.objects.create(
            name='Contrôle continu',
            code='CC',
            weight=Decimal('1.0'),
            is_active=True,
            created_by=self.user
        )
    
    def test_category_creation(self):
        """Test la création d'une catégorie."""
        self.assertIsNotNone(self.category)
        self.assertEqual(self.category.name, 'Contrôle continu')
        self.assertEqual(self.category.code, 'CC')
    
    def test_get_category(self):
        """Test la méthode get_category()."""
        category = GradeCategory.get_category(self.category.id)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, 'Contrôle continu')
        
        # Test avec ID invalide
        category = GradeCategory.get_category(99999)
        self.assertIsNone(category)


class AssessmentTestCase(TestCase):
    """Tests pour le modèle Assessment."""
    
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
        self.assessment = Assessment.objects.create(
            name='Contrôle de Mathématiques',
            subject=self.subject,
            class_section=self.class_section,
            category=self.category,
            date=date.today(),
            coefficient=Decimal('1.0'),
            max_score=Decimal('20.00'),
            academic_year=self.academic_year,
            is_active=True,
            created_by=self.user
        )
    
    def test_assessment_creation(self):
        """Test la création d'une évaluation."""
        self.assertIsNotNone(self.assessment)
        self.assertEqual(self.assessment.name, 'Contrôle de Mathématiques')
        self.assertEqual(self.assessment.subject, self.subject)
        self.assertEqual(self.assessment.class_section, self.class_section)
    
    def test_get_assessment(self):
        """Test la méthode get_assessment()."""
        assessment = Assessment.get_assessment(self.assessment.id)
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.name, 'Contrôle de Mathématiques')
        
        # Test avec ID invalide
        assessment = Assessment.get_assessment(99999)
        self.assertIsNone(assessment)
    
    def test_get_assessments_by_class(self):
        """Test la méthode get_assessments_by_class()."""
        assessments = Assessment.get_assessments_by_class(self.class_section.id)
        self.assertEqual(assessments.count(), 1)
        self.assertEqual(assessments.first().name, 'Contrôle de Mathématiques')


class StudentGradeTestCase(TestCase):
    """Tests pour le modèle StudentGrade."""
    
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
        self.assessment = Assessment.objects.create(
            name='Contrôle de Mathématiques',
            subject=self.subject,
            class_section=self.class_section,
            category=self.category,
            date=date.today(),
            coefficient=Decimal('1.0'),
            max_score=Decimal('20.00'),
            academic_year=self.academic_year,
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
        self.student_grade = StudentGrade.objects.create(
            student=self.student,
            assessment=self.assessment,
            score=Decimal('15.50'),
            is_absent=False,
            is_active=True,
            created_by=self.user
        )
    
    def test_student_grade_creation(self):
        """Test la création d'une note."""
        self.assertIsNotNone(self.student_grade)
        self.assertEqual(self.student_grade.student, self.student)
        self.assertEqual(self.student_grade.assessment, self.assessment)
        self.assertEqual(self.student_grade.score, Decimal('15.50'))
    
    def test_get_student_grade(self):
        """Test la méthode get_student_grade()."""
        grade = StudentGrade.get_student_grade(self.student_grade.id)
        self.assertIsNotNone(grade)
        self.assertEqual(grade.score, Decimal('15.50'))
        
        # Test avec ID invalide
        grade = StudentGrade.get_student_grade(99999)
        self.assertIsNone(grade)
    
    def test_get_grades_by_student(self):
        """Test la méthode get_grades_by_student()."""
        grades = StudentGrade.get_grades_by_student(self.student.id)
        self.assertEqual(grades.count(), 1)
        self.assertEqual(grades.first().score, Decimal('15.50'))
    
    def test_calculate_average(self):
        """Test la méthode calculate_average()."""
        # Créer une autre évaluation et note
        assessment2 = Assessment.objects.create(
            name='Devoir de Mathématiques',
            subject=self.subject,
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
            assessment=assessment2,
            score=Decimal('18.00'),
            is_absent=False,
            is_active=True
        )
        
        # Calculer la moyenne
        average = StudentGrade.calculate_average(
            self.student.id,
            self.subject.id,
            self.academic_year.id
        )
        self.assertIsNotNone(average)
        # Moyenne attendue : (15.50 + 18.00) / 2 = 16.75
        self.assertEqual(average, Decimal('16.75'))


class ReportCardTestCase(TestCase):
    """Tests pour le modèle ReportCard."""
    
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
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        student_user = User.objects.create_user(
            username='teststudent2',
            email='student2@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=student_user)
        profile.full_name = 'Test Student'
        profile.role = 'student'
        profile.is_active = True
        profile.save()
        self.student = Student.objects.create(
            profile=profile,
            is_active=True
        )
        self.report_card = ReportCard.objects.create(
            student=self.student,
            academic_year=self.academic_year,
            term='Trimestre 1',
            overall_average=Decimal('15.50'),
            rank=5,
            total_students=30,
            is_active=True,
            created_by=self.user
        )
    
    def test_report_card_creation(self):
        """Test la création d'un bulletin."""
        self.assertIsNotNone(self.report_card)
        self.assertEqual(self.report_card.student, self.student)
        self.assertEqual(self.report_card.term, 'Trimestre 1')
        self.assertEqual(self.report_card.overall_average, Decimal('15.50'))
    
    def test_get_report_card(self):
        """Test la méthode get_report_card()."""
        report_card = ReportCard.get_report_card(self.report_card.id)
        self.assertIsNotNone(report_card)
        self.assertEqual(report_card.term, 'Trimestre 1')
        
        # Test avec ID invalide
        report_card = ReportCard.get_report_card(99999)
        self.assertIsNone(report_card)
    
    def test_generate_report_card(self):
        """Test la méthode generate_report_card()."""
        report_card = ReportCard.generate_report_card(
            self.student.id,
            self.academic_year.id,
            'Trimestre 2'
        )
        self.assertIsNotNone(report_card)
        self.assertEqual(report_card.term, 'Trimestre 2')
        self.assertEqual(report_card.student, self.student)
