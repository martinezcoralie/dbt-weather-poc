"""Radar des spots météo en Ariège – demo minimal.

Lit la table marts.agg_station_latest_24h pour afficher le titre et la
date de dernière observation disponible.
"""
from __future__ import annotations

import streamlit as st

from champions import metric_card
from data import (
    format_last_update,
    load_latest_station_metrics,
    load_latest_timestamp,
)
from layers import freshness_badge


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    def intensity_emoji(kind: str, level: int | None) -> str:
        """Quick visual cue by intensity."""
        if level is None:
            return ""
        if kind == "temp":
            # 1 = froid, max = très chaud
            return "🧊" * max(1, min(3, 4 - min(level, 4))) if level <= 3 else "🔥" * max(1, min(3, level - 2))
        if kind == "snow":
            return "❄️" * max(1, min(4, level))
        if kind == "rain":
            return "💧" * max(1, min(4, level))
        if kind == "wind":
            return "🌬️" * max(1, min(4, level // 3 + 1))
        return ""

    # Chargement des données
    max_ts = load_latest_timestamp()
    subtitle = format_last_update(max_ts)
    latest = load_latest_station_metrics()

    # HEADER
    label, color = freshness_badge(max_ts)

    st.markdown(
        f'<div style="display:flex; gap:10px; align-items:center;">'
        f'<div style="font-size:48px; font-weight:700; color:#0f172a; margin-right:24px">Radar des spots météo en Ariège</div>'
        f'<span style="background:{color}; color:white; padding:6px 10px; '
        f'border-radius:12px; font-size:22px; font-weight:600;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:16px; color:#475569;">'
        'Classement des stations météo sur les dernières 24h : confort thermique, neige, pluie, vent.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(subtitle)

    # SECTION 1 : confort thermique
    st.markdown('<div style="font-size:18px; font-weight:700; margin:18px 0 10px;">Tu cherches le confort thermique</div>', unsafe_allow_html=True)
    temp_df = latest.dropna(subset=["temp_24h_intensity_label", "temp_24h_intensity_level"]) if not latest.empty else latest

    if temp_df.empty:
        st.info("Aucune donnée température disponible.")
    else:
        levels = (
            temp_df[["temp_24h_intensity_level", "temp_24h_intensity_label"]]
            .drop_duplicates()
            .sort_values(by="temp_24h_intensity_level", ascending=False)
        )

        # Palette du froid (1) vers le chaud (max)
        palette = ["#0369a1", "#0ea5e9", "#22c55e", "#f59e0b", "#f97316", "#ef4444", "#b91c1c"]

        cols = st.columns(len(levels))
        for col, (_, row) in zip(cols, levels.iterrows()):
            lvl = row["temp_24h_intensity_level"]
            label_txt = row["temp_24h_intensity_label"]
            subset = temp_df[temp_df["temp_24h_intensity_level"] == lvl]
            names = ", ".join(sorted(subset["station_name"].tolist())) if not subset.empty else "Aucune station"
            val = f"{len(subset)} stations" if len(subset) > 1 else f"{len(subset)} station"
            accent = palette[int(lvl) - 1] if lvl is not None else "#475569"
            display_label = f"{intensity_emoji('temp', int(lvl))} {label_txt}" if lvl is not None else label_txt
            with col:
                metric_card(display_label, val, names, accent)

    # SECTION 2 : neige
    st.markdown('<div style="font-size:18px; font-weight:700; margin:18px 0 10px;">Tu cherches la neige</div>', unsafe_allow_html=True)
    snow_df = latest.dropna(subset=["snow_24h_intensity_level", "snow_24h_intensity_label"]) if not latest.empty else latest

    if snow_df.empty:
        st.info("Aucune donnée neige disponible.")
    else:
        snow_levels = (
            snow_df[["snow_24h_intensity_level", "snow_24h_intensity_label"]]
            .drop_duplicates()
            .sort_values(by="snow_24h_intensity_level", ascending=False)
        )

        palette_snow = ["#e0f2fe", "#bae6fd", "#7dd3fc", "#38bdf8", "#0ea5e9"]

        cols = st.columns(len(snow_levels))
        for col, (_, row) in zip(cols, snow_levels.iterrows()):
            lvl = row["snow_24h_intensity_level"]
            label_txt = row["snow_24h_intensity_label"]
            subset = snow_df[snow_df["snow_24h_intensity_level"] == lvl]
            names = ", ".join(sorted(subset["station_name"].tolist())) if not subset.empty else "Aucune station"
            val = f"{len(subset)} stations" if len(subset) > 1 else f"{len(subset)} station"
            accent = palette_snow[min(int(lvl) - 1, len(palette_snow) - 1)] if lvl is not None else "#475569"
            display_label = f"{intensity_emoji('snow', int(lvl))} {label_txt}" if lvl is not None else label_txt
            with col:
                metric_card(display_label, val, names, accent)

    # SECTION 3 : pluie
    st.markdown('<div style="font-size:18px; font-weight:700; margin:18px 0 10px;">Tu fuis la pluie</div>', unsafe_allow_html=True)
    rain_df = latest.dropna(subset=["precip_24h_intensity_level", "precip_24h_intensity_label"]) if not latest.empty else latest

    if rain_df.empty:
        st.info("Aucune donnée pluie disponible.")
    else:
        rain_levels = (
            rain_df[["precip_24h_intensity_level", "precip_24h_intensity_label"]]
            .drop_duplicates()
            .sort_values(by="precip_24h_intensity_level", ascending=False)
        )

        palette_rain = ["#e0f2fe", "#bae6fd", "#7dd3fc", "#38bdf8", "#0ea5e9"]

        cols = st.columns(len(rain_levels))
        for col, (_, row) in zip(cols, rain_levels.iterrows()):
            lvl = row["precip_24h_intensity_level"]
            label_txt = row["precip_24h_intensity_label"]
            subset = rain_df[rain_df["precip_24h_intensity_level"] == lvl]
            names = ", ".join(sorted(subset["station_name"].tolist())) if not subset.empty else "Aucune station"
            val = f"{len(subset)} stations" if len(subset) > 1 else f"{len(subset)} station"
            accent = palette_rain[min(int(lvl) - 1, len(palette_rain) - 1)] if lvl is not None else "#475569"
            with col:
                metric_card(f"{intensity_emoji('rain', int(lvl))} {label_txt}", val, names, accent)

    # SECTION 4 : vent
    st.markdown('<div style="font-size:18px; font-weight:700; margin:18px 0 10px;">Tu veux éviter le vent fort</div>', unsafe_allow_html=True)
    wind_df = latest.dropna(subset=["wind_beaufort", "wind_beaufort_label"]) if not latest.empty else latest

    if wind_df.empty:
        st.info("Aucune donnée vent disponible.")
    else:
        wind_levels = (
            wind_df[["wind_beaufort", "wind_beaufort_label"]]
            .drop_duplicates()
            .sort_values(by="wind_beaufort", ascending=False)
        )

        palette_wind = ["#cffafe", "#a5f3fc", "#67e8f9", "#22d3ee", "#06b6d4", "#0891b2", "#0e7490", "#155e75", "#164e63"]

        cols = st.columns(len(wind_levels))
        for col, (_, row) in zip(cols, wind_levels.iterrows()):
            lvl = row["wind_beaufort"]
            label_txt = row["wind_beaufort_label"]
            subset = wind_df[wind_df["wind_beaufort"] == lvl]
            names = ", ".join(sorted(subset["station_name"].tolist())) if not subset.empty else "Aucune station"
            val = f"{len(subset)} stations" if len(subset) > 1 else f"{len(subset)} station"
            idx = min(int(lvl), len(palette_wind) - 1) if lvl is not None else 0
            accent = palette_wind[idx]
            with col:
                metric_card(f"{intensity_emoji('wind', int(lvl))} {label_txt}", val, names, accent)


if __name__ == "__main__":
    main()
