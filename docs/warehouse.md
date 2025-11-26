# 🔎 Inspection du DataWarehouse (DuckDB)

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

## Afficher toutes les infos d'une table

```bash
make dwh-table TABLE=raw.stations
```