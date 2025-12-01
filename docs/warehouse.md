# 🔎 Inspection du DataWarehouse (DuckDB)


Ces commandes Make permettent d’inspecter rapidement le contenu du warehouse DuckDB
sans ouvrir manuellement la CLI.

Le paramètre `TABLE` attend un nom complet de table au format `schema.table` (ex. `raw.stations`).

---

## Lister l'ensemble des tables

```bash
make dwh-tables
```

## Afficher les colonnes d'une table

```bash
make dwh-table-info TABLE=raw.stations
```

## Afficher un extrait d'une table

```bash
make dwh-table-sample TABLE=raw.stations
```

## Afficher les dimensions d'une table

```bash
make dwh-table-shape TABLE=raw.stations
```

## Afficher un résumé complet d'une table

```bash
make dwh-table TABLE=raw.stations
```

Ce dernier raccourci combine : shape, info colonnes et sample.