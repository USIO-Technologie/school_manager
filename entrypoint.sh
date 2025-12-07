#!/bin/bash
#set -e  #  Stoppe le script si une commande échoue
#set -o pipefail  #  Stoppe le script si une commande dans un pipe échoue

# ===========================================================
#  Migration de la base de données
# ===========================================================
echo " Running database migrations..."
# makemigrations peut créer de nouvelles migrations si elles n'existent pas
python manage.py makemigrations --noinput
# Applique toutes les migrations sur la base de données
python manage.py migrate --noinput

# ===========================================================
#  Collecte des fichiers statiques
# ===========================================================
echo " Collecting static files..."

# Collecte tous les fichiers statiques dans le dossier défini par STATIC_ROOT
mkdir -p /app/staticfiles
python manage.py collectstatic --noinput --clear

# Donner les permissions à l'utilisateur 1000
chown -R 1000:1000 /app/staticfiles
chmod -R 755 /app/staticfiles

# ===========================================================
# Lancement du serveur Gunicorn
# ===========================================================
echo " Starting Gunicorn..."
# exec remplace le shell actuel par Gunicorn, pour que les signaux Docker soient correctement reçus
# --workers : nombre de processus (adapté aux CPU)
# --threads : nombre de threads par worker
# --timeout : augmente le timeout pour éviter kill lors de requêtes longues
exec gunicorn school_manager.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
