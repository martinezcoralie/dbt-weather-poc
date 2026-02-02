"""Read marts from DuckDB or BigQuery for the Streamlit dashboard."""

import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

DATA_BACKEND = os.getenv("DATA_BACKEND", "duckdb").lower()
DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")

# BigQuery configuration (used when DATA_BACKEND=bigquery).
BQ_PROJECT = os.getenv("BQ_PROJECT") or os.getenv("GCP_PROJECT")
BQ_DATASET = os.getenv("BQ_DATASET", "analytics")
BQ_TABLE = os.getenv("BQ_TABLE", "agg_station_latest")


def _load_bq_latest_station_metrics() -> pd.DataFrame:
    """Load latest station metrics from BigQuery."""
    if not BQ_PROJECT:
        raise ValueError("Missing BQ_PROJECT or GCP_PROJECT for BigQuery backend.")
    from google.cloud import bigquery

    client = bigquery.Client(project=BQ_PROJECT)
    query = f"SELECT * FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`"
    return client.query(query).to_dataframe()


def _load_bq_latest_timestamp():
    """Load latest timestamp from BigQuery."""
    if not BQ_PROJECT:
        raise ValueError("Missing BQ_PROJECT or GCP_PROJECT for BigQuery backend.")
    from google.cloud import bigquery

    client = bigquery.Client(project=BQ_PROJECT)
    query = f"SELECT MAX(validity_time_utc) AS max_ts FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`"
    result = client.query(query).result()
    row = next(iter(result), None)
    return row.max_ts if row else None


def _load_duckdb_latest_station_metrics() -> pd.DataFrame:
    import duckdb

    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            select *
            from marts.agg_station_latest
            """
        ).df()


def _load_duckdb_latest_timestamp():
    import duckdb

    with duckdb.connect(DB_PATH, read_only=True) as con:
        result = con.execute(
            """
            select max(validity_time_utc) as max_ts
            from marts.agg_station_latest
            """
        ).fetchone()
    return result[0] if result else None


def _filter_recent_measurements(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows within 2 hours of the global max validity_time_utc."""
    if df is None or df.empty or "validity_time_utc" not in df.columns:
        return df
    max_ts = df["validity_time_utc"].max()
    if not isinstance(max_ts, datetime):
        max_ts = pd.to_datetime(max_ts, utc=True, errors="coerce")
    if pd.isna(max_ts):
        return df
    threshold = max_ts - timedelta(hours=2)
    return df[df["validity_time_utc"] >= threshold]


@st.cache_data(ttl=60)
def load_latest_station_metrics() -> pd.DataFrame:
    """Dernière observation par station (DuckDB ou BigQuery)."""
    if DATA_BACKEND == "bigquery":
        return _filter_recent_measurements(_load_bq_latest_station_metrics())
    if DATA_BACKEND != "duckdb":
        raise ValueError(f"Unsupported DATA_BACKEND: {DATA_BACKEND}")
    return _filter_recent_measurements(_load_duckdb_latest_station_metrics())


@st.cache_data(ttl=60)
def load_latest_timestamp() -> datetime | None:
    """Horodatage le plus récent disponible (DuckDB ou BigQuery)."""
    if DATA_BACKEND == "bigquery":
        return _load_bq_latest_timestamp()
    if DATA_BACKEND != "duckdb":
        raise ValueError(f"Unsupported DATA_BACKEND: {DATA_BACKEND}")
    return _load_duckdb_latest_timestamp()


def format_last_update(ts: datetime | None) -> str:
    """Retourne une phrase prête à afficher sur l'horodatage le plus récent."""
    if not isinstance(ts, datetime):
        return "Aucune donnée disponible dans marts.agg_station_latest"
    ts_formatted = ts if ts.tzinfo else ts.replace(tzinfo=None)
    return f"Données issues de l'API Météo France, mises à jour le {ts_formatted:%d/%m/%Y %H:%M UTC}"
