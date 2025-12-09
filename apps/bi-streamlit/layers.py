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

from dataclasses import dataclass
from typing import Optional

def list_card_html(title: str, station_text: str, count_text: str, accent: str, icon: str = "") -> str:
    """Return the HTML for a list-style card (for use inside flex containers)."""
    import textwrap

    html = textwrap.dedent(
        f"""\
        <div class="focus-card" style="--card-accent: {accent};">
            <div class="focus-card-title">{icon}{title}</div>
            <div class="focus-card-body">{station_text}</div>
            <div class="focus-card-count">{count_text}</div>
        </div>
        """
    ).strip()
    return html

# Placeholder icon URLs (Twemoji). Replace with your own PNGs if desired.
ICON_URLS = {
    "🔥": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f525.png",
    "🍃": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f343.png",
    "🥶": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f976.png",
    "🌧️": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f327.png",
    "💧💧": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4a7.png",
    "💧": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4a7.png",
    "🌤️": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f324.png",
    "❄️❄️": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2744.png",
    "🌨️🌨️": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f328.png",
    "💨": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4a8.png",
    "💨💨": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4a8.png",
    "😌": "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f60c.png",
}


def build_focus_cards(latest: pd.DataFrame) -> tuple[str, list[tuple[str, pd.DataFrame, str]]]:
    """Return (cards_html, map_options) for the focus section."""
    cards_html = ""
    map_options: list[tuple[str, pd.DataFrame, str]] = []

    if latest.empty:
        return cards_html, map_options

    def add_focus(df: pd.DataFrame, title: str, icon: str, accent: str) -> None:
        nonlocal cards_html, map_options
        if df.empty:
            return
        df_points = df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status=title)
        count = len(df_points)
        names = ", ".join(sorted(df_points["station_name"].tolist()))
        cards_html += list_card_html(title, names, f"{count} station(s)", accent, icon=f"{icon} ")
        icon_url = ICON_URLS.get(icon.strip())
        if icon_url:
            map_options.append((icon, df_points, icon_url))

    # Temp focus
    add_focus(latest[latest["temp_24h_intensity_level"].fillna(0) >= 4], "Confort thermique", "🔥", "#ef4444")
    add_focus(latest[latest["temp_24h_intensity_level"].fillna(0) == 3], "Frais", "🍃", "#0ea5e9")
    add_focus(latest[latest["temp_24h_intensity_level"].fillna(0).isin([1, 2])], "Grand froid", "🥶", "#0ea5e9")

    # Rain focus
    add_focus(latest[latest["precip_24h_intensity_level"].fillna(0).isin([4, 5])], "Pluie soutenue", "🌧️", "#0ea5e9")
    add_focus(latest[latest["precip_24h_intensity_level"].fillna(0) == 3], "Pluie modérée", "💧💧", "#38bdf8")
    add_focus(
        latest[(latest["precip_24h_intensity_level"].fillna(0) == 1) & (latest["precip_24h_mm"].fillna(0) > 0)],
        "Quelques gouttes",
        "💧",
        "#60a5fa",
    )
    add_focus(latest[latest["precip_24h_mm"].fillna(0) == 0], "Au sec", "🌤️", "#22c55e")

    # Snow focus
    add_focus(latest[latest["snow_24h_intensity_level"].fillna(0).isin([2, 3])], "Neige faible", "❄️❄️", "#38bdf8")
    add_focus(latest[latest["snow_24h_intensity_level"].fillna(0).isin([4, 5])], "Neige forte", "🌨️🌨️", "#0ea5e9")

    # Wind focus
    add_focus(latest[latest["wind_beaufort"].fillna(-1).isin([2, 3])], "Brise", "🍃", "#38bdf8")
    add_focus(latest[latest["wind_beaufort"].fillna(-1) == 4], "Vent fort", "💨", "#0ea5e9")
    add_focus(latest[latest["wind_beaufort"].fillna(-1) == 5], "Vent très fort", "💨💨", "#0b7a9b")
    add_focus(latest[latest["wind_beaufort"].fillna(-1) == 1], "Pas de vent", "😌", "#22c55e")

    return cards_html, map_options
