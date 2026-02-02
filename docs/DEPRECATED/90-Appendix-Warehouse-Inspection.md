# Annexe — Inspection du warehouse DuckDB

Ces commandes Make permettent d’inspecter rapidement le contenu du warehouse DuckDB sans ouvrir manuellement la CLI.

Le paramètre `TABLE` attend un nom complet au format `schema.table` (ex. `raw.stations`).

## Lister les tables

```bash
make dwh-tables
```

## Infos colonnes

```bash
make dwh-table-info TABLE=raw.stations
```

## Dimensions (row count / column count)

```bash
make dwh-table-shape TABLE=raw.stations
```

## Échantillon

```bash
make dwh-table-sample TABLE=raw.stations
```

## Résumé complet

```bash
make dwh-table TABLE=raw.stations
```

Ce dernier raccourci combine : shape, info colonnes et sample.
