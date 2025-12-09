"""Radar des spots météo en Ariège – demo minimal.

Lit la table marts.agg_station_latest_24h pour afficher le titre et la
date de dernière observation disponible.
"""
from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from data import load_latest_timestamp


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    max_ts = load_latest_timestamp()
    subtitle = "Aucune donnée disponible dans marts.agg_station_latest_24h" if max_ts is None else (
        f"Données mises à jour le {max_ts:%d/%m/%Y %H:%M UTC}" if isinstance(max_ts, datetime) else str(max_ts)
    )

    st.title("Radar des spots météo en Ariège")
    st.caption(subtitle)


if __name__ == "__main__":
    main()
