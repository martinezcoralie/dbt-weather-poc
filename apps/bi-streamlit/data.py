import os

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
            select
                station_id,
                station_name,
                latitude,
                longitude,
                validity_time_utc,
                temp_24h_c,
                precip_24h_mm,
                snow_24h_m,
                precip_24h_intensity_level,
                precip_24h_intensity_label,
                snow_24h_intensity_level,
                snow_24h_intensity_label,
                temperature_c,
                precip_mm_h,
                wind_speed_kmh,
                wind_sector,
                visibility_cat
            from marts.agg_station_latest_24h
            """
        ).df()
