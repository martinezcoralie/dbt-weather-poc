from datetime import datetime, timezone

import pandas as pd
import pydeck as pdk
import streamlit as st

from data import format_last_update


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


__all__ = [
    "compute_view_state",
    "freshness_badge",
    "render_freshness",
    "_base_layer",
    "_icon_layer",
]
