"""
Tests unitaires pour l'application app_attendance.

Ce module contient les tests pour tous les modèles de présence.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    AttendanceRule, Attendance, Absence, Excuse
)
from app_academic.models import AcademicYear, Grade, Class
from app_profile.models import Profile, Student, Teacher


class AttendanceRuleTestCase(TestCase):
    """Tests pour le modèle AttendanceRule."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.rule = AttendanceRule.objects.create(
            name='Règle standard',
            max_absences=5,
            alert_threshold=3,
            period_days=30,
            is_active=True,
            created_by=self.user
        )
    
    def test_attendance_rule_creation(self):
        """Test la création d'une règle."""
        self.assertIsNotNone(self.rule)
        self.assertEqual(self.rule.name, 'Règle standard')
        self.assertEqual(self.rule.max_absences, 5)
    
    def test_get_rule(self):
        """Test la méthode get_rule()."""
        rule = AttendanceRule.get_rule(self.rule.id)
        self.assertIsNotNone(rule)
        self.assertEqual(rule.name, 'Règle standard')
        
        # Test avec ID invalide
        rule = AttendanceRule.get_rule(99999)
        self.assertIsNone(rule)


class AttendanceTestCase(TestCase):
    """Tests pour le modèle Attendance."""
    
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
        self.attendance = Attendance.objects.create(
            student=self.student,
            class_section=self.class_section,
            date=date.today(),
            status='present',
            time_in='08:00:00',
            is_active=True,
            created_by=self.user
        )
    
    def test_attendance_creation(self):
        """Test la création d'une présence."""
        self.assertIsNotNone(self.attendance)
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.status, 'present')
    
    def test_get_attendance(self):
        """Test la méthode get_attendance()."""
        attendance = Attendance.get_attendance(self.attendance.id)
        self.assertIsNotNone(attendance)
        self.assertEqual(attendance.status, 'present')
        
        # Test avec ID invalide
        attendance = Attendance.get_attendance(99999)
        self.assertIsNone(attendance)
    
    def test_get_attendance_by_student(self):
        """Test la méthode get_attendance_by_student()."""
        attendances = Attendance.get_attendance_by_student(
            self.student.id,
            date.today() - timedelta(days=7),
            date.today()
        )
        self.assertEqual(attendances.count(), 1)
        self.assertEqual(attendances.first().status, 'present')
    
    def test_get_attendance_by_class(self):
        """Test la méthode get_attendance_by_class()."""
        attendances = Attendance.get_attendance_by_class(
            self.class_section.id,
            date.today()
        )
        self.assertEqual(attendances.count(), 1)
        self.assertEqual(attendances.first().status, 'present')


class AbsenceTestCase(TestCase):
    """Tests pour le modèle Absence."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
        self.absence = Absence.objects.create(
            student=self.student,
            start_date=date.today(),
            reason='Maladie',
            is_justified=False,
            is_active=True,
            created_by=self.user
        )
    
    def test_absence_creation(self):
        """Test la création d'une absence."""
        self.assertIsNotNone(self.absence)
        self.assertEqual(self.absence.student, self.student)
        self.assertEqual(self.absence.reason, 'Maladie')
        self.assertFalse(self.absence.is_justified)
    
    def test_get_absence(self):
        """Test la méthode get_absence()."""
        absence = Absence.get_absence(self.absence.id)
        self.assertIsNotNone(absence)
        self.assertEqual(absence.reason, 'Maladie')
        
        # Test avec ID invalide
        absence = Absence.get_absence(99999)
        self.assertIsNone(absence)
    
    def test_get_absences_by_student(self):
        """Test la méthode get_absences_by_student()."""
        absences = Absence.get_absences_by_student(self.student.id)
        self.assertEqual(absences.count(), 1)
        self.assertEqual(absences.first().reason, 'Maladie')


class ExcuseTestCase(TestCase):
    """Tests pour le modèle Excuse."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        student_user = User.objects.create_user(
            username='teststudent3',
            email='student3@example.com',
            password='testpass123'
        )
        profile_student = Profile.objects.get(user=student_user)
        profile_student.full_name = 'Test Student'
        profile_student.role = 'student'
        profile_student.is_active = True
        profile_student.save()
        self.student = Student.objects.create(
            profile=profile_student,
            is_active=True
        )
        self.absence = Absence.objects.create(
            student=self.student,
            start_date=date.today(),
            reason='Maladie',
            is_justified=False,
            is_active=True
        )
        # Créer un enseignant pour approuver
        teacher_user = User.objects.create_user(username='teacher', password='test')
        profile_teacher = Profile.objects.get(user=teacher_user)
        profile_teacher.full_name = 'Test Teacher'
        profile_teacher.role = 'teacher'
        profile_teacher.is_active = True
        profile_teacher.save()
        self.teacher = Teacher.objects.create(profile=profile_teacher, is_active=True)
        # Note: document est obligatoire mais peut être vide pour les tests
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        self.excuse = Excuse.objects.create(
            absence=self.absence,
            document=test_file,
            status='pending',
            is_active=True,
            created_by=self.user
        )
    
    def test_excuse_creation(self):
        """Test la création d'un justificatif."""
        self.assertIsNotNone(self.excuse)
        self.assertEqual(self.excuse.absence, self.absence)
        self.assertEqual(self.excuse.status, 'pending')
    
    def test_get_excuse(self):
        """Test la méthode get_excuse()."""
        excuse = Excuse.get_excuse(self.excuse.id)
        self.assertIsNotNone(excuse)
        self.assertEqual(excuse.status, 'pending')
        
        # Test avec ID invalide
        excuse = Excuse.get_excuse(99999)
        self.assertIsNone(excuse)
    
    def test_approve_excuse(self):
        """Test la méthode approve_excuse()."""
        self.excuse.approve_excuse(self.teacher.id)
        self.excuse.refresh_from_db()
        self.assertEqual(self.excuse.status, 'approved')
        self.assertEqual(self.excuse.reviewed_by, self.teacher)
        self.assertIsNotNone(self.excuse.reviewed_at)
        # Vérifier que l'absence est justifiée
        self.absence.refresh_from_db()
        self.assertTrue(self.absence.is_justified)
    
    def test_reject_excuse(self):
        """Test la méthode reject_excuse()."""
        self.excuse.reject_excuse(self.teacher.id, 'Document invalide')
        self.excuse.refresh_from_db()
        self.assertEqual(self.excuse.status, 'rejected')
        self.assertEqual(self.excuse.reviewed_by, self.teacher)
        self.assertEqual(self.excuse.notes, 'Document invalide')
