# Architecture

Flux principal :
```text
Météo-France API
  ↓ (ingestion Python)
DuckDB raw.*
  ↓ (dbt)
DuckDB staging → intermediate → marts
  ↓
Streamlit (dashboard)
  ↕
Prefect (schedule ingestion + dbt)
```

## Composants
- **Ingestion** : scripts Python (`scripts/ingestion/`) → tables `raw.stations` et `raw.obs_hourly` (clé logique pour déduplication, enrichissement `dept_code`/`load_time`).
- **Warehouse** : DuckDB (local ou volume Docker `weather-data`), chemin par défaut `data/warehouse.duckdb`.
- **dbt** : projet `weather_dbt`, layering `staging/intermediate/marts`, macros météo, seeds (Beaufort, intensités), modèles incrémentaux (merge), contrats + tests.
- **BI** : Streamlit (`apps/bi-streamlit/app.py`), dépendance principale `marts.agg_station_latest_24h`.
- **Orchestration** : Prefect flow `weather_hourly_pipeline` (ingestion → dbt), deployment horaire optionnel.
- **CI** : GitHub Actions rejoue ingestion + `dbt build` et publie dbt Docs (Pages).

## Docker
- **Image unique** pour tous les services (code + deps + profils dbt + DuckDB démo).
- **Volume nommé** `weather-data` monté en `/app/data` (warehouse partagé).
- **Seed auto** : copie `demo_warehouse.duckdb` → `data/warehouse.duckdb` sur volume vide.

## Profils/Config
- Variables clés : `METEOFRANCE_TOKEN`, `DUCKDB_PATH` (ex. `data/warehouse.duckdb`).
- Profil dbt local : `export DBT_PROFILES_DIR=./profiles`.
