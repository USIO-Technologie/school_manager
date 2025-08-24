# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404, NoReverseMatch

class SchoolMiddleware:
    EXEMPT_URL_NAMES = {
        "comptes:choisir_ecole", "choisir_ecole",
        "comptes:login", "login",
        "comptes:logout", "logout",
    }
    EXEMPT_PREFIXES = ("/admin/", "/static/", "/media/")
    EXEMPT_PATHS    = ("/comptes/choisir-ecole/", "/accounts/login/", "/comptes/login/", "/comptes/logout/")

    def __init__(self, get_response):
        self.get_response = get_response

    def _reverse_safe(self, *names, fallback="/comptes/choisir-ecole/"):
        for name in names:
            try:
                return reverse(name)
            except NoReverseMatch:
                pass
        return fallback

    def __call__(self, request):
        # 0) Laisser passer les anonymes
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 1) Hydrater request.ecole depuis la session si possible
        request.ecole = None
        profil = getattr(request.user, "profil", None)
        if profil is not None:
            ecole_id = request.session.get("ecole_id")
            if ecole_id:
                try:
                    request.ecole = profil.ecoles.get(pk=ecole_id)
                except profil.ecoles.model.DoesNotExist:
                    request.session.pop("ecole_id", None)

        # 2) Déterminer l’exemption de façon robuste
        path = request.path_info or "/"

        # a) par préfixe
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return self.get_response(request)
        # b) par chemin exact connu (fallback)
        if path in self.EXEMPT_PATHS:
            return self.get_response(request)
        # c) par nom, en résolvant explicitement le chemin (ne pas lire request.resolver_match ici)
        try:
            match = resolve(path)
            full_name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name
            if (match.url_name in self.EXEMPT_URL_NAMES) or (full_name in self.EXEMPT_URL_NAMES):
                return self.get_response(request)
        except Resolver404:
            # Si on ne sait pas résoudre, ne bloque pas “à l’aveugle”
            return self.get_response(request)

        # 3) Redirection uniquement si pas d'école
        if not request.user.is_superuser and request.ecole is None:
            target = self._reverse_safe("comptes:choisir_ecole", "choisir_ecole")
            return redirect(target)

        return self.get_response(request)
