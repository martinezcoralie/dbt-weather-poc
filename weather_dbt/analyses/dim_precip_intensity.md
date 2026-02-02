{% docs doc_dim_precip_intensity %}

# dim_precip_intensity

BI interpretation of 24h precipitation totals, derived from the
`precip_intensity` seed (mm ranges and labels). Joined on
`fct_obs_hourly.precip_24h_mm` to produce 24h intensity fields.

**Grain**: 1 row = 1 intensity level
**Use**: classify 24h totals into business categories for BI.

{% enddocs %}
