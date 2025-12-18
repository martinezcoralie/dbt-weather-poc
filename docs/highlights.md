# Highlights — Compétences démontrées

- **dbt qualité** : tests génériques + métier, contrats de schéma, exposures, seeds.
- **dbt performance** : incrémental (merge) pour éviter les full refresh, macros partagées pour conversions météo et time series.
- **Ingestion réelle** : API Météo-France, idempotence et déduplication, enrichissement dept/load_time.
- **BI** : dashboard Streamlit branché sur les marts dbt, exposure déclarée.
- **CI/CD** : GitHub Actions rejoue ingestion + dbt build et publie la documentation dbt (Pages).
- **Orchestration** : Prefect 3 (flow, deployment horaire, logs).
- **Ops & DX** : Makefile centralisé, Docker image unique + volume partagé, resets simples.
