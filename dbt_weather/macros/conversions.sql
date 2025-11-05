-- macros/conversions.sql
{% macro kelvin_to_c(col) %} case when {{ col }} is not null then {{ col }} - 273.15 end {% endmacro %}
{% macro ms_to_kmh(col) %}   case when {{ col }} is not null then {{ col }} * 3.6 end {% endmacro %}