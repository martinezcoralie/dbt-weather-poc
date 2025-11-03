-- models/staging/meteofrance/stg_obs_hourly.sql
{{ config(materialized='view') }}

with base as (
  select
    station_code_insee                     as station_id,
    reference_time                         as production_time_utc,
    validity_time                          as validity_time_utc,
    insert_time                            as insert_time_utc,
    lat                                    as latitude,
    lon                                    as longitude,
    -- météorologie (cf. doc Météo-France)
    t      as temperature_k,               -- K :contentReference[oaicite:3]{index=3}
    (t - 273.15) as temperature_c,         -- °C dérivé
    td     as dew_point_k,                 -- K (si présent) :contentReference[oaicite:4]{index=4}
    (td - 273.15) as dew_point_c,
    tx     as t_max_k, (tx - 273.15) as t_max_c,  -- si présent :contentReference[oaicite:5]{index=5}
    tn     as t_min_k, (tn - 273.15) as t_min_c,  -- si présent :contentReference[oaicite:6]{index=6}
    u      as humidity_pct,                -- % :contentReference[oaicite:7]{index=7}
    ff     as wind_speed_ms,               -- m/s :contentReference[oaicite:8]{index=8}
    dd     as wind_dir_deg,                -- ° (0-360) :contentReference[oaicite:9]{index=9}
    fxy    as wind_gust_ms,                -- si présent (rafale max heure) :contentReference[oaicite:10]{index=10}
    rr1    as precip_mm,                   -- mm/h :contentReference[oaicite:11]{index=11}
    vv     as visibility_m,                -- m :contentReference[oaicite:12]{index=12}
    pres   as pressure_station_pa,         -- Pa :contentReference[oaicite:13]{index=13}
    pmer   as pressure_sea_pa,             -- Pa :contentReference[oaicite:14]{index=14}
    n      as nebulosity_octas,            -- si présent :contentReference[oaicite:15]{index=15}
    dept_code,
    load_ts
  from {{ source('raw', 'obs_hourly') }}
)
select * from base
