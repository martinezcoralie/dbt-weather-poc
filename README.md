# 🌤️ dbt-weather-poc — Pipeline analytics météo (dbt + DuckDB)

Pipeline analytique de bout en bout autour des observations horaires Météo-France : ingestion Python → **DuckDB** (`raw`) → **dbt** (`staging / intermediate / marts`) → **Streamlit** (dashboard).  
Orchestration locale **Prefect 3** disponible.

## Compétences principales démontrées (dbt)

- **Modélisation dbt “layered”** (`staging → intermediate → marts`) et conventions de structuration.
- **Sources + fraîcheur** : sources dbt déclarées avec `loaded_at_field` et seuils de freshness (warn/error).
- **Qualité** : tests (génériques + métier), **contrats** sur modèles critiques, seeds, exposures.
- **Performance** : modèles **incrémentaux** (stratégie `merge`) et macros utilitaires.
- **Traçabilité** : **dbt Docs** (modèles, colonnes, tests, lineage, exposure).
- **Consommation BI** : mart BI stable (`marts.agg_station_latest_24h`) consommé par le dashboard Streamlit.


## Compétences complémentaires démontrées (delivery)

- **Docker / Compose** : image Docker publique (démo sans token) + `docker compose` multi-services pour rejouer ingestion, dbt et Prefect.
- **CI/CD (GitHub Actions)** : CI dbt sur données réelles + publication automatique des **dbt Docs** sur GitHub Pages
- **Orchestration** : Prefect 3 local (mode `run` et `serve`) pour planifier ingestion → dbt (horaire) et observer les exécutions.

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
docker pull dbt-weather-poc/weather-app:latest
docker run --rm -p 8501:8501 -v weather-data:/app/data dbt-weather-poc/weather-app:latest
# Dashboard : http://localhost:8501
```

### Option B — Explorer le pipeline en Docker Compose (multi-services)

Le `compose.yaml` propose des services et profils pour rejouer **dbt**, lancer l’**ingestion** (token requis) et démarrer **Prefect**.

Démarrer le dashboard (démo) :

```bash
docker compose up --build app
```

Rejouer dbt (job ponctuel, tests inclus, utilisera le seed si l’ingestion n’a pas tourné) :

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
