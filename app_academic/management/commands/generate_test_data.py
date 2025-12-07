"""
Commande de management pour générer des données de test.

Usage:
    python manage.py generate_test_data
    python manage.py generate_test_data --clear
    python manage.py generate_test_data --students=50
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

from app_academic.models import AcademicYear, Grade, ClassRoom, Class, Subject, Course, Schedule
from app_profile.models import Profile, Student, Teacher, Parent
from app_grades.models import GradeScale, GradeCategory, Assessment, StudentGrade, ReportCard
from app_attendance.models import AttendanceRule, Attendance, Absence, Excuse


class Command(BaseCommand):
    help = 'Generate test data for the school management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data',
        )
        parser.add_argument(
            '--students',
            type=int,
            default=30,
            help='Number of students to create (default: 30)',
        )
        parser.add_argument(
            '--teachers',
            type=int,
            default=10,
            help='Number of teachers to create (default: 10)',
        )
        parser.add_argument(
            '--parents',
            type=int,
            default=20,
            help='Number of parents to create (default: 20)',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)
        num_students = options.get('students', 30)
        num_teachers = options.get('teachers', 10)
        num_parents = options.get('parents', 20)
        
        if clear:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self._clear_data()
        
        self.stdout.write('Generating test data...')
        
        with transaction.atomic():
            # Créer un utilisateur admin pour les champs created_by
            admin_user, _ = User.objects.get_or_create(
                username='admin_test',
                defaults={'email': 'admin@test.com', 'is_staff': True, 'is_superuser': True}
            )
            admin_user.set_password('admin123')
            admin_user.save()
            
            # 1. Années scolaires
            self.stdout.write('Creating academic years...')
            academic_years = self._create_academic_years(admin_user)
            
            # 2. Niveaux
            self.stdout.write('Creating grades...')
            grades = self._create_grades(admin_user)
            
            # 3. Salles de classe
            self.stdout.write('Creating classrooms...')
            classrooms = self._create_classrooms(admin_user)
            
            # 4. Matières
            self.stdout.write('Creating subjects...')
            subjects = self._create_subjects(admin_user)
            
            # 5. Classes
            self.stdout.write('Creating classes...')
            classes = self._create_classes(academic_years, grades, classrooms, admin_user)
            
            # 6. Enseignants
            self.stdout.write(f'Creating {num_teachers} teachers...')
            teachers = self._create_teachers(num_teachers, subjects, classes, admin_user)
            
            # 7. Cours
            self.stdout.write('Creating courses...')
            courses = self._create_courses(subjects, classes, teachers, academic_years, admin_user)
            
            # 8. Emploi du temps
            self.stdout.write('Creating schedules...')
            self._create_schedules(courses, classrooms, admin_user)
            
            # 9. Élèves
            self.stdout.write(f'Creating {num_students} students...')
            students = self._create_students(num_students, classes, academic_years, admin_user)
            
            # 10. Parents
            self.stdout.write(f'Creating {num_parents} parents...')
            parents = self._create_parents(num_parents, students, admin_user)
            
            # 11. Barèmes et catégories
            self.stdout.write('Creating grade scales and categories...')
            grade_scales = self._create_grade_scales(admin_user)
            categories = self._create_grade_categories(admin_user)
            
            # 12. Évaluations
            self.stdout.write('Creating assessments...')
            assessments = self._create_assessments(subjects, classes, categories, academic_years, admin_user)
            
            # 13. Notes
            self.stdout.write('Creating grades...')
            self._create_student_grades(students, assessments, admin_user)
            
            # 14. Bulletins
            self.stdout.write('Creating report cards...')
            self._create_report_cards(students, academic_years, admin_user)
            
            # 15. Règles de présence
            self.stdout.write('Creating attendance rules...')
            rules = self._create_attendance_rules(admin_user)
            
            # 16. Présences
            self.stdout.write('Creating attendance records...')
            self._create_attendances(students, classes, academic_years, admin_user)
            
            # 17. Absences
            self.stdout.write('Creating absences...')
            absences = self._create_absences(students, academic_years, admin_user)
            
            # 18. Justificatifs
            self.stdout.write('Creating excuses...')
            self._create_excuses(absences, teachers, admin_user)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Successfully generated test data!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Academic Years: {AcademicYear.objects.count()}')
        self.stdout.write(f'  - Grades: {Grade.objects.count()}')
        self.stdout.write(f'  - Classrooms: {ClassRoom.objects.count()}')
        self.stdout.write(f'  - Classes: {Class.objects.count()}')
        self.stdout.write(f'  - Subjects: {Subject.objects.count()}')
        self.stdout.write(f'  - Teachers: {Teacher.objects.count()}')
        self.stdout.write(f'  - Students: {Student.objects.count()}')
        self.stdout.write(f'  - Parents: {Parent.objects.count()}')
        self.stdout.write(f'  - Courses: {Course.objects.count()}')
        self.stdout.write(f'  - Assessments: {Assessment.objects.count()}')
        self.stdout.write(f'  - Student Grades: {StudentGrade.objects.count()}')
        self.stdout.write(f'  - Attendances: {Attendance.objects.count()}')
        self.stdout.write(f'\nAdmin user: admin_test / admin123\n')
    
    def _clear_data(self):
        """Supprime toutes les données de test."""
        Excuse.objects.all().delete()
        Absence.objects.all().delete()
        Attendance.objects.all().delete()
        AttendanceRule.objects.all().delete()
        ReportCard.objects.all().delete()
        StudentGrade.objects.all().delete()
        Assessment.objects.all().delete()
        GradeCategory.objects.all().delete()
        GradeScale.objects.all().delete()
        Schedule.objects.all().delete()
        Course.objects.all().delete()
        Parent.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Class.objects.all().delete()
        Subject.objects.all().delete()
        ClassRoom.objects.all().delete()
        Grade.objects.all().delete()
        AcademicYear.objects.all().delete()
        # Ne pas supprimer les profils et utilisateurs pour éviter les problèmes
    
    def _create_academic_years(self, admin_user):
        """Crée des années scolaires."""
        years = []
        current_year = date.today().year
        for i in range(3):
            year_name = f"{current_year - 1 + i}-{current_year + i}"
            start_date = date(current_year - 1 + i, 9, 1)
            end_date = date(current_year + i, 6, 30)
            is_current = (i == 1)  # L'année du milieu est courante
            
            year, _ = AcademicYear.objects.get_or_create(
                name=year_name,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_current': is_current,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            years.append(year)
        return years
    
    def _create_grades(self, admin_user):
        """Crée des niveaux scolaires."""
        grade_names = [
            ('CP', 'CP', 1),
            ('CE1', 'CE1', 2),
            ('CE2', 'CE2', 3),
            ('CM1', 'CM1', 4),
            ('CM2', 'CM2', 5),
            ('6ème', '6EME', 6),
            ('5ème', '5EME', 7),
            ('4ème', '4EME', 8),
            ('3ème', '3EME', 9),
        ]
        grades = []
        for name, code, order in grade_names:
            grade, _ = Grade.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'order': order,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            grades.append(grade)
        return grades
    
    def _create_classrooms(self, admin_user):
        """Crée des salles de classe."""
        classrooms = []
        for i in range(1, 16):
            name = f'Salle {100 + i}'
            capacity = random.randint(25, 35)
            floor = random.randint(1, 3)
            
            classroom, _ = ClassRoom.objects.get_or_create(
                name=name,
                defaults={
                    'capacity': capacity,
                    'floor': floor,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            classrooms.append(classroom)
        return classrooms
    
    def _create_subjects(self, admin_user):
        """Crée des matières."""
        subjects_data = [
            ('Mathématiques', 'MATH', 3.0),
            ('Français', 'FR', 3.0),
            ('Histoire-Géographie', 'HIST-GEO', 2.0),
            ('Sciences', 'SCI', 2.0),
            ('Anglais', 'ANG', 2.0),
            ('Espagnol', 'ESP', 2.0),
            ('Physique-Chimie', 'PC', 2.0),
            ('SVT', 'SVT', 2.0),
            ('EPS', 'EPS', 1.0),
            ('Arts Plastiques', 'ART', 1.0),
        ]
        subjects = []
        for name, code, coefficient in subjects_data:
            subject, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'coefficient': Decimal(str(coefficient)),
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            subjects.append(subject)
        return subjects
    
    def _create_classes(self, academic_years, grades, classrooms, admin_user):
        """Crée des classes."""
        classes = []
        current_year = academic_years[1]  # Année courante
        
        for grade in grades[5:]:  # À partir de la 6ème
            for letter in ['A', 'B']:
                class_name = f"{grade.name} {letter}"
                code = f"{grade.code}{letter}-{current_year.name[:4]}"
                classroom = random.choice(classrooms) if classrooms else None
                
                class_obj, _ = Class.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': class_name,
                        'grade': grade,
                        'academic_year': current_year,
                        'classroom': classroom,
                        'capacity': 30,
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
                classes.append(class_obj)
        return classes
    
    def _create_teachers(self, num_teachers, subjects, classes, admin_user):
        """Crée des enseignants."""
        teachers = []
        first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Anne', 'Paul', 'Julie', 'Marc', 'Claire']
        last_names = ['Dupont', 'Martin', 'Bernard', 'Dubois', 'Laurent', 'Moreau', 'Simon', 'Michel', 'Garcia', 'David']
        
        for i in range(num_teachers):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'teacher_{i+1}'
            email = f'{username}@school.com'
            
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
            )
            user.set_password('teacher123')
            user.save()
            
            profile = Profile.objects.get(user=user)
            profile.full_name = f'{first_name} {last_name}'
            profile.role = 'teacher'
            profile.is_active = True
            profile.save()
            
            teacher, _ = Teacher.objects.get_or_create(profile=profile, defaults={'is_active': True})
            
            # Assigner des matières et classes
            teacher.subjects.set(random.sample(subjects, min(3, len(subjects))))
            teacher.classes.set(random.sample(classes, min(2, len(classes))))
            
            teachers.append(teacher)
        return teachers
    
    def _create_courses(self, subjects, classes, teachers, academic_years, admin_user):
        """Crée des cours."""
        courses = []
        current_year = academic_years[1]
        
        for class_obj in classes:
            # Assigner plusieurs matières à chaque classe
            class_subjects = random.sample(subjects, min(5, len(subjects)))
            for subject in class_subjects:
                # Trouver un enseignant qui enseigne cette matière
                available_teachers = [t for t in teachers if subject in t.subjects.all()]
                if available_teachers:
                    teacher = random.choice(available_teachers)
                    course, _ = Course.objects.get_or_create(
                        subject=subject,
                        class_section=class_obj,
                        academic_year=current_year,
                        defaults={
                            'teacher': teacher,
                            'is_active': True,
                            'created_by': admin_user
                        }
                    )
                    courses.append(course)
        return courses
    
    def _create_schedules(self, courses, classrooms, admin_user):
        """Crée un emploi du temps."""
        days = [0, 1, 2, 3, 4]  # Lundi à Vendredi
        time_slots = [
            ('08:00', '09:00'),
            ('09:00', '10:00'),
            ('10:15', '11:15'),
            ('11:15', '12:15'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
        ]
        
        for course in courses[:len(courses)//2]:  # Créer un emploi du temps pour la moitié des cours
            day = random.choice(days)
            start_time, end_time = random.choice(time_slots)
            classroom = random.choice(classrooms) if classrooms else None
            
            Schedule.objects.get_or_create(
                course=course,
                day_of_week=day,
                start_time=start_time,
                defaults={
                    'end_time': end_time,
                    'classroom': classroom,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
    
    def _create_students(self, num_students, classes, academic_years, admin_user):
        """Crée des élèves."""
        students = []
        first_names = ['Lucas', 'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia', 'Mason', 'Isabella']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        current_year = academic_years[1]
        
        for i in range(num_students):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'student_{i+1}'
            email = f'{username}@school.com'
            
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
            )
            user.set_password('student123')
            user.save()
            
            profile = Profile.objects.get(user=user)
            profile.full_name = f'{first_name} {last_name}'
            profile.role = 'student'
            profile.is_active = True
            profile.save()
            
            class_obj = random.choice(classes) if classes else None
            student, _ = Student.objects.get_or_create(
                profile=profile,
                defaults={
                    'class_section': class_obj,
                    'academic_year': current_year,
                    'student_number': f'STU{1000 + i}',
                    'is_active': True
                }
            )
            students.append(student)
        return students
    
    def _create_parents(self, num_parents, students, admin_user):
        """Crée des parents et les lie aux élèves."""
        parents = []
        first_names = ['Robert', 'Jennifer', 'Michael', 'Patricia', 'William', 'Linda', 'David', 'Barbara']
        last_names = ['Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia']
        
        for i in range(num_parents):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'parent_{i+1}'
            email = f'{username}@school.com'
            
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
            )
            user.set_password('parent123')
            user.save()
            
            profile = Profile.objects.get(user=user)
            profile.full_name = f'{first_name} {last_name}'
            profile.role = 'parent'
            profile.is_active = True
            profile.save()
            
            parent, _ = Parent.objects.get_or_create(profile=profile, defaults={'is_active': True})
            
            # Lier à 1-3 enfants aléatoires
            num_children = random.randint(1, min(3, len(students)))
            parent.children.set(random.sample(students, num_children))
            
            parents.append(parent)
        return parents
    
    def _create_grade_scales(self, admin_user):
        """Crée des barèmes de notes."""
        scales = []
        scale_data = [
            ('0-20', Decimal('0.00'), Decimal('20.00'), Decimal('10.00')),
        ]
        for name, min_score, max_score, passing_score in scale_data:
            scale, _ = GradeScale.objects.get_or_create(
                name=name,
                defaults={
                    'min_score': min_score,
                    'max_score': max_score,
                    'passing_score': passing_score,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            scales.append(scale)
        return scales
    
    def _create_grade_categories(self, admin_user):
        """Crée des catégories de notes."""
        categories = []
        category_data = [
            ('Contrôle', 'CTRL', Decimal('1.0')),
            ('Devoir maison', 'DM', Decimal('1.0')),
            ('Interrogation', 'INT', Decimal('0.5')),
            ('Examen', 'EXAM', Decimal('2.0')),
        ]
        for name, code, weight in category_data:
            category, _ = GradeCategory.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'weight': weight,
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            categories.append(category)
        return categories
    
    def _create_assessments(self, subjects, classes, categories, academic_years, admin_user):
        """Crée des évaluations."""
        assessments = []
        current_year = academic_years[1]
        
        for class_obj in classes:
            class_subjects = list(subjects)[:5]  # 5 matières par classe
            for subject in class_subjects:
                # Créer 2-3 évaluations par matière
                for i in range(random.randint(2, 3)):
                    category = random.choice(categories)
                    assessment_name = f'{category.name} {subject.name} - {i+1}'
                    assessment_date = date.today() - timedelta(days=random.randint(1, 60))
                    
                    assessment, _ = Assessment.objects.get_or_create(
                        name=assessment_name,
                        subject=subject,
                        class_section=class_obj,
                        date=assessment_date,
                        academic_year=current_year,
                        defaults={
                            'category': category,
                            'coefficient': Decimal('1.0'),
                            'max_score': Decimal('20.00'),
                            'is_active': True,
                            'created_by': admin_user
                        }
                    )
                    assessments.append(assessment)
        return assessments
    
    def _create_student_grades(self, students, assessments, admin_user):
        """Crée des notes pour les élèves."""
        for assessment in assessments:
            class_students = [s for s in students if s.class_section == assessment.class_section]
            for student in class_students:
                # 80% de chance d'avoir une note, sinon absent
                if random.random() < 0.8:
                    score = Decimal(str(random.uniform(8.0, 20.0))).quantize(Decimal('0.01'))
                    is_absent = False
                else:
                    score = None
                    is_absent = True
                
                StudentGrade.objects.get_or_create(
                    student=student,
                    assessment=assessment,
                    defaults={
                        'score': score,
                        'is_absent': is_absent,
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
    
    def _create_report_cards(self, students, academic_years, admin_user):
        """Crée des bulletins."""
        current_year = academic_years[1]
        terms = ['Trimestre 1', 'Trimestre 2', 'Trimestre 3']
        
        for student in students:
            for term in terms:
                overall_avg = Decimal(str(random.uniform(10.0, 18.0))).quantize(Decimal('0.01'))
                ReportCard.objects.get_or_create(
                    student=student,
                    academic_year=current_year,
                    term=term,
                    defaults={
                        'overall_average': overall_avg,
                        'rank': random.randint(1, 30),
                        'total_students': 30,
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
    
    def _create_attendance_rules(self, admin_user):
        """Crée des règles de présence."""
        rule, _ = AttendanceRule.objects.get_or_create(
            name='Règle standard',
            defaults={
                'max_absences': 5,
                'alert_threshold': 3,
                'period_days': 30,
                'is_active': True,
                'created_by': admin_user
            }
        )
        return [rule]
    
    def _create_attendances(self, students, classes, academic_years, admin_user):
        """Crée des enregistrements de présence."""
        current_year = academic_years[1]
        statuses = ['present', 'present', 'present', 'present', 'late', 'absent']  # Plus de présents
        
        # Créer des présences pour les 30 derniers jours
        for i in range(30):
            attendance_date = date.today() - timedelta(days=i)
            if attendance_date.weekday() < 5:  # Seulement les jours de semaine
                for class_obj in classes:
                    class_students = [s for s in students if s.class_section == class_obj]
                    for student in class_students:
                        status = random.choice(statuses)
                        time_in = f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}:00" if status == 'present' or status == 'late' else None
                        
                        Attendance.objects.get_or_create(
                            student=student,
                            class_section=class_obj,
                            date=attendance_date,
                            defaults={
                                'status': status,
                                'time_in': time_in,
                                'is_active': True,
                                'created_by': admin_user
                            }
                        )
    
    def _create_absences(self, students, academic_years, admin_user):
        """Crée des absences."""
        absences = []
        current_year = academic_years[1]
        reasons = ['Maladie', 'Rendez-vous médical', 'Problème familial', 'Transport']
        
        # Créer quelques absences pour certains élèves
        for student in random.sample(students, min(10, len(students))):
            num_absences = random.randint(1, 3)
            for _ in range(num_absences):
                start_date = date.today() - timedelta(days=random.randint(1, 60))
                end_date = start_date + timedelta(days=random.randint(0, 2))
                reason = random.choice(reasons)
                is_justified = random.random() < 0.5  # 50% justifiées
                
                absence = Absence.objects.create(
                    student=student,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason,
                    is_justified=is_justified,
                    is_active=True,
                    created_by=admin_user
                )
                absences.append(absence)
        return absences
    
    def _create_excuses(self, absences, teachers, admin_user):
        """Crée des justificatifs pour certaines absences."""
        statuses = ['pending', 'approved', 'rejected']
        
        for absence in random.sample(absences, min(5, len(absences))):
            if not absence.is_justified:
                status = random.choice(statuses)
                teacher = random.choice(teachers) if teachers and status != 'pending' else None
                
                excuse = Excuse.objects.create(
                    absence=absence,
                    status=status,
                    reviewed_by=teacher if status != 'pending' else None,
                    reviewed_at=timezone.now() if status != 'pending' else None,
                    is_active=True,
                    created_by=admin_user
                )
                
                if status == 'approved':
                    absence.is_justified = True
                    absence.justified_by = teacher
                    absence.save()

