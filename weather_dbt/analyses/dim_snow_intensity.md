{% docs doc_dim_snow_intensity %}

# dim_snow_intensity

BI interpretation of 24h snow depth totals (m), from the `snow_intensity` seed
with ordered levels and labels. Joined on `fct_obs_hourly.snow_24h_m` to produce
24h intensity fields.

**Grain**: 1 row = 1 intensity level
**Use**: classify 24h snow totals for BI.

{% enddocs %}
