{% docs doc_dim_beaufort %}

# dim_beaufort

Simplified Beaufort scale (5 grouped levels) with business labels and min/max
wind speed in m/s. Joined to `fct_obs_hourly` on wind speed.

**Grain**: 1 row = 1 simplified Beaufort level (1 to 5)
**Use**: provide a readable Beaufort level for marts and the dashboard via
`fct_obs_hourly`.

{% enddocs %}
