-- macros/timeseries.sql
{# Rolling sum sur fenêtre temporelle (X heures)
   col_precip: nom de colonne (string), ts_col: timestamp, part_col: partition (ex: station_id) #}
{% macro rolling_sum_hours(col_expr, ts_col, part_col, hours) -%}
  {{ adapter.dispatch('rolling_sum_hours', 'weather_dbt')(col_expr, ts_col, part_col, hours) }}
{%- endmacro %}

{# Rolling avg sur fenêtre temporelle (X heures)
   col_precip: nom de colonne (string), ts_col: timestamp, part_col: partition (ex: station_id) #}
{% macro rolling_avg_hours(col_expr, ts_col, part_col, hours) -%}
  {{ adapter.dispatch('rolling_avg_hours', 'weather_dbt')(col_expr, ts_col, part_col, hours) }}
{%- endmacro %}

{# DuckDB: supporte RANGE avec INTERVAL sur un ORDER BY timestamp #}
{% macro duckdb__rolling_sum_hours(col_expr, ts_col, part_col, hours) -%}
  sum({{ col_expr }}) over (
    partition by {{ part_col }}
    order by {{ ts_col }}
    range between interval {{ hours }} hour preceding and current row
  )
{%- endmacro %}

{# DuckDB: supporte RANGE avec INTERVAL sur un ORDER BY timestamp #}
{% macro duckdb__rolling_avg_hours(col_expr, ts_col, part_col, hours) -%}
  avg({{ col_expr }}) over (
    partition by {{ part_col }}
    order by {{ ts_col }}
    range between interval {{ hours }} hour preceding and current row
  )
{%- endmacro %}

{# BigQuery: RANGE exige un ORDER BY numerique -> secondes unix #}
{% macro bigquery__rolling_sum_hours(col_expr, ts_col, part_col, hours) -%}
  sum({{ col_expr }}) over (
    partition by {{ part_col }}
    order by unix_seconds(cast({{ ts_col }} as timestamp))
    range between {{ hours * 3600 }} preceding and current row
  )
{%- endmacro %}

{# BigQuery: RANGE exige un ORDER BY numerique -> secondes unix #}
{% macro bigquery__rolling_avg_hours(col_expr, ts_col, part_col, hours) -%}
  avg({{ col_expr }}) over (
    partition by {{ part_col }}
    order by unix_seconds(cast({{ ts_col }} as timestamp))
    range between {{ hours * 3600 }} preceding and current row
  )
{%- endmacro %}
