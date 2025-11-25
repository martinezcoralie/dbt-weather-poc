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

    -- enrichissement via dimension Beaufort
    dim_beaufort.beaufort_level,
    dim_beaufort.beaufort_label,

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
    obs_features.humidity_pct

from obs_windows
left join obs_features
    on obs_windows.event_id = obs_features.event_id

left join dim_stations
    on obs_windows.station_id = dim_stations.station_id

left join dim_beaufort
    on obs_features.wind_speed_ms between dim_beaufort.ms_min
                                    and dim_beaufort.ms_max
;
