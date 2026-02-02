# Cloud Analytics Pipeline (GCP)

This document summarizes how the analytics pipeline runs on GCP.

---

## Scope

Covered:
- ingestion, transformations, and dashboard execution on GCP
- main cloud components and their roles

Out of scope:
- step-by-step GCP console setup
- Infrastructure as Code (Terraform planned but not yet implemented)

---

## Architecture

```text
Météo‑France API → Cloud Run Job (ingest) → BigQuery raw
                         ↓
                   Cloud Run Job (dbt) → BigQuery staging/intermediate/marts
                         ↓
                  Cloud Run Service (Streamlit)
```

---

## Components (High Level)

### BigQuery datasets
- `raw` (ingestion)
- `staging`, `intermediate`, `marts` (dbt models)
- `seeds` (seeded dimensions)

### Cloud Run Jobs
- **Weather observations ingestion** → `raw.obs_hourly`
- **dbt transformations** → `staging` / `intermediate` / `marts`
- **Stations ingestion (one-off)** → `raw.stations`  
  Reuses the ingestion Docker image with a command override.

### Cloud Run Service
- Streamlit dashboard (reads `marts.agg_station_latest`)

### Cloud Scheduler
- Triggers hourly ingestion + dbt jobs

---

## Execution Flow

1. Ingest observations into BigQuery (`raw`)
2. Run dbt build on BigQuery
3. Dashboard reads latest marts

---

## Ingestion Guarantees

- Idempotent loads (logical dedup key: `validity_time`, `geo_id_insee`,
  `reference_time`).
- Raw tables preserve source column names and types; semantic changes happen in
  dbt staging.
- API resilience: explicit timeouts, retries with exponential backoff, and
  `Retry-After` support for rate limiting.

---

## Configuration

Environment variables (examples):
- `GCP_PROJECT`
- `BQ_DATASET`
- `DATA_BACKEND=bigquery`

Secrets:
- `METEOFRANCE_TOKEN` stored in Secret Manager (token setup guide: see `docs/appendix/api-access.md`).

---

## IAM (High Level)

Dedicated service accounts with least-privilege permissions:
- BigQuery read/write for ingestion and dbt jobs
- BigQuery read-only for the dashboard service
- Secret access for ingestion jobs
