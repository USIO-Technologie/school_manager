import random, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker

from ecoles.models import Ecole, CycleEtude
from academiques.models import Classe, Eleve, Cours
from finance.models import Paiement
from presence.models import Presence

fake = Faker("fr_FR")
User = get_user_model()


class Command(BaseCommand):
    help = "Crée des données de démonstration (écoles, classes, élèves, cours, paiements, présences)"

    def add_arguments(self, parser):
        parser.add_argument("--ecoles", type=int, default=1, help="Nombre d'écoles")
        parser.add_argument("--eleves", type=int, default=50, help="Élèves par école")

    def handle(self, *args, **opts):
        n_ecoles  = opts["ecoles"]
        n_eleves  = opts["eleves"]

        # superadmin déjà existant ?
        superuser, _ = User.objects.get_or_create(
            username="root", defaults=dict(email="root@example.com", is_superuser=True, is_staff=True)
        )
        if _.get("password") is not None:
            superuser.set_password("pass123")
            superuser.save()

        self.stdout.write(self.style.SUCCESS(f"✔ Superadmin root / pass123"))

        for i in range(n_ecoles):
            ecole = Ecole.objects.create(
                nom=f"Ecole Demo {i+1}",
                slogan="Excellence & Innovation",
                description=fake.paragraph(),
                adresse=fake.address(),
                ville=fake.city(),
                pays="RDC",
                email_contact=f"contact{i+1}@demo.ecole",
                telephone_contact=fake.phone_number(),
                create_by=superuser,
            )
            self.stdout.write(self.style.SUCCESS(f"✔ Créée : {ecole.nom}"))

            # cycles
            cycles = [
                CycleEtude.objects.get_or_create(nom="Primaire", defaults={"niveau": 1})[0],
                CycleEtude.objects.get_or_create(nom="Secondaire", defaults={"niveau": 2})[0],
            ]
            classes = []
            for cycle in cycles:
                for n in range(1, 3):
                    clazz = Classe.objects.create(
                        nom=f"{cycle.nom[:1]}{n}",
                        cycle=cycle,
                        ecole=ecole,
                        annee_scolaire="2024-2025",
                        create_by=superuser,
                    )
                    classes.append(clazz)

            # élèves
            eleves = []
            for _ in range(n_eleves):
                clazz = random.choice(classes)
                eleve = Eleve.objects.create(
                    nom=fake.last_name(),
                    prenom=fake.first_name(),
                    genre=random.choice(["M", "F"]),
                    date_naissance=fake.date_of_birth(minimum_age=6, maximum_age=18),
                    classe=clazz,
                    ecole=ecole,
                    create_by=superuser,
                )
                eleves.append(eleve)

            # cours
            courses = []
            for clazz in classes:
                for c in ["Maths", "Français", "Sciences"]:
                    course = Cours.objects.create(
                        nom=c,
                        description=f"Cours de {c}",
                        classe=clazz,
                        ecole=ecole,
                        create_by=superuser,
                    )
                    courses.append(course)

            # paiements (12 mois)
            for eleve in eleves:
                for m in range(1, 13):
                    date_pay = datetime.date(2024, m, random.randint(1, 28))
                    Paiement.objects.create(
                        eleve=eleve,
                        montant=Decimal("50.00"),
                        date_paiement=date_pay,
                        ecole=ecole,
                        create_by=superuser,
                    )

            # présences (semaine en cours)
            today = datetime.date.today()
            monday = today - datetime.timedelta(days=today.weekday())
            for eleve in eleves:
                for d in range(5):  # lun-ven
                    pres_date = monday + datetime.timedelta(days=d)
                    Presence.objects.create(
                        eleve=eleve,
                        date=pres_date,
                        present=random.choice([True, True, False]),
                        ecole=ecole,
                        create_by=superuser,
                    )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées"))