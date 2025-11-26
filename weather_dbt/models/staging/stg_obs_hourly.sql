-- models/staging/meteofrance/stg_obs_hourly.sql
{{ config(materialized='view') }}

with base as (
    select
    -- Ids / localisation
        geo_id_insee                                        as station_id,        -- texte ddnnnpp
        case 
            when {{ safe_double('lat') }} between -90 and 90 
                then {{ safe_double('lat') }} 
        end                                                 as latitude,
        case 
            when {{ safe_double('lon') }} between -180 and 180 
                then {{ safe_double('lon') }} 
        end                                                 as longitude,

        -- Timestamps (ISO 8601 / UTC)
        try_cast(reference_time as timestamptz)             as production_time_utc,
        try_cast(insert_time    as timestamptz)             as insert_time_utc,
        try_cast(validity_time  as timestamptz)             as validity_time_utc,
        load_time                                           as load_time_utc,

        -- Températures (K)
        {{ safe_double('t') }}                               as temperature_k,
        {{ safe_double('td') }}                              as dew_point_k,
        {{ safe_double('tx') }}                              as t_max_k,
        {{ safe_double('tn') }}                              as t_min_k,

        -- Humidité (%)
        case
            when {{ safe_int('u') }} between 0 and 100 
                then {{ safe_int('u') }}
        end                                                 as humidity_pct,
        case 
            when {{ safe_int('ux') }} between 0 and 100 
                then {{ safe_int('ux') }} 
        end                                                 as humidity_max_pct,
        case 
            when {{ safe_int('un') }} between 0 and 100 
                then {{ safe_int('un') }} 
        end                                                 as humidity_min_pct,

        -- Vent (moyen / max / rafales) - direction en degrés (0-360)
        case 
            when {{ safe_int('dd') }} between 0 and 360 
                then {{ safe_int('dd') }} 
        end                                                 as wind_dir_deg,
        {{ safe_double('ff') }}                             as wind_speed_ms,

        case 
            when {{ safe_int('dxy') }} between 0 and 360 
                then {{ safe_int('dxy') }} 
        end                                                 as wind_dir_gust_avg_max_deg,
        {{ safe_double('fxy') }}                            as wind_gust_avg_max_ms,

        case 
            when {{ safe_int('dxi') }} between 0 and 360 
                then {{ safe_int('dxi') }} 
        end                                                 as wind_dir_gust_abs_max_deg,
        {{ safe_double('fxi') }}                             as wind_gust_abs_max_ms,

        -- Précipitations (horaire mm)
        {{ safe_double('rr1') }}                             as precip_mm_h,

        -- Températures du sol (K)
        {{ safe_double('t_10') }}                            as soil_t_10cm_k,
        {{ safe_double('t_20') }}                            as soil_t_20cm_k,
        {{ safe_double('t_50') }}                            as soil_t_50cm_k,
        {{ safe_double('t_100') }}                           as soil_t_100cm_k,

        -- Visibilité (m)
        {{ safe_int('vv') }}                                 as visibility_m,

        -- État du sol (code)
        {{ safe_int('etat_sol') }}                           as soil_state_code,

        -- Neige (m)
        {{ safe_double('sss') }}                             as snow_depth_m,

        -- Ensoleillement / rayonnement
        {{ safe_double('insolh') }}                          as sunshine_duration_min,
        {{ safe_double('ray_glo01') }}                       as global_radiation_j_m2,

        -- Pressions (Pa)
        {{ safe_double('pres') }}                            as pressure_station_pa,
        {{ safe_double('pmer') }}                            as pressure_sea_pa

    from {{ source('raw', 'obs_hourly') }}
)

select * from base
