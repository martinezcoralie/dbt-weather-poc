import pydeck as pdk
import streamlit as st

from champions import compute_champions, metric_card
from data import load_latest_station_metrics, load_station_list
from layers import build_map_layers, compute_view_state


def main() -> None:
    st.set_page_config(page_title="Météo – Observations horaires", layout="wide")
    st.title("Observations météo – marts DBT")

    stations = load_station_list()
    latest_metrics = load_latest_station_metrics()

    st.subheader("Les champions (dernières 24h)")
    if latest_metrics.empty:
        st.info("Aucune donnée disponible pour calculer les champions.")
        return

    champs = compute_champions(latest_metrics)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Plus doux", champs.warm_value, champs.warm_names, "#eba625")
    with c2:
        metric_card("Plus froid", champs.cold_value, champs.cold_names, "#0ea5e9")
    with c3:
        metric_card("Au sec (24h)", champs.dry_value, champs.dry_names, "#22c55e")
    with c4:
        metric_card("Neige (24h)", champs.snow_value, champs.snow_names, "#f97316")
    with c5:
        metric_card("Plus arrosé (24h)", champs.wet_value, champs.wet_names, "#a855f7")

    st.subheader("Carte des stations")
    view_state = compute_view_state(stations)
    layers = build_map_layers(stations, champs)
    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"text": "{station_name}\n{status}\n(lat: {lat}, lon: {lon})"},
        )
    )


if __name__ == "__main__":
    main()
