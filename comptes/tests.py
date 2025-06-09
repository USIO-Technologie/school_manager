from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser

from ecoles.models import Ecole
from comptes.middleware import SchoolMiddleware
from comptes.models import Profil   # assure-toi qu'il existe

User = get_user_model()


class SchoolMiddlewareTest(TestCase):
    def setUp(self):
        self.factory     = RequestFactory()
        self.middleware  = SchoolMiddleware(lambda r: r)

        # -- Création d'une école complète (champs obligatoires) --
        self.ecole = Ecole.objects.create(
            nom="École Alpha",
            slogan="Excellence",
            description="",
            adresse="123 Rue X",
            ville="Kinshasa",
            pays="RDC",
            email_contact="alpha@example.com",
            telephone_contact="+243810000000"
        )

        # -- Création d'un utilisateur et de son profil --
        self.user = User.objects.create_user(
            username="tester",
            password="pass123"
        )
        # Si un signal auto-crée le profil, récupérons-le ; sinon créons-le
        try:
            self.profil = self.user.profil # type: ignore
        except ObjectDoesNotExist:
            self.profil = Profil.objects.create(
                user=self.user,
                nom=self.user.username,
                matricule=f"M{self.user.pk}"
            )
        self.profil.ecoles.add(self.ecole)

    # utilitaire : ajoute une session valide à la requête
    def _add_session(self, request):
        session_mw = SessionMiddleware(lambda r: HttpResponse())
        session_mw.process_request(request)
        request.session.save()

    # ---------- TESTS -----------
    def test_ecole_injectee_si_selection_valide(self):
        request = self.factory.get("/")
        self._add_session(request)
        request.session["ecole_id"] = self.ecole.pk
        request.user = self.user

        self.middleware(request)
        self.assertEqual(request.ecole, self.ecole) # type: ignore

    def test_ecole_none_si_aucune_selection(self):
        request = self.factory.get("/")
        self._add_session(request)
        request.user = self.user

        self.middleware(request)
        self.assertIsNone(request.ecole) # type: ignore

    def test_ecole_none_si_selection_hors_profil(self):
        # crée une 2ᵉ école non liée au profil
        autre_ecole = Ecole.objects.create(
            nom="École Beta",
            slogan="",
            description="",
            adresse="456 Rue Y",
            ville="Lubumbashi",
            pays="RDC",
            email_contact="beta@example.com",
            telephone_contact="+243810000111"
        )
        request = self.factory.get("/")
        self._add_session(request)
        request.session["ecole_id"] = autre_ecole.pk      # id non autorisé
        request.user = self.user

        self.middleware(request)
        self.assertIsNone(request.ecole) # type: ignore

    def test_ecole_none_si_user_non_authentifie(self):
        request = self.factory.get("/")
        self._add_session(request)
        request.user = AnonymousUser()
        
        self.middleware(request)
        self.assertIsNone(request.ecole) # type: ignore
