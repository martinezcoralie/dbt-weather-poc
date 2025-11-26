-- models/intermediate/int_obs_features.sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}

with base as (
    select
        {{ dbt_utils.generate_surrogate_key(['obs_hourly.station_id','obs_hourly.validity_time_utc']) }} as event_id,
        obs_hourly.*,
        {{ kelvin_to_c('obs_hourly.temperature_k') }} as temperature_c
    from {{ ref('stg_obs_hourly') }} as obs_hourly
    {% if is_incremental() %}
    -- On n’ingère que les nouvelles heures
        where obs_hourly.validity_time_utc > (
            select coalesce(max(validity_time_utc), '1900-01-01') from {{ this }}
        )
    {% endif %}
)

select
    event_id,
    station_id,
    validity_time_utc,

    -- Vent
    wind_dir_deg,
    wind_speed_ms,
    {{ ms_to_kmh('wind_speed_ms') }} as wind_speed_kmh,
    {{ wind_sector('wind_dir_deg') }} as wind_sector,

    -- Visibilité
    {{ visibility_category('visibility_m') }} as visibility_cat,
    visibility_m,

    -- Drapeaux
    {{ freezing_flag('temperature_c') }} as freezing_flag,
    {{ precip_flag('precip_mm_h') }} as precip_flag,
    {{ snow_on_ground_flag('snow_depth_m') }} as snow_on_ground_flag,

    -- Mesures brutes utiles aux rollings
    precip_mm_h,
    snow_depth_m,
    temperature_c,
    humidity_pct
from base
