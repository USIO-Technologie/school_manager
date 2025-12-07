# ===========================================================
#  BASE IMAGE
# ===========================================================
# Utilise Python 3.13 slim : légère, sécurisée, maintenue
FROM python:3.13-slim AS base

# ===========================================================
#   VARIABLES D'ENVIRONNEMENT PYTHON
# ===========================================================
# Empêche Python de générer des fichiers .pyc
# → Réduit la pollution et la taille du conteneur
ENV PYTHONDONTWRITEBYTECODE=1

# Affiche les logs en temps réel (non bufferisés)
# → Utile pour Docker logs et monitoring
ENV PYTHONUNBUFFERED=1

# ===========================================================
#  RÉPERTOIRE DE TRAVAIL
# ===========================================================
# Définition du dossier de travail dans le conteneur
# Tous les fichiers seront relatifs à /app
WORKDIR /app

# ===========================================================
#  INSTALLATION DES DÉPENDANCES PYTHON
# ===========================================================
# Copie seulement requirements.txt pour utiliser le cache Docker
COPY requirements.txt .

# Installe les dépendances Python + Gunicorn
# Gunicorn : serveur WSGI pour Django
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn \
    && apt-get purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Pourquoi :
# - libpq-dev : nécessaire pour psycopg2 (PostgreSQL)
# - gcc : compilation temporaire des packages
# - purge/autoremove : réduit la taille finale de l’image

# ===========================================================
#  MÉTADONNÉES DU CONTENEUR
# ===========================================================
LABEL authors="Nsole"
LABEL version="1.0.0"
LABEL description="Conteneur Django prêt pour production derrière Caddy"

# ===========================================================
#  UTILISATEUR NON-ROOT
# ===========================================================
# Sécurité : exécuter le conteneur avec UID/GID 1000
USER 1000:1000

# ===========================================================
#  COPIE DU CODE SOURCE
# ===========================================================
# Copie tout le projet dans le conteneur
COPY . .

# ===========================================================
#  ENTRYPOINT
# ===========================================================
# Script pour lancer migrations, collectstatic ou autres initialisations
COPY --chmod=755 entrypoint.sh /entrypoint.sh


# ===========================================================
#  COMMANDE PAR DÉFAUT
# ===========================================================
# Lance Gunicorn avec WSGI Django
# - bind sur 0.0.0.0:8003 pour être accessible dans le réseau Docker
# - logs d’accès et d’erreur sur stdout/stderr (Docker friendly)
CMD ["gunicorn", "school_manager.wsgi:application", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]

# ===========================================================
#  NOTES
# ===========================================================
# - Caddy s’occupe du HTTPS et du reverse proxy
# - Le conteneur n’expose pas directement le port 80/443
# - Les données persistantes (DB, static files) sont gérées via volumes Docker Compose
