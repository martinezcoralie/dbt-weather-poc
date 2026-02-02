{% docs doc_dim_stations %}

# Dimension `dim_stations`

This dimension provides a simplified, stable view of weather stations:

- technical station id (`station_id`);
- readable name (`station_name`) for BI use;
- geographic coordinates (`latitude`, `longitude`);
- altitude.

## Role in the data model

`dim_stations` is mainly used to:

- show readable labels in the dashboard (instead of raw codes);
- place stations on a map using coordinates;

In this project, the dimension is consumed by `agg_station_latest` to expose
name and coordinates in the dashboard.

Quality checks (latitude/longitude/altitude ranges, station uniqueness, etc.)
are applied upstream in the staging model `stg_stations`. The dimension then
projects only the columns needed for analytics.

## Change frequency

The Météo-France station reference changes slowly over time. This is a
low-change dimension used as a reference table.

{% enddocs %}
