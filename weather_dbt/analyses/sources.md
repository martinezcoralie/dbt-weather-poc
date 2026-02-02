{% docs sources_doc %}

# `raw` schema – Météo-France sources

The **raw** schema contains data exactly as received from the Météo-France API,
*without transformation* beyond minimal ingestion enrichment (loading timestamp). It is the base for dbt staging, where typing, cleaning,
normalization, and checks are applied.

{% enddocs %}
