"""
Modèles pour l'application app_profile.

Ce module contient les modèles Django pour la gestion des profils utilisateurs,
des enfants et des organisations dans le système Monity World.

Architecture:
- ParentProfile: Profil principal du titulaire du compte
- ChildProfile: Profils secondaires rattachés à un parent
- Organisation: Entités (maison, famille, entreprise) avec gestion des membres
"""
from datetime import date
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from app_config.models import Country
from .managers import ParentProfileManager, ChildProfileManager, OrganisationManager, ProfileManager


class Profile(models.Model):
    """
    Modèle de base pour les profils utilisateurs.

    Ce modèle peut être étendu pour des profils spécifiques
    comme ParentProfile ou ChildProfile.
    """

    GENDER = [('male', 'Masculin'), ('female', 'Féminin'), ('other', 'Autre')]

    # Relation avec le système d'authentification Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        help_text="Utilisateur Django associé à ce profil",
        related_name="profile"
    )

    # Référence unique UUID
    reference = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name="Référence",
        help_text="Référence unique UUID du profil"
    )

    # Informations personnelles
    full_name = models.CharField(
        max_length=200,
        verbose_name="Nom complet",
        help_text="Nom et prénom du titulaire du compte"
    )

    firstname = models.CharField(
        max_length=100,
        verbose_name="Prénom",
        null=True,
        blank=True,
        help_text="Prénom du titulaire du compte"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nom de famille",
        null=True,
        blank=True,
        help_text="Nom de famille du titulaire du compte"
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de naissance",
        help_text="Date de naissance du titulaire (optionnel)"
    )

    id_card_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de pièce d'identité",
        help_text="Numéro de la pièce d'identité (optionnel)"
    )

    pincode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Code PIN",
        help_text="Code PIN personnel (optionnel)"
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER,
        blank=True,
        null=True,
        verbose_name="Genre",
        help_text="Genre du titulaire (optionnel)"
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        verbose_name="Pays",
        blank=True,
        null=True,
        help_text="Pays d'origine du titulaire"
    )

    # Informations de contact (optionnelles)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone (optionnel)"
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Vérifié",
        help_text="Indique si le profil a été vérifié"
    )

    # Rôle principal du profil
    ROLE_CHOICES = [
        ('student', 'Élève'),
        ('teacher', 'Enseignant'),
        ('parent', 'Parent'),
        ('admin', 'Administrateur'),
        ('staff', 'Personnel'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Rôle",
        help_text="Rôle principal du profil"
    )

    # Limite de wallets
    max_wallets = models.PositiveIntegerField(
        default=5,
        verbose_name="Nombre maximum de wallets",
        help_text="Nombre maximum de wallets que cet utilisateur peut créer (0 = illimité)"
    )

    # Photo de profil
    photo = models.ImageField(
        upload_to='profiles/photos/',
        blank=True,
        null=True,
        verbose_name="Photo de profil",
        help_text="Photo de profil de l'utilisateur (max 2 Mo)"
    )

    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le profil est actif"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    objects = ProfileManager()

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ['created_at']
        unique_together = ['phone']
    
    def __str__(self):
        """Représentation textuelle du profil."""
        return f"{self.full_name} ({self.user.username})"
    
    def get_completion_rate(self):
        """
        Calcule le taux de complétion du profil.
        
        Vérifie les champs clés du profil et retourne un pourcentage
        de complétion basé sur les champs remplis.
        
        Returns:
            int: Pourcentage de complétion (0-100)
        """
        # Champs clés à vérifier
        key_fields = [
            'full_name',
            'firstname',
            'name',
            'birth_date',
            'gender',
            'country',
            'phone',
            'pincode',
        ]
        
        # Compter les champs remplis
        filled_fields = 0
        for field_name in key_fields:
            value = getattr(self, field_name, None)
            if value:  # Si le champ a une valeur (non None, non vide)
                filled_fields += 1
        
        # Calculer le pourcentage
        completion_rate = int((filled_fields / len(key_fields)) * 100)
        return completion_rate
    
    @property
    def completion_rate(self):
        """
        Propriété pour accéder facilement au taux de complétion.
        
        Returns:
            int: Pourcentage de complétion (0-100)
        """
        return self.get_completion_rate()
    
    def is_admin_user(self):
        """
        Vérifie si ce profil a le rôle administrateur.
        
        Returns:
            bool: True si le profil est admin, False sinon
        """
        try:
            from app_config.permissions import is_admin
            return is_admin(self)
        except Exception:
            return False
    
    @classmethod
    def user_exists_by_phone(cls, phone):
        """
        Vérifie si un utilisateur existe par son numéro de téléphone.
        
        Args:
            phone (str): Numéro de téléphone à vérifier
        
        Returns:
            bool: True si un utilisateur existe avec ce numéro, False sinon
        """
        from django.contrib.auth.models import User
        
        # Vérifier dans User (username) et Profile (phone)
        user_exists = User.objects.filter(username=phone, is_active=True).exists()
        profile_exists = cls.objects.filter(phone=phone, is_active=True).exists()
        
        return user_exists or profile_exists

class ParentProfile(models.Model):
    """
    Modèle représentant le profil principal du titulaire du compte.
    
    Ce modèle hérite de models.Model et utilise une relation OneToOneField
    avec le modèle User de Django pour l'authentification.
    """

    profile = models.OneToOneField(Profile, verbose_name="Profile", on_delete=models.CASCADE, related_name="parent_profile")
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le profil est actif"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    # Manager personnalisé
    objects = ParentProfileManager()
    
    class Meta:
        verbose_name = "Profil Parent"
        verbose_name_plural = "Profils Parents"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.profile.full_name
    
    def get_children(self):
        """
        Retourne la liste des ChildProfile liés à ce parent.
        
        Returns:
            QuerySet: Liste des profils enfants
        """
        return self.childprofile_set.all()
    
    def get_organisations(self):
        """
        Retourne les organisations associées à ce parent.
        
        Returns:
            QuerySet: Liste des organisations possédées par ce parent
        """
        return self.organisation_set.all()
    
    def get_children_count(self):
        """
        Retourne le nombre d'enfants associés à ce parent.
        
        Returns:
            int: Nombre d'enfants
        """
        return self.childprofile_set.count()
    
    def get_organisations_count(self):
        """
        Retourne le nombre d'organisations possédées par ce parent.
        
        Returns:
            int: Nombre d'organisations
        """
        return self.organisation_set.count()
    
    def can_add_child(self):
        """
        Vérifie si le parent peut ajouter un nouvel enfant.
        
        Cette méthode peut être étendue pour ajouter des règles métier
        comme des limites sur le nombre d'enfants.
        
        Returns:
            bool: True si l'ajout est autorisé
        """
        return self.is_active
    
    def deactivate(self):
        """
        Désactive le profil parent et tous ses enfants.
        
        Cette méthode implémente la logique métier pour la désactivation
        en cascade des profils liés.
        """
        self.is_active = False
        self.save()
        
        # Désactiver tous les enfants
        for child in self.get_children():
            child.is_active = False
            child.save()

class Organisation(models.Model):
    """
    Modèle représentant une entité organisationnelle.
    
    Ce modèle peut représenter une maison, une famille élargie,
    une entreprise ou toute autre forme d'organisation.
    """
    
    # Informations de base
    name = models.CharField(
        max_length=200,
        verbose_name="Nom",
        help_text="Nom de l'organisation"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de l'organisation (optionnel)"
    )
    
    # Relations
    owner = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        verbose_name="Propriétaire",
        help_text="Profil parent propriétaire de l'organisation"
    )
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'organisation est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    # Manager personnalisé
    objects = OrganisationManager()
    
    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        ordering = ['name', '-created_at']
        unique_together = ['owner', 'name']
    
    def __str__(self):
        return f"{self.name} (Propriétaire: {self.owner.profile.full_name})"
    
    def get_members(self):
        """
        Retourne les enfants ou membres de l'organisation.
        
        Returns:
            QuerySet: Membres de l'organisation
        """
        return self.members.filter(is_active=True)
    
    def get_members_count(self):
        """
        Retourne le nombre de membres actifs de l'organisation.
        
        Returns:
            int: Nombre de membres actifs
        """
        return self.get_members().count()
    
    def add_member(self, child_profile):
        """
        Ajoute un ChildProfile à l'organisation.
        
        Args:
            child_profile (ChildProfile): Profil enfant à ajouter
            
        Returns:
            bool: True si l'ajout a réussi
            
        Raises:
            ValueError: Si l'enfant ne peut pas être ajouté
        """
        if not child_profile.can_be_added_to_organisation(self):
            raise ValueError(
                f"L'enfant {child_profile.profile.full_name} ne peut pas être ajouté "
                f"à l'organisation {self.name}"
            )
        
        self.members.add(child_profile)
        return True
    
    def remove_member(self, child_profile):
        """
        Retire un ChildProfile de l'organisation.
        
        Args:
            child_profile (ChildProfile): Profil enfant à retirer
            
        Returns:
            bool: True si le retrait a réussi
        """
        self.members.remove(child_profile)
        return True
    
    def can_add_member(self, child_profile):
        """
        Vérifie si un enfant peut être ajouté à cette organisation.
        
        Args:
            child_profile (ChildProfile): Profil enfant à vérifier
            
        Returns:
            bool: True si l'ajout est possible
        """
        return child_profile.can_be_added_to_organisation(self)
    
    def get_owner_name(self):
        """
        Retourne le nom du propriétaire de l'organisation.
        
        Returns:
            str: Nom complet du propriétaire
        """
        return self.owner.profile.full_name
    
    def deactivate(self):
        """
        Désactive l'organisation.
        
        Cette méthode implémente la logique métier pour la désactivation
        de l'organisation.
        """
        self.is_active = False
        self.save()
        
        # Retirer tous les membres
        self.members.clear()

class DocumentVerification(models.Model):
    """
    Modèle pour gérer la vérification KYC des profils utilisateurs.
    
    Ce modèle stocke les documents soumis par les utilisateurs pour la vérification
    de leur identité (KYC - Know Your Customer).
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('id_card', 'Carte d\'identité'),
        ('passport', 'Passeport'),
        ('driver_license', 'Permis de conduire'),
        ('other', 'Autre document'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('under_review', 'En cours de vérification'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    # Relation avec le profil
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='verification_documents',
        verbose_name="Profil",
        help_text="Profil à vérifier"
    )
    
    # Type de document
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name="Type de document",
        help_text="Type de document d'identité"
    )
    
    # Fichiers du document
    document_front = models.ImageField(
        upload_to='verifications/documents/',
        verbose_name="Recto du document",
        help_text="Photo du recto du document (max 5 Mo)"
    )
    
    document_back = models.ImageField(
        upload_to='verifications/documents/',
        blank=True,
        null=True,
        verbose_name="Verso du document",
        help_text="Photo du verso du document (max 5 Mo, optionnel)"
    )
    
    # Photo de soi-même pour vérification
    selfie_photo = models.ImageField(
        upload_to='verifications/selfies/',
        verbose_name="Photo de soi-même",
        help_text="Photo de soi-même pour la vérification (max 5 Mo)"
    )
    
    # Adresse
    address = models.TextField(
        verbose_name="Adresse",
        help_text="Adresse complète de l'utilisateur"
    )
    
    # Statut de vérification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut",
        help_text="Statut de la vérification"
    )
    
    # Commentaires et notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes administrateur",
        help_text="Notes internes pour la vérification"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="Raison du rejet",
        help_text="Raison du rejet si la vérification est refusée"
    )
    
    # Métadonnées
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents',
        verbose_name="Vérifié par",
        help_text="Administrateur qui a vérifié le document"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de vérification",
        help_text="Date à laquelle le document a été vérifié"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de soumission"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Vérification de document"
        verbose_name_plural = "Vérifications de documents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.get_document_type_display()} ({self.get_status_display()})"
    
    def approve(self, verified_by, notes=None):
        """
        Approves the document verification.
        
        Args:
            verified_by: Administrator user who approves
            notes: Optional notes
        """
        self.status = 'approved'
        self.verified_by = verified_by
        self.verified_at = timezone.now()
        if notes:
            self.admin_notes = notes
        self.save()
        
        # Update profile verification status
        self.profile.is_verified = True
        self.profile.save()
    
    def reject(self, verified_by, reason):
        """
        Rejects the document verification.
        
        Args:
            verified_by: Administrator user who rejects
            reason: Rejection reason
        """
        self.status = 'rejected'
        self.verified_by = verified_by
        self.verified_at = timezone.now()
        self.rejection_reason = reason
        self.save()
        
        # Ensure profile is not verified
        self.profile.is_verified = False
        self.profile.save()
    
    def set_under_review(self):
        """Marque le document comme en cours de vérification."""
        self.status = 'under_review'
        self.save()
    
    @property
    def is_pending(self):
        """Retourne True si le document est en attente."""
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        """Retourne True si le document est approuvé."""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Retourne True si le document est rejeté."""
        return self.status == 'rejected'

class UserSession(models.Model):
    """
    Modèle pour gérer les sessions actives des utilisateurs.
    
    Permet de suivre les sessions actives et de les gérer
    (déconnexion à distance, etc.).
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_sessions',
        verbose_name="Utilisateur",
        help_text="Utilisateur propriétaire de la session"
    )
    
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Clé de session",
        help_text="Clé unique de la session Django"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP de la connexion"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="User agent du navigateur/appareil"
    )
    
    device_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom de l'appareil",
        help_text="Nom identifiant l'appareil (ex: Chrome on Windows)"
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localisation",
        help_text="Localisation estimée (ville, pays)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si la session est active"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière activité",
        help_text="Dernière activité sur cette session"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé à",
        help_text="Date de création de la session"
    )
    
    class Meta:
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateur"
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name or 'Unknown'} ({self.ip_address})"

class LoginHistory(models.Model):
    """
    Modèle pour l'historique des connexions.
    
    Enregistre toutes les tentatives de connexion (réussies et échouées).
    """
    
    STATUS_CHOICES = [
        ('success', 'Succès'),
        ('failed', 'Échec'),
        ('blocked', 'Bloqué'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        null=True,
        blank=True,
        verbose_name="Utilisateur",
        help_text="Utilisateur concerné (null si échec)"
    )
    
    username = models.CharField(
        max_length=150,
        verbose_name="Nom d'utilisateur",
        help_text="Nom d'utilisateur utilisé pour la connexion"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP de la connexion"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="User agent du navigateur/appareil"
    )
    
    device_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nom de l'appareil",
        help_text="Nom identifiant l'appareil"
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localisation",
        help_text="Localisation estimée"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        verbose_name="Statut",
        help_text="Statut de la tentative de connexion"
    )
    
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Raison de l'échec",
        help_text="Raison de l'échec de connexion (si applicable)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date",
        help_text="Date et heure de la tentative"
    )
    
    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['username', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        status_display = self.get_status_display()
        return f"{self.username} - {status_display} ({self.created_at})"

class TrustedDevice(models.Model):
    """
    Modèle pour les appareils de confiance.
    
    Permet aux utilisateurs de marquer des appareils comme de confiance
    pour éviter les vérifications répétées.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trusted_devices',
        verbose_name="Utilisateur",
        help_text="Utilisateur propriétaire de l'appareil"
    )
    
    device_name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'appareil",
        help_text="Nom identifiant l'appareil"
    )
    
    device_fingerprint = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Empreinte de l'appareil",
        help_text="Empreinte unique de l'appareil (hash)"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP lors de l'enregistrement"
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="User agent de l'appareil"
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localisation",
        help_text="Localisation lors de l'enregistrement"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'appareil est toujours de confiance"
    )
    
    last_used = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière utilisation",
        help_text="Dernière fois que l'appareil a été utilisé"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé à",
        help_text="Date d'enregistrement de l'appareil"
    )
    
    class Meta:
        verbose_name = "Appareil de confiance"
        verbose_name_plural = "Appareils de confiance"
        ordering = ['-last_used']
        unique_together = [['user', 'device_fingerprint']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_fingerprint']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_name}"

class UserPreferences(models.Model):
    """
    Modèle pour les préférences utilisateur.
    
    Stocke les préférences de langue, timezone, notifications,
    affichage et confidentialité.
    """
    
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
        ('es', 'Español'),
        ('pt', 'Português'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name="Profil",
        help_text="Profil utilisateur"
    )
    
    # Préférences de langue
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='fr',
        verbose_name="Langue",
        help_text="Langue préférée de l'interface"
    )
    
    # Préférences de timezone
    timezone = models.CharField(
        max_length=100,
        default='UTC',
        verbose_name="Timezone",
        help_text="Timezone préférée (ex: Africa/Kinshasa, UTC)"
    )
    
    # Paramètres de notification
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications email",
        help_text="Recevoir des notifications par email"
    )
    
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="Notifications SMS",
        help_text="Recevoir des notifications par SMS"
    )
    
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications push",
        help_text="Recevoir des notifications push"
    )
    
    transaction_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications de transactions",
        help_text="Recevoir des notifications pour les transactions"
    )
    
    security_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications de sécurité",
        help_text="Recevoir des notifications de sécurité"
    )
    
    # Préférences d'affichage
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light',
        verbose_name="Thème",
        help_text="Thème d'affichage préféré"
    )
    
    items_per_page = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
        verbose_name="Éléments par page",
        help_text="Nombre d'éléments à afficher par page"
    )
    
    # Paramètres de confidentialité
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('friends', 'Friends only'),
        ],
        default='private',
        verbose_name="Visibilité du profil",
        help_text="Qui peut voir votre profil"
    )
    
    show_email = models.BooleanField(
        default=False,
        verbose_name="Afficher l'email",
        help_text="Afficher l'email dans le profil public"
    )
    
    show_phone = models.BooleanField(
        default=False,
        verbose_name="Afficher le téléphone",
        help_text="Afficher le numéro de téléphone dans le profil public"
    )
    
    allow_search = models.BooleanField(
        default=True,
        verbose_name="Autoriser la recherche",
        help_text="Permettre aux autres utilisateurs de vous trouver"
    )
    
    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé à"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié à"
    )
    
    class Meta:
        verbose_name = "Préférences utilisateur"
        verbose_name_plural = "Préférences utilisateur"
    
    def __str__(self):
        return f"Préférences de {self.profile.full_name}"


class Student(models.Model):
    """
    Modèle représentant un élève.
    
    Ce modèle hérite via OneToOne du modèle Profile.
    """
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Profil",
        related_name="student",
        help_text="Profil associé à cet élève"
    )
    
    # Informations spécifiques à l'élève
    student_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Numéro d'élève",
        help_text="Numéro unique d'identification de l'élève"
    )
    
    enrollment_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date d'inscription",
        help_text="Date d'inscription de l'élève"
    )
    
    class_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Niveau de classe",
        help_text="Niveau ou classe de l'élève"
    )
    
    # Relations académiques
    class_section = models.ForeignKey(
        'app_academic.Class',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Classe",
        help_text="Classe de l'élève"
    )
    
    academic_year = models.ForeignKey(
        'app_academic.AcademicYear',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Année scolaire",
        help_text="Année scolaire de l'élève"
    )
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'élève est actif"
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
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_created',
        verbose_name="Créé par",
        help_text="Utilisateur qui a créé cet élève"
    )
    
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students_updated',
        verbose_name="Modifié par",
        help_text="Utilisateur qui a modifié cet élève"
    )
    
    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_number']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.student_number or 'Sans numéro'}"
    
    @classmethod
    def get_student(cls, student_id):
        """
        Récupère un élève actif par ID.
        
        Args:
            student_id: ID de l'élève
            
        Returns:
            Student ou None: Instance de l'élève ou None si non trouvé
        """
        instances = cls.objects.filter(id=student_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_active_students(cls):
        """
        Récupère tous les élèves actifs.
        
        Returns:
            QuerySet: Liste des élèves actifs
        """
        return cls.objects.filter(is_active=True).select_related('profile', 'profile__user')


class Teacher(models.Model):
    """
    Modèle représentant un enseignant.
    
    Ce modèle hérite via OneToOne du modèle Profile.
    """
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Profil",
        related_name="teacher",
        help_text="Profil associé à cet enseignant"
    )
    
    # Informations spécifiques à l'enseignant
    teacher_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Numéro d'enseignant",
        help_text="Numéro unique d'identification de l'enseignant"
    )
    
    hire_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date d'embauche",
        help_text="Date d'embauche de l'enseignant"
    )
    
    specialization = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Spécialisation",
        help_text="Domaine de spécialisation de l'enseignant"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Département",
        help_text="Département de l'enseignant"
    )
    
    # Relations académiques
    subjects = models.ManyToManyField(
        'app_academic.Subject',
        related_name='teachers',
        blank=True,
        verbose_name="Matières enseignées",
        help_text="Matières que l'enseignant enseigne"
    )
    
    classes = models.ManyToManyField(
        'app_academic.Class',
        related_name='teachers',
        blank=True,
        verbose_name="Classes enseignées",
        help_text="Classes où l'enseignant enseigne"
    )
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'enseignant est actif"
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
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers_created',
        verbose_name="Créé par",
        help_text="Utilisateur qui a créé cet enseignant"
    )
    
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teachers_updated',
        verbose_name="Modifié par",
        help_text="Utilisateur qui a modifié cet enseignant"
    )
    
    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher_number']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.teacher_number or 'Sans numéro'}"
    
    @classmethod
    def get_teacher(cls, teacher_id):
        """
        Récupère un enseignant actif par ID.
        
        Args:
            teacher_id: ID de l'enseignant
            
        Returns:
            Teacher ou None: Instance de l'enseignant ou None si non trouvé
        """
        instances = cls.objects.filter(id=teacher_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_active_teachers(cls):
        """
        Récupère tous les enseignants actifs.
        
        Returns:
            QuerySet: Liste des enseignants actifs
        """
        return cls.objects.filter(is_active=True).select_related('profile', 'profile__user')


class Parent(models.Model):
    """
    Modèle représentant un parent.
    
    Ce modèle hérite via OneToOne du modèle Profile.
    """
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Profil",
        related_name="parent",
        help_text="Profil associé à ce parent"
    )
    
    # Informations spécifiques au parent
    parent_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Numéro de parent",
        help_text="Numéro unique d'identification du parent"
    )
    
    relationship_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Type de relation",
        help_text="Type de relation (père, mère, tuteur, etc.)"
    )
    
    occupation = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Profession",
        help_text="Profession du parent"
    )
    
    emergency_contact = models.BooleanField(
        default=False,
        verbose_name="Contact d'urgence",
        help_text="Indique si ce parent est un contact d'urgence"
    )
    
    # Relations avec les enfants
    children = models.ManyToManyField(
        'app_profile.Student',
        related_name='parents',
        blank=True,
        verbose_name="Enfants",
        help_text="Enfants de ce parent"
    )
    
    # Statut et métadonnées
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le parent est actif"
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
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parents_created',
        verbose_name="Créé par",
        help_text="Utilisateur qui a créé ce parent"
    )
    
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parents_updated',
        verbose_name="Modifié par",
        help_text="Utilisateur qui a modifié ce parent"
    )
    
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent_number']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.parent_number or 'Sans numéro'}"
    
    @classmethod
    def get_parent(cls, parent_id):
        """
        Récupère un parent actif par ID.
        
        Args:
            parent_id: ID du parent
            
        Returns:
            Parent ou None: Instance du parent ou None si non trouvé
        """
        instances = cls.objects.filter(id=parent_id, is_active=True)
        if instances:
            return instances[0]
        return None
    
    @classmethod
    def get_active_parents(cls):
        """
        Récupère tous les parents actifs.
        
        Returns:
            QuerySet: Liste des parents actifs
        """
        return cls.objects.filter(is_active=True).select_related('profile', 'profile__user')
