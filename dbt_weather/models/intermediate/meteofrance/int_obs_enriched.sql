-- models/intermediate/int_obs_enriched.sql
{{ config(materialized='view') }}

select
    o.station_id,
    s.station_name,
    o.validity_time_utc,
    o.temperature_c,
    o.humidity_pct,
    o.precip_mm,
    o.wind_speed_ms,
    o.pressure_sea_pa,
    -- clé métier unique (station + timestamp)
    concat(o.station_id, '_', o.validity_time_utc) as event_id
from {{ ref('stg_obs_hourly') }} o
left join {{ ref('stg_stations') }} s using (station_id)
