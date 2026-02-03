{% docs doc_dim_temp_intensity %}

# dim_temp_intensity

BI interpretation of 24h rolling average temperature (C), derived from the
`temp_intensity` seed. Joined on `fct_obs_hourly.temp_24h_c` to produce 24h
intensity fields.

**Grain**: 1 row = 1 intensity level
**Use**: classify 24h temperature into business categories.

{% enddocs %}
