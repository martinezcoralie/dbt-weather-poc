# 🌤️ dbt-weather-poc — Pipeline analytics météo (dbt + DuckDB)

Pipeline analytique de bout en bout autour des observations horaires Météo-France : ingestion Python → **DuckDB** (`raw`) → **dbt** (`staging / intermediate / marts`) → **Streamlit** (dashboard).  
Orchestration locale **Prefect 3** disponible en option.

## Compétences dbt démontrées

- **Modélisation dbt “layered”** (`staging → intermediate → marts`) et conventions de structuration.
- **Qualité** : tests (génériques + métier), **contrats** sur modèles critiques, seeds, exposures.
- **Performance** : modèles **incrémentaux** (stratégie `merge`) et macros utilitaires.
- **Traçabilité** : **dbt Docs** (modèles, colonnes, tests, lineage, exposure).
- **Consommation BI** : dashboard Streamlit branché sur `marts.agg_station_latest_24h`.

## Architecture (résumé)

```text
Météo-France API
  ↓ (ingestion Python)
DuckDB raw.*
  ↓ (dbt build)
DuckDB staging → intermediate → marts
  ↓
Streamlit (dashboard)
  ↕ (option)
Prefect (schedule ingestion + dbt)
```

Détails : [docs/00-Architecture.md](docs/00-Architecture.md)

## Démarrage rapide

### Option A — Démo immédiate (image Docker publique)

Une image Docker publique est fournie avec un **DuckDB de démonstration** (pas de token requis).

```bash
IMAGE=dbt-weather-poc/weather-app:latest
docker pull "$IMAGE"
docker run --rm -p 8501:8501 "$IMAGE" make app VENV=system
# Dashboard : http://localhost:8501
```

### Option B — Explorer le pipeline en Docker Compose (multi-services)

Le `compose.yaml` propose des services et profils pour rejouer **dbt**, lancer l’**ingestion** (token requis) et démarrer **Prefect**.

Démarrer le dashboard (démo) :

```bash
docker compose up --build app
```

Rejouer dbt (job ponctuel, tests inclus) :

```bash
docker compose --profile build run --rm dbt
```

Ingestion réelle (token requis) :

```bash
DEPT=75 docker compose --profile ingest run --rm ingest
```

Orchestration Prefect (option) :

```bash
docker compose --profile prefect up --build prefect-server
# UI Prefect : http://localhost:4200
docker compose --profile prefect up --build prefect
```

Reset complet (reseed du DuckDB démo au prochain run) :

```bash
docker compose down -v
```

Détails et explications : [README.Docker.md](README.Docker.md) 

### Option C — Développement local (sans Docker)

Pré-requis : token Météo-France (voir [docs/10-Setup.md](docs/10-Setup.md))

```bash
make env-setup && source .venv/bin/activate
export DBT_PROFILES_DIR=./profiles

make dwh-ingest DEPT=75
make dbt-build
make app
```

#### Commandes (Makefile)

Toutes les commandes (ingestion, dbt, docs, utilitaires DuckDB, lint, etc.) sont centralisées dans le **Makefile** :

```bash
make help
```

## Vérifier rapidement la modélisation (dbt Docs)

```bash
make dbt-docs
# http://localhost:8080
```

## Documentation
- Index : [docs/README.md](docs/README.md)
- Docker / Compose : [README.Docker.md](README.Docker.md)