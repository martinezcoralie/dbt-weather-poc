"""Radar des spots météo en Ariège – demo minimal.

Lit la table marts.agg_station_latest_24h pour afficher le titre et la
date de dernière observation disponible.
"""
from __future__ import annotations

import streamlit as st

from data import load_latest_timestamp
from layers import render_freshness


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    max_ts = load_latest_timestamp()

    st.title("Radar des spots météo en Ariège")
    render_freshness(max_ts)


if __name__ == "__main__":
    main()
