"""
Tests unitaires pour les relations académiques dans app_profile.

Ce module contient les tests pour les nouvelles relations ForeignKey et ManyToMany.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from .models import Profile, Student, Teacher, Parent
from app_academic.models import AcademicYear, Grade, Class, Subject


class StudentRelationsTestCase(TestCase):
    """Tests pour les relations académiques de Student."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Student'
        )
        # Le profil est créé automatiquement par le signal
        self.profile = Profile.objects.get(user=self.user)
        self.profile.full_name = 'Test Student'
        self.profile.role = 'student'
        self.profile.is_active = True
        self.profile.save()
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
        self.student = Student.objects.create(
            profile=self.profile,
            class_section=self.class_section,
            academic_year=self.academic_year,
            is_active=True
        )
    
    def test_student_class_section_relation(self):
        """Test la relation ForeignKey class_section."""
        self.assertIsNotNone(self.student.class_section)
        self.assertEqual(self.student.class_section.name, '6ème A')
        self.assertEqual(self.student.class_section.grade, self.grade)
    
    def test_student_academic_year_relation(self):
        """Test la relation ForeignKey academic_year."""
        self.assertIsNotNone(self.student.academic_year)
        self.assertEqual(self.student.academic_year.name, '2024-2025')
    
    def test_student_reverse_relation(self):
        """Test la relation inverse depuis Class."""
        students = self.class_section.students.all()
        self.assertIn(self.student, students)
    
    def test_student_can_be_created_without_class(self):
        """Test qu'un élève peut être créé sans classe."""
        user2 = User.objects.create_user(username='student2', password='test')
        profile2 = Profile.objects.get(user=user2)
        profile2.full_name = 'Student 2'
        profile2.role = 'student'
        profile2.is_active = True
        profile2.save()
        student2 = Student.objects.create(profile=profile2, is_active=True)
        self.assertIsNone(student2.class_section)
        self.assertIsNone(student2.academic_year)


class TeacherRelationsTestCase(TestCase):
    """Tests pour les relations académiques de Teacher."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testteacher',
            email='teacher@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher'
        )
        # Le profil est créé automatiquement par le signal
        self.profile = Profile.objects.get(user=self.user)
        self.profile.full_name = 'Test Teacher'
        self.profile.role = 'teacher'
        self.profile.is_active = True
        self.profile.save()
        self.teacher = Teacher.objects.create(profile=self.profile, is_active=True)
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
        self.subject1 = Subject.objects.create(name='Mathématiques', code='MATH', coefficient=3.0, is_active=True)
        self.subject2 = Subject.objects.create(name='Français', code='FR', coefficient=3.0, is_active=True)
    
    def test_teacher_subjects_relation(self):
        """Test la relation ManyToMany subjects."""
        self.teacher.subjects.add(self.subject1, self.subject2)
        self.assertEqual(self.teacher.subjects.count(), 2)
        self.assertIn(self.subject1, self.teacher.subjects.all())
        self.assertIn(self.subject2, self.teacher.subjects.all())
    
    def test_teacher_classes_relation(self):
        """Test la relation ManyToMany classes."""
        self.teacher.classes.add(self.class_section)
        self.assertEqual(self.teacher.classes.count(), 1)
        self.assertIn(self.class_section, self.teacher.classes.all())
    
    def test_teacher_reverse_relations(self):
        """Test les relations inverses."""
        self.teacher.subjects.add(self.subject1)
        self.teacher.classes.add(self.class_section)
        
        # Vérifier depuis Subject
        teachers = self.subject1.teachers.all()
        self.assertIn(self.teacher, teachers)
        
        # Vérifier depuis Class
        teachers = self.class_section.teachers.all()
        self.assertIn(self.teacher, teachers)
    
    def test_teacher_can_have_multiple_subjects(self):
        """Test qu'un enseignant peut avoir plusieurs matières."""
        subject3 = Subject.objects.create(name='Sciences', code='SCI', coefficient=2.0, is_active=True)
        self.teacher.subjects.add(self.subject1, self.subject2, subject3)
        self.assertEqual(self.teacher.subjects.count(), 3)
    
    def test_teacher_can_have_multiple_classes(self):
        """Test qu'un enseignant peut avoir plusieurs classes."""
        class2 = Class.objects.create(
            name='6ème B',
            code='6B-2024',
            grade=self.grade,
            academic_year=self.academic_year,
            capacity=30,
            is_active=True
        )
        self.teacher.classes.add(self.class_section, class2)
        self.assertEqual(self.teacher.classes.count(), 2)


class ParentRelationsTestCase(TestCase):
    """Tests pour les relations de Parent avec les enfants."""
    
    def setUp(self):
        """Préparation des données de test."""
        self.user = User.objects.create_user(
            username='testparent',
            email='parent@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Parent'
        )
        # Le profil est créé automatiquement par le signal
        self.profile = Profile.objects.get(user=self.user)
        self.profile.full_name = 'Test Parent'
        self.profile.role = 'parent'
        self.profile.is_active = True
        self.profile.save()
        self.parent = Parent.objects.create(profile=self.profile, is_active=True)
        
        # Créer des enfants
        user1 = User.objects.create_user(username='child1', password='test')
        profile1 = Profile.objects.get(user=user1)
        profile1.full_name = 'Child 1'
        profile1.role = 'student'
        profile1.is_active = True
        profile1.save()
        self.student1 = Student.objects.create(profile=profile1, is_active=True)
        
        user2 = User.objects.create_user(username='child2', password='test')
        profile2 = Profile.objects.get(user=user2)
        profile2.full_name = 'Child 2'
        profile2.role = 'student'
        profile2.is_active = True
        profile2.save()
        self.student2 = Student.objects.create(profile=profile2, is_active=True)
    
    def test_parent_children_relation(self):
        """Test la relation ManyToMany children."""
        self.parent.children.add(self.student1, self.student2)
        self.assertEqual(self.parent.children.count(), 2)
        self.assertIn(self.student1, self.parent.children.all())
        self.assertIn(self.student2, self.parent.children.all())
    
    def test_parent_reverse_relation(self):
        """Test la relation inverse depuis Student."""
        self.parent.children.add(self.student1)
        
        # Vérifier depuis Student
        parents = self.student1.parents.all()
        self.assertIn(self.parent, parents)
    
    def test_parent_can_have_multiple_children(self):
        """Test qu'un parent peut avoir plusieurs enfants."""
        user3 = User.objects.create_user(username='child3', password='test')
        profile3 = Profile.objects.get(user=user3)
        profile3.full_name = 'Child 3'
        profile3.role = 'student'
        profile3.is_active = True
        profile3.save()
        student3 = Student.objects.create(profile=profile3, is_active=True)
        
        self.parent.children.add(self.student1, self.student2, student3)
        self.assertEqual(self.parent.children.count(), 3)
    
    def test_student_can_have_multiple_parents(self):
        """Test qu'un élève peut avoir plusieurs parents."""
        user2 = User.objects.create_user(username='parent2', password='test')
        profile2 = Profile.objects.get(user=user2)
        profile2.full_name = 'Parent 2'
        profile2.role = 'parent'
        profile2.is_active = True
        profile2.save()
        parent2 = Parent.objects.create(profile=profile2, is_active=True)
        
        self.parent.children.add(self.student1)
        parent2.children.add(self.student1)
        
        # L'élève doit avoir 2 parents
        self.assertEqual(self.student1.parents.count(), 2)

