#!/usr/bin/env python3
import duckdb
import argparse
import os

def run(con, title, sql):
    print(f"\n=== {title} ===")
    df = con.sql(sql).df()
    print(df)
    return df

def main():
    ap = argparse.ArgumentParser(
        description="Show a sample of a table from DuckDB warehouse"
    )
    ap.add_argument(
        "--table",
        required=True,
        help="table_schema.table_name (ex. 'raw.obs_hourly', 'staging.stg_obs_hourly')."
    )
    ap.add_argument(
        "--db",
        default=os.getenv("DUCKDB_PATH", "./warehouse.duckdb")
    )
    args = ap.parse_args()

    con = duckdb.connect(args.db)

    table = args.table

    # Échantillon de données
    run(
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
