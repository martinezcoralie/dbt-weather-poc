# 📚 Documentation dbt

Une fois les modèles exécutés (`make dbt-build` ou `make dbt-rebuild`), on peut générer et explorer la documentation dbt (modèles, sources, tests, lineage).

## Générer la documentation

```bash
make dbt-docs-generate
```

Cela crée les fichiers HTML/JSON de documentation dans le dossier `target/`.

## Servir la documentation en local

```bash
make dbt-docs-serve
```

Puis ouvrir le navigateur sur :

* http://localhost:8080

On y retrouve :

* la liste des sources et modèles (staging, intermediate, marts) ;
* les descriptions de tables et de colonnes définies dans les fichiers YAML ;
* les tests associés ;
* le **graph de lineage** permettant de visualiser le flux `raw → staging → intermediate → marts`. Accessible via le bouton « Lineage » en bas à droite du panneau dbt Docs : <img src="images/lineage-graph-icon.png" width="50">
