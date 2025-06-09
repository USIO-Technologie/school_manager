from django.db import models
from django.contrib.auth.models import User, AbstractUser

class Role(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "ROLES"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Profil(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    nom = models.CharField(max_length=150)
    date_naissance = models.DateTimeField(blank=True, null=True)
    matricule = models.CharField(max_length=50, unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    roles = models.ManyToManyField(Role, related_name='profil', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "PROFILS"
        ordering = ['nom']
        
    def __str__(self):
        return f"{self.nom} ({self.user.username})"
