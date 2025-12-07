"""
Modèles pour l'application app_grades.

Ce module contient les modèles Django pour la gestion des notes et évaluations :
- Barèmes de notation
- Catégories d'évaluations
- Évaluations
- Notes
- Bulletins
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class GradeScale(models.Model):
    """
    Modèle représentant un barème de notation.
    
    Exemple : "0-20", "A-F", "0-100"
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nom",
        help_text="Nom du barème (ex: 0-20, A-F)"
    )
    
    min_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note minimale",
        help_text="Note minimale du barème"
    )
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note maximale",
        help_text="Note maximale du barème"
    )
    
    passing_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Note de passage",
        help_text="Note minimale pour réussir"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description du barème"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le barème est actif"
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
        related_name='grade_scales_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grade_scales_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Barème de notation"
        verbose_name_plural = "Barèmes de notation"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_grade_scale(cls, scale_id):
        """
        Récupère un barème actif par ID.
        
        Args:
            scale_id: ID du barème
            
        Returns:
            GradeScale ou None: Instance du barème ou None si non trouvé
        """
        instances = cls.objects.filter(id=scale_id, is_active=True)
        if instances:
            return instances[0]
        return None


class GradeCategory(models.Model):
    """
    Modèle représentant une catégorie d'évaluation.
    
    Exemple : "Contrôle continu", "Examen", "Devoir maison"
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom de la catégorie (ex: Contrôle continu, Examen)"
    )
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code",
        help_text="Code unique de la catégorie"
    )
    
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)],
        verbose_name="Poids",
        help_text="Poids de la catégorie pour le calcul de la moyenne"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de la catégorie"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la catégorie est active"
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
        related_name='grade_categories_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grade_categories_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Catégorie d'évaluation"
        verbose_name_plural = "Catégories d'évaluation"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_category(cls, category_id):
        """
        Récupère une catégorie active par ID.
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            GradeCategory ou None: Instance de la catégorie ou None si non trouvée
        """
        instances = cls.objects.filter(id=category_id, is_active=True)
        if instances:
            return instances[0]
        return None


class Assessment(models.Model):
    """
    Modèle représentant une évaluation.
    
    Exemple : "Contrôle de Mathématiques", "Examen de Français"
    """
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nom",
        help_text="Nom de l'évaluation (ex: Contrôle de Mathématiques)"
    )
    
    subject = models.ForeignKey(
        'app_academic.Subject',
        on_delete=models.PROTECT,
        related_name='assessments',
        verbose_name="Matière",
        help_text="Matière concernée"
    )
    
    class_section = models.ForeignKey(
        'app_academic.Class',
        on_delete=models.PROTECT,
        related_name='assessments',
        verbose_name="Classe",
        help_text="Classe concernée"
    )
    
    category = models.ForeignKey(
        GradeCategory,
        on_delete=models.PROTECT,
        related_name='assessments',
        verbose_name="Catégorie",
        help_text="Catégorie de l'évaluation"
    )
    
    date = models.DateField(
        verbose_name="Date",
        help_text="Date de l'évaluation"
    )
    
    coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)],
        verbose_name="Coefficient",
        help_text="Coefficient de l'évaluation"
    )
    
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Note maximale",
        help_text="Note maximale possible"
    )
    
    academic_year = models.ForeignKey(
        'app_academic.AcademicYear',
        on_delete=models.PROTECT,
        related_name='assessments',
        verbose_name="Année scolaire",
        help_text="Année scolaire de l'évaluation"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de l'évaluation"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'évaluation est active"
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
        related_name='assessments_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessments_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        ordering = ['-date', 'subject', 'class_section']
        indexes = [
            models.Index(fields=['subject', 'class_section', 'date']),
            models.Index(fields=['academic_year', 'is_active']),
            models.Index(fields=['category', 'date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.class_section.name} ({self.date})"
    
    @classmethod
    def get_assessment(cls, assessment_id):
        """
        Récupère une évaluation active par ID.
        
        Args:
            assessment_id: ID de l'évaluation
            
        Returns:
            Assessment ou None: Instance de l'évaluation ou None si non trouvée
        """
        instances = cls.objects.filter(id=assessment_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_assessments_by_class(cls, class_id):
        """
        Récupère toutes les évaluations actives d'une classe.
        
        Args:
            class_id: ID de la classe
            
        Returns:
            QuerySet: Liste des évaluations de la classe
        """
        return cls.objects.filter(class_section_id=class_id, is_active=True).select_related('subject', 'class_section', 'category', 'academic_year').order_by('-date')


class StudentGrade(models.Model):
    """
    Modèle représentant une note d'un élève pour une évaluation.
    """
    
    student = models.ForeignKey(
        'app_profile.Student',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Élève",
        help_text="Élève concerné"
    )
    
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Évaluation",
        help_text="Évaluation concernée"
    )
    
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Note",
        help_text="Note obtenue par l'élève"
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaire",
        help_text="Commentaire sur la note"
    )
    
    is_absent = models.BooleanField(
        default=False,
        verbose_name="Absent",
        help_text="Indique si l'élève était absent lors de l'évaluation"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la note est active"
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
        related_name='student_grades_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_grades_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Note d'élève"
        verbose_name_plural = "Notes d'élèves"
        ordering = ['-assessment__date', 'student']
        unique_together = [['student', 'assessment']]
        indexes = [
            models.Index(fields=['student', 'assessment']),
            models.Index(fields=['assessment', 'is_active']),
        ]
    
    def __str__(self):
        if self.is_absent:
            return f"{self.student.profile.full_name} - Absent ({self.assessment.name})"
        return f"{self.student.profile.full_name} - {self.score or 'N/A'}/{self.assessment.max_score} ({self.assessment.name})"
    
    @classmethod
    def get_student_grade(cls, grade_id):
        """
        Récupère une note active par ID.
        
        Args:
            grade_id: ID de la note
            
        Returns:
            StudentGrade ou None: Instance de la note ou None si non trouvée
        """
        instances = cls.objects.filter(id=grade_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_grades_by_student(cls, student_id):
        """
        Récupère toutes les notes actives d'un élève.
        
        Args:
            student_id: ID de l'élève
            
        Returns:
            QuerySet: Liste des notes de l'élève
        """
        return cls.objects.filter(student_id=student_id, is_active=True).select_related('student', 'assessment', 'assessment__subject', 'assessment__class_section').order_by('-assessment__date')
    
    @classmethod
    def calculate_average(cls, student_id, subject_id, year_id=None):
        """
        Calcule la moyenne d'un élève pour une matière.
        
        Args:
            student_id: ID de l'élève
            subject_id: ID de la matière
            year_id: ID de l'année scolaire (optionnel)
            
        Returns:
            Decimal: Moyenne calculée ou None
        """
        grades = cls.objects.filter(
            student_id=student_id,
            assessment__subject_id=subject_id,
            is_active=True,
            is_absent=False
        )
        
        if year_id:
            grades = grades.filter(assessment__academic_year_id=year_id)
        
        grades = grades.select_related('assessment')
        
        if not grades.exists():
            return None
        
        total_score = Decimal('0')
        total_coefficient = Decimal('0')
        
        for grade in grades:
            if grade.score is not None:
                coefficient = grade.assessment.coefficient
                total_score += grade.score * coefficient
                total_coefficient += coefficient
        
        if total_coefficient == 0:
            return None
        
        return total_score / total_coefficient


class ReportCard(models.Model):
    """
    Modèle représentant un bulletin de notes.
    """
    
    student = models.ForeignKey(
        'app_profile.Student',
        on_delete=models.CASCADE,
        related_name='report_cards',
        verbose_name="Élève",
        help_text="Élève concerné"
    )
    
    academic_year = models.ForeignKey(
        'app_academic.AcademicYear',
        on_delete=models.PROTECT,
        related_name='report_cards',
        verbose_name="Année scolaire",
        help_text="Année scolaire du bulletin"
    )
    
    term = models.CharField(
        max_length=50,
        verbose_name="Trimestre/Semestre",
        help_text="Période (ex: Trimestre 1, Semestre 1)"
    )
    
    overall_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Moyenne générale",
        help_text="Moyenne générale de l'élève"
    )
    
    rank = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Classement",
        help_text="Classement de l'élève dans sa classe"
    )
    
    total_students = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre total d'élèves",
        help_text="Nombre total d'élèves dans la classe"
    )
    
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaires",
        help_text="Commentaires généraux sur le bulletin"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le bulletin est actif"
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
        related_name='report_cards_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='report_cards_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering = ['-academic_year', 'student', '-term']
        unique_together = [['student', 'academic_year', 'term']]
        indexes = [
            models.Index(fields=['student', 'academic_year']),
            models.Index(fields=['academic_year', 'term']),
        ]
    
    def __str__(self):
        return f"Bulletin {self.term} - {self.student.profile.full_name} ({self.academic_year.name})"
    
    @classmethod
    def get_report_card(cls, report_card_id):
        """
        Récupère un bulletin actif par ID.
        
        Args:
            report_card_id: ID du bulletin
            
        Returns:
            ReportCard ou None: Instance du bulletin ou None si non trouvé
        """
        instances = cls.objects.filter(id=report_card_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def generate_report_card(cls, student_id, year_id, term):
        """
        Génère ou récupère un bulletin pour un élève.
        
        Args:
            student_id: ID de l'élève
            year_id: ID de l'année scolaire
            term: Trimestre/Semestre
            
        Returns:
            ReportCard: Instance du bulletin
        """
        from .services.utils import calculate_overall_average
        
        report_card, created = cls.objects.get_or_create(
            student_id=student_id,
            academic_year_id=year_id,
            term=term,
            defaults={'is_active': True}
        )
        
        # Calculer la moyenne générale
        overall_avg = calculate_overall_average(student_id, year_id)
        if overall_avg:
            report_card.overall_average = overall_avg
            report_card.save()
        
        return report_card
