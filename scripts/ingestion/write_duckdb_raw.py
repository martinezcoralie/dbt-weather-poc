#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Write DataFrames from the Météo-France Paquet API into DuckDB (raw.*)"""

from __future__ import annotations
import argparse
import os
from typing import Sequence
import duckdb
import pandas as pd
from dotenv import load_dotenv


# --------------------------------------------------------------------------- #
# Utils
# --------------------------------------------------------------------------- #
def _connect(db_path: str) -> duckdb.DuckDBPyConnection:
    """Connect to DuckDB and ensure `raw` schema exists.

    Args:
        db_path (str): Path to the DuckDB file.

    Returns:
        duckdb.DuckDBPyConnection: Open connection object.
    """
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    return con


def write_raw_dedup(df: pd.DataFrame, table: str, pk_cols: Sequence[str], db_path: str) -> None:
    """Insert a DataFrame into a DuckDB table with PK-based deduplication.

    Args:
        df (pd.DataFrame): Input dataset.
        table (str): Fully qualified table name (e.g. 'raw.obs_hourly').
        pk_cols (Sequence[str]): Columns used as logical primary key.
        db_path (str): DuckDB database path.

    Raises:
        ValueError: If a PK column is missing in df.
    """
    missing = set(pk_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing PK columns in DataFrame: {missing}")

    df = df.copy()
    df["load_time"] = pd.Timestamp.now(tz="UTC")

    with _connect(db_path) as con:
        # Utiliser le DF complet et créer une table vide avec les bons types
        con.register("df", df)
        con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0;")
        con.unregister("df")

        con.register("df", df)
        on_clause = " AND ".join([f"t.{c} = df.{c}" for c in pk_cols])
        con.execute(f"""
            INSERT INTO {table} BY NAME
            SELECT * FROM df
            WHERE NOT EXISTS (
                SELECT 1 FROM {table} t WHERE {on_clause}
            );
        """)
        con.unregister("df")


# --------------------------------------------------------------------------- #
# Main CLI
# --------------------------------------------------------------------------- #
def main() -> None:
    """Fetch and load hourly observations for a département into DuckDB."""
    load_dotenv()

    ap = argparse.ArgumentParser(description="Ingest hourly department data -> DuckDB raw.obs_hourly")
    ap.add_argument("--dept", required=True, help="Code département (ex. '09', '75', '2A', '2B').")
    ap.add_argument("--db", default=os.getenv("DUCKDB_PATH", "./warehouse.duckdb"))
    args = ap.parse_args()

    # import du fetcher (DRY)
    from scripts.ingestion.fetch_meteofrance_paquetobs import (
        open_session_paquetobs,
        fetch_stations,
        fetch_hourly_for_dept,
    )

    session = open_session_paquetobs()

    # Stations → raw.stations
    df_st = fetch_stations(session)
    pk_st = ["Id_station"]
    write_raw_dedup(df_st, "raw.stations", pk_st, args.db)
    print(f"raw.stations: {len(df_st):,} rows (dedup)")

    # Observations horaires → raw.obs_hourly
    df_hr = fetch_hourly_for_dept(session, args.dept)
    pk_hr = ["validity_time", "geo_id_insee", "reference_time"]
    write_raw_dedup(df_hr, "raw.obs_hourly", pk_hr, args.db)
    print(f"raw.obs_hourly[{args.dept}]: {len(df_hr):,} rows (dedup)")


if __name__ == "__main__":
    main()
