{{ config(materialized='table') }}

select
    cast(row_number() over (order by coalesce(max_m, 9999), min_m) as integer) as snow_intensity_level,
    min_m,
    max_m,
    label as snow_intensity_label
from {{ ref('snow_intensity') }}
