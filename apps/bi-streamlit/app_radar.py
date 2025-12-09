"""Radar des spots météo en Ariège – demo minimal.

Lit la table marts.agg_station_latest_24h pour afficher le titre et la
date de dernière observation disponible.
"""
from __future__ import annotations

import os
from datetime import datetime

import duckdb
import streamlit as st

DB_PATH = os.getenv("DUCKDB_PATH", "data/warehouse.duckdb")


def _latest_timestamp() -> datetime | None:
    """Return the max validity_time_utc from the mart, or None if empty."""
    with duckdb.connect(DB_PATH, read_only=True) as con:
        result = con.execute(
            """
            select max(validity_time_utc) as max_ts
            from marts.agg_station_latest_24h
            """
        ).fetchone()
    max_ts = result[0] if result else None
    return max_ts


def main() -> None:
    st.set_page_config(page_title="Radar des spots météo en Ariège", layout="wide")

    max_ts = _latest_timestamp()
    subtitle = "Aucune donnée disponible dans marts.agg_station_latest_24h" if max_ts is None else (
        f"Données mises à jour le {max_ts:%d/%m/%Y %H:%M UTC}" if isinstance(max_ts, datetime) else str(max_ts)
    )

    st.title("Radar des spots météo en Ariège")
    st.caption(subtitle)


if __name__ == "__main__":
    main()
