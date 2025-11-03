{{ config(materialized='table') }}
select
  station_id,
  date_trunc('day', validity_time_utc) as day_utc,
  avg(temperature_c) as avg_temp_c,
  sum(precip_mm)    as sum_precip_mm,
  max(wind_speed_ms) as max_wind_ms
from {{ ref('fct_obs_hourly') }}
group by 1,2
