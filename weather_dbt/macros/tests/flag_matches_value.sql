{% test precip_flag_matches_value(model, column_name, value_column) %}
select *
from {{ model }}
where {{ column_name }} = 0
  and {{ value_column }} > 0
{% endtest %}

{% test snow_flag_matches_value(model, column_name, value_column) %}
select *
from {{ model }}
where {{ column_name }} = 0
  and {{ value_column }} > 0
{% endtest %}

{% test freezing_flag_matches_value(model, column_name, value_column) %}
select *
from {{ model }}
where {{ column_name }} = 0
  and {{ value_column }} <= 0
{% endtest %}
