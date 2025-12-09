"""UI/pydeck helpers for the map and focus cards."""

from datetime import datetime, timezone

import pandas as pd
import pydeck as pdk

from config import FLAG_DICT


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


def build_station_scatter_layer(stations: pd.DataFrame) -> pdk.Layer:
    """Grey scatter layer for all stations (map background)."""
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


def build_icon_layer(data: pd.DataFrame, icon_url: str, size) -> pdk.Layer | None:
    """Icon layer for a given category; returns None when no points to display."""
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


def render_focus_card_html(title: str, station_text: str, count_text: str, accent: str, icon_html: str = "") -> str:
    """Render the HTML for a focus card (used inside the flex container)."""
    import textwrap

    html = textwrap.dedent(
        f"""\
        <div class="focus-card" style="--card-accent: {accent};">
            <div class="focus-card-title">{icon_html}{title}</div>
            <div class="focus-card-body">{station_text}</div>
            <div class="focus-card-count" style="margin-top:auto; align-self:flex-start;">{count_text}</div>
        </div>
        """
    ).strip()
    return html


def build_focus_cards(latest: pd.DataFrame) -> tuple[str, list[tuple[str, pd.DataFrame, str]]]:
    """Return (cards_html, map_options) for the focus section; requires is_* flags in data."""
    cards_html = ""
    map_options: list[tuple[str, pd.DataFrame, str]] = []

    if latest.empty:
        return cards_html, map_options

    def pick_with_flag(df: pd.DataFrame, flag: str) -> pd.DataFrame:
        """Select rows where a boolean flag is true; raises if flag is missing."""
        if flag not in df.columns:
            raise KeyError(f"Flag column missing: {flag}")
        return df[df[flag].fillna(False)]

    def add_focus(df: pd.DataFrame, title: str, icon_url: str, accent: str) -> None:
        nonlocal cards_html, map_options
        if df.empty:
            return
        df_points = df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status=title)
        count = len(df_points)
        names = ", ".join(sorted(df_points["station_name"].tolist()))
        icon_html = (
            f'<img src="{icon_url}" alt="{title}" width="18" height="18" '
            'style="vertical-align:middle; margin-right:6px;" />'
        )
        cards_html += render_focus_card_html(title, names, f"{count} station(s)", accent, icon_html=icon_html)
        map_options.append((title, df_points, icon_url))

    for flag, meta in FLAG_DICT.items():
        df_flag = pick_with_flag(latest, flag)
        add_focus(
            df_flag,
            meta["title"],
            meta["icon_url"],
            meta["accent"],
        )

    return cards_html, map_options
