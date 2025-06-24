from django.db import models
from django.utils.text import slugify

from ecoles.utils import generic_upload_to
from school_manager import settings


class Ecole(models.Model):
    """Modèle représentant une école."""

    nom = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    slogan = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, verbose_name="Description de l'ecole")
    logo = models.ImageField(upload_to=generic_upload_to, blank=True, null=True, verbose_name="Limage de l'ecole")

    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    email_contact = models.EmailField(max_length=100)
    telephone_contact = models.CharField(max_length=50)

    site_web = models.URLField(blank=True)
    map_link = models.URLField(blank=True)

    nom_directeur = models.CharField(max_length=255, blank=True)
    email_directeur = models.EmailField(blank=True)
    telephone_directeur = models.CharField(max_length=50, blank=True)

    cycle = models.ManyToManyField('CycleEtude', related_name='ecoles', blank=True)
    langues = models.ManyToManyField('Langue', related_name='ecoles', blank=True, verbose_name="Langues disponibles")
    langue_principale = models.ForeignKey(
        'Langue', related_name='ecoles_principales', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Langue principale"
    )
    theme_color = models.CharField(max_length=7, default="#000")
    nombre_max_classes = models.IntegerField(blank=True, null=True)
    date_ouverture = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation" )
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Date Modification")
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Ecole_createby", verbose_name="Créé par")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Ecole_updateby", verbose_name="Mis à jour par")
    

    class Meta:
        verbose_name = "Ecole"
        verbose_name_plural = "ECOLES"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

class CycleEtude(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    niveau = models.IntegerField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation" )
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Date Modification")
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="CycleEtude_createby", verbose_name="Créé par")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="CycleEtude_updateby", verbose_name="Mis à jour par")
    
    class Meta:
        verbose_name = "Cylce"
        verbose_name_plural= "CYCLES"
        ordering = ["-created_at"]
        
    def __str__(self):
        return self.nom
        
class Langue(models.Model):
    code = models.CharField(max_length=10, unique=True)  # ex: 'fr', 'en', 'ja'
    nom = models.CharField(max_length=100)               # ex: 'Français', 'Anglais', 'Japonais'
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date creation" )
    is_active = models.BooleanField(default=True, verbose_name="Est actif")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Date Modification")
    create_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Langue_createby", verbose_name="Créé par")
    update_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="Langue_updateby", verbose_name="Mis à jour par")
    
    class Meta:
        verbose_name = "Langue"
        verbose_name_plural = "LANGUES"
        ordering = ["-created_at"]

    def __str__(self):
        return self.nom
    
    