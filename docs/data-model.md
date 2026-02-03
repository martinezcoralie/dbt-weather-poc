# Data Model & Analytics Logic

This document describes the analytical data model exposed to consumers
(dashboard, analysis).

---

## Overview

The data model is built around **hourly weather observations per station**.

Grain:
- 1 row = 1 station × 1 hour

Primary consumer:
- Streamlit dashboard

---

## Layers

`raw → staging → intermediate → marts`

- **raw**: raw observations and reference data as ingested
- **staging**: cleaning, typing, normalization
- **intermediate**: feature engineering and rolling windows
- **marts**: stable analytical tables for BI consumption

---

## Key Tables

- `fct_obs_hourly` (fact, grain: `station_id` × `validity_time_utc`)
- `agg_station_latest` (latest metrics per station)

---

## Dimensions & Reference Data

- `dim_stations` (station metadata)

- Reference dimensions (from seeds):
  - wind (Beaufort scale)
  - temperature intensity
  - precipitation intensity
  - snow intensity


---

## dbt Design Notes

- Incremental models use `merge` to avoid full refreshes.
- BigQuery tables are partitioned (and clustered where relevant) to reduce scan
  cost.
- Tests and contracts enforce schema stability and domain constraints on marts.
- The Streamlit dashboard is declared as a dbt exposure for targeted runs/tests.
- The lineage graph helps visualize dependencies from raw → marts and scope
  targeted builds.

---

## Data Quality Guarantees

- Stable schemas for analytical tables
- Enforced uniqueness and referential integrity at the fact level
- Domain constraints on physical values (temperature, wind, precipitation)

The dashboard relies exclusively on these validated marts.
