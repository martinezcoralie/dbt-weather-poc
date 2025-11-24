{% docs sources_doc %}

# Schéma `raw` – Sources Météo-France

Le schéma **raw** contient les données exactement telles qu’elles proviennent de l’API Météo-France, *sans transformation* autre que l’enrichissement minimal d’ingestion (horodatage, département).
Il constitue la base des étapes de staging dans dbt, où sont appliqués typage, nettoyage, normalisation et contrôles.

{% enddocs %}
