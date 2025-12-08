import os

import duckdb
import pandas as pd
import streamlit as st

DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")

st.set_page_config(page_title="Météo – Observations horaires", layout="wide")
st.title("Observations météo – marts DBT")


@st.cache_data(ttl=60)  # 60s de cache = assez pour naviguer sans bloquer dbt
def load_station_list():
    """Liste des stations."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute("""
            select station_id, station_name, latitude, longitude
            from marts.dim_stations
            order by station_name
        """).df()


@st.cache_data(ttl=60)
def load_latest_station_metrics():
    """Dernière mesure par station."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            with ranked as (
                select
                    station_id,
                    station_name,
                    validity_time_utc,
                    temp_24h_c,
                    precip_24h_mm,
                    snow_24h_m,
                    row_number() over (
                        partition by station_id
                        order by validity_time_utc desc
                    ) as rn
                from marts.fct_obs_hourly
            )
            select station_id, station_name, validity_time_utc, temp_24h_c, precip_24h_mm, snow_24h_m
            from ranked
            where rn = 1
            """
        ).df()


@st.cache_data(ttl=60)
def load_obs_for(station_id):
    """
    Toutes les mesures pour une station.
    
    :param station_id: id de la station
    """
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            select *
            from marts.fct_obs_hourly
            where station_id = ?
            order by validity_time_utc
        """,
            [station_id],
        ).df()


stations = load_station_list()
latest_metrics = load_latest_station_metrics()


def _champion(df, col, fn):
    df_valid = df[pd.notna(df[col])]
    if df_valid.empty:
        return None, pd.DataFrame()
    value = fn(df_valid[col])
    champs = df_valid[df_valid[col] == value]
    return value, champs


def _names(df):
    return ", ".join(sorted(df["station_name"].tolist()))


def metric_card(title, value, detail, accent):
    st.markdown(
        f"""
        <div style="
            padding: 14px 16px;
            border-radius: 14px;
            background: linear-gradient(135deg, {accent} 0%, #0f172a 120%);
            box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            color: #f8fafc;
            ">
            <div style="font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.8;">
                {title}
            </div>
            <div style="font-size: 28px; font-weight: 700; margin: 6px 0;">
                {value}
            </div>
            <div style="font-size: 14px; opacity: 0.9;">
                {detail}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.subheader("Les champions (dernières 24h)")
if latest_metrics.empty:
    st.info("Aucune donnée disponible pour calculer les champions.")
else:
    warm_val, warm_df = _champion(latest_metrics, "temp_24h_c", pd.Series.max)
    cold_val, cold_df = _champion(latest_metrics, "temp_24h_c", pd.Series.min)
    dry_df = latest_metrics[latest_metrics["precip_24h_mm"].fillna(0) == 0]
    snow_df_all = latest_metrics[latest_metrics["snow_24h_m"].fillna(0) > 0]
    snow_val, snow_df = _champion(snow_df_all, "snow_24h_m", pd.Series.max)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Plus doux",
            f"{warm_val:.1f} °C" if warm_val is not None else "N/A",
            _names(warm_df) if not warm_df.empty else "Pas de mesure",
            "#2563eb",
        )
    with c2:
        metric_card(
            "Plus froid",
            f"{cold_val:.1f} °C" if cold_val is not None else "N/A",
            _names(cold_df) if not cold_df.empty else "Pas de mesure",
            "#0ea5e9",
        )
    with c3:
        metric_card(
            "Au sec (24h)",
            f"{len(dry_df)} station(s)",
            _names(dry_df) if not dry_df.empty else "Aucune station au sec",
            "#22c55e",
        )
    with c4:
        metric_card(
            "Neige (24h)",
            f"{snow_val:.2f} m" if snow_val is not None else "N/A",
            _names(snow_df) if not snow_df.empty else "Pas de neige mesurée",
            "#f97316",
        )

chosen = st.selectbox("Station", stations["station_name"])
station_id = stations.loc[stations["station_name"] == chosen, "station_id"].iloc[0]

df = load_obs_for(station_id)

import pydeck as pdk

# Carte : toutes les stations + mise en évidence de la station sélectionnée
stations_map = stations.rename(columns={"longitude": "lon", "latitude": "lat"})

# Couche "toutes les stations"
all_layer = pdk.Layer(
    "ScatterplotLayer",
    data=stations_map,
    get_position="[lon, lat]",
    get_radius=2000,  # ajuste selon l’échelle
    get_color=[0, 122, 255],  # bleu
    pickable=True,
)

# Couche "station sélectionnée"
selected_station = stations_map[stations_map["station_name"] == chosen]
selected_layer = pdk.Layer(
    "ScatterplotLayer",
    data=selected_station,
    get_position="[lon, lat]",
    get_radius=4000,
    get_color=[255, 60, 60],  # rouge
    pickable=True,
)

# Vue initiale centrée sur le barycentre (fallback si vide)
center_lat = stations_map["lat"].mean() if not stations_map.empty else 46.5
center_lon = stations_map["lon"].mean() if not stations_map.empty else 2.5

view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=5)

st.subheader("Carte des stations")
st.pydeck_chart(
    pdk.Deck(
        layers=[all_layer, selected_layer],
        initial_view_state=view_state,
        tooltip={"text": "{station_name}\n(lat: {lat}, lon: {lon})"},
    )
)


col1, col2, col3 = st.columns(3)
if not df.empty:
    freshness_hours = (
        pd.Timestamp.utcnow() - pd.to_datetime(df["validity_time_utc"]).max()
    ).total_seconds() / 3600
    col1.metric("Fraîcheur (h)", f"{freshness_hours:.1f}")
    col2.metric(
        "Température dernière (°C)",
        f"{df['temperature_c'].iloc[-1]:.1f}"
        if pd.notna(df["temperature_c"].iloc[-1])
        else "NA",
    )
    col3.metric(
        "Précip. dernière (mm/h)",
        f"{df['precip_mm_h'].iloc[-1]:.2f}"
        if pd.notna(df["precip_mm_h"].iloc[-1])
        else "NA",
    )

st.line_chart(df.set_index("validity_time_utc")[["temperature_c"]])
st.bar_chart(df.set_index("validity_time_utc")[["precip_mm_h"]])
st.dataframe(df.tail(24))
