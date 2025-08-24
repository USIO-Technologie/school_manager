from django.db import models
from django.conf import settings
from ecoles.models import Ecole
from academiques.models import Eleve

class Presence(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, verbose_name="Eleve")
    date = models.DateTimeField(verbose_name="Date", help_text="Date de presence")
    present = models.BooleanField(default=True, verbose_name="Est-il present ?")
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, verbose_name="Ecole")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creer Le ?")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last update ?")
    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Presence_createby",
    )
    update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="Presence_updateby",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Presence"
        verbose_name_plural = "Presences".upper()

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.eleve} - {self.date}"
