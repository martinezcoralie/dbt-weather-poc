# Docker (dbt-weather-poc)

Expérience Docker “portfolio friendly” : **une image unique**, **volume DuckDB partagé**, **Compose multi-services** piloté par `make`.

## Concepts clés

1) **Image unique**
Tous les services (`app`, `dbt`, `ingest`, `prefect-server`, `prefect`) utilisent la même image :
- code + dépendances Python
- profils dbt
- DuckDB démo embarqué (`demo_warehouse.duckdb`)

2) **Volume nommé** (DuckDB partagé)
Volume `weather-data` monté dans `/app/data`, commun à tous les services :
- fichier warehouse : `/app/data/warehouse.duckdb`

3) **Seed automatique** (entrypoint)
Au premier démarrage d’un volume vide, l’entrypoint copie la base démo :
- source : `/app/demo/demo_warehouse.duckdb`
- destination : `/app/data/warehouse.duckdb`
Le volume persiste ensuite entre les runs.

## Prérequis
- Docker Desktop (ou Docker Engine)
- Docker Compose v2 (inclus Docker Desktop)

## Services Compose
- `app` : Streamlit (`make app`) — port `8501:8501`
- `dbt` (profile `build`) : job ponctuel `make dbt-build`
- `ingest` (profile `ingest`) : job ponctuel `make dwh-ingest` (token requis)
- `prefect-server` (profile `prefect`) : UI + API Prefect — port `4200:4200`
- `prefect` (profile `prefect`) : exécution/serve du flow (`make flow-serve`)

## Réinitialisation (reseed DuckDB démo)
Supprime conteneurs + volume (reseed automatique au prochain run) :
```bash
docker compose down -v
```
