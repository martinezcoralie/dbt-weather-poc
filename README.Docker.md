# Docker / Docker Compose (dbt-weather-poc)

Objectif : proposer une expérience “portfolio‑friendly” avec :
- **une image Docker unique** (dashboard, dbt, ingestion, Prefect)
- **un warehouse DuckDB persistant** via un volume Docker nommé
- **un démarrage possible sans token** grâce à un warehouse de démonstration (si aucun warehouse n’est présent)

## Prérequis
- Docker Desktop (ou Docker Engine)
- Docker Compose v2 (inclus Docker Desktop)

## Démo dashboard (sans token)
Le dashboard peut démarrer sur un warehouse de démonstration (seed): 
**aucun appel à l’API Météo-France n’est requis**.

### Option A — Image publiée (sans cloner le dépôt)
```bash
docker pull dbt-weather-poc/weather-app:latest
docker run --rm -p 8501:8501 -v weather-data:/app/data dbt-weather-poc/weather-app:latest
# http://localhost:8501
```
Notes :
- Nécessite que l’image soit publiée et accessible

### Option B — Depuis le dépôt (build local)
```bash
docker compose up --build app
# http://localhost:8501
```

Notes :
- `--build` force la reconstruction locale de l’image à partir du `Dockerfile`.
- Pour **forcer l’utilisation de l’image publiée** avec Compose (sans rebuild local) :

  ```bash
  docker compose pull app
  docker compose up --no-build app
  ```

## Services Docker Compose
Tous les services utilisent la même image (`dbt-weather-poc/weather-app:latest`) et le même volume `weather-data` monté dans `/app/data`.

- `app` : dashboard Streamlit — port `8501:8501`
- `dbt` (profile `build`) : job ponctuel `make dbt-build` (tests inclus)
- `ingest` (profile `ingest`) : job ponctuel `make dwh-ingest` (**token requis**)
- `prefect-server` (profile `prefect`) : UI + API Prefect — port `4200:4200`
- `prefect` (profile `prefect`) :serve du flow (`make flow-serve`), connecté à `prefect-server`

## Commandes utiles

### Ingestion réelle (token requis)
1) Créer un `.env` (non commité) avec `METEOFRANCE_TOKEN`. Voir : [docs/10-Setup.md](docs/10-Setup.md)
2) Lancer l’ingestion pour un département (format sans zéro initial (`9`, `75` ; pas `09`)) :
```bash
DEPT=75 docker compose --profile ingest run --rm ingest
```

### Rejouer dbt (job ponctuel)
```bash
docker compose --profile build run --rm dbt
```
Notes :
- Par défaut, dbt cible `/app/data/warehouse.duckdb`. Si l’ingestion a été exécutée, dbt transformera les données ingérées ; sinon il transformera le dataset de démo seedé.

### Orchestration Prefect
```bash
docker compose --profile prefect up --build prefect-server prefect
# UI Prefect : http://localhost:4200
```

### Reset complet (reseed au prochain run)
Supprime conteneurs + volume (le seed sera recréé automatiquement au prochain démarrage) :
```bash
docker compose down -v
```
