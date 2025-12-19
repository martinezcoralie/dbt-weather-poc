# Setup

## Pré‑requis

- Python (utilisé par les scripts ingestion, dbt, Streamlit, Prefect)
- `make`
- (Option) Docker Desktop / Docker Compose v2

## Installation (mode local)

```bash
make env-setup
source .venv/bin/activate
export DBT_PROFILES_DIR=./profiles
```

## Configuration (.env)

Créer un fichier `.env` à la racine (ne pas le commiter).

Exemple minimal :

```bash
# API Météo‑France (requis pour l’ingestion réelle)
METEOFRANCE_TOKEN=xxxxx

# Chemin du warehouse (adapter si besoin)
DUCKDB_PATH=data/warehouse.duckdb
```

## 🔑 Obtenir une clé API Météo-France

1) Créer un compte sur le portail des API Météo-France  
   - Ouvrir la page “Données Publiques – Paquet Observation” : https://portail-api.meteofrance.fr/web/fr/api/DonneesPubliquesPaquetObservation  
   - Cliquer sur **“Souscrire à l’API gratuitement”** (clé gratuite, usage raisonnable)

2) Récupérer le token et le placer dans `.env` 

## Vérification rapide

```bash
make api-check
```

En cas d’échec : vérifier le token, la connectivité réseau et les quotas API.

Prochaine étape : [20-Ingestion.md](20-Ingestion.md).
