# Generated manually

import uuid
from django.db import migrations, models


def generate_uuid_for_profiles(apps, schema_editor):
    """Génère un UUID unique pour chaque profil existant."""
    Profile = apps.get_model('app_profile', 'Profile')
    for profile in Profile.objects.all():
        profile.reference = uuid.uuid4()
        profile.save(update_fields=['reference'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_profile', '0005_alter_profile_country_delete_country'),
    ]

    operations = [
        # Ajouter le champ reference pour Profile (sans unique d'abord)
        migrations.AddField(
            model_name='profile',
            name='reference',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text='Référence unique UUID du profil',
                null=True,
                verbose_name='Référence'
            ),
        ),
        # Générer les UUIDs pour les profils existants
        migrations.RunPython(generate_uuid_for_profiles, migrations.RunPython.noop),
        # Rendre le champ unique maintenant que tous les profils ont un UUID
        migrations.AlterField(
            model_name='profile',
            name='reference',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text='Référence unique UUID du profil',
                unique=True,
                verbose_name='Référence'
            ),
        ),
        # Ajouter l'index
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(fields=['reference'], name='app_profile_referen_idx'),
        ),
    ]

