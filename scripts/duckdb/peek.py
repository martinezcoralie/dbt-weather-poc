#!/usr/bin/env python3
"""Print a small sample of a DuckDB table (quick debug helper)."""

import duckdb
import argparse
import os


def print_sample(con, title, sql):
    """Run a DuckDB query and print the resulting DataFrame."""
    print(f"\n=== {title} ===")
    df = con.sql(sql).df()
    print(df)
    return df


def main():
    """CLI: print 5 rows of a given table."""
    ap = argparse.ArgumentParser(
        description="Show a sample of a table from DuckDB warehouse"
    )
    ap.add_argument(
        "--table",
        required=True,
        help="table_schema.table_name (ex. 'raw.obs_hourly', 'staging.stg_obs_hourly').",
    )
    ap.add_argument("--db", default=os.getenv("DUCKDB_PATH", "data/warehouse.duckdb"))
    args = ap.parse_args()

    con = duckdb.connect(args.db)

    table = args.table

    # Échantillon de données
    print_sample(
        con,
        "Extrait de 5 lignes",
        f"""
        SELECT *
        FROM {table}
        LIMIT 5
        """,
    )


if __name__ == "__main__":
    main()
