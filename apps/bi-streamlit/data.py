import os
from datetime import datetime

import duckdb
import pandas as pd
import streamlit as st

DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")


@st.cache_data(ttl=60)
def load_station_list() -> pd.DataFrame:
    """Stations ayant des mesures (via la vue agg_station_latest_24h)."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            select station_id, station_name, latitude, longitude
            from marts.agg_station_latest_24h
            order by station_name
            """
        ).df()


@st.cache_data(ttl=60)
def load_latest_station_metrics() -> pd.DataFrame:
    """Dernière observation par station, enrichie des labels BI (vue agg_station_latest_24h)."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            select *
            from marts.agg_station_latest_24h
            """
        ).df()


@st.cache_data(ttl=60)
def load_latest_timestamp() -> datetime | None:
    """Horodatage le plus récent disponible dans le mart agg_station_latest_24h."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        result = con.execute(
            """
            select max(validity_time_utc) as max_ts
            from marts.agg_station_latest_24h
            """
        ).fetchone()
    return result[0] if result else None


def format_last_update(ts: datetime | None) -> str:
    """Retourne une phrase prête à afficher sur l'horodatage le plus récent."""
    if not isinstance(ts, datetime):
        return "Aucune donnée disponible dans marts.agg_station_latest_24h"
    ts_formatted = ts if ts.tzinfo else ts.replace(tzinfo=None)
    return f"Données issues de l'API Météo France, mises à jour le {ts_formatted:%d/%m/%Y %H:%M UTC}"
