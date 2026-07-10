"""Data literals and pure helpers used by 0007_Human_vs_AI_Behavioral_Cloning.py (Layer 1 extraction)."""

import base64
import json
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.bq_client import fetch_data_from_bq
from utils.gcp_client import _storage_client


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


@st.cache_data(show_spinner=False)
def load_c3_metrics():
    """Fetches the monolith and cascade metrics JSON blobs for the Cognitive Cascade comparison."""
    bucket = _storage_client().bucket("pienza-streamlit")
    mono = json.loads(bucket.blob("0508_monolith_metrics.json").download_as_text())
    casc = json.loads(bucket.blob("0509_cascade_metrics.json").download_as_text())
    return mono, casc


@st.cache_data(show_spinner=False)
def load_sim_parquet_v3():
    """Fetches the Layer 1 threshold-simulator probability parquet from GCS."""
    b = _storage_client().bucket("pienza-streamlit")
    return pd.read_parquet(BytesIO(b.blob("0509_sim_proba.parquet").download_as_bytes()))


@st.cache_data(show_spinner=False)
def load_realized_fares(ids_key: str) -> dict:
    """Fetches realized fares for a SQL-ready comma-separated list of offer IDs."""
    q = f"""
    SELECT offer_id, realized_fare
    FROM `645009831643.pienza_mini.v_mission_dossier`
    WHERE offer_id IN ({ids_key})
      AND realized_fare IS NOT NULL
    """
    df = fetch_data_from_bq(q)
    return dict(zip(df["offer_id"], df["realized_fare"]))


@st.cache_data(show_spinner=False)
def load_shap_l1():
    """Fetches the Layer 1 (nuanced_rest) SHAP values parquet from GCS."""
    return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("0509_shap_l1_nuanced.parquet").download_as_bytes()))


@st.cache_data(show_spinner=False)
def load_shap_l2():
    """Fetches the Layer 2 SHAP values parquet from GCS."""
    return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("0509_shap_l2.parquet").download_as_bytes()))


@st.cache_data(show_spinner=False)
def load_lc_l1():
    """Fetches the Layer 1 learning-curve parquet from GCS."""
    return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_learning_curve_L1.parquet").download_as_bytes()))


@st.cache_data(show_spinner=False)
def load_lc_l2():
    """Fetches the Layer 2 learning-curve parquet from GCS."""
    return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_learning_curve_L2.parquet").download_as_bytes()))


@st.cache_data(show_spinner=False)
def load_lc_spartan():
    """Fetches the Spartan-baseline learning-curve parquet from GCS."""
    return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_spartan_learning_curve.parquet").download_as_bytes()))
