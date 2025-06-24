from django.db import models
from django.conf import settings

from ecoles.models import Ecole
from academiques.models import Eleve


class Presence(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=True)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
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

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.eleve} - {self.date}"

    """migrations code
    operations = [
        migrations.CreateModel(
            name='Presence',
            fields=[...],
        )
    ]
    """
