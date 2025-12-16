# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Empêche la génération de .pyc et force les logs à s’afficher immédiatement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail pour tout le reste de la build
WORKDIR /app

# DuckDB de démonstration embarqué pour faire tourner dbt/Streamlit sans clé API
RUN mkdir -p /app/data
COPY data/demo_warehouse.duckdb /app/data/warehouse.duckdb

# Installe make et git (pour le Makefile et dbt), puis nettoie les caches apt
RUN apt-get update && \
    apt-get install -y make git && \
    rm -rf /var/lib/apt/lists/*

# Installe les dépendances en montant requirements.txt sans copier tout le repo,
# et en réutilisant le cache pip entre builds
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copie tout le projet dans /app
COPY . .

# Pointe dbt vers le dossier des profils dans l’image
ENV DBT_PROFILES_DIR=/app/profiles

# Indique que le service écoute sur le port 8501
EXPOSE 8501

# Commande par défaut au démarrage du conteneur
CMD ["make", "help"]
