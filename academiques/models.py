from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from ecoles.models import Ecole, CycleEtude


class Classe(models.Model):
    nom = models.CharField(max_length=50, verbose_name="Nom")
    cycle = models.ForeignKey(CycleEtude, on_delete=models.CASCADE, verbose_name="Cycle")
    annee_scolaire = models.CharField(max_length=9, verbose_name="Annee Scolaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de creacion")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last update")
    is_active = models.BooleanField(default=True, verbose_name="Est active ?")
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Classe_createby",
    )
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Classe_updateby",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Classe"
        verbose_name_plural = "Classes".upper()

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom

class Eleve(models.Model):
    GENRE_CHOICES = (
        ("M", "Masculin"),
        ("F", "Feminin"),
    )

    # Modification de la relation avec User pour être optionnelle
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,  # Pour éviter la suppression en cascade
        verbose_name="User",
        related_name="eleve",
        null=True,  # Rend la relation optionnelle
        blank=True
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prenom")
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES, verbose_name="Genre")
    date_naissance = models.DateField(verbose_name="Date de naissance", help_text="Date de naissance de l'élève")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name="Classe")
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, verbose_name="Ecole")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creer le ?")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last update ?")
    is_active = models.BooleanField(default=True, verbose_name="Est-il actif ?")
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Eleve_createby",
    )
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Eleve_updateby",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Eleve"
        verbose_name_plural = "Eleves".upper()

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.prenom} {self.nom}"

class Cours(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name="Classe")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creer le ?")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last update ?")
    is_active = models.BooleanField(default=True, verbose_name="Est-il actif ?")
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Cours_createby",
    )
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Cours_updateby",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Courses"
        verbose_name_plural = "Courses".upper()

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom
