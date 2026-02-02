# Local Development

This document describes how to run the project **locally** for development and
testing purposes.

Local execution mirrors the cloud pipeline logic but uses DuckDB as the
analytical warehouse for fast iteration.

---

## Prerequisites

- Docker (Docker Desktop or Docker Engine)
- Docker Compose v2

No cloud account is required for local execution.

---

## Local Execution Model

- A single Docker image is used to run:
  - the Streamlit dashboard
  - dbt transformations
  - ingestion jobs (optional)
- A persistent DuckDB warehouse is stored in a Docker volume.
- If no warehouse exists, a **demo dataset is automatically seeded**.

This allows the dashboard to run **without calling the external API**.

---

## Start the Dashboard (Demo Mode)

Run the dashboard using the seeded DuckDB warehouse:

```bash
docker compose up app
```

The dashboard will be available at:

```
http://localhost:8501
```

This mode does not require any API token.

---

## Run Transformations (dbt)

To execute dbt transformations locally:

```bash
docker compose --profile dbt run --rm dbt
```

Notes:

* dbt targets the local DuckDB warehouse
* If ingestion has not been executed, transformations run on the demo dataset

---

## Run Ingestion Locally (Optional)

To ingest real data locally, an API token is required.

1. Create a `.env` file (not committed) containing:

   ```
   METEOFRANCE_TOKEN=...
   ```

2. Run ingestion for a given department:

   ```bash
   DEPT=75 docker compose --profile ingest run --rm ingest
   ```

The local DuckDB warehouse will be updated with the ingested data.

---

## Reset Local State

To remove containers and reset the local warehouse:

```bash
docker compose down -v
```

The demo dataset will be recreated on the next run.

---

## Alternative: run without Docker

For those who prefer running locally without containers:

```bash
make env-setup && source .venv/bin/activate
export DBT_PROFILES_DIR=./configs/dbt
make help
```