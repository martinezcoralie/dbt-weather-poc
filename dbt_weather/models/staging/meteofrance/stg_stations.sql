-- models/staging/meteofrance/stg_stations.sql
{{ config(materialized='view') }}

with base as (
  select
    -- Identifiant / nom (nettoyage léger)
    nullif(trim(id_station), '')                         as station_id,
    nullif(trim(nom_usuel), '')                          as station_name,

    -- Coordonnées : numeric + bornes géographiques
    case
      when {{ safe_double('latitude') }} between -90 and 90
      then {{ safe_double('latitude') }}
    end                                                  as latitude,

    case
      when {{ safe_double('longitude') }} between -180 and 180
      then {{ safe_double('longitude') }}
    end                                                  as longitude,

    -- Altitude en mètres (bornes larges : -500m..9000m pour couvrir cas extrêmes)
    case
      when {{ safe_double('altitude') }} between -500 and 9000
      then {{ safe_double('altitude') }}
    end                                                  as altitude_m,

    -- Date d'ouverture (date civile, pas de TZ)
    try_cast(nullif(trim(date_ouverture), '') as date)   as opening_date

  from {{ source('raw', 'stations') }}
)

select * from base;