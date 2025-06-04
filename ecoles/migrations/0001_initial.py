from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ecole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=255, unique=True)),
                ("slug", models.SlugField(blank=True, unique=True)),
                ("slogan", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                ("logo", models.ImageField(upload_to="ecoles")),
                ("adresse", models.CharField(max_length=255)),
                ("ville", models.CharField(max_length=100)),
                ("pays", models.CharField(max_length=100)),
                ("email_contact", models.EmailField(max_length=254)),
                ("telephone_contact", models.CharField(max_length=50)),
                ("site_web", models.URLField(blank=True)),
                ("map_link", models.URLField(blank=True)),
                ("nom_directeur", models.CharField(blank=True, max_length=255)),
                ("email_directeur", models.EmailField(blank=True, max_length=254)),
                ("telephone_directeur", models.CharField(blank=True, max_length=50)),
                (
                    "cycle",
                    models.CharField(
                        choices=[
                            ("maternelle", "Maternelle"),
                            ("primaire", "Primaire"),
                            ("secondaire", "Secondaire"),
                            ("supérieur", "Supérieur"),
                        ],
                        max_length=20,
                    ),
                ),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_ouverture", models.DateField(blank=True, null=True)),
                ("est_active", models.BooleanField(default=True)),
                ("langue_principale", models.CharField(default="fr", max_length=5)),
                ("theme_color", models.CharField(default="#000", max_length=7)),
                ("nombre_max_classes", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "École",
                "verbose_name_plural": "Écoles",
                "ordering": ["nom"],
            },
        ),
    ]

