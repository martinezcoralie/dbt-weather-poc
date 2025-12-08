{{ config(materialized='table') }}

with ranked as (
    select
        f.station_id,
        f.validity_time_utc,
        f.temp_24h_c,
        f.precip_24h_mm,
        f.snow_24h_m,
        f.precip_24h_intensity_level,
        f.precip_24h_intensity_label,
        f.snow_24h_intensity_level,
        f.snow_24h_intensity_label,
        f.wind_beaufort,
        f.wind_beaufort_label,
        f.temperature_c,
        f.precip_mm_h,
        f.wind_speed_kmh,
        f.wind_sector,
        f.visibility_cat,
        s.station_name,
        s.latitude,
        s.longitude,
        row_number() over (
            partition by f.station_id
            order by f.validity_time_utc desc
        ) as rn
    from {{ ref('fct_obs_hourly') }} f
    join {{ ref('dim_stations') }} s on s.station_id = f.station_id
)

select
    station_id,
    station_name,
    latitude,
    longitude,
    validity_time_utc,
    temp_24h_c,
    precip_24h_mm,
    snow_24h_m,
    precip_24h_intensity_level,
    precip_24h_intensity_label,
    snow_24h_intensity_level,
    snow_24h_intensity_label,
    wind_beaufort,
    wind_beaufort_label,
    temperature_c,
    precip_mm_h,
    wind_speed_kmh,
    wind_sector,
    visibility_cat
from ranked
where rn = 1
