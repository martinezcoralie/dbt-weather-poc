from __future__ import annotations

import streamlit as st
import pydeck as pdk

from layers import _base_layer, _icon_layer, compute_view_state, freshness_badge, build_focus_cards
from data import format_last_update, load_latest_station_metrics, load_latest_timestamp


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    st.markdown(
        """
        <style>
        .hero-header {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .hero-title {
            font-size: 48px;
            line-height: 1.1;
            font-weight: 700;
            color: #0f172a;
            margin-right: 24px;
        }
        .hero-badge {
            background: #0ea5e9;
            color: white;
            padding: 6px 10px;
            border-radius: 12px;
            font-size: 22px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
        }
        .cards-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: stretch;
            margin: 12px 0 4px;
        }
        .focus-card {
            flex: 1 1 calc(50% - 12px);
            min-width: 150px;
            max-width: 260px;
            min-height: 150px;
            padding: 14px 16px;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--card-accent, #0ea5e9) 0%, #0f172a 120%);
            box-shadow: 0 10px 18px rgba(0,0,0,0.12);
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .focus-card-title {
            font-size: 18px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.8;
        }
        .focus-card-body {
            font-size: 13px;
            line-height: 1.4;
            opacity: 0.9;
        }
        .focus-card-count {
            font-size: 12px;
            font-weight: 700;
            opacity: 0.92;
            align-self: flex-end;
        }
        @media (max-width: 768px) {
            .hero-title {
                font-size: 28px;
                line-height: 1.2;
                margin-right: 12px;
            }
            .hero-badge {
                font-size: 16px;
                padding: 6px 8px;
            }
            .cards-wrap {
                gap: 10px;
            }
            .focus-card {
                flex: 1 1 calc(50% - 10px);
                min-width: 0;
                max-width: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Chargement des données
    max_ts = load_latest_timestamp()
    subtitle = format_last_update(max_ts)
    latest = load_latest_station_metrics()

    # HEADER
    label, color = freshness_badge(max_ts)

    st.markdown(
        f'<div class="hero-header">'
        f'<div class="hero-title">Radar des spots météo en Ariège</div>'
        f'<span class="hero-badge" style="background:{color};">{label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.caption(subtitle)

    cards_html, map_options = build_focus_cards(latest)

    tabs = st.tabs(["Focus stations", "Carte"])
    with tabs[0]:
        if cards_html:
            st.markdown(
                f"""
                <div class="cards-wrap">
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
        options_labels = [label for label, _, _ in map_options]
        selected = st.pills(
            "Spots à afficher",
            options_labels,
            selection_mode="multi",
            default=options_labels,
            label_visibility="collapsed",
        )

        layers = [_base_layer(stations)]
        for label, df_points, icon_url in map_options:
            if label in selected:
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
