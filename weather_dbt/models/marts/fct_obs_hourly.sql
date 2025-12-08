-- models/marts/fct_obs_hourly.sql

{{ config(materialized='table') }}

with obs_windows as (
    select *
    from {{ ref('int_obs_windows') }}
),

obs_features as (
    select *
    from {{ ref('int_obs_features') }}
),

dim_stations as (
    select
        station_id,
        station_name
    from {{ ref('dim_stations') }}
),

dim_beaufort as (
    select
        beaufort_level,
        beaufort_label,
        ms_min,
        ms_max
    from {{ ref('dim_beaufort') }}
),

dim_precip as (
    select
        intensity_level,
        min_mm,
        max_mm,
        label as precip_intensity_label
    from {{ ref('dim_precip_intensity') }}
),

dim_snow as (
    select
        snow_intensity_level,
        min_m,
        max_m,
        snow_intensity_label
    from {{ ref('dim_snow_intensity') }}
)

select
    -- clés
    obs_windows.event_id,
    obs_windows.station_id,
    obs_windows.validity_time_utc,

    -- station
    dim_stations.station_name,

    -- fenêtres (rollings)
    obs_windows.precip_1h_mm,
    obs_windows.precip_3h_mm,
    obs_windows.precip_24h_mm,
    obs_windows.snow_1h_m,
    obs_windows.snow_3h_m,
    obs_windows.snow_24h_m,
    obs_windows.temp_1h_c,
    obs_windows.temp_3h_c,
    obs_windows.temp_24h_c,

    -- météo atomique
    obs_features.wind_dir_deg,
    obs_features.wind_sector,
    obs_features.wind_speed_kmh,
    obs_features.wind_speed_ms,

    -- visibilité & flags
    obs_features.visibility_m,
    obs_features.visibility_cat,
    obs_features.freezing_flag,
    obs_features.precip_flag,
    obs_features.snow_on_ground_flag,

    -- mesures brutes utiles
    obs_features.precip_mm_h,
    obs_features.snow_depth_m,
    obs_features.temperature_c,
    obs_features.humidity_pct,
    
    -- interprétation BI du vent via échelle de Beaufort
    dim_beaufort.beaufort_level as wind_beaufort,
    dim_beaufort.beaufort_label as wind_beaufort_label,

    -- interprétation BI des précip 24h
    dim_precip.intensity_level as precip_intensity_level,
    dim_precip.precip_intensity_label,

    -- interprétation BI de la neige 24h
    dim_snow.snow_intensity_level,
    dim_snow.snow_intensity_label

from obs_windows
left join obs_features
    on obs_windows.event_id = obs_features.event_id

left join dim_stations
    on obs_windows.station_id = dim_stations.station_id

left join dim_beaufort
    on obs_features.wind_speed_ms >= dim_beaufort.ms_min and obs_features.wind_speed_ms <  dim_beaufort.ms_max

left join dim_precip
    on obs_windows.precip_24h_mm > dim_precip.min_mm
   and (dim_precip.max_mm is null or obs_windows.precip_24h_mm <= dim_precip.max_mm)

left join dim_snow
    on obs_windows.snow_24h_m > dim_snow.min_m
   and (dim_snow.max_m is null or obs_windows.snow_24h_m <= dim_snow.max_m)
