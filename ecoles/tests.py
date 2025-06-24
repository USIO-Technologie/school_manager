from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.urls import path
from django.http import HttpResponse
from django.views.generic import ListView

from ecoles.models import Ecole
from comptes.models import Profil, Role
from ecoles.mixins import EcoleRequiredMixin
from comptes.middleware import SchoolMiddleware   # ← pour injecter request.ecole

User = get_user_model()

# --------------------------------------------------------------------
#                          Dummy view
# --------------------------------------------------------------------
class EcoleListDummyView(EcoleRequiredMixin, ListView):
    model = Ecole

    def render_to_response(self, context, **kwargs):
        # retourne simplement les noms d'école séparés par virgule
        return HttpResponse(",".join(e.nom for e in context["object_list"]))


urlpatterns = [
    path("ecoles/", EcoleListDummyView.as_view()),
]

# utilitaire : ajoute une session à la requête
def add_session(request):
    mw = SessionMiddleware(lambda r: None)
    mw.process_request(request)
    request.session.save()

# --------------------------------------------------------------------
#                          TestCase
# --------------------------------------------------------------------
class EcoleMixinTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # superuser Django
        cls.superuser = User.objects.create_superuser(
            username="root", password="pass123", email="root@example.com"
        )

        # rôle admin_ecole
        role_admin, _ = Role.objects.get_or_create(nom="admin_ecole")

        # user normal + profil
        cls.user = User.objects.create_user(username="normal", password="pass123")
        profil = Profil.objects.create(user=cls.user, nom="Normal", matricule="N1")
        profil.roles.add(role_admin)

        # écoles
        cls.ecole_a = Ecole.objects.create(
            nom="Alpha",
            adresse="1 rue A", ville="VilleA", pays="RDC",
            email_contact="a@ex.cd", telephone_contact="+2431",
            create_by=cls.superuser
        )
        cls.ecole_b = Ecole.objects.create(
            nom="Beta",
            adresse="2 rue B", ville="VilleB", pays="RDC",
            email_contact="b@ex.cd", telephone_contact="+2432",
            create_by=cls.superuser
        )
        profil.ecoles.add(cls.ecole_a)   # l’utilisateur normal n’a accès qu’à Alpha

    # helper pour appeler la vue avec middleware
    def _response(self, user, ecole_id=None):
        factory = RequestFactory()
        req = factory.get("/ecoles/")
        add_session(req)
        req.user = user
        if ecole_id:
            req.session["ecole_id"] = ecole_id

        # injecte request.ecole via le middleware
        SchoolMiddleware(lambda r: r)(req)

        return EcoleListDummyView.as_view()(req)

    # --------------- TESTS ----------------
    def test_slug_and_create_by(self):
        self.assertEqual(self.ecole_a.slug, "alpha")
        self.assertEqual(self.ecole_a.create_by, self.superuser)

    def test_user_without_school_gets_403(self):
        resp = self._response(self.user)                # pas de ecole_id
        self.assertEqual(resp.status_code, 403)

    def test_user_sees_only_his_school(self):
        resp = self._response(self.user, self.ecole_a.id)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alpha")

    def test_superuser_sees_all(self):
        resp = self._response(self.superuser)           # aucun filtre
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alpha")
        self.assertContains(resp, "Beta")
