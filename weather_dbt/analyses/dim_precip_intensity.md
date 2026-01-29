{% docs doc_dim_precip_intensity %}

# dim_precip_intensity

Dimension d'interpretation BI des cumuls de precipitations sur 24h, derivee du
seed `precip_intensity` (plages en mm et libelles). Jointee sur
`fct_obs_hourly.precip_24h_mm` pour produire les champs d'intensite 24h.

**Grain** : 1 ligne = 1 niveau d'intensite
**Usage** : classer les cumuls 24h en categories metier pour la BI.

{% enddocs %}
