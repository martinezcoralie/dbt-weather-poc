# dbt Docs & Lineage

Après exécution des modèles (`make dbt-build` ou `make dbt-rebuild`), dbt peut générer une documentation HTML permettant d’explorer :

- modèles, sources, tests et colonnes
- contrats de schéma
- **lineage graph** (raw → staging → intermediate → marts)
- exposure du dashboard

## Générer et servir la documentation

```bash
make dbt-docs-generate
make dbt-docs-serve
# http://localhost:8080
```

Raccourci :

```bash
make dbt-docs
```

## Ce qu’il est utile de regarder

- Fiche modèle : descriptions, colonnes, tests et contraintes.
- Lineage : chaînage complet jusqu’aux marts consommées.
- Exposure : périmètre minimal pour (re)jouer uniquement ce qui alimente le dashboard.

---

## Aperçu de la documentation dbt

### Navigation dans dbt Docs

L’interface permet d’explorer facilement l’ensemble des modèles, sources, tests et descriptions.

<img src="images/dbt_sidebar.png" width="250" />

### Fiche d’un modèle analytique (`fct_obs_hourly`)

Chaque modèle documenté expose sa description, ses colonnes, ses contraintes et ses tests associés.

<img src="images/dbt_table_extract.png" width="600" />


### Lineage complet (`raw → staging → intermediate → marts`)

Le graphe de dépendances (lineage) permet de visualiser le flux de transformation de bout en bout, jusqu’à la consommation BI.

<img src="images/lineage-graph.png" width="800" />

Le lineage est accessible via le bouton « Lineage » en bas à droite du panneau dbt Docs : <img src="images/lineage-graph-icon.png" width="50" />