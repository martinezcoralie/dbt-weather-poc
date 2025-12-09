from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class ChampionSet:
    warm_value: str
    warm_names: str
    cold_value: str
    cold_names: str
    dry_value: str
    dry_names: str
    snow_value: str
    snow_names: str
    wet_value: str
    wet_names: str
    warm_points: pd.DataFrame
    cold_points: pd.DataFrame
    snow_points: pd.DataFrame
    wet_points: pd.DataFrame


def _format_names(df: pd.DataFrame) -> str:
    return ", ".join(sorted(df["station_name"].tolist()))


def _champion_extreme(df: pd.DataFrame, col: str, fn) -> tuple[Optional[float], pd.DataFrame]:
    """Return extreme value and matching rows for a numeric column."""
    df_valid = df[pd.notna(df[col])]
    if df_valid.empty:
        return None, pd.DataFrame()
    value = fn(df_valid[col])
    champs = df_valid[df_valid[col] == value]
    return value, champs


def _top_by_level(df: pd.DataFrame, level_col: str) -> tuple[Optional[int], pd.DataFrame, pd.DataFrame]:
    """Return max level, champions at that level, and lower-level rows."""
    df_valid = df[pd.notna(df[level_col])]
    if df_valid.empty:
        return None, pd.DataFrame(), pd.DataFrame()
    max_level = int(df_valid[level_col].max())
    champs = df_valid[df_valid[level_col] == max_level]
    lower = df_valid[df_valid[level_col] < max_level]
    return max_level, champs, lower


def compute_champions(latest_metrics: pd.DataFrame) -> ChampionSet:
    """Compute cards and map datasets from the latest-per-station mart."""
    warm_val, warm_df = _champion_extreme(latest_metrics, "temp_24h_c", pd.Series.max)
    cold_val, cold_df = _champion_extreme(latest_metrics, "temp_24h_c", pd.Series.min)

    dry_df = latest_metrics[latest_metrics["precip_24h_intensity_level"].fillna(0) <= 1]

    wet_level, wet_df, wet_lower = _top_by_level(
        latest_metrics[latest_metrics["precip_24h_intensity_level"].fillna(0) > 0],
        "precip_24h_intensity_level",
    )
    wet_label = wet_df["precip_24h_intensity_label"].iloc[0] if not wet_df.empty else None

    snow_filtered = latest_metrics[latest_metrics["snow_24h_intensity_level"].fillna(0) >= 3]
    snow_level, snow_df, snow_lower = _top_by_level(snow_filtered, "snow_24h_intensity_level")
    snow_label = snow_df["snow_24h_intensity_label"].iloc[0] if not snow_df.empty else None

    wet_other_levels = (
        ", ".join(str(int(x)) for x in sorted(wet_lower["precip_24h_intensity_level"].unique()))
        if not wet_lower.empty
        else "none"
    )
    snow_other_levels = (
        ", ".join(str(int(x)) for x in sorted(snow_lower["snow_24h_intensity_level"].unique()))
        if not snow_lower.empty
        else "none"
    )

    # Map-ready points
    warm_points = (
        warm_df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Plus doux")
        if not warm_df.empty
        else pd.DataFrame()
    )
    cold_points = (
        cold_df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Plus froid")
        if not cold_df.empty
        else pd.DataFrame()
    )
    snow_points = (
        snow_df.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(
            status="Neige 24h", icon_size=(snow_df["snow_24h_intensity_level"] - 1) * 9
        )
        if not snow_df.empty
        else pd.DataFrame()
    )
    wet_points = (
        wet_df.rename(columns={"longitude": "lon", "latitude": "lat"})
        .assign(status="Pluie 24h")
        .assign(icon_size=(wet_df["precip_24h_intensity_level"].clip(lower=2) - 1) * 9)
        if not wet_df.empty
        else pd.DataFrame()
    )

    return ChampionSet(
        warm_value=f"{warm_val:.1f} °C" if warm_val is not None else "N/A",
        warm_names=_format_names(warm_df) if not warm_df.empty else "Pas de mesure",
        cold_value=f"{cold_val:.1f} °C" if cold_val is not None else "N/A",
        cold_names=_format_names(cold_df) if not cold_df.empty else "Pas de mesure",
        dry_value=f"{len(dry_df)} station(s)",
        dry_names=_format_names(dry_df) if not dry_df.empty else "Aucune station au sec (niveau 1)",
        snow_value=f"Niveau {snow_level} ({snow_label})" if snow_level is not None else "N/A",
        snow_names=(
            _format_names(snow_df) + f" · Autres niveaux: {snow_other_levels}"
            if not snow_df.empty
            else "Pas de neige mesurée"
        ),
        wet_value=f"Niveau {wet_level} ({wet_label})" if wet_level is not None else "N/A",
        wet_names=(
            _format_names(wet_df) + f" · Autres niveaux: {wet_other_levels}"
            if not wet_df.empty
            else "Aucune station avec pluie"
        ),
        warm_points=warm_points,
        cold_points=cold_points,
        snow_points=snow_points,
        wet_points=wet_points,
    )


def metric_card(title: str, value: str, detail: str, accent: str, emoji: str | None = None) -> None:
    """Render a small stat card with optional emoji row."""
    import streamlit as st  # local import to avoid circularity
    import textwrap

    emoji_row = f'<div style="font-size:18px; margin:4px 0;">{emoji}</div>' if emoji else ""
    html = textwrap.dedent(
        f"""\
        <div style="width: 240px; max-width: 260px; min-height: 170px; padding: 14px 16px;
                   border-radius: 14px;
                   background: linear-gradient(135deg, {accent} 0%, #0f172a 120%);
                   box-shadow: 0 12px 24px rgba(0,0,0,0.12);
                   color: #f8fafc;
                   display: flex;
                   flex-direction: column;
                   justify-content: space-between;
                   gap: 4px;">
            <div style="font-size: 18px; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.8;">{title}</div>
            {emoji_row}
            <div style="font-size: 24px; font-weight: 700; margin: 6px 0;">{value}</div>
            <div style="font-size: 14px; opacity: 0.9;">{detail}</div>
        </div>
        """
    ).strip()

    st.markdown(html, unsafe_allow_html=True)


def list_card(title: str, stations: list[str] | str, count: int, accent: str, emoji: str | None = None) -> None:
    """Render a compact card showing a list of stations and a count at the bottom."""
    import streamlit as st  # local import to avoid circularity
    import textwrap

    if isinstance(stations, str):
        station_text = stations or "Aucune station"
    else:
        station_text = ", ".join(sorted([s for s in stations if s])) or "Aucune station"

    count_text = f"{count} station{'s' if count != 1 else ''}"
    icon = f"{emoji} " if emoji else ""

    html = list_card_html(title, station_text, count_text, accent, icon)
    st.markdown(html, unsafe_allow_html=True)


def list_card_html(title: str, station_text: str, count_text: str, accent: str, icon: str = "") -> str:
    """Return the HTML for a list-style card (for use inside flex containers)."""
    import textwrap

    html = textwrap.dedent(
        f"""\
        <div style="width: 240px; max-width: 260px; min-height: 150px; padding: 14px 16px;
                   border-radius: 14px;
                   background: linear-gradient(135deg, {accent} 0%, #0f172a 120%);
                   box-shadow: 0 10px 18px rgba(0,0,0,0.12);
                   color: #f8fafc;
                   display: flex;
                   flex-direction: column;
                   gap: 8px;">
            <div style="font-size: 18px; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.8;">{icon}{title}</div>
            <div style="font-size: 13px; line-height: 1.4; opacity: 0.9;">{station_text}</div>
            <div style="font-size: 12px; font-weight: 700; opacity: 0.92; align-self: flex-end;">{count_text}</div>
        </div>
        """
    ).strip()
    return html
