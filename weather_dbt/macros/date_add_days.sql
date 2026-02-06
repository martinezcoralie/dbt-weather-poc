{% macro date_add_days(date_expr, days) -%}
  {{ adapter.dispatch('date_add_days', 'weather_dbt')(date_expr, days) }}
{%- endmacro %}

{% macro duckdb__date_add_days(date_expr, days) -%}
  date_add({{ date_expr }}, interval '{{ days }} day')
{%- endmacro %}

{% macro bigquery__date_add_days(date_expr, days) -%}
  date_add({{ date_expr }}, interval {{ days }} day)
{%- endmacro %}
