"""
Modèles pour l'application app_attendance.

Ce module contient les modèles Django pour la gestion des présences et absences :
- Règles de présence
- Présences quotidiennes
- Absences
- Justificatifs
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class AttendanceRule(models.Model):
    """
    Modèle représentant une règle de présence.
    
    Définit les seuils et alertes pour les absences.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
        help_text="Nom de la règle"
    )
    
    max_absences = models.IntegerField(
        default=5,
        verbose_name="Nombre maximum d'absences",
        help_text="Nombre maximum d'absences autorisées"
    )
    
    alert_threshold = models.IntegerField(
        default=3,
        verbose_name="Seuil d'alerte",
        help_text="Nombre d'absences déclenchant une alerte"
    )
    
    period_days = models.IntegerField(
        default=30,
        verbose_name="Période (jours)",
        help_text="Période en jours pour le calcul des absences"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de la règle"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la règle est active"
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
        related_name='attendance_rules_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_rules_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Règle de présence"
        verbose_name_plural = "Règles de présence"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_rule(cls, rule_id):
        """
        Récupère une règle active par ID.
        
        Args:
            rule_id: ID de la règle
            
        Returns:
            AttendanceRule ou None: Instance de la règle ou None si non trouvée
        """
        instances = cls.objects.filter(id=rule_id, is_active=True)
        if instances:
            return instances[0]
        return None


class Attendance(models.Model):
    """
    Modèle représentant une présence quotidienne d'un élève.
    """
    
    STATUS_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('late', 'En retard'),
        ('excused', 'Excusé'),
    ]
    
    student = models.ForeignKey(
        'app_profile.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Élève",
        help_text="Élève concerné"
    )
    
    class_section = models.ForeignKey(
        'app_academic.Class',
        on_delete=models.PROTECT,
        related_name='attendances',
        verbose_name="Classe",
        help_text="Classe concernée"
    )
    
    date = models.DateField(
        verbose_name="Date",
        help_text="Date de la présence"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name="Statut",
        help_text="Statut de présence"
    )
    
    time_in = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure d'arrivée",
        help_text="Heure d'arrivée de l'élève"
    )
    
    time_out = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de départ",
        help_text="Heure de départ de l'élève"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes supplémentaires"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la présence est active"
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
        related_name='attendances_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        ordering = ['-date', 'student']
        unique_together = [['student', 'class_section', 'date']]
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['class_section', 'date']),
            models.Index(fields=['status', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.profile.full_name} - {self.date} ({self.get_status_display()})"
    
    @classmethod
    def get_attendance(cls, attendance_id):
        """
        Récupère une présence active par ID.
        
        Args:
            attendance_id: ID de la présence
            
        Returns:
            Attendance ou None: Instance de la présence ou None si non trouvée
        """
        instances = cls.objects.filter(id=attendance_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_attendance_by_student(cls, student_id, start_date=None, end_date=None):
        """
        Récupère les présences d'un élève sur une période.
        
        Args:
            student_id: ID de l'élève
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            QuerySet: Liste des présences
        """
        queryset = cls.objects.filter(student_id=student_id, is_active=True)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('student', 'class_section').order_by('-date')
    
    @classmethod
    def get_attendance_by_class(cls, class_id, date):
        """
        Récupère les présences d'une classe pour une date.
        
        Args:
            class_id: ID de la classe
            date: Date concernée
            
        Returns:
            QuerySet: Liste des présences
        """
        return cls.objects.filter(
            class_section_id=class_id,
            date=date,
            is_active=True
        ).select_related('student', 'class_section').order_by('student__profile__full_name')


class Absence(models.Model):
    """
    Modèle représentant une absence d'un élève.
    """
    
    student = models.ForeignKey(
        'app_profile.Student',
        on_delete=models.CASCADE,
        related_name='absences',
        verbose_name="Élève",
        help_text="Élève concerné"
    )
    
    start_date = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'absence"
    )
    
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin de l'absence (si absence sur plusieurs jours)"
    )
    
    reason = models.TextField(
        verbose_name="Motif",
        help_text="Motif de l'absence"
    )
    
    is_justified = models.BooleanField(
        default=False,
        verbose_name="Justifiée",
        help_text="Indique si l'absence est justifiée"
    )
    
    justified_by = models.ForeignKey(
        'app_profile.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='justified_absences',
        verbose_name="Justifiée par",
        help_text="Enseignant qui a justifié l'absence"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'absence est active"
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
        related_name='absences_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='absences_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        ordering = ['-start_date', 'student']
        indexes = [
            models.Index(fields=['student', 'start_date']),
            models.Index(fields=['is_justified', 'start_date']),
        ]
    
    def __str__(self):
        if self.end_date:
            return f"{self.student.profile.full_name} - {self.start_date} au {self.end_date}"
        return f"{self.student.profile.full_name} - {self.start_date}"
    
    @classmethod
    def get_absence(cls, absence_id):
        """
        Récupère une absence active par ID.
        
        Args:
            absence_id: ID de l'absence
            
        Returns:
            Absence ou None: Instance de l'absence ou None si non trouvée
        """
        instances = cls.objects.filter(id=absence_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_absences_by_student(cls, student_id):
        """
        Récupère toutes les absences actives d'un élève.
        
        Args:
            student_id: ID de l'élève
            
        Returns:
            QuerySet: Liste des absences de l'élève
        """
        return cls.objects.filter(student_id=student_id, is_active=True).select_related('student', 'justified_by').order_by('-start_date')


class Excuse(models.Model):
    """
    Modèle représentant un justificatif d'absence.
    """
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    absence = models.OneToOneField(
        Absence,
        on_delete=models.CASCADE,
        related_name='excuse',
        verbose_name="Absence",
        help_text="Absence concernée"
    )
    
    document = models.FileField(
        upload_to='excuses/documents/',
        blank=True,
        null=True,
        verbose_name="Document",
        help_text="Document justificatif (PDF, image)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut",
        help_text="Statut du justificatif"
    )
    
    reviewed_by = models.ForeignKey(
        'app_profile.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_excuses',
        verbose_name="Examiné par",
        help_text="Enseignant qui a examiné le justificatif"
    )
    
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'examen",
        help_text="Date à laquelle le justificatif a été examiné"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur le justificatif"
    )
    
    # Champs obligatoires
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le justificatif est actif"
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
        related_name='excuses_created',
        verbose_name="Créé par"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excuses_updated',
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Justificatif"
        verbose_name_plural = "Justificatifs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['absence']),
        ]
    
    def __str__(self):
        return f"Justificatif - {self.absence.student.profile.full_name} ({self.get_status_display()})"
    
    @classmethod
    def get_excuse(cls, excuse_id):
        """
        Récupère un justificatif actif par ID.
        
        Args:
            excuse_id: ID du justificatif
            
        Returns:
            Excuse ou None: Instance du justificatif ou None si non trouvé
        """
        instances = cls.objects.filter(id=excuse_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    def approve_excuse(self, teacher_id):
        """
        Approuve le justificatif.
        
        Args:
            teacher_id: ID de l'enseignant qui approuve
        """
        from app_profile.models import Teacher
        
        teacher = Teacher.get_teacher(teacher_id)
        if teacher:
            self.status = 'approved'
            self.reviewed_by = teacher
            self.reviewed_at = timezone.now()
            self.absence.is_justified = True
            self.absence.justified_by = teacher
            self.absence.save()
            self.save()
    
    def reject_excuse(self, teacher_id, reason):
        """
        Rejette le justificatif.
        
        Args:
            teacher_id: ID de l'enseignant qui rejette
            reason: Raison du rejet
        """
        from app_profile.models import Teacher
        
        teacher = Teacher.get_teacher(teacher_id)
        if teacher:
            self.status = 'rejected'
            self.reviewed_by = teacher
            self.reviewed_at = timezone.now()
            self.notes = reason
            self.save()
