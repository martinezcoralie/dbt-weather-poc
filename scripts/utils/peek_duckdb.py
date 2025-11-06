#!/usr/bin/env python3
import duckdb
import pandas as pd

def run(con, title, sql):
    print(f"\n=== {title} ===")
    df = con.sql(sql).df()
    print(df)
    return df

def main():
    con = duckdb.connect("warehouse.duckdb")

    # Lister les tables et schémas
    run(con, "Liste des schémas", "SELECT * FROM information_schema.schemata")
    run(con, "Tables disponibles", "SELECT table_schema, table_name FROM information_schema.tables ORDER BY table_schema, table_name")

    # Comptages
    run(con, "Nombre de stations", "SELECT count(*) AS c FROM raw.stations")
    run(con, "Nombre d'observations horaires", "SELECT count(*) AS c FROM raw.obs_hourly")

    # Échantillons de données
    run(con, "5 dernières obs_hourly (tout)", """
        SELECT *
        FROM raw.obs_hourly
        ORDER BY validity_time DESC
        LIMIT 5
    """)

    run(con, "5 dernières obs_hourly (champs clés)", """
        SELECT validity_time, station_code_insee
        FROM raw.obs_hourly
        ORDER BY validity_time DESC
        LIMIT 5
    """)

if __name__ == "__main__":
    main()
