# CI/CD (GitHub Actions)

## Documentation dbt déployée automatiquement (GitHub Pages)

Une GitHub Action génère et déploie automatiquement la documentation dbt à chaque push sur `main`
(build + upload d’artefacts, puis publication sur Pages).

- Accès : https://martinezcoralie.github.io/dbt-weather-poc/

## CI : validation dbt sur données réelles

Une CI GitHub Actions rejoue une partie du pipeline à chaque push / PR sur `main` :

- ingestion des données brutes depuis l’API Météo-France via `make dwh-ingest DEPT=9`,
- création d’un warehouse DuckDB dans l’environnement CI,
- exécution de `dbt deps` puis `dbt build` avec `DBT_PROFILES_DIR=./profiles`.

## CI : smoke test des services Docker

Une vérification rapide s’assure que le service `app` démarre correctement via Docker Compose :

- démarrage du service `app` et du serveur Prefect,
- health check HTTP sur `/_stcore/health` et `http://localhost:4200/api/health`.

## Secrets / variables

La CI s’appuie sur :

- un secret GitHub Actions `METEOFRANCE_TOKEN` (clé API Météo-France),
- une variable d’environnement `DUCKDB_PATH` pointant vers `data/warehouse.duckdb`.

## Pourquoi ce choix

Ce dispositif permet de tester les modèles dbt et leurs tests métier sur des données réelles, sans versionner les données Météo-France dans le dépôt (repo propre, reproductible, et “portfolio-friendly”).
