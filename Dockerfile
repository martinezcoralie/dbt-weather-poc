# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# --- AJOUT ICI ---
# On installe Make et Git (nécessaires pour ton Makefile et dbt)
# On nettoie ensuite les fichiers temporaires pour garder l'image légère
RUN apt-get update && \
    apt-get install -y make git && \
    rm -rf /var/lib/apt/lists/*
# -----------------

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

ENV DBT_PROFILES_DIR=/app/profiles

EXPOSE 8501

CMD ["make", "help"]