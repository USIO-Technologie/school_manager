# comptes/mixins.py
from django.http import HttpResponseForbidden
from django.core.exceptions import FieldError


class EcoleRequiredMixin:
    """
    • Bloque l'accès si aucune école active *sauf* pour les super-admins.
    • Filtre automatiquement le queryset sur .ecole=request.ecole,
      sauf pour les super-admins.

    ▸ L'utilisateur est considéré super-admin si
        - user.is_superuser  (drapeau Django natif)  **ou**
        - user.role == 'superadmin'  (ton champ perso)
    """

    # ---------- ACCÈS ----------
    def dispatch(self, request, *args, **kwargs):
        if self._is_superadmin(request.user):
            return super().dispatch(request, *args, **kwargs)

        if not getattr(request, "ecole", None):
            return HttpResponseForbidden("Sélectionnez d'abord une école.")

        return super().dispatch(request, *args, **kwargs)

    # ---------- FILTRAGE ----------
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if self._is_superadmin(user):
            return qs  # super-admin voit tout

        try:
            return qs.filter(ecole=self.request.ecole)
        except (FieldError, AttributeError):
            return qs  # modèle sans champ 'ecole'

    # ---------- UTILITAIRE ----------
    @staticmethod
    def _is_superadmin(user):
        return user.is_superuser or getattr(user, "role", "") == "superadmin"
