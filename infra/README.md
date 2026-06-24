# GCP Infrastructure — dbt-weather-poc

## Architecture
- **Cloud Run Jobs**
  - weather data ingestion (Météo-France → BigQuery raw)
  - dbt transformations (staging → marts)
- **Cloud Scheduler** to trigger jobs every 2 hours
- **BigQuery** as the data warehouse
- **Streamlit** dashboard on Cloud Run Service (public via IAM `allUsers`)


## Why this setup
Lightweight, serverless, production-ready analytics.

## Principles
- One service account per workload
- Least-privilege IAM
- Reproducible infrastructure (Terraform)

## Costs
Near-zero on free tier / low traffic.
