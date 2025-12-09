from __future__ import annotations

import streamlit as st
import pydeck as pdk

from layers import _base_layer, _icon_layer, compute_view_state, freshness_badge, build_focus_cards
from data import format_last_update, load_latest_station_metrics, load_latest_timestamp


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

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
    st.caption(subtitle)

    cards_html, map_options = build_focus_cards(latest)

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
