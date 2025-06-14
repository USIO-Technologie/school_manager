from django.db import models
from django.conf import settings

from ecoles.models import Ecole, CycleEtude


class Classe(models.Model):
    nom = models.CharField(max_length=50)
    cycle = models.ForeignKey(CycleEtude, on_delete=models.CASCADE)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE)
    annee_scolaire = models.CharField(max_length=9)

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom

    """migrations code
    operations = [
        migrations.CreateModel(
            name='Classe',
            fields=[...],
        )
    ]
    """


class Eleve(models.Model):
    GENRE_CHOICES = (
        ("M", "Masculin"),
        ("F", "Feminin"),
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    date_naissance = models.DateField()
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.prenom} {self.nom}"

    """migrations code
    operations = [
        migrations.CreateModel(
            name='Eleve',
            fields=[...],
        )
    ]
    """


class Cours(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom

    """migrations code
    operations = [
        migrations.CreateModel(
            name='Cours',
            fields=[...],
        )
    ]
    """
