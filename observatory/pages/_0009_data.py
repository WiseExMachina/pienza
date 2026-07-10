"""Data literals and pure helpers used by 0009_Generative_Moonshots:_pienza_big.py (Layer 1 extraction)."""

import base64
from pathlib import Path

import streamlit as st


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()
