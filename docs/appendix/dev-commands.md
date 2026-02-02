# Dev Commands

This page lists the local Make commands used for development without Docker.
If you run the services with Docker Compose, follow `docs/local-dev.md`
instead; use this appendix when you want to run everything directly on your
machine.

---

## Setup

```bash
make env-setup
source .venv/bin/activate
export DBT_PROFILES_DIR=./configs/dbt
```

---

## Ingestion

```bash
make dwh-ingest DEPT=75
```

---

## dbt

```bash
make dbt-build
make dbt-test
```

---

## Launch Streamlit Dashboard

```bash
make app
```

---

## DuckDB Inspection

```bash
make dwh-tables
make dwh-table-info TABLE=raw.stations
make dwh-table-shape TABLE=raw.stations
make dwh-table-sample TABLE=raw.stations
make dwh-table TABLE=raw.stations
```

---

## Orchestration with Prefect (Local)

```bash
make prefect-server
make flow-run DEPT=9
make flow-serve DEPT=9
```

---

## Discover More

```bash
make help
```
