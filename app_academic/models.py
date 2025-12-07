"""
Modèles pour l'application app_academic.

Ce module contient les modèles Django pour la gestion académique :
- Années scolaires
- Niveaux/Grades
- Salles de classe
- Classes/Sections
- Matières
- Cours
- Emploi du temps
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class AcademicYear(models.Model):
    """
    Modèle représentant une année scolaire.
    
    Exemple : "2024-2025", "2025-2026"
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom",
        help_text="Nom de l'année scolaire (ex: 2024-2025)"
    )
    
    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'année scolaire"
    )
    
    end_date = models.DateField(
        verbose_name="Date de fin",
        help_text="Date de fin de l'année scolaire"
    )
    
    is_current = models.BooleanField(
        default=False,
        verbose_name="Année courante",
        help_text="Indique si c'est l'année scolaire actuelle"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'année scolaire est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='academic_years_created',
        verbose_name="Créé par",
        help_text="Utilisateur qui a créé cette année scolaire"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='academic_years_updated',
        verbose_name="Modifié par",
        help_text="Utilisateur qui a modifié cette année scolaire"
    )
    
    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_current', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_academic_year(cls, year_id):
        """
        Récupère une année scolaire active par ID.
        
        Args:
            year_id: ID de l'année scolaire
            
        Returns:
            AcademicYear ou None: Instance de l'année scolaire ou None si non trouvée
        """
        instances = cls.objects.filter(id=year_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_current_year(cls):
        """
        Récupère l'année scolaire courante.
        
        Returns:
            AcademicYear ou None: Année scolaire courante ou None si non trouvée
        """
        instances = cls.objects.filter(is_current=True, is_active=True)
        if instances:
            return instances[0]
        return None


class Grade(models.Model):
    """
    Modèle représentant un niveau scolaire.
    
    Exemple : "CP", "CE1", "CE2", "CM1", "CM2", "6ème", "5ème", etc.
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom",
        help_text="Nom du niveau (ex: CP, CE1, 6ème)"
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code",
        help_text="Code unique du niveau"
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name="Ordre",
        help_text="Ordre d'affichage du niveau"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description du niveau"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le niveau est actif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grades_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grades_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_grade(cls, grade_id):
        """
        Récupère un niveau actif par ID.
        
        Args:
            grade_id: ID du niveau
            
        Returns:
            Grade ou None: Instance du niveau ou None si non trouvé
        """
        instances = cls.objects.filter(id=grade_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_all_grades(cls):
        """
        Récupère tous les niveaux actifs.
        
        Returns:
            QuerySet: Liste des niveaux actifs ordonnés
        """
        return cls.objects.filter(is_active=True).order_by('order', 'name')


class ClassRoom(models.Model):
    """
    Modèle représentant une salle de classe.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom de la salle (ex: Salle 101, Laboratoire de Sciences)"
    )
    
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Capacité",
        help_text="Nombre maximum d'élèves que la salle peut accueillir"
    )
    
    floor = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Étage",
        help_text="Numéro de l'étage (optionnel)"
    )
    
    equipment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Équipements",
        help_text="Liste des équipements disponibles dans la salle"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la salle est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classrooms_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classrooms_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Salle de classe"
        verbose_name_plural = "Salles de classe"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_classroom(cls, classroom_id):
        """
        Récupère une salle active par ID.
        
        Args:
            classroom_id: ID de la salle
            
        Returns:
            ClassRoom ou None: Instance de la salle ou None si non trouvée
        """
        instances = cls.objects.filter(id=classroom_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_available_classrooms(cls):
        """
        Récupère toutes les salles actives disponibles.
        
        Returns:
            QuerySet: Liste des salles actives
        """
        return cls.objects.filter(is_active=True).order_by('name')


class Class(models.Model):
    """
    Modèle représentant une classe/section.
    
    Exemple : "6ème A", "5ème B", "Terminale S"
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nom",
        help_text="Nom de la classe (ex: 6ème A, 5ème B)"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code",
        help_text="Code unique de la classe"
    )
    
    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        related_name='classes',
        verbose_name="Niveau",
        help_text="Niveau scolaire de la classe"
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='classes',
        verbose_name="Année scolaire",
        help_text="Année scolaire de la classe"
    )
    
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
        verbose_name="Salle de classe",
        help_text="Salle de classe principale"
    )
    
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Capacité",
        help_text="Nombre maximum d'élèves dans la classe"
    )
    
    teacher = models.ForeignKey(
        'app_profile.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='main_classes',
        verbose_name="Professeur principal",
        help_text="Professeur principal de la classe"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la classe est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['academic_year', 'grade__order', 'name']
        unique_together = [['code', 'academic_year']]
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['academic_year', 'is_active']),
            models.Index(fields=['grade', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.academic_year.name})"
    
    @classmethod
    def get_class(cls, class_id):
        """
        Récupère une classe active par ID.
        
        Args:
            class_id: ID de la classe
            
        Returns:
            Class ou None: Instance de la classe ou None si non trouvée
        """
        instances = cls.objects.filter(id=class_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_classes_by_year(cls, year_id):
        """
        Récupère toutes les classes actives d'une année scolaire.
        
        Args:
            year_id: ID de l'année scolaire
            
        Returns:
            QuerySet: Liste des classes de l'année
        """
        return cls.objects.filter(academic_year_id=year_id, is_active=True).select_related('grade', 'academic_year', 'classroom', 'teacher')
    
    def get_students_count(self):
        """
        Retourne le nombre d'élèves actifs dans cette classe.
        
        Returns:
            int: Nombre d'élèves
        """
        from app_profile.models import Student
        return Student.objects.filter(class_section=self, is_active=True).count()


class Subject(models.Model):
    """
    Modèle représentant une matière.
    
    Exemple : "Mathématiques", "Français", "Histoire-Géographie"
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom de la matière (ex: Mathématiques, Français)"
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code",
        help_text="Code unique de la matière"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de la matière"
    )
    
    coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)],
        verbose_name="Coefficient",
        help_text="Coefficient pour le calcul de la moyenne"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la matière est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_subject(cls, subject_id):
        """
        Récupère une matière active par ID.
        
        Args:
            subject_id: ID de la matière
            
        Returns:
            Subject ou None: Instance de la matière ou None si non trouvée
        """
        instances = cls.objects.filter(id=subject_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_all_subjects(cls):
        """
        Récupère toutes les matières actives.
        
        Returns:
            QuerySet: Liste des matières actives
        """
        return cls.objects.filter(is_active=True).order_by('name')


class Course(models.Model):
    """
    Modèle représentant un cours.
    
    Un cours lie une matière, une classe, un enseignant et une année scolaire.
    """
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Matière",
        help_text="Matière enseignée"
    )
    
    class_section = models.ForeignKey(
        Class,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Classe",
        help_text="Classe concernée"
    )
    
    teacher = models.ForeignKey(
        'app_profile.Teacher',
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Enseignant",
        help_text="Enseignant responsable du cours"
    )
    
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Année scolaire",
        help_text="Année scolaire du cours"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le cours est actif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['academic_year', 'class_section', 'subject']
        unique_together = [['subject', 'class_section', 'teacher', 'academic_year']]
        indexes = [
            models.Index(fields=['academic_year', 'is_active']),
            models.Index(fields=['class_section', 'subject']),
            models.Index(fields=['teacher', 'academic_year']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.class_section.name} ({self.academic_year.name})"
    
    @classmethod
    def get_course(cls, course_id):
        """
        Récupère un cours actif par ID.
        
        Args:
            course_id: ID du cours
            
        Returns:
            Course ou None: Instance du cours ou None si non trouvé
        """
        instances = cls.objects.filter(id=course_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_courses_by_teacher(cls, teacher_id):
        """
        Récupère tous les cours actifs d'un enseignant.
        
        Args:
            teacher_id: ID de l'enseignant
            
        Returns:
            QuerySet: Liste des cours de l'enseignant
        """
        return cls.objects.filter(teacher_id=teacher_id, is_active=True).select_related('subject', 'class_section', 'academic_year')
    
    @classmethod
    def get_courses_by_class(cls, class_id):
        """
        Récupère tous les cours actifs d'une classe.
        
        Args:
            class_id: ID de la classe
            
        Returns:
            QuerySet: Liste des cours de la classe
        """
        return cls.objects.filter(class_section_id=class_id, is_active=True).select_related('subject', 'teacher', 'academic_year')


class Schedule(models.Model):
    """
    Modèle représentant un créneau d'emploi du temps.
    """
    
    DAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Cours",
        help_text="Cours concerné"
    )
    
    day_of_week = models.IntegerField(
        choices=DAY_CHOICES,
        verbose_name="Jour de la semaine",
        help_text="Jour de la semaine (0=Lundi, 6=Dimanche)"
    )
    
    start_time = models.TimeField(
        verbose_name="Heure de début",
        help_text="Heure de début du cours"
    )
    
    end_time = models.TimeField(
        verbose_name="Heure de fin",
        help_text="Heure de fin du cours"
    )
    
    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules',
        verbose_name="Salle",
        help_text="Salle de classe pour ce créneau"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le créneau est actif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedules_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Emploi du temps"
        verbose_name_plural = "Emplois du temps"
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['course', 'day_of_week']),
            models.Index(fields=['day_of_week', 'start_time']),
        ]
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        return f"{day_name} {self.start_time} - {self.end_time} ({self.course})"
    
    @classmethod
    def get_schedule(cls, schedule_id):
        """
        Récupère un créneau actif par ID.
        
        Args:
            schedule_id: ID du créneau
            
        Returns:
            Schedule ou None: Instance du créneau ou None si non trouvé
        """
        instances = cls.objects.filter(id=schedule_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_schedule_by_class(cls, class_id):
        """
        Récupère l'emploi du temps d'une classe.
        
        Args:
            class_id: ID de la classe
            
        Returns:
            QuerySet: Liste des créneaux de la classe
        """
        return cls.objects.filter(
            course__class_section_id=class_id,
            is_active=True
        ).select_related('course', 'course__subject', 'course__teacher', 'classroom').order_by('day_of_week', 'start_time')
    
    @classmethod
    def get_schedule_by_teacher(cls, teacher_id):
        """
        Récupère l'emploi du temps d'un enseignant.
        
        Args:
            teacher_id: ID de l'enseignant
            
        Returns:
            QuerySet: Liste des créneaux de l'enseignant
        """
        return cls.objects.filter(
            course__teacher_id=teacher_id,
            is_active=True
        ).select_related('course', 'course__subject', 'course__class_section', 'classroom').order_by('day_of_week', 'start_time')
