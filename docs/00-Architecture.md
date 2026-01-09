# Architecture

## Vue d’ensemble

```text
Météo‑France API
  ↓ (ingestion Python)
DuckDB raw.*
  ↓ (dbt build)
DuckDB staging → intermediate → marts
  ↓
Streamlit (dashboard)
  ↕ (option)
Prefect (schedule ingestion + dbt)
```

## Composants
- **Ingestion** : scripts Python (`scripts/ingestion/`) → tables `raw.stations` et `raw.obs_hourly` (clé logique pour déduplication, enrichissement `dept_code`/`load_time`).
- **Warehouse** : DuckDB (local ou volume Docker `weather-data`), chemin par défaut `data/warehouse.duckdb`.
- **dbt** : projet `weather_dbt`, layering `staging/intermediate/marts`, macros météo, seeds (Beaufort, intensités), modèles incrémentaux (merge), contrats + tests, exposure.
- **BI** : Streamlit (`apps/bi-streamlit/app.py`), dépendance principale `marts.agg_station_latest_24h`.
- **Orchestration** : Prefect flow `weather_hourly_pipeline` (ingestion → dbt), deployment horaire optionnel.
- **CI** : GitHub Actions exécute lint Ruff, ingestion + `dbt build`, smoke tests Docker (app + Prefect), et publie dbt Docs (Pages).

## Modes d’exécution

- **Local** : pilotage via `make` (ingestion, dbt, app, docs, Prefect).
- **Docker Compose** : multi‑services avec profils (`dbt`, `ingest`, `prefect`) et volume partagé pour le warehouse.

Prochaine étape : [10-Setup.md](10-Setup.md).
