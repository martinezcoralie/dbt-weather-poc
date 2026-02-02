# Weather Analytics Pipeline (GCP)

## Overview

This project implements an **end-to-end analytics pipeline on GCP**:
hourly ingestion of public weather observations, transformation with dbt on
BigQuery, and exposure through a live dashboard.

The cloud deployment is the reference execution environment; a local setup is
provided for development and testing.

---

## Architecture & Execution Model

**Cloud (reference execution)**
- BigQuery as analytical warehouse
- Cloud Run Jobs for ingestion and dbt transformations
- Cloud Scheduler triggering hourly runs
- Cloud Run Service serving the Streamlit dashboard

**Local (for development and testing)**
- DuckDB and dbt for fast iteration
- Docker / Docker Compose for reproducibility

---

## Data Pipeline

Weather observations are fetched hourly and loaded **idempotently** into BigQuery.
Transformations are implemented with dbt using a **layered structure**
(staging, intermediate, marts), with **incremental models** and **partition pruning**.

Analytical marts are consumed directly by a Streamlit dashboard.

---

## Reliability & Data Quality

- Idempotent ingestion (no duplicates observations)
- Partitioned tables to limit scanned data
- Incremental dbt models
- Column-level tests and enforced schema contracts on marts
- Freshness logic applied in analytics and dashboard

---

## Delivery

- CI validates ingestion and dbt transformations on each push
- Python code is linted
- Docker services are smoke-tested

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

## Documentation ou Further resources

- dbt documentation (models, tests, lineage): https://martinezcoralie.github.io/dbt-weather-poc/
- CI/CD notes (secrets): docs/appendix/ci-cd.md


---

## Author

Coralie Martinez
