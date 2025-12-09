"""Radar des spots météo en Ariège – demo minimal.

Lit la table marts.agg_station_latest_24h pour afficher le titre et la
date de dernière observation disponible.
"""
from __future__ import annotations

import streamlit as st

from data import format_last_update, load_latest_timestamp
from layers import freshness_badge


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    max_ts = load_latest_timestamp()
    subtitle = format_last_update(max_ts)
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


if __name__ == "__main__":
    main()
