import duckdb, pandas as pd, streamlit as st
import os

DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")

st.set_page_config(page_title="Météo – Observations horaires", layout="wide")
st.title("Observations météo – marts DBT")

@st.cache_data(ttl=60)  # 60s de cache = assez pour naviguer sans bloquer dbt
def load_station_list():
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute("""
            select distinct s.station_id, s.station_name, s.latitude, s.longitude
            from marts.dim_stations s
            join marts.fct_obs_hourly f on f.station_id = s.station_id
            order by s.station_name
        """).df()

@st.cache_data(ttl=60)
def load_obs_for(station_id):
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute("""
            select validity_time_utc, temperature_c, wind_speed_kmh, precip_mm_h
            from marts.fct_obs_hourly
            where station_id = ?
            order by validity_time_utc
        """, [station_id]).df()

stations = load_station_list()

chosen = st.selectbox("Station", stations["station_name"])
station_id = stations.loc[stations["station_name"]==chosen, "station_id"].iloc[0]

df = load_obs_for(station_id)

col1, col2, col3 = st.columns(3)
if not df.empty:
    freshness_hours = (pd.Timestamp.utcnow() - pd.to_datetime(df["validity_time_utc"]).max()).total_seconds()/3600
    col1.metric("Fraîcheur (h)", f"{freshness_hours:.1f}")
    col2.metric("Température dernière (°C)", f"{df['temperature_c'].iloc[-1]:.1f}" if pd.notna(df['temperature_c'].iloc[-1]) else "NA")
    col3.metric("Précip. dernière (mm/h)", f"{df['precip_mm_h'].iloc[-1]:.2f}" if pd.notna(df['precip_mm_h'].iloc[-1]) else "NA")

st.line_chart(df.set_index("validity_time_utc")[["temperature_c"]])
st.bar_chart(df.set_index("validity_time_utc")[["precip_mm_h"]])
st.dataframe(df.tail(24))
