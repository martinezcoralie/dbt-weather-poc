-- macros/weather_features.sql
{# Secteur de vent sur 8 points cardinaux #}
{% macro wind_sector(dir_deg) -%}
  case
    when {{ dir_deg }} is null then null
    when {{ dir_deg }} >= 337.5 or {{ dir_deg }} < 22.5  then 'N'
    when {{ dir_deg }} < 67.5  then 'NE'
    when {{ dir_deg }} < 112.5 then 'E'
    when {{ dir_deg }} < 157.5 then 'SE'
    when {{ dir_deg }} < 202.5 then 'S'
    when {{ dir_deg }} < 247.5 then 'SW'
    when {{ dir_deg }} < 292.5 then 'W'
    else 'NW'
  end
{%- endmacro %}

{# Visibilité -> catégories #}
{% macro visibility_category(visibility_m) -%}
  case
    when {{ visibility_m }} is null then null
    when {{ visibility_m }} < 200 then 'dense_fog'
    when {{ visibility_m }} < 1000 then 'fog'
    when {{ visibility_m }} < 5000 then 'haze'
    else 'good'
  end
{%- endmacro %}

{# Drapeaux simples #}
{% macro freezing_flag(temp_c) -%} case when {{ temp_c }} <= 0 then 1 end {%- endmacro %}
{% macro precip_flag(precip_mm) -%} case when {{ precip_mm }} > 0 then 1 end {%- endmacro %}
{% macro snow_on_ground_flag(snow_depth_m) -%}
  case when {{ snow_depth_m }} is not null and {{ snow_depth_m }} > 0 then 1 end
{%- endmacro %}