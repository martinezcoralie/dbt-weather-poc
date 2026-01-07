#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Client fetch-only pour l'API Météo-France DPPaquetObs (Paquet Observations).

Fonctionnalités :
- /liste-stations (CSV)
- /paquet/horaire (CSV)

Dépendances : requests, pandas, python-dotenv
"""

from __future__ import annotations

import argparse
import io
import os
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Chargement de l'environnement
# --------------------------------------------------------------------------- #

# Charger .env une seule fois à l'import
load_dotenv()

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #

BASE_URL: str = "https://public-api.meteofrance.fr/public/DPPaquetObs/v1"
USER_AGENT: str = "dbt-weather-poc"

# Timeout (connect, read)
TIMEOUT: tuple[int, int] = (10, 60)

ENDPOINTS = {
    "stations": f"{BASE_URL}/liste-stations",
    "hourly": f"{BASE_URL}/paquet/horaire",
}

# --------------------------------------------------------------------------- #
# Utilitaires
# --------------------------------------------------------------------------- #


def _require_env(var_name: str) -> str:
    """Récupère une variable d'environnement (après chargement .env) ou lève."""
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
            "Accept": "text/csv",
            "apikey": token,
            "User-Agent": USER_AGENT,
        }
    )
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.8,  # exponential backoff: 0.8, 1.6, 3.2, 6.4...
        status_forcelist=[429, 502, 503, 504],
        allowed_methods={"GET"},
        raise_on_status=False,
        respect_retry_after_header=True,
      )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


# --------------------------------------------------------------------------- #
# Validations
# --------------------------------------------------------------------------- #


def normalize_dept_code(dept: str) -> str:
    """Normalise le code département."""
    return str(dept).strip().upper()


# --------------------------------------------------------------------------- #
# Fetchers
# --------------------------------------------------------------------------- #


def fetch_stations(session: requests.Session) -> pd.DataFrame:
    """Récupère la liste des stations (CSV) — RAW inchangé."""
    resp = session.get(ENDPOINTS["stations"], params={"format": "csv"}, timeout=TIMEOUT)
    resp.raise_for_status()
    # Lire depuis bytes pour éviter les surprises d'encodage
    df = pd.read_csv(io.BytesIO(resp.content), sep=";", dtype=str, low_memory=False)
    return df


def fetch_hourly_for_dept(session: requests.Session, dept: str) -> pd.DataFrame:
    """Récupère les observations horaires (24h) d’un département (CSV).

    Retourne une DataFrame RAW :
    - colonnes exactement telles que renvoyées par l'API
    - ajoute `dept_code` uniquement si absent
    """
    dept_code = normalize_dept_code(dept)
    resp = session.get(
        ENDPOINTS["hourly"],
        params={"id-departement": dept_code, "format": "csv"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    df = pd.read_csv(io.BytesIO(resp.content), sep=";", dtype=str, low_memory=False)
    df["dept_code"] = dept_code
    return df


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI parser (stations list and/or hourly by dept)."""
    ap = argparse.ArgumentParser(
        description="Client fetch-only Météo-France DPPaquetObs"
    )
    ap.add_argument(
        "--list-stations",
        action="store_true",
        help="Affiche un extrait de /liste-stations (CSV).",
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

    if not (args.list_stations or args.dept):
        ap.error("Spécifiez au moins une action : --list-stations et/ou --dept 09")

    session = open_session_paquetobs()

    if args.list_stations:
        df_st = fetch_stations(session)
        print(df_st.head(args.head).to_string(index=False))
        print(f"\nStations : {len(df_st):,}")

    if args.dept:
        df_hr = fetch_hourly_for_dept(session, args.dept)
        print(df_hr.head(args.head).to_string(index=False))
        print(
            f"\nObservations horaires pour le département {normalize_dept_code(args.dept)} : {len(df_hr):,}"
        )


if __name__ == "__main__":
    main()
