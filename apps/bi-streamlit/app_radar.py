"""
Radar des spots météo en Ariège – demo minimal.
"""
from __future__ import annotations

import streamlit as st

from champions import list_card, list_card_html, metric_card
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
            return "💨" * max(1, min(4, level // 3 + 1))
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
    # st.markdown(
    #     '<div style="font-size:16px; color:#475569;">'
    #     'Classement des stations météo sur les dernières 24h : confort thermique, neige, pluie, vent.'
    #     '</div>',
    #     unsafe_allow_html=True,
    # )
    st.caption(subtitle)

    # Focus card : stations les plus douces (temp_24h_intensity_level 4 ou 5)
    high_temp = latest[latest["temp_24h_intensity_level"].fillna(0) >= 4] if not latest.empty else latest
    nb_high = len(high_temp)
    names_high = sorted(high_temp["station_name"].tolist()) if nb_high > 0 else []

    cold_temp = latest[latest["temp_24h_intensity_level"].fillna(0).isin([1, 2])] if not latest.empty else latest
    nb_cold = len(cold_temp)
    names_cold = sorted(cold_temp["station_name"].tolist()) if nb_cold > 0 else []

    cool_temp = latest[latest["temp_24h_intensity_level"].fillna(0) == 3] if not latest.empty else latest
    nb_cool = len(cool_temp)
    names_cool = sorted(cool_temp["station_name"].tolist()) if nb_cool > 0 else []

    cards_html = ""
    if nb_high > 0:
        cards_html += list_card_html(
            "Confort thermique",
            ", ".join(names_high),
            f"{nb_high} station(s)",
            "#ef4444",
            icon="🔥 ",
        )
    if nb_cool > 0:
        cards_html += list_card_html(
            "Frais",
            ", ".join(names_cool),
            f"{nb_cool} station(s)",
            "#0ea5e9",
            icon="🍃 ",
        )
    if nb_cold > 0:
        cards_html += list_card_html(
            "Grand froid",
            ", ".join(names_cold),
            f"{nb_cold} station(s)",
            "#0ea5e9",
            icon="❄️ ",
        )

    # Highlight pluie & sec as focus cards (wrap) appended to same container
    heavy_rain = latest[latest["precip_24h_intensity_level"].fillna(0).isin([4, 5])] if not latest.empty else latest
    nb_heavy_rain = len(heavy_rain)
    names_heavy_rain = sorted(heavy_rain["station_name"].tolist()) if nb_heavy_rain > 0 else []
    if nb_heavy_rain > 0:
        cards_html += list_card_html(
            "Pluie soutenue",
            ", ".join(names_heavy_rain),
            f"{nb_heavy_rain} station(s)",
            "#0ea5e9",
            icon="🌧️ "
        )

    moderate_rain = latest[latest["precip_24h_intensity_level"].fillna(0) == 3] if not latest.empty else latest
    nb_moderate_rain = len(moderate_rain)
    names_moderate_rain = sorted(moderate_rain["station_name"].tolist()) if nb_moderate_rain > 0 else []
    if nb_moderate_rain > 0:
        cards_html += list_card_html(
            "Pluie modérée",
            ", ".join(names_moderate_rain),
            f"{nb_moderate_rain} station(s)",
            "#38bdf8",
            icon="💧 "
        )

    few_drops = latest[(latest["precip_24h_intensity_level"].fillna(0) == 1) & (latest["precip_24h_mm"].fillna(0) > 0)] if not latest.empty else latest
    nb_few_drops = len(few_drops)
    names_few_drops = sorted(few_drops["station_name"].tolist()) if nb_few_drops > 0 else []
    if nb_few_drops > 0:
        cards_html += list_card_html(
            "Quelques gouttes",
            ", ".join(names_few_drops),
            f"{nb_few_drops} station(s)",
            "#60a5fa",
            icon="💧 "
        )

    dry_rain = latest[latest["precip_24h_mm"].fillna(0) == 0] if not latest.empty else latest
    nb_dry = len(dry_rain)
    names_dry = sorted(dry_rain["station_name"].tolist()) if nb_dry > 0 else []
    if nb_dry > 0:
        cards_html += list_card_html(
            "Au sec",
            ", ".join(names_dry),
            f"{nb_dry} station(s)",
            "#22c55e",
            icon="🌤️ "
        )

    # Neige faible (levels 2 ou 3)
    snow_light = latest[latest["snow_24h_intensity_level"].fillna(0).isin([2, 3])] if not latest.empty else latest
    nb_snow_light = len(snow_light)
    names_snow_light = sorted(snow_light["station_name"].tolist()) if nb_snow_light > 0 else []
    if nb_snow_light > 0:
        cards_html += list_card_html(
            "Neige faible",
            ", ".join(names_snow_light),
            f"{nb_snow_light} station(s)",
            "#38bdf8",
            icon="❄️❄️ "
        )

    # Neige forte (levels 4 ou 5)
    snow_heavy = latest[latest["snow_24h_intensity_level"].fillna(0).isin([4, 5])] if not latest.empty else latest
    nb_snow_heavy = len(snow_heavy)
    names_snow_heavy = sorted(snow_heavy["station_name"].tolist()) if nb_snow_heavy > 0 else []
    if nb_snow_heavy > 0:
        cards_html += list_card_html(
            "Neige forte",
            ", ".join(names_snow_heavy),
            f"{nb_snow_heavy} station(s)",
            "#0ea5e9",
            icon="🌨️🌨️ "
        )

    if cards_html:
        st.markdown(
            f"""
            <div style="display:flex; flex-wrap:wrap; gap:12px; align-items:stretch; margin:12px 0 4px;">
                {cards_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # SECTION 4 : vent
    st.markdown('<div style="font-size:18px; font-weight:700; margin:18px 0 10px;">Tu veux éviter le vent fort</div>', unsafe_allow_html=True)
    wind_df = latest.dropna(subset=["wind_beaufort", "wind_beaufort_label"]) if not latest.empty else latest

    if wind_df.empty:
        st.info("Aucune donnée vent disponible.")
    else:
        wind_levels = (
            wind_df[["wind_beaufort", "wind_beaufort_label"]]
            .drop_duplicates()
            .sort_values(by="wind_beaufort", ascending=True)
        )

        palette_wind = ["#cffafe", "#a5f3fc", "#67e8f9", "#22d3ee", "#06b6d4", "#0891b2", "#0e7490", "#155e75", "#164e63"]

        cols = st.columns(len(wind_levels), gap="small")
        for col, (_, row) in zip(cols, wind_levels.iterrows()):
            lvl = row["wind_beaufort"]
            label_txt = row["wind_beaufort_label"]
            subset = wind_df[wind_df["wind_beaufort"] == lvl]
            names = ", ".join(sorted(subset["station_name"].tolist())) if not subset.empty else "Aucune station"
            val = f"{len(subset)} stations" if len(subset) > 1 else f"{len(subset)} station"
            idx = min(int(lvl), len(palette_wind) - 1) if lvl is not None else 0
            accent = palette_wind[idx]
            with col:
                metric_card(label_txt, val, names, accent, emoji=intensity_emoji('wind', int(lvl)) if lvl is not None else None)


if __name__ == "__main__":
    main()
