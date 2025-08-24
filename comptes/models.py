from django.contrib.auth.models import User
import random
from school_manager import settings
from ecoles.models import Ecole
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Role(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation" )
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Date Modification")
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Role_createby", verbose_name="Créé par")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Role_updateby", verbose_name="Mis à jour par")

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "ROLES"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Profil(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    ecoles = models.ManyToManyField(Ecole, related_name='profil', blank=True)
    nom = models.CharField(max_length=150)
    date_naissance = models.DateTimeField(blank=True, null=True)
    matricule = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    roles = models.ManyToManyField(Role, related_name='profil', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation" )
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Date Modification")
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Profil_createby", verbose_name="Créé par")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Profil_updateby", verbose_name="Mis à jour par")
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "PROFILS"
        ordering = ['nom']
        
    def __str__(self):
        return f"{self.nom} ({self.user.username})"

class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
    
    def is_blocked(self):
        return self.blocked or self.attempts >= 3
    
    def generer_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.attempts = 0
        self.blocked = False
        self.created_at = timezone.now()
        print(f"*********************EmailOTP generer_otp otp: {self.otp}")
        self.save()
        
    def verifier_otp(self, code_saisi):
        if self.is_expired():
            self.blocked = True
            self.save()
            return "expired"

        if self.is_blocked():
            return "blocked"

        if self.otp == code_saisi:
            self.blocked = True  # Block after successful verification
            self.save()
            return "ok"
        else:
            self.attempts += 1
            if self.attempts >= 3:
                self.blocked = True
            self.save()
            return "invalid"
    


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() - self.created_at < timedelta(hours=1)