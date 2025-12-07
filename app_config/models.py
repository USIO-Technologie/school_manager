from datetime import timedelta
import random
from django.utils import timezone
from django.db import models
from django.conf import settings


class Country(models.Model):
    """
    Modèle pour représenter les pays.

    Ce modèle sera utilisé comme ForeignKey dans ParentProfile
    pour une meilleure normalisation des données.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Nom du pays",
        help_text="Nom complet du pays"
    )
    code = models.CharField(
        max_length=3,
        verbose_name="Code pays",
        help_text="Code ISO du pays (ex: FRA, USA)"
    )

    prefix = models.CharField(
        max_length=5,
        verbose_name="Préfixe téléphonique international",
        help_text="Préfixe téléphonique international (ex: 243)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le pays est actif"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Pays"
        verbose_name_plural = "Pays"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class CountryPrefix(models.Model):
    """
    Représente un indicatif téléphonique d'un pays et les informations associées.
    """

    name = models.CharField(
        max_length=100,
        help_text="Nom du pays (ex: Congo-Kinshasa)"
    )
    prefix = models.CharField(
        max_length=5,
        help_text="Préfixe téléphonique international (ex: 243)"
    )
    corps = models.CharField(
        max_length=20,
        help_text="Optionnel, reste du numéro après le préfixe (ex: 817928892 pour la RDC)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indique si le préfixe est actif pour la validation"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date de création")
    last_update = models.DateTimeField(auto_now=True, help_text="Date de dernière mise à jour")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="countryprefix_created",
        help_text="Utilisateur ayant créé ce préfixe"
    )
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="countryprefix_updated",
        help_text="Utilisateur ayant modifié ce préfixe"
    )

    class Meta:
        verbose_name = "Country Prefix"
        verbose_name_plural = "Country Prefixes"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (+{self.prefix})"

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    isActif = models.BooleanField(verbose_name="Actif",default=True)

    create = models.DateTimeField(verbose_name="Created", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Last update", auto_now=True)
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="checkUsager_createby")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="checkUsager_updateby")
    class Meta:
        ordering = ('-create',)
        verbose_name = 'code otp envoyé'
        verbose_name_plural = 'CODE OTP ENVOYE'

    def is_valid(self):
        return timezone.now() < self.create + timedelta(minutes=5)

    def has_attempts_left(self):
        return self.attempts < 3

    @staticmethod
    def generateOtp(phone_number):
        code = f"{random.randint(100000, 999999)}"
        print(f"=== OTP généré pour {phone_number} : {code} ===")
        PhoneOTP.objects.filter(phone_number=phone_number).update(isActif=False)
        PhoneOTP.objects.create(
            phone_number=phone_number,
            code= code
        )

        return code

    @staticmethod
    def validateOtp(phone_number, code):
        try:
            otp = PhoneOTP.objects.get(phone_number=phone_number, isActif=True)

            print(f"=== OTP trouvé pour {phone_number} : {otp.code} ===")

            # Déjà expiré ?
            if timezone.now() - otp.create > timedelta(minutes=settings.TIME_EXPIRE_OTP):
                otp.isActif = False
                otp.save()
                print(f"=== OTP expiré pour {phone_number} : {code} ===")
                return False

            # Trop de tentatives ?
            if otp.attempts >= settings.ATTEMPTS_OTP:
                otp.isActif = False
                otp.save()
                print(f"=== OTP tentative pour {phone_number} : {code} ===")
                return False

            if otp.code == code:
                otp.isActif = False  # on désactive après utilisation
                otp.save()
                print(f"=== OTP validé pour {phone_number} : {code} ===")
                return True
            else:
                otp.attempts += 1
                otp.save()
                print(f"=== OTP invalide pour attempts {phone_number} : {code} ===")
                return False

        except PhoneOTP.DoesNotExist:
            return False

    class Meta:
        ordering = ('-create',)
        verbose_name = 'PhoneOTP'
        verbose_name_plural = 'PhoneOTP'

    def __str__(self):
        return f"{self.id}"

class Language(models.Model):
    """
    Modèle pour représenter les langues disponibles dans l'application.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la langue",
        help_text="Nom complet de la langue (ex: Français, English)"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Code de la langue",
        help_text="Code de la langue (ex: fr, en)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la langue est active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Langue"
        verbose_name_plural = "Langues"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Permission(models.Model):
    """
    Modèle pour définir les permissions disponibles dans l'application.
    
    Les permissions sont définies par ressource (app_profile, finance_app, etc.)
    et action (view, create, edit, delete).
    """
    
    RESOURCE_CHOICES = [
        ('app_profile', 'Profile Application'),
        ('app_academic', 'Academic Application'),
        ('app_grades', 'Grades Application'),
        ('app_attendance', 'Attendance Application'),
        ('app_config', 'Configuration Application'),
    ]
    
    ACTION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('verify', 'Verify'),
        ('manage', 'Manage'),
    ]
    
    # Informations de base
    name = models.CharField(
        max_length=200,
        verbose_name="Permission Name",
        help_text="Nom unique de la permission (ex: app_profile.view_profile)"
    )
    
    codename = models.CharField(
        verbose_name="Code Name",
        help_text="Code unique de la permission (ex: view_profile)"
    )
    
    resource = models.CharField(
        max_length=50,
        choices=RESOURCE_CHOICES,
        verbose_name="Resource",
        help_text="Ressource concernée par cette permission"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action",
        help_text="Action autorisée par cette permission"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de la permission"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si la permission est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['resource', 'action', 'name']
        unique_together = [['resource', 'action', 'codename']]
        indexes = [
            models.Index(fields=['resource', 'action']),
            models.Index(fields=['codename']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.resource}.{self.action})"


class Role(models.Model):
    """
    Modèle pour définir les rôles système.
    
    Les rôles peuvent avoir des permissions associées.
    """
    
    ROLE_TYPE_CHOICES = [
        ('system', 'System Role'),
        ('custom', 'Custom Role'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Role Name",
        help_text="Nom du rôle (ex: Admin, User, Manager)"
    )
    
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Code Name",
        help_text="Code unique du rôle (ex: admin, user)"
    )
    
    role_type = models.CharField(
        max_length=20,
        choices=ROLE_TYPE_CHOICES,
        default='custom',
        verbose_name="Role Type",
        help_text="Type de rôle (système ou personnalisé)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description du rôle"
    )
    
    permissions = models.ManyToManyField(
        'Permission',
        blank=True,
        related_name='roles',
        verbose_name="Permissions",
        help_text="Permissions associées à ce rôle"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si le rôle est actif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']
        indexes = [
            models.Index(fields=['codename']),
        ]
    
    def __str__(self):
        return self.name


class UserPermission(models.Model):
    """
    Modèle pour lier les permissions aux profils utilisateurs.
    
    Permet d'assigner des permissions spécifiques à un utilisateur,
    en plus des permissions de son rôle.
    
    Un profil peut recevoir plusieurs permissions dans un même enregistrement.
    """
    
    profile = models.ForeignKey(
        'app_profile.Profile',
        on_delete=models.CASCADE,
        related_name='user_permissions',
        verbose_name="Profile",
        help_text="Profil utilisateur"
    )
    
    permissions = models.ManyToManyField(
        'Permission',
        related_name='user_permissions',
        verbose_name="Permissions",
        help_text="Permissions assignées"
    )
    
    granted = models.BooleanField(
        default=True,
        verbose_name="Granted",
        help_text="True pour accorder, False pour refuser explicitement"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Indique si cette assignation de permissions est active"
    )
    
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permissions_granted',
        verbose_name="Granted By",
        help_text="Utilisateur qui a accordé ces permissions"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "User Permission"
        verbose_name_plural = "User Permissions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', 'granted']),
            models.Index(fields=['profile', 'is_active']),
        ]
    
    def __str__(self):
        status = "Granted" if self.granted else "Denied"
        permissions_count = self.permissions.count()
        return f"{self.profile.full_name} - {permissions_count} permission(s) ({status})"


class UserRole(models.Model):
    """
    Modèle pour lier les rôles aux profils utilisateurs.
    
    Un utilisateur peut avoir plusieurs rôles.
    """
    
    profile = models.ForeignKey(
        'app_profile.Profile',
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="Profile",
        help_text="Profil utilisateur"
    )
    
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name="Role",
        help_text="Rôle assigné"
    )
    
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned',
        verbose_name="Assigned By",
        help_text="Utilisateur qui a assigné ce rôle"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si le rôle est actif pour cet utilisateur"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = [['profile', 'role']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', 'role']),
        ]
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.role.name}"