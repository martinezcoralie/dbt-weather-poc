import pandas as pd
import pydeck as pdk
import streamlit as st

from champions import compute_champions, metric_card
from data import load_latest_station_metrics, load_station_list
from layers import build_map_layers, compute_view_state


def main() -> None:
    st.set_page_config(page_title="Ariège météo – 24h BI", layout="wide")

    stations = load_station_list()
    latest_metrics = load_latest_station_metrics()

    # Header / hero
    st.markdown(
        """
        <style>
        .app-hero {
            padding: 18px 20px;
            border-radius: 18px;
            background: radial-gradient(circle at 20% 20%, rgba(37,99,235,0.12), transparent 30%), 
                        radial-gradient(circle at 80% 10%, rgba(14,165,233,0.12), transparent 28%),
                        linear-gradient(135deg, #0b1221 0%, #0f1c36 100%);
            color: #f8fafc;
            box-shadow: 0 14px 30px rgba(0,0,0,0.18);
            margin-bottom: 14px;
        }
        .app-hero h1 { margin: 0; }
        .section-title { font-size: 18px; font-weight: 700; margin: 10px 0 4px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="app-hero">
            <h1>Ariège – Radar des spots météo</h1>
            <p style="margin: 6px 0 0; opacity: 0.85;">Lecture BI des marts dbt : confort thermique, neige, pluie — basé sur agg_station_latest_24h.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if latest_metrics.empty:
        st.info("Aucune donnée disponible pour calculer le radar météo.")
        return

    champs = compute_champions(latest_metrics)
    join_names = lambda df: ", ".join(sorted(df["station_name"].tolist()))

    # Section A: confort thermique
    st.markdown('<div class="section-title">Tu cherches le confort thermique</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        metric_card("Coin cocooning", champs.warm_value, champs.warm_names, "#90ffa0")
    with c2:
        metric_card("Pas fait pour toi", champs.cold_value, champs.cold_names, "#e90e0e")

    # Section B: neige par niveau (modérée/forte/très forte)
    st.markdown('<div class="section-title">Tu cherches la neige</div>', unsafe_allow_html=True)
    snow_levels = {
        3: "Neige modérée",
        4: "Neige forte",
        5: "Neige très forte",
    }
    snow_cards = []
    for lvl, label in snow_levels.items():
        df_lvl = latest_metrics[latest_metrics["snow_24h_intensity_level"] == lvl]
        if df_lvl.empty:
            continue
        snow_cards.append(
            (
                label,
                f"{df_lvl['snow_24h_m'].max():.2f} m",
                f"{join_names(df_lvl)}",
            )
        )
    if snow_cards:
        cols = st.columns(len(snow_cards))
        for col, (title, val, detail) in zip(cols, snow_cards):
            with col:
                metric_card(title, val, detail, "#16dbf94a")
    else:
        st.info("Pas de neige modérée ou plus.")

    # Section Vent (catégories Beaufort)
    st.markdown('<div class="section-title">Le vent, ça t’intéresse ?</div>', unsafe_allow_html=True)
    wind_buckets = [
        ("Brise légère à modérée", 0, 3),
        ("Vent soutenu", 4, 6),
        ("Coup de vent", 7, 9),
        ("Tempête", 10, 12),
    ]
    wind_cards = []
    for title, lo, hi in wind_buckets:
        df_lvl = latest_metrics[
            (latest_metrics["wind_beaufort"].fillna(-1) >= lo)
            & (latest_metrics["wind_beaufort"].fillna(-1) <= hi)
        ]
        if df_lvl.empty:
            continue
        wind_cards.append(
            (
                title,
                f"{df_lvl['wind_speed_kmh'].max():.1f} km/h",
                f"{join_names(df_lvl)}",
            )
        )
    if wind_cards:
        cols = st.columns(len(wind_cards))
        for col, (title, val, detail) in zip(cols, wind_cards):
            with col:
                metric_card(title, val, detail, "#7dd3fc")
    else:
        st.info("Pas de vent notable sur les dernières 24h.")

    # Section C: pluie 
    st.markdown('<div class="section-title">Tu fuis la pluie</div>', unsafe_allow_html=True)
    dry_df = latest_metrics[latest_metrics["precip_24h_intensity_level"] == 1]
    rain_df = latest_metrics[latest_metrics["precip_24h_intensity_level"] > 1]
    
    c1, c2 = st.columns(2)
    with c1:
        metric_card(
            "au sec",
            f"{len(dry_df)} station(s)",
            join_names(dry_df) if not dry_df.empty else "Aucune station à ce niveau",
            "#90ffa0",
        )
    with c2:
        metric_card(
            "pas fait pour toi",
            f"{len(rain_df)} station(s)",
            join_names(rain_df) if not rain_df.empty else "Aucune station à ce niveau",
            "#e90e0e",
        )

    # Carte & table
    st.markdown('<div class="section-title">Carte & détails</div>', unsafe_allow_html=True)
    tab_map, tab_stations = st.tabs(["Carte", "Stations"])
    with tab_map:
        view_state = compute_view_state(stations)
        layers = build_map_layers(stations, champs)
        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip={"text": "{station_name}\n{status}\n(lat: {lat}, lon: {lon})"},
            )
        )

    with tab_stations:
        st.dataframe(
            latest_metrics[
                [
                    "station_name",
                    "validity_time_utc",
                    "temp_24h_c",
                    "wind_speed_kmh",
                    "wind_sector",
                    "wind_beaufort",
                    "wind_beaufort_label",
                    "precip_mm_h",
                    "precip_24h_mm",
                    "precip_24h_intensity_label",
                    "snow_24h_m",
                    "snow_24h_intensity_label",
                    "humidity_pct"
                ]
            ].rename(
                columns={
                    "station_name": "Station",
                    "validity_time_utc": "Validité",
                    "temp_24h_c": "Temp 24h (°C)",
                    "wind_speed_kmh": "Vent (km/h)",
                    "wind_sector": "Secteur vent",
                    "precip_mm_h": "Pluie instant (mm/h)",
                    "precip_24h_mm": "Pluie 24h (mm)",
                    "precip_24h_intensity_label": "Intensité pluie",
                    "snow_24h_m": "Neige 24h (m)",
                    "snow_24h_intensity_label": "Intensité neige",
                }
            ),
            height=420,
        )


if __name__ == "__main__":
    main()
