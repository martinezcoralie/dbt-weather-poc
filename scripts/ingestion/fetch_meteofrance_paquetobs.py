#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client fetch-only pour l'API Météo-France DPPaquetObs (Paquet Observations).

Fonctionnalités :
- /liste-stations (CSV)
- /paquet/infrahoraire-6m (JSON)
- /paquet/horaire (GeoJSON)

Dépendances : requests, pandas, python-dotenv
"""

from __future__ import annotations

import argparse
import io
import os
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #

BASE_URL: str = "https://public-api.meteofrance.fr/public/DPPaquetObs/v1"
USER_AGENT: str = "dbt-weather-poc"
TIMEOUT_S: int = 60

ENDPOINTS = {
    "stations": f"{BASE_URL}/liste-stations",
    "6m": f"{BASE_URL}/paquet/infrahoraire-6m",
    "hourly": f"{BASE_URL}/paquet/horaire",
}

# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #

def _cast_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Cast en datetime (UTC) les colonnes temps existantes."""
    for col in ("validity_time", "reference_time", "insert_time"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def _require_env(var_name: str) -> str:
    """Récupère une variable d'environnement (après chargement .env) ou lève."""
    load_dotenv()
    value = os.getenv(var_name, "").strip()
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante : {var_name}")
    return value


# --------------------------------------------------------------------------- #
# Session HTTP
# --------------------------------------------------------------------------- #

def open_session_paquetobs(apikey: Optional[str] = None) -> requests.Session:
    """Crée une session HTTP authentifiée (header `apikey`)."""
    token = apikey or _require_env("METEOFRANCE_TOKEN")
    s = requests.Session()
    s.headers.update(
        {
            "accept": "*/*",
            "apikey": token,
            "User-Agent": USER_AGENT,
        }
    )
    return s


# --------------------------------------------------------------------------- #
# Validations
# --------------------------------------------------------------------------- #

def validate_station_id(station_id: str) -> str:
    """Valide/normalise un id_station (8 chiffres, zéros initiaux conservés)."""
    sid = str(station_id).strip()
    if len(sid) != 8 or not sid.isdigit():
        raise ValueError("`id_station` doit contenir exactement 8 chiffres (zéros initiaux inclus).")
    return sid


def normalize_dept_code(dept: str) -> str:
    """Normalise le code département."""
    d = str(dept).strip().upper()
    return d


# --------------------------------------------------------------------------- #
# Fetchers
# --------------------------------------------------------------------------- #

def fetch_stations(session: requests.Session) -> pd.DataFrame:
    """Récupère la liste des stations (CSV)."""
    resp = session.get(ENDPOINTS["stations"], timeout=TIMEOUT_S)
    resp.raise_for_status()
    return pd.read_csv(io.StringIO(resp.text), dtype=str, low_memory=False)


def fetch_6m_for_station(session: requests.Session, station_id: str) -> pd.DataFrame:
    """Récupère le paquet infra-horaire 6 min (24h) pour une station (JSON)."""
    sid = validate_station_id(station_id)
    resp = session.get(
        ENDPOINTS["6m"],
        params={"id_station": sid, "format": "json"},
        timeout=TIMEOUT_S,
    )
    resp.raise_for_status()

    df = pd.json_normalize(resp.json())
    return _cast_timestamps(df)


def fetch_hourly_for_dept(session: requests.Session, dept: str) -> pd.DataFrame:
    """Récupère les observations horaires (24h) d’un département (GeoJSON).

    Retourne une DataFrame aplatie :
    - propriétés GeoJSON (préfixe `properties.` retiré)
    - colonnes `lon` et `lat` extraites depuis `geometry.coordinates`
    - colonne `dept_code` ajoutée
    """
    dept_code = normalize_dept_code(dept)
    resp = session.get(
        ENDPOINTS["hourly"],
        params={"id-departement": dept_code, "format": "geojson"},
        timeout=TIMEOUT_S,
    )
    resp.raise_for_status()

    payload = resp.json()

    # GeoJSON classique : on privilégie le tableau des features s’il existe
    if isinstance(payload, dict) and "features" in payload and isinstance(payload["features"], list):
        df = pd.json_normalize(payload["features"])
    else:
        df = pd.json_normalize(payload)

    # lon/lat depuis geometry.coordinates (liste [lon, lat])
    if "geometry.coordinates" in df.columns:
        coords = df["geometry.coordinates"]
        df["lon"] = coords.apply(lambda xy: xy[0] if isinstance(xy, (list, tuple)) and len(xy) > 0 else None)
        df["lat"] = coords.apply(lambda xy: xy[1] if isinstance(xy, (list, tuple)) and len(xy) > 1 else None)

    # Colonnes plus lisibles (on enlève le préfixe properties.)
    df.columns = [c.replace("properties.", "") for c in df.columns]

    df["dept_code"] = dept_code

    return _cast_timestamps(df)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Client fetch-only Météo-France DPPaquetObs")
    ap.add_argument(
        "--list-stations",
        action="store_true",
        help="Affiche un extrait de /liste-stations (CSV).",
    )
    ap.add_argument(
        "--station",
        type=str,
        metavar="ID_STATION_8C",
        help="Identifiant station (8 chiffres) pour /paquet/infrahoraire-6m (24h).",
    )
    ap.add_argument(
        "--dept",
        type=str,
        metavar="CODE_DEPT",
        help="Code département pour /paquet/horaire (ex. '09', '75', '2A', '2B').",
    )
    ap.add_argument(
        "--head",
        type=int,
        default=5,
        help="Nombre de lignes à afficher (par défaut: 5).",
    )
    return ap


def main() -> None:
    ap = _build_arg_parser()
    args = ap.parse_args()

    if not (args.list_stations or args.station or args.dept):
        ap.error("Spécifiez au moins une action : --list-stations, --station 01014002, et/ou --dept 09")

    session = open_session_paquetobs()

    if args.list_stations:
        df_st = fetch_stations(session)
        print(df_st.head(args.head).to_string(index=False))
        print(f"\nStations : {len(df_st):,}")

    if args.station:
        df_6m = fetch_6m_for_station(session, args.station)
        print(df_6m.head(args.head).to_string(index=False))
        print(f"\nObservations 6m pour {args.station} : {len(df_6m):,}")

    if args.dept:
        df_hr = fetch_hourly_for_dept(session, args.dept)
        print(df_hr.head(args.head).to_string(index=False))
        print(f"\nObservations horaires pour le département {normalize_dept_code(args.dept)} : {len(df_hr):,}")


if __name__ == "__main__":
    main()
