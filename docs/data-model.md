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

## Layered Structure

The warehouse follows a standard layered approach:

`raw → staging → intermediate → marts`

- **raw**
  - Raw observations and reference data  as ingested
- **staging**
  - Cleaning, typing, normalization
- **intermediate**
  - Feature engineering and rolling windows
- **marts**
  - Stable analytical tables for BI consumption

---

## Core Fact Table

### `fct_obs_hourly`

Hourly fact table at station level.

Grain:
- `station_id`
- `validity_time_utc`

Content:
- rolling metrics (precipitation, snow, temperature over 1h / 3h / 24h)
- atomic measurements (wind, temperature, humidity, visibility)
- derived flags and categories (e.g. freezing, precipitation, wind strength)
- joins to reference dimensions

This table is the main analytical backbone.

---

## Analytical Aggregates

### `agg_station_latest`

One row per station, representing the **latest available observation**.

Used by:
- dashboard rankings
- map visualizations

This model is optimized for fast BI access.

---

## Dimensions & Reference Data

- `dim_stations`
  - station metadata (name, location)
- Reference dimensions (from seeds):
  - wind (Beaufort scale)
  - temperature intensity
  - precipitation intensity
  - snow intensity

These dimensions encode domain rules and keep interpretations consistent.

---

## Incremental Strategy (High-Level)

- Data is processed incrementally based on the observation date.
- On BigQuery, analytical tables are partitioned by date to reduce scan cost.
- On DuckDB, incremental logic avoids full recomputation.

---

## Data Quality Guarantees

- Stable schemas for analytical tables
- Enforced uniqueness and referential integrity at the fact level
- Domain constraints on physical values (temperature, wind, precipitation)

The dashboard relies exclusively on these validated marts.
