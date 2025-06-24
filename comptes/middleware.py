# comptes/middleware.py
from django.http import HttpResponseForbidden
from ecoles.models import Ecole

class SchoolMiddleware:
    """Assure qu'une 'école active' est connue pour tout utilisateur connecté."""
    EXEMPT_PATHS = ("/comptes/choisir-ecole/", "/comptes/logout/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.ecole = None

        if request.user.is_authenticated and hasattr(request.user, "profil"):
            profil = request.user.profil
            ecole_id = request.session.get("ecole_id")

            if ecole_id:                       # tente de récupérer
                try:
                    request.ecole = profil.ecoles.get(pk=ecole_id)
                except Ecole.DoesNotExist:     # ID plus valide → purge
                    request.session.pop("ecole_id", None)

        # blocage si aucune école choisie (et vue non exempte)
        if request.user.is_authenticated and request.ecole is None \
           and request.path not in self.EXEMPT_PATHS and not request.user.is_superuser:
            return HttpResponseForbidden("Sélectionnez une école pour continuer.")

        return self.get_response(request)
