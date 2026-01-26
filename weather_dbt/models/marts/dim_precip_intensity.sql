{{ config(materialized='table') }}

select
    cast(row_number() over (order by coalesce(max_mm, 9999), min_mm) as integer) as intensity_level,
    {{ safe_double('min_mm') }} as min_mm,
    {{ safe_double('max_mm') }} as max_mm,
    label as intensity_label
from {{ ref('precip_intensity') }}
