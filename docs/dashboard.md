# Dashboard

The Streamlit dashboard is the primary consumer of the analytics layer.

---

## Purpose

The dashboard provides a real-time view of weather conditions per station:
- rankings
- summaries
- map-based exploration

It is designed as a **read-only consumer** of analytical tables.

---

## Data Source

The dashboard reads exclusively from:

- `marts.agg_station_latest`

All aggregations and business logic are computed upstream in dbt.
The application layer remains thin and stable.

---

## Data Freshness

Freshness is evaluated based on the latest available observation timestamp.

Indicative thresholds:
- Fresh: ≤ 3 hours
- Delayed: 3–6 hours
- Stale: > 6 hours

These indicators help detect ingestion or transformation issues.

---

## Visual Overview

### Summary view
<img src="images/dashboard-desktop-fresh.png" width="900" />

### Delayed data example
<img src="images/dashboard-desktop-late.png" width="900" />

### Map view
<img src="images/dashboard-desktop-map.png" width="900" />

---

## Deployment

The dashboard is deployed as a Cloud Run service and reads data directly from BigQuery.

(Local execution is documented separately.)


