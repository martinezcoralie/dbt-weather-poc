# 🌤️ dbt-weather-poc — Pipeline météo (dbt + DuckDB)

Pipeline analytique de bout en bout autour des données horaires Météo-France :
**ingestion Python → DuckDB (raw) → dbt (staging/intermediate/marts) → Streamlit (BI)**,
avec orchestration locale optionnelle via **Prefect**.

## En bref
- Données réelles Météo-France, ingestion Python idempotente vers DuckDB.
- Modélisation **dbt** (layering, tests génériques + custom, contrats, incrémental merge, macros métiers).
- Exposition BI **Streamlit** et déclaration en **exposure dbt**.
- **CI GitHub Actions** : build dbt + publication automatique des docs.
- **Orchestration Prefect** : cron horaire ingestion → dbt.

## Architecture rapide
```text
Météo-France API
  ↓ (ingestion Python)
DuckDB (raw.*)
  ↓ (dbt)
DuckDB (staging → intermediate → marts)
  ↓
Streamlit (dashboard)
  ↕
Prefect (schedule ingestion + dbt)
```
Plus de détails : docs/architecture.md.

## Ce que ce projet démontre (dbt)
- Tests dbt complets (intégrité + métier) et contrats sur les modèles critiques.
- Modèles incrémentaux (stratégie merge) pour limiter les full refresh.
- Macros métiers météo (unités, secteurs de vent, flags) et seeds (Beaufort, intensités).
- Exposure déclarée pour le dashboard BI.
- Documentation dbt générée et publiée automatiquement (Pages).

## 🚀 Démo immédiate (Docker, 2 commandes)
Image prête avec DuckDB démo (pas de token requis) :
```bash
docker pull dbt-weather-poc/weather-app:latest
docker run --rm -p 8501:8501 dbt-weather-poc/weather-app:latest make app VENV=system
```
Dashboard : http://localhost:8501. Plus d’options : README.Docker.md.

## Démo complète (Docker Compose)
Pré-requis : Docker + Compose v2.
```bash
git clone https://github.com/martinezcoralie/dbt-weather-poc.git
cd dbt-weather-poc
```
1) (Option) Ingestion API Météo-France :
```bash
cp .env.example .env
# voir docs/meteofrance_token.md
DEPT=9 docker compose --profile ingest run --rm ingest
```
2) Modélisation dbt :
```bash
docker compose --profile build run --rm dbt
```
3) Dashboard Streamlit :
```bash
docker compose up app
```
4) Orchestration Prefect (horaire) :
```bash
docker compose --profile prefect up -d prefect-server prefect
```
Reset complet (reseed DuckDB démo) :
```bash
docker compose down -v
```

## Parcours dev local (sans Docker)
Pré-requis : clé API Météo-France (docs/meteofrance_token.md).
```bash
git clone https://github.com/martinezcoralie/dbt-weather-poc.git
cd dbt-weather-poc
make env-setup && source .venv/bin/activate
export DBT_PROFILES_DIR=./profiles
make help                    # toutes les commandes
make dwh-ingest DEPT=9       # ingestion brute (API → DuckDB)
make dbt-build               # modèles + tests + seeds
make dbt-docs-generate       # docs dbt (HTML/JSON)
make dbt-docs-serve          # http://localhost:8080
make app                     # dashboard Streamlit
```

## 📎 Documentation complémentaire
- docs/overview.md — vue d’ensemble
- docs/highlights.md — compétences démontrées (dbt, CI, orchestration)
- docs/architecture.md — flux et stockage
- docs/meteofrance_token.md — récupérer une clé API Météo-France
- docs/ingestion.md — ingestion API → DuckDB (`raw.*`)
- docs/warehouse.md — commandes d’exploration DuckDB
- docs/dbt.md — structure dbt, layering, incrémental, macros, tests
- docs/dbt-docs.md — génération/exploration de dbt Docs
- docs/dashboard.md — dashboard Streamlit (exposure dbt)
- docs/orchestration.md — orchestration locale avec Prefect
