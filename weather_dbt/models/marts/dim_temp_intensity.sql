{{ config(materialized='table') }}

select
    cast(row_number() over (order by coalesce(max_c, 9999), min_c) as integer) as intensity_level,
    {{ safe_double('min_c') }} as min_c,
    {{ safe_double('max_c') }} as max_c,
    label as intensity_label
from {{ ref('temp_intensity') }}
