# Generated by Django 5.2.1 on 2025-05-29 08:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'ROLES',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Profil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
                ('date_naissance', models.DateTimeField(blank=True, null=True)),
                ('matricule', models.CharField(max_length=50, unique=True)),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
                ('roles', models.ManyToManyField(blank=True, related_name='profil', to='comptes.role')),
            ],
            options={
                'verbose_name': 'Profil',
                'verbose_name_plural': 'PROFILS',
                'ordering': ['nom'],
            },
        ),
    ]
