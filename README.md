# Weather Analytics Pipeline (GCP)

## Overview

This project implements an **end-to-end analytics pipeline on GCP**:
scheduled ingestion of public weather observations, transformation with dbt on
BigQuery, and exposure through a live dashboard.

The cloud deployment is the reference execution environment; a local setup is
provided for development and testing.

---

## Architecture & Execution Model

**Cloud (reference execution)**
- BigQuery as analytical warehouse
- Cloud Run Jobs for ingestion and dbt transformations
- Cloud Scheduler triggering runs every 2 hours
- Cloud Run Service serving the Streamlit dashboard

**Local (for development and testing)**
- DuckDB and dbt for fast iteration
- Docker / Docker Compose for reproducibility

---

## Key Guarantees

- Idempotent ingestion (no duplicate observations)
- Partitioned tables to limit scanned data
- Incremental and layered dbt models
- Column-level tests and enforced schema contracts on marts
- Freshness logic applied in analytics and dashboard

---

## Run Locally

A local setup mirrors the cloud pipeline for development:
DuckDB as warehouse, dbt models shared with the cloud target, and Docker-based
execution.

Details: [docs/local-dev.md](docs/local-dev.md)

---

## Live Demo

- Dashboard: https://streamlit-372280565516.europe-west1.run.app

---

## Documentation

- dbt documentation (models, tests, lineage): https://martinezcoralie.github.io/dbt-weather-poc/
- CI/CD notes (secrets): docs/appendix/ci-cd.md


---

## Author

Coralie Martinez
