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

import pydeck as pdk

# Carte : toutes les stations + mise en évidence de la station sélectionnée
stations_map = stations.rename(columns={"longitude": "lon", "latitude": "lat"})

# Couche "toutes les stations"
all_layer = pdk.Layer(
    "ScatterplotLayer",
    data=stations_map,
    get_position="[lon, lat]",
    get_radius=2000,            # ajuste selon l’échelle
    get_color=[0, 122, 255],    # bleu
    pickable=True
)

# Couche "station sélectionnée"
selected_station = stations_map[stations_map["station_name"] == chosen]
selected_layer = pdk.Layer(
    "ScatterplotLayer",
    data=selected_station,
    get_position="[lon, lat]",
    get_radius=4000,
    get_color=[255, 60, 60],    # rouge
    pickable=True
)

# Vue initiale centrée sur le barycentre (fallback si vide)
center_lat = stations_map["lat"].mean() if not stations_map.empty else 46.5
center_lon = stations_map["lon"].mean() if not stations_map.empty else 2.5

view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=5)

st.subheader("Carte des stations")
st.pydeck_chart(pdk.Deck(
    layers=[all_layer, selected_layer],
    initial_view_state=view_state,
    tooltip={"text": "{station_name}\n(lat: {lat}, lon: {lon})"}
))


col1, col2, col3 = st.columns(3)
if not df.empty:
    freshness_hours = (pd.Timestamp.utcnow() - pd.to_datetime(df["validity_time_utc"]).max()).total_seconds()/3600
    col1.metric("Fraîcheur (h)", f"{freshness_hours:.1f}")
    col2.metric("Température dernière (°C)", f"{df['temperature_c'].iloc[-1]:.1f}" if pd.notna(df['temperature_c'].iloc[-1]) else "NA")
    col3.metric("Précip. dernière (mm/h)", f"{df['precip_mm_h'].iloc[-1]:.2f}" if pd.notna(df['precip_mm_h'].iloc[-1]) else "NA")

st.line_chart(df.set_index("validity_time_utc")[["temperature_c"]])
st.bar_chart(df.set_index("validity_time_utc")[["precip_mm_h"]])
st.dataframe(df.tail(24))
