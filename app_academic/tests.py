"""
Tests unitaires pour l'application app_academic.

Ce module contient les tests pour tous les modèles académiques.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from .models import (
    AcademicYear, Grade, ClassRoom, Class, Subject, Course, Schedule
)
from app_profile.models import Profile, Teacher


class AcademicYearTestCase(TestCase):
    """Tests pour le modèle AcademicYear."""
    
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
            is_active=True,
            created_by=self.user
        )
    
    def test_academic_year_creation(self):
        """Test la création d'une année scolaire."""
        self.assertIsNotNone(self.academic_year)
        self.assertEqual(self.academic_year.name, '2024-2025')
        self.assertTrue(self.academic_year.is_current)
        self.assertTrue(self.academic_year.is_active)
    
    def test_get_academic_year(self):
        """Test la méthode get_academic_year()."""
        # Test avec ID valide
        year = AcademicYear.get_academic_year(self.academic_year.id)
        self.assertIsNotNone(year)
        self.assertEqual(year.name, '2024-2025')
        
        # Test avec ID invalide
        year = AcademicYear.get_academic_year(99999)
        self.assertIsNone(year)
        
        # Test avec année inactive
        self.academic_year.is_active = False
        self.academic_year.save()
        year = AcademicYear.get_academic_year(self.academic_year.id)
        self.assertIsNone(year)
    
    def test_get_current_year(self):
        """Test la méthode get_current_year()."""
        year = AcademicYear.get_current_year()
        self.assertIsNotNone(year)
        self.assertEqual(year.name, '2024-2025')
        self.assertTrue(year.is_current)
        
        # Désactiver l'année courante
        self.academic_year.is_current = False
        self.academic_year.save()
        year = AcademicYear.get_current_year()
        self.assertIsNone(year)


class GradeTestCase(TestCase):
    """Tests pour le modèle Grade."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.grade = Grade.objects.create(
            name='6ème',
            code='6EME',
            order=6,
            is_active=True,
            created_by=self.user
        )
    
    def test_grade_creation(self):
        """Test la création d'un niveau."""
        self.assertIsNotNone(self.grade)
        self.assertEqual(self.grade.name, '6ème')
        self.assertEqual(self.grade.code, '6EME')
    
    def test_get_grade(self):
        """Test la méthode get_grade()."""
        grade = Grade.get_grade(self.grade.id)
        self.assertIsNotNone(grade)
        self.assertEqual(grade.name, '6ème')
        
        # Test avec ID invalide
        grade = Grade.get_grade(99999)
        self.assertIsNone(grade)
    
    def test_get_all_grades(self):
        """Test la méthode get_all_grades()."""
        # Créer un autre niveau
        Grade.objects.create(name='5ème', code='5EME', order=5, is_active=True)
        
        grades = Grade.get_all_grades()
        self.assertEqual(grades.count(), 2)
        self.assertTrue(all(g.is_active for g in grades))


class ClassRoomTestCase(TestCase):
    """Tests pour le modèle ClassRoom."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.classroom = ClassRoom.objects.create(
            name='Salle 101',
            capacity=30,
            floor=1,
            is_active=True,
            created_by=self.user
        )
    
    def test_classroom_creation(self):
        """Test la création d'une salle."""
        self.assertIsNotNone(self.classroom)
        self.assertEqual(self.classroom.name, 'Salle 101')
        self.assertEqual(self.classroom.capacity, 30)
    
    def test_get_classroom(self):
        """Test la méthode get_classroom()."""
        classroom = ClassRoom.get_classroom(self.classroom.id)
        self.assertIsNotNone(classroom)
        self.assertEqual(classroom.name, 'Salle 101')
        
        # Test avec ID invalide
        classroom = ClassRoom.get_classroom(99999)
        self.assertIsNone(classroom)
    
    def test_get_available_classrooms(self):
        """Test la méthode get_available_classrooms()."""
        ClassRoom.objects.create(name='Salle 102', capacity=25, is_active=True)
        
        classrooms = ClassRoom.get_available_classrooms()
        self.assertEqual(classrooms.count(), 2)
        self.assertTrue(all(c.is_active for c in classrooms))


class ClassTestCase(TestCase):
    """Tests pour le modèle Class."""
    
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
        self.grade = Grade.objects.create(
            name='6ème',
            code='6EME',
            order=6,
            is_active=True
        )
        self.classroom = ClassRoom.objects.create(
            name='Salle 101',
            capacity=30,
            is_active=True
        )
        self.class_section = Class.objects.create(
            name='6ème A',
            code='6A-2024',
            grade=self.grade,
            academic_year=self.academic_year,
            classroom=self.classroom,
            capacity=30,
            is_active=True,
            created_by=self.user
        )
    
    def test_class_creation(self):
        """Test la création d'une classe."""
        self.assertIsNotNone(self.class_section)
        self.assertEqual(self.class_section.name, '6ème A')
        self.assertEqual(self.class_section.grade, self.grade)
        self.assertEqual(self.class_section.academic_year, self.academic_year)
    
    def test_get_class(self):
        """Test la méthode get_class()."""
        class_obj = Class.get_class(self.class_section.id)
        self.assertIsNotNone(class_obj)
        self.assertEqual(class_obj.name, '6ème A')
        
        # Test avec ID invalide
        class_obj = Class.get_class(99999)
        self.assertIsNone(class_obj)
    
    def test_get_classes_by_year(self):
        """Test la méthode get_classes_by_year()."""
        classes = Class.get_classes_by_year(self.academic_year.id)
        self.assertEqual(classes.count(), 1)
        self.assertEqual(classes.first().name, '6ème A')
    
    def test_get_students_count(self):
        """Test la méthode get_students_count()."""
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        user2 = User.objects.create_user(
            username='teststudent2',
            email='student2@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=user2)
        profile.full_name = 'Test Student'
        profile.role = 'student'
        profile.is_active = True
        profile.save()
        
        from app_profile.models import Student
        student = Student.objects.create(
            profile=profile,
            class_section=self.class_section,
            academic_year=self.academic_year,
            is_active=True
        )
        
        count = self.class_section.get_students_count()
        self.assertEqual(count, 1)


class SubjectTestCase(TestCase):
    """Tests pour le modèle Subject."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.subject = Subject.objects.create(
            name='Mathématiques',
            code='MATH',
            coefficient=3.0,
            is_active=True,
            created_by=self.user
        )
    
    def test_subject_creation(self):
        """Test la création d'une matière."""
        self.assertIsNotNone(self.subject)
        self.assertEqual(self.subject.name, 'Mathématiques')
        self.assertEqual(self.subject.code, 'MATH')
    
    def test_get_subject(self):
        """Test la méthode get_subject()."""
        subject = Subject.get_subject(self.subject.id)
        self.assertIsNotNone(subject)
        self.assertEqual(subject.name, 'Mathématiques')
        
        # Test avec ID invalide
        subject = Subject.get_subject(99999)
        self.assertIsNone(subject)
    
    def test_get_all_subjects(self):
        """Test la méthode get_all_subjects()."""
        Subject.objects.create(name='Français', code='FR', coefficient=3.0, is_active=True)
        
        subjects = Subject.get_all_subjects()
        self.assertEqual(subjects.count(), 2)
        self.assertTrue(all(s.is_active for s in subjects))


class CourseTestCase(TestCase):
    """Tests pour le modèle Course."""
    
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
            coefficient=3.0,
            is_active=True
        )
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        teacher_user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=teacher_user)
        profile.full_name = 'Test Teacher'
        profile.role = 'teacher'
        profile.is_active = True
        profile.save()
        self.teacher = Teacher.objects.create(
            profile=profile,
            is_active=True
        )
        self.course = Course.objects.create(
            subject=self.subject,
            class_section=self.class_section,
            teacher=self.teacher,
            academic_year=self.academic_year,
            is_active=True,
            created_by=self.user
        )
    
    def test_course_creation(self):
        """Test la création d'un cours."""
        self.assertIsNotNone(self.course)
        self.assertEqual(self.course.subject, self.subject)
        self.assertEqual(self.course.class_section, self.class_section)
        self.assertEqual(self.course.teacher, self.teacher)
    
    def test_get_course(self):
        """Test la méthode get_course()."""
        course = Course.get_course(self.course.id)
        self.assertIsNotNone(course)
        self.assertEqual(course.subject.name, 'Mathématiques')
        
        # Test avec ID invalide
        course = Course.get_course(99999)
        self.assertIsNone(course)
    
    def test_get_courses_by_teacher(self):
        """Test la méthode get_courses_by_teacher()."""
        courses = Course.get_courses_by_teacher(self.teacher.id)
        self.assertEqual(courses.count(), 1)
        self.assertEqual(courses.first().subject.name, 'Mathématiques')
    
    def test_get_courses_by_class(self):
        """Test la méthode get_courses_by_class()."""
        courses = Course.get_courses_by_class(self.class_section.id)
        self.assertEqual(courses.count(), 1)
        self.assertEqual(courses.first().subject.name, 'Mathématiques')


class ScheduleTestCase(TestCase):
    """Tests pour le modèle Schedule."""
    
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
        self.subject = Subject.objects.create(name='Mathématiques', code='MATH', coefficient=3.0, is_active=True)
        # Créer un utilisateur et récupérer son profil (créé automatiquement par le signal)
        teacher_user = User.objects.create_user(
            username='testteacher2',
            email='teacher2@example.com',
            password='testpass123'
        )
        profile = Profile.objects.get(user=teacher_user)
        profile.full_name = 'Test Teacher'
        profile.role = 'teacher'
        profile.is_active = True
        profile.save()
        self.teacher = Teacher.objects.create(profile=profile, is_active=True)
        self.course = Course.objects.create(
            subject=self.subject,
            class_section=self.class_section,
            teacher=self.teacher,
            academic_year=self.academic_year,
            is_active=True
        )
        self.classroom = ClassRoom.objects.create(name='Salle 101', capacity=30, is_active=True)
        self.schedule = Schedule.objects.create(
            course=self.course,
            day_of_week=0,  # Lundi
            start_time='08:00:00',
            end_time='09:00:00',
            classroom=self.classroom,
            is_active=True,
            created_by=self.user
        )
    
    def test_schedule_creation(self):
        """Test la création d'un créneau."""
        self.assertIsNotNone(self.schedule)
        self.assertEqual(self.schedule.course, self.course)
        self.assertEqual(self.schedule.day_of_week, 0)
        self.assertEqual(self.schedule.classroom, self.classroom)
    
    def test_get_schedule(self):
        """Test la méthode get_schedule()."""
        schedule = Schedule.get_schedule(self.schedule.id)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.day_of_week, 0)
        
        # Test avec ID invalide
        schedule = Schedule.get_schedule(99999)
        self.assertIsNone(schedule)
    
    def test_get_schedule_by_class(self):
        """Test la méthode get_schedule_by_class()."""
        schedules = Schedule.get_schedule_by_class(self.class_section.id)
        self.assertEqual(schedules.count(), 1)
        self.assertEqual(schedules.first().day_of_week, 0)
    
    def test_get_schedule_by_teacher(self):
        """Test la méthode get_schedule_by_teacher()."""
        schedules = Schedule.get_schedule_by_teacher(self.teacher.id)
        self.assertEqual(schedules.count(), 1)
        self.assertEqual(schedules.first().day_of_week, 0)
