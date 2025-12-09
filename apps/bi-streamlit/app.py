from __future__ import annotations

import streamlit as st
import pydeck as pdk

from layers import _base_layer, _icon_layer, compute_view_state, freshness_badge, list_card_html, build_focus_cards
from data import format_last_update, load_latest_station_metrics, load_latest_timestamp
from data import (
    format_last_update,
    load_latest_station_metrics,
    load_latest_timestamp,
)


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    # Chargement des données
    max_ts = load_latest_timestamp()
    subtitle = format_last_update(max_ts)
    latest = load_latest_station_metrics()
    cards_html, map_options = build_focus_cards(latest)

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
            icon="❄️ ",
        )
    if nb_cold > 0:
        cards_html += list_card_html(
            "Grand froid",
            ", ".join(names_cold),
            f"{nb_cold} station(s)",
            "#0ea5e9",
            icon="❄️❄️ ",
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
            icon="💧💧 "
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

    # Vent brise (level 2)
    wind_breeze = latest[latest["wind_beaufort"].fillna(-1).isin([2, 3])] if not latest.empty else latest
    nb_wind_breeze = len(wind_breeze)
    names_wind_breeze = sorted(wind_breeze["station_name"].tolist()) if nb_wind_breeze > 0 else []
    if nb_wind_breeze > 0:
        cards_html += list_card_html(
            "Brise",
            ", ".join(names_wind_breeze),
            f"{nb_wind_breeze} station(s)",
            "#38bdf8",
            icon="🍃 "
        )
    # Vent fort (level 4)
    wind_strong4 = latest[latest["wind_beaufort"].fillna(-1) == 4] if not latest.empty else latest
    nb_wind_strong4 = len(wind_strong4)
    names_wind_strong4 = sorted(wind_strong4["station_name"].tolist()) if nb_wind_strong4 > 0 else []
    if nb_wind_strong4 > 0:
        cards_html += list_card_html(
            "Vent fort",
            ", ".join(names_wind_strong4),
            f"{nb_wind_strong4} station(s)",
            "#0ea5e9",
            icon="💨 "
        )

    # Vent très fort (level 5)
    wind_very_strong = latest[latest["wind_beaufort"].fillna(-1) == 5] if not latest.empty else latest
    nb_wind_very_strong = len(wind_very_strong)
    names_wind_very_strong = sorted(wind_very_strong["station_name"].tolist()) if nb_wind_very_strong > 0 else []
    if nb_wind_very_strong > 0:
        cards_html += list_card_html(
            "Vent très fort",
            ", ".join(names_wind_very_strong),
            f"{nb_wind_very_strong} station(s)",
            "#0b7a9b",
            icon="💨💨 "
        )

    # Pas de vent (level 1)
    wind_calm = latest[latest["wind_beaufort"].fillna(-1) == 1] if not latest.empty else latest
    nb_wind_calm = len(wind_calm)
    names_wind_calm = sorted(wind_calm["station_name"].tolist()) if nb_wind_calm > 0 else []
    if nb_wind_calm > 0:
        cards_html += list_card_html(
            "Pas de vent",
            ", ".join(names_wind_calm),
            f"{nb_wind_calm} station(s)",
            "#22c55e",
            icon="😌 "
        )

    # Options de couches pour la carte
    # Icon URLs (placeholder: Twemoji); you can replace per pill if needed.
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

    map_options = []
    if nb_high > 0:
        map_options.append(("🔥", high_temp.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Confort thermique")))
    if nb_cool > 0:
        map_options.append(("🍃", cool_temp.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Frais")))
    if nb_cold > 0:
        map_options.append(("🥶", cold_temp.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Grand froid")))
    if nb_heavy_rain > 0:
        map_options.append(("🌧️", heavy_rain.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Pluie soutenue")))
    if nb_moderate_rain > 0:
        map_options.append(("💧💧", moderate_rain.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Pluie modérée")))
    if nb_few_drops > 0:
        map_options.append(("💧", few_drops.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Quelques gouttes")))
    if nb_dry > 0:
        map_options.append(("🌤️", dry_rain.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Au sec")))
    if nb_snow_light > 0:
        map_options.append(("❄️❄️", snow_light.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Neige faible")))
    if nb_snow_heavy > 0:
        map_options.append(("🌨️🌨️", snow_heavy.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Neige forte")))
    if nb_wind_breeze > 0:
        map_options.append(("🍃", wind_breeze.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Brise")))
    if nb_wind_strong4 > 0:
        map_options.append(("💨", wind_strong4.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Vent fort")))
    if nb_wind_very_strong > 0:
        map_options.append(("💨💨", wind_very_strong.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Vent très fort")))
    if nb_wind_calm > 0:
        map_options.append(("😌", wind_calm.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(status="Pas de vent")))

    tabs = st.tabs(["Focus stations", "Carte"])
    with tabs[0]:
        if cards_html:
            st.markdown(
                f"""
                <div style="display:flex; flex-wrap:wrap; gap:12px; align-items:stretch; margin:12px 0 4px;">
                    {cards_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Aucune station à mettre en avant pour le moment.")
    with tabs[1]:
        st.markdown(
            '<div style="font-size:16px; font-weight:700; margin:12px 0 8px;">Carte des stations</div>',
            unsafe_allow_html=True,
        )
        stations = latest[["station_id", "station_name", "latitude", "longitude"]].drop_duplicates() if not latest.empty else latest
        options_labels = [label for label, _ in map_options]
        selected = st.pills(
            "Spots à afficher",
            options_labels,
            selection_mode="multi",
            default=options_labels,
            label_visibility="collapsed",
        )

        layers = [_base_layer(stations)]
        for label, df_points in map_options:
            if label in selected:
                icon_url = ICON_URLS.get(label)
                if not icon_url:
                    continue
                layer = _icon_layer(df_points, icon_url, 28)
                if layer:
                    layers.append(layer)
        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=compute_view_state(stations),
                tooltip={"text": "{station_name}\n{status}\n(lat: {lat}, lon: {lon})"},
            )
        )

if __name__ == "__main__":
    main()
