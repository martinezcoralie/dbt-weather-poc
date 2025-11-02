#!/usr/bin/env python3
import duckdb

con = duckdb.connect('warehouse.duckdb')
print(con.sql("select count(*) as c from raw.stations").df())
print(con.sql("select count(*) as c from raw.obs_hourly").df())
print(con.sql("select validity_time, station_code_insee from raw.obs_hourly order by validity_time desc limit 5").df())