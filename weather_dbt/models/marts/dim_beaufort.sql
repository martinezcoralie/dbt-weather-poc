{{ config(materialized='table') }}

with grouped as (
    select
        simple_level        as beaufort_level,
        simple_label        as beaufort_label,
        min(ms_min)         as ms_min,
        max(ms_max)         as ms_max
    from {{ ref('beaufort_scale') }}
    group by 1, 2
)

select * from grouped
