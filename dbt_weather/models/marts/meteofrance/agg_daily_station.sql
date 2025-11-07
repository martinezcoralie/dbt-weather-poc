{{ config(materialized='table') }}
select
    station_id,
    station_name,
    date_trunc('day', validity_time_utc) as day_utc,
    avg(temperature_c) as avg_temp_c,
    sum(precip_mm_h)    as sum_precip_mm_h,
    max(wind_speed_kmh) as max_wind_kmh
from {{ ref('fct_obs_hourly') }}
group by 1,2,3
