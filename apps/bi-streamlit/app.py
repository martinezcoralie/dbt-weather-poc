import os

import duckdb
import pandas as pd
import pydeck as pdk
import streamlit as st

DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")

st.set_page_config(page_title="Météo – Observations horaires", layout="wide")
st.title("Observations météo – marts DBT")


@st.cache_data(ttl=60)  # 60s de cache = assez pour naviguer sans bloquer dbt
def load_station_list():
    """Liste des stations pour lesquelles on a des mesures."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute("""
            select stations.station_id, stations.station_name, stations.latitude, stations.longitude
            from marts.dim_stations stations
            join marts.fct_obs_hourly obs on obs.station_id = stations.station_id
            order by stations.station_name
        """).df()


@st.cache_data(ttl=60)
def load_latest_station_metrics():
    """Dernière mesure par station + coord pour la carto."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        return con.execute(
            """
            with ranked as (
                select
                    f.station_id,
                    s.station_name,
                    s.latitude,
                    s.longitude,
                    f.validity_time_utc,
                    f.temp_24h_c,
                    f.precip_24h_mm,
                    f.snow_24h_m,
                    f.precip_intensity_level,
                    f.precip_intensity_label,
                    row_number() over (
                        partition by f.station_id
                        order by f.validity_time_utc desc
                    ) as rn
                from marts.fct_obs_hourly f
                join marts.dim_stations s on s.station_id = f.station_id
            )
            select station_id, station_name, latitude, longitude, validity_time_utc, temp_24h_c, precip_24h_mm, snow_24h_m, precip_intensity_level, precip_intensity_label
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
warm_df = cold_df = wet_df = pd.DataFrame()


def _champion(df, col, fn):
    df_valid = df[pd.notna(df[col])]
    if df_valid.empty:
        return None, pd.DataFrame()
    value = fn(df_valid[col])
    champs = df_valid[df_valid[col] == value]
    return value, champs


def _names(df):
    return ", ".join(sorted(df["station_name"].tolist()))

def _icon_layer(
    data: pd.DataFrame,
    icon_url: str,
    size: int | str = 4,
    size_scale: int = 12,
    size_field: str | None = None,
):
    """
    Créer une IconLayer si des points sont disponibles.

    :param data: DataFrame contenant au moins les colonnes lat, lon
    :param icon_url: URL absolue de l'icône (PNG/SVG)
    :param size: taille “abstraite” (multiplée par size_scale)
    :param size_scale: facteur d'échelle pour la taille effective
    :param size_field: nom de colonne à utiliser pour la taille (optionnel)
    """
    if data is None or data.empty:
        return None

    # On fait une copie pour ne pas modifier le DF d'origine “par surprise”
    df = data.copy()

    icon_data = {
        "url": icon_url,
        "width": 128,     # adapter aux dimensions réelles de l’image
        "height": 128,
        "anchorY": 128,   # ancrage au bas de l’icône
    }

    # Même icône pour toutes les lignes de ce DataFrame
    df["icon_data"] = [icon_data] * len(df)

    return pdk.Layer(
        "IconLayer",
        data=df,
        get_icon="icon_data",
        get_position="[lon, lat]",
        get_size=size_field or size,      # taille relative ou champ
        size_scale=size_scale,
        pickable=True,
        billboard=True,
    )

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
    wet_df_all = latest_metrics[latest_metrics["precip_24h_mm"].fillna(0) > 0]
    wet_val, wet_df = _champion(wet_df_all, "precip_24h_mm", pd.Series.max)

    snow_others = snow_df_all[snow_df_all["snow_24h_m"] < (snow_val or 0)]
    snow_other_detail = (
        f"Autres neige : {len(snow_others)} station(s) (≤ {snow_others['snow_24h_m'].max():.2f} m)"
        if not snow_others.empty
        else "Pas d'autres stations enneigées"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

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
            _names(snow_df) + f" · {snow_other_detail}" if not snow_df.empty else "Pas de neige mesurée",
            "#f97316",
        )
    with c5:
        metric_card(
            "Plus arrosé (24h)",
            f"{wet_val:.2f} mm" if wet_val is not None else "N/A",
            _names(wet_df) if not wet_df.empty else "Aucune station avec pluie",
            "#a855f7",
        )

# Carte : toutes les stations + champions
stations_map = stations.rename(columns={"longitude": "lon", "latitude": "lat"})
stations_map["status"] = "Station"

# vue initiale
center_lat = stations_map["lat"].mean() if not stations_map.empty else 46.5
center_lon = stations_map["lon"].mean() if not stations_map.empty else 2.5

# Couche "toutes les stations"
all_layer = pdk.Layer(
    "ScatterplotLayer",
    data=stations_map,
    get_position="[lon, lat]",
    get_radius=1000,  # ajuste selon l’échelle
    get_color=[128, 128, 128],  # gris
    pickable=True,
)

# Icônes pour les champions chaud/froid 
HOT_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f525.png"  # 🔥
COLD_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2744.png"  # ❄️
RAIN_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2614.png"  # ☔


# Couche "champions chaud/froid"
warm_points = pd.DataFrame()
if warm_df is not None and not warm_df.empty:
    warm_points = warm_df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(
        status="Plus doux"
    )
    icon_data = {
        "url": HOT_ICON_URL,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }
    warm_points["icon_data"] = [icon_data] * len(warm_points)


cold_points = pd.DataFrame()
if cold_df is not None and not cold_df.empty:
    cold_points = cold_df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(
        status="Plus froid"
    )
    icon_data = {
        "url": COLD_ICON_URL,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }
    cold_points["icon_data"] = [icon_data] * len(cold_points)

wet_points = pd.DataFrame()
if wet_df is not None and not wet_df.empty:
    wet_points = (
        wet_df.rename(columns={"longitude": "lon", "latitude": "lat"})
        .assign(status="Pluie 24h")
        .query("precip_intensity_level >= 3")  # on affiche modéré et plus
    )
    icon_data = {
        "url": RAIN_ICON_URL,
        "width": 242,
        "height": 242,
        "anchorY": 242,
    }
    wet_points["icon_data"] = [icon_data] * len(wet_points)
    # Taille proportionnelle à l'intensité (3=modérée -> petit, 5=très forte -> grand)
    wet_points["icon_size"] = (wet_points["precip_intensity_level"] - 2) * 9

ICON_SIZE = 20

warm_icon_layer = pdk.Layer(
    "IconLayer",
    data=warm_points,
    get_icon="icon_data",
    get_size=ICON_SIZE,
    size_scale=1,
    get_position=["lon", "lat"],
    pickable=True,
    billboard=True,
) if not warm_points.empty else None

cold_icon_layer = pdk.Layer(
    "IconLayer",
    data=cold_points,
    get_icon="icon_data",
    get_size=ICON_SIZE,
    size_scale=1,
    get_position=["lon", "lat"],
    pickable=True,
    billboard=True,
) if not cold_points.empty else None

wet_icon_layer = pdk.Layer(
    "IconLayer",
    data=wet_points,
    get_icon="icon_data",
    get_size="icon_size",
    size_scale=1,
    get_position=["lon", "lat"],
    pickable=True,
    billboard=True,
) if not wet_points.empty else None

view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=7)

st.subheader("Carte des stations")
layers = [
    layer
    for layer in [
        all_layer,
        warm_icon_layer,
        cold_icon_layer,
        wet_icon_layer,
    ]
    if layer is not None
]

st.pydeck_chart(
    pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip={"text": "{station_name}\n{status}\n(lat: {lat}, lon: {lon})"},
    )
)
