from django.test import TestCase
from django.contrib.auth import get_user_model

from ecoles.models import Ecole
from comptes.models import Profil

User = get_user_model()

class DashboardDataViewTest(TestCase):
    def setUp(self):
        self.ecole = Ecole.objects.create(
            nom="Ecole Test",
            slogan="",
            description="",
            adresse="Rue 1",
            ville="Ville",
            pays="Pays",
            email_contact="a@a.com",
            telephone_contact="000"
        )
        self.user = User.objects.create_user(username="u", password="p")
        self.profil = Profil.objects.create(user=self.user, nom="u", matricule="M1")
        self.profil.ecoles.add(self.ecole)
        self.client.force_login(self.user)
        session = self.client.session
        session["ecole_id"] = self.ecole.id
        session.save()

    def test_dashboard_json_keys(self):
        response = self.client.get("/comptes/dashboard/data/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for key in [
            "effectif",
            "n_classes",
            "n_cours",
            "total_encaisse",
            "taux_presence",
            "chart",
            "timeline",
        ]:
            self.assertIn(key, data)
