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
        f.temp_24h_intensity_level,
        f.temp_24h_intensity_label,
        f.wind_beaufort,
        f.wind_beaufort_label,
        f.temperature_c,
        f.precip_mm_h,
        f.wind_speed_kmh,
        f.wind_sector,
        f.visibility_cat,
        f.humidity_pct,
        s.station_name,
        s.latitude,
        s.longitude,
        /* Pre-calculated focus flags for BI/dashboard */
        coalesce(f.temp_24h_intensity_level, 0) >= 4 as is_temp_comfort,
        coalesce(f.temp_24h_intensity_level, 0) = 3 as is_temp_cool,
        coalesce(f.temp_24h_intensity_level, 0) in (1, 2) as is_temp_cold,
        coalesce(f.precip_24h_intensity_level, 0) in (4, 5) as is_rain_heavy,
        coalesce(f.precip_24h_intensity_level, 0) = 3 as is_rain_moderate,
        coalesce(f.precip_24h_intensity_level, 0) = 1
            and coalesce(f.precip_24h_mm, 0) > 0 as is_rain_drops,
        coalesce(f.precip_24h_mm, 0) = 0 as is_rain_dry,
        coalesce(f.snow_24h_intensity_level, 0) in (2, 3) as is_snow_light,
        coalesce(f.snow_24h_intensity_level, 0) in (4, 5) as is_snow_heavy,
        coalesce(f.wind_beaufort, -1) in (2, 3) as is_wind_breeze,
        coalesce(f.wind_beaufort, -1) = 4 as is_wind_strong,
        coalesce(f.wind_beaufort, -1) = 5 as is_wind_very_strong,
        coalesce(f.wind_beaufort, -1) = 1 as is_wind_calm,
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
    temp_24h_intensity_level,
    temp_24h_intensity_label,
    wind_beaufort,
    wind_beaufort_label,
    temperature_c,
    precip_mm_h,
    humidity_pct,
    wind_speed_kmh,
    wind_sector,
    visibility_cat,
    is_temp_comfort,
    is_temp_cool,
    is_temp_cold,
    is_rain_heavy,
    is_rain_moderate,
    is_rain_drops,
    is_rain_dry,
    is_snow_light,
    is_snow_heavy,
    is_wind_breeze,
    is_wind_strong,
    is_wind_very_strong,
    is_wind_calm
from ranked
where rn = 1
