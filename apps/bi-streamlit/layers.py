from datetime import datetime, timezone

import pandas as pd
import pydeck as pdk
import streamlit as st

from champions import ChampionSet
from data import format_last_update


HOT_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f525.png"
COLD_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1F9CA.png"
RAIN_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1F4A7.png"
SNOW_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2744.png"


def compute_view_state(stations: pd.DataFrame) -> pdk.ViewState:
    """Center map on barycenter of stations (fallback to France-ish)."""
    center_lat = stations["latitude"].mean() if not stations.empty else 46.5
    center_lon = stations["longitude"].mean() if not stations.empty else 2.5
    return pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=8)


def freshness_badge(max_ts: datetime | None) -> tuple[str, str]:
    """Return (label, color) to display data freshness based on latest timestamp (FR labels)."""
    if not isinstance(max_ts, datetime):
        return ("Indisponible", "#9ca3af")

    ts_utc = max_ts if max_ts.tzinfo else max_ts.replace(tzinfo=timezone.utc)
    now_utc = datetime.now(timezone.utc)
    delay_hours = (now_utc - ts_utc).total_seconds() / 3600

    if delay_hours <= 3:
        return ("À jour", "#22c55e")
    if delay_hours <= 6:
        return ("En retard", "#f97316")
    return ("Stale", "#ef4444")


def render_freshness(max_ts: datetime | None) -> None:
    """Render the freshness line (last update + badge) with consistent styling."""
    subtitle = format_last_update(max_ts)
    label, color = freshness_badge(max_ts)

    st.markdown(
        f'<div style="display:flex; gap:8px; align-items:center; font-size:13px; color:#475569;">'
        f'<span>{subtitle}</span>'
        f'<span style="background:{color}; color:white; padding:6px 10px; '
        f'border-radius:12px; font-size:12px; font-weight:600;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _base_layer(stations: pd.DataFrame) -> pdk.Layer:
    stations_map = stations.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(
        status="Station"
    )
    return pdk.Layer(
        "ScatterplotLayer",
        data=stations_map,
        get_position="[lon, lat]",
        get_radius=1000,
        get_color=[128, 128, 128],
        pickable=True,
    )


def _icon_layer(data: pd.DataFrame, icon_url: str, size) -> pdk.Layer | None:
    if data is None or data.empty:
        return None

    df = data.copy()
    df["icon_data"] = [
        {"url": icon_url, "width": 242, "height": 242, "anchorY": 242}
    ] * len(df)

    return pdk.Layer(
        "IconLayer",
        data=df,
        get_icon="icon_data",
        get_size=size,
        size_scale=1,
        get_position=["lon", "lat"],
        pickable=True,
        billboard=True,
    )


def emoji_layer(data: pd.DataFrame, emoji: str, size: int = 28) -> pdk.Layer | None:
    """TextLayer with an emoji marker."""
    if data is None or data.empty:
        return None
    df = data.copy()
    df["text"] = emoji
    return pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="text",
        get_size=size,
        get_color=[0, 0, 0, 255],
        get_angle=0,
        get_text_anchor="middle",
        get_alignment_baseline="center",
        size_units="pixels",
        billboard=True,
        pickable=True,
    )


def build_map_layers(stations: pd.DataFrame, champs: ChampionSet) -> list[pdk.Layer]:
    """Build all map layers (base + champions)."""
    warm_layer = _icon_layer(champs.warm_points, HOT_ICON_URL, 20)
    cold_layer = _icon_layer(champs.cold_points, COLD_ICON_URL, 20)
    snow_layer = _icon_layer(champs.snow_points, SNOW_ICON_URL, "icon_size")
    wet_layer = _icon_layer(champs.wet_points, RAIN_ICON_URL, "icon_size")

    layers = [
        _base_layer(stations),
        warm_layer,
        cold_layer,
        snow_layer,
        wet_layer,
    ]
    return [l for l in layers if l is not None]
