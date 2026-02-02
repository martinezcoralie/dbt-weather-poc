# Cloud Analytics Pipeline (GCP)

This document describes how the analytics pipeline runs on GCP.

---

## Scope

Covered:
- ingestion, transformations, and dashboard execution on GCP
- main cloud components and their roles

Out of scope:
- step-by-step GCP console setup
- Infrastructure as Code (Terraform planned but not yet implemented)

---

## Components

### BigQuery
Analytical warehouse used as the reference data store.

Datasets:
- `raw`  
  - `obs_hourly` (hourly observations, partitioned)
  - `stations` (station metadata)
- `staging`, `intermediate`, `marts`  
  - managed by dbt

---

### Cloud Run Jobs

- **Weather observations ingestion**
  - Fetches hourly observations from the Météo-France API
  - Loads data idempotently into `raw.obs_hourly`

- **dbt transformations**
  - Executes `dbt build` targeting BigQuery
  - Builds staging, intermediate, and marts models

- **Stations ingestion (one-off)**
  - Loads quasi-static station metadata
  - Executed manually (no scheduler)

---

### Cloud Scheduler

- Triggers:
  - hourly ingestion job
  - hourly dbt job
- Scheduler configuration is currently managed outside this repository

---

### Cloud Run Service

- Streamlit dashboard
- Reads analytical marts directly from BigQuery
- Public, read-only access (demo purpose)

---

## Execution Flow

On an hourly basis:

1. Weather observations are ingested into BigQuery (`raw`)
2. dbt transformations are executed on BigQuery
3. The dashboard reflects the latest transformed data

The dashboard does not trigger transformations; it is purely a consumer.

---

## Configuration

### Environment variables (examples)

- `GCP_PROJECT`
- `BQ_DATASET`
- `DATA_BACKEND=bigquery`

Secrets:
- `METEOFRANCE_TOKEN` (stored in Secret Manager)

---

## IAM (High Level)

Dedicated service accounts are used with least-privilege permissions:
- BigQuery read/write for ingestion and dbt jobs
- BigQuery read-only for the dashboard service
- Secret access for ingestion jobs

---
