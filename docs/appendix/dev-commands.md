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
make api-check
make dwh-ingest DEPT=75
```

---

## dbt

```bash
make dbt-build
make dbt-test
```

Targeted selections:

```bash
dbt run --select stg_obs_hourly
dbt run --select tag:stg
dbt run --full-refresh -s tag:mart
dbt run -s +exposure:weather_bi_streamlit
dbt test -s +exposure:weather_bi_streamlit
```

---

## dbt Docs

```bash
make dbt-docs-generate
make dbt-docs-serve
# http://localhost:8080
```

---

## Run the App

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

- `make prefect-server` starts the Prefect server (UI: http://localhost:4200).
- `make flow-run DEPT=9` runs the pipeline once.
- `make flow-serve DEPT=9` creates/keeps an hourly deployment schedule.

---

## Discover More

```bash
make help
```
