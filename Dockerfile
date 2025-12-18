# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installe make et git (pour le Makefile et dbt), puis nettoie les caches apt
RUN apt-get update && apt-get install -y \
    make \
    git && \
    rm -rf /var/lib/apt/lists/*

# Démo DuckDB embarquée (hors /app/data pour ne pas être masqué par le volume)
RUN mkdir -p /app/demo /app/data
COPY data/demo_warehouse.duckdb /app/demo/demo_warehouse.duckdb

# Dépendances Python
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copie tout le projet dans /app
COPY . .

ENV DBT_PROFILES_DIR=/app/profiles

EXPOSE 8501 4200

# Entrypoint de seed
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

# L’entrypoint garantit que /app/data/warehouse.duckdb existe (seed si besoin)
ENTRYPOINT ["/app/docker/entrypoint.sh"]

CMD ["make", "help"]
