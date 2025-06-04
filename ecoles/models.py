from django.db import models
from django.utils.text import slugify


class Ecole(models.Model):
    """Modèle représentant une école."""

    CYCLE_CHOICES = [
        ("maternelle", "Maternelle"),
        ("primaire", "Primaire"),
        ("secondaire", "Secondaire"),
        ("supérieur", "Supérieur"),
    ]

    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    slogan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="ecoles")

    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    email_contact = models.EmailField()
    telephone_contact = models.CharField(max_length=50)

    site_web = models.URLField(blank=True)
    map_link = models.URLField(blank=True)

    nom_directeur = models.CharField(max_length=255, blank=True)
    email_directeur = models.EmailField(blank=True)
    telephone_directeur = models.CharField(max_length=50, blank=True)

    cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_ouverture = models.DateField(blank=True, null=True)

    est_active = models.BooleanField(default=True)
    langue_principale = models.CharField(max_length=5, default="fr")
    theme_color = models.CharField(max_length=7, default="#000")
    nombre_max_classes = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "École"
        verbose_name_plural = "Écoles"
        ordering = ["nom"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

