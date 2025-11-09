-- macros/conversions.sql

{% macro kelvin_to_c(col) -%}
  case when {{ col }} is not null then {{ col }} - 273.15 end
{%- endmacro %}

{% macro kelvin_to_f(col) -%}
  case when {{ col }} is not null then ({{ col }} * 9.0/5.0) - 459.67 end
{%- endmacro %}

{% macro c_to_f(col) -%}
  case when {{ col }} is not null then ({{ col }} * 9.0/5.0) + 32.0 end
{%- endmacro %}

{% macro f_to_c(col) -%}
  case when {{ col }} is not null then ({{ col }} - 32.0) * 5.0/9.0 end
{%- endmacro %}

{% macro ms_to_kmh(col) %}   
    case when {{ col }} is not null then {{ col }} * 3.6 
end {% endmacro %}