# Docker (dbt-weather-poc)

Ce projet fournit une expérience Docker “portfolio friendly” avec **une image unique**, un **volume DuckDB partagé**, et un **Compose multi-services** piloté par `make`.

## Concepts

### 1) Image unique
Tous les services (`app`, `dbt`, `ingest`, `prefect-server`, `prefect`) utilisent **la même image** :
- code + dépendances Python
- profils dbt
- un DuckDB de démonstration embarqué (`demo_warehouse.duckdb`)

Cette image permet :
- une démo immédiate (sans token)
- des jobs ponctuels (`dbt build`, ingestion)
- l’orchestration du pipeline (Prefect)

### 2) Volume nommé (DuckDB partagé)
Un volume nommé `weather-data` est monté dans `/app/data`.

Tous les services lisent/écrivent le même fichier :
- `/app/data/warehouse.duckdb`

### 3) Seed automatique de la base démo (entrypoint)
Au **premier démarrage** (volume vide), un entrypoint copie le DuckDB de démonstration vers le volume :
- source : `/app/demo/demo_warehouse.duckdb`
- destination : `/app/data/warehouse.duckdb`

Ensuite, tant que le volume existe, la base persiste entre les runs.

---

## Prérequis
- Docker Desktop (ou Docker Engine)
- Docker Compose v2 (inclus avec Docker Desktop)

---

## Services Compose (résumé)

* `app` : Streamlit (`make app`) — port `8501:8501`
* `dbt` (profile `build`) : job ponctuel `make dbt-build`
* `ingest` (profile `ingest`) : job ponctuel `make dwh-ingest` (token requis)
* `prefect-server` (profile `prefect`) : UI + API Prefect — port `4200:4200`
* `prefect` (profile `prefect`) : exécution/serve du flow (`make flow-serve`)

---

## Réinitialisation (reseed du DuckDB démo)

Supprime conteneurs + volume (au prochain run, seed automatique) :

```bash
docker compose down -v
```