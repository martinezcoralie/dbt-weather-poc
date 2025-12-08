import pandas as pd
import pydeck as pdk

from champions import ChampionSet


HOT_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f525.png"
COLD_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1F9CA.png"
RAIN_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1F4A7.png"
SNOW_ICON_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/2744.png"


def compute_view_state(stations: pd.DataFrame) -> pdk.ViewState:
    """Center map on barycenter of stations (fallback to France-ish)."""
    center_lat = stations["latitude"].mean() if not stations.empty else 46.5
    center_lon = stations["longitude"].mean() if not stations.empty else 2.5
    return pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=8)


def _base_layer(stations: pd.DataFrame) -> pdk.Layer:
    stations_map = stations.rename(columns={"longitude": "lon", "latitude": "lat"}).assign(
        status="Station"
    )
    return pdk.Layer(
        "ScatterplotLayer",
        data=stations_map,
        get_position="[lon, lat]",
        get_radius=1000,
        get_color=[128, 128, 128],
        pickable=True,
    )


def _icon_layer(data: pd.DataFrame, icon_url: str, size) -> pdk.Layer | None:
    if data is None or data.empty:
        return None

    df = data.copy()
    df["icon_data"] = [
        {"url": icon_url, "width": 242, "height": 242, "anchorY": 242}
    ] * len(df)

    return pdk.Layer(
        "IconLayer",
        data=df,
        get_icon="icon_data",
        get_size=size,
        size_scale=1,
        get_position=["lon", "lat"],
        pickable=True,
        billboard=True,
    )


def build_map_layers(stations: pd.DataFrame, champs: ChampionSet) -> list[pdk.Layer]:
    """Build all map layers (base + champions)."""
    warm_layer = _icon_layer(champs.warm_points, HOT_ICON_URL, 20)
    cold_layer = _icon_layer(champs.cold_points, COLD_ICON_URL, 20)
    snow_layer = _icon_layer(champs.snow_points, SNOW_ICON_URL, "icon_size")
    wet_layer = _icon_layer(champs.wet_points, RAIN_ICON_URL, "icon_size")

    layers = [
        _base_layer(stations),
        warm_layer,
        cold_layer,
        snow_layer,
        wet_layer,
    ]
    return [l for l in layers if l is not None]
