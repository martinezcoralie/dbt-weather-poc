-- macros/timeseries.sql
{# Rolling sum sur fenêtre temporelle (X heures)
   col_precip: nom de colonne (string), ts_col: timestamp, part_col: partition (ex: station_id) #}
{% macro rolling_sum_hours(col_expr, ts_col, part_col, hours) -%}
  sum({{ col_expr }}) over (
    partition by {{ part_col }}
    order by {{ ts_col }}
    range between interval {{ hours }} hour preceding and current row
  )
{%- endmacro %}

{# Rolling avg sur fenêtre temporelle (X heures)
   col_precip: nom de colonne (string), ts_col: timestamp, part_col: partition (ex: station_id) #}
{% macro rolling_avg_hours(col_expr, ts_col, part_col, hours) -%}
  avg({{ col_expr }}) over (
    partition by {{ part_col }}
    order by {{ ts_col }}
    range between interval {{ hours }} hour preceding and current row
  )
{%- endmacro %}
