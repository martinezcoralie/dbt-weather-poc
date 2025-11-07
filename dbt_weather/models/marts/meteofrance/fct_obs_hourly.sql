-- models/marts/fct_obs_hourly.sql

{{ config(materialized='table') }}

with w as (
  select * from {{ ref('int_obs_windowing') }}
),
f as (
  select * from {{ ref('int_obs_features') }}
),
d as (
  select station_id, station_name
  from {{ ref('dim_stations') }}
)

select
  w.event_id,
  w.station_id,
  w.validity_time_utc,
  d.station_name,          
  -- fenêtres
  w.precip_1h_mm, w.precip_3h_mm, w.precip_24h_mm,
  w.snow_1h_m, w.snow_3h_m, w.snow_24h_m,
  w.temp_1h_c, w.temp_3h_c, w.temp_24h_c,
  -- features météo
  f.wind_dir_deg, f.wind_sector, f.wind_speed_kmh, f.wind_beaufort,
  f.visibility_m, f.visibility_cat,
  f.freezing_flag, f.precip_flag, f.snow_on_ground_flag,
  f.precip_mm_h, f.snow_depth_m, f.temperature_c, f.humidity_pct
from w
left join f using (event_id)
left join d using (station_id)
