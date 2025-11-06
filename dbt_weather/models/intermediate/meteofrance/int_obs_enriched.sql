-- models/intermediate/int_obs_enriched.sql
{{ config(materialized='view') }}

with base as (
  select
    o.*,
    {{ kelvin_to_c('o.temperature_k') }} as temperature_c
  from {{ ref('stg_obs_hourly') }} o
)

select
  -- clé métier unique (station + timestamp)
  concat(b.station_id, '_', b.validity_time_utc) as event_id,

  b.station_id,
  b.validity_time_utc,
  s.station_name,

  -- Vent
  b.wind_dir_deg,
  {{ wind_sector('b.wind_dir_deg') }} as wind_sector,
  {{ ms_to_kmh('b.wind_speed_ms') }} as wind_speed_kmh,
  {{ beaufort('b.wind_speed_ms') }} as wind_beaufort,

  -- Précip cumuls
  {{ rolling_sum_hours('b.precip_mm_h', 'b.validity_time_utc', 'b.station_id', 1) }}  as precip_1h_mm,
  {{ rolling_sum_hours('b.precip_mm_h', 'b.validity_time_utc', 'b.station_id', 3) }}  as precip_3h_mm,
  {{ rolling_sum_hours('b.precip_mm_h', 'b.validity_time_utc', 'b.station_id', 24) }} as precip_24h_mm,
  b.precip_mm_h,

  -- Snow cumuls
  {{ rolling_sum_hours('b.snow_depth_m', 'b.validity_time_utc', 'b.station_id', 1) }}  as snow_1h_m,
  {{ rolling_sum_hours('b.snow_depth_m', 'b.validity_time_utc', 'b.station_id', 3) }}  as snow_3h_m,
  {{ rolling_sum_hours('b.snow_depth_m', 'b.validity_time_utc', 'b.station_id', 24) }} as snow_24h_m,
  b.snow_depth_m,

  -- Temp cumuls
  {{ rolling_sum_hours('b.temperature_c', 'b.validity_time_utc', 'b.station_id', 1) }}  as temp_1h_c,
  {{ rolling_sum_hours('b.temperature_c', 'b.validity_time_utc', 'b.station_id', 3) }}  as temp_3h_c,
  {{ rolling_sum_hours('b.temperature_c', 'b.validity_time_utc', 'b.station_id', 24) }} as temp_24h_c,
  b.temperature_c,

  -- Visibilité
  {{ visibility_category('b.visibility_m') }} as visibility_cat,
  b.visibility_m,

  -- Drapeaux
  {{ freezing_flag('b.temperature_c') }} as freezing_flag,
  {{ precip_flag('b.precip_mm_h') }} as precip_flag,
  {{ snow_on_ground_flag('b.snow_depth_m') }} as snow_on_ground_flag,

  b.humidity_pct

from base b
left join {{ ref('stg_stations') }} s using (station_id)
