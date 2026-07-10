"""Data literals and pure helpers used by 0008_The_Quest_to_O1_NLP.py (Layer 1 extraction)."""

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.gcp_client import fetch_bytes_from_gcs


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


# Shared loader for 260702_minibabel_holdout_audit.parquet — Streamlit renders
# every tab panel's content on each rerun (they're just hidden via CSS, not
# lazily skipped), so P1/P2/P3 were each fetching + parsing this same parquet
# under their own differently-named @st.cache_data function, tripling the
# work. One shared cache entry now serves all three tabs.
@st.cache_data(show_spinner=False)
def load_holdout_audit():
    """Fetches and parses the miniBabel holdout-audit parquet from GCS."""
    from io import BytesIO
    raw = fetch_bytes_from_gcs("pienza-streamlit", "260702_minibabel_holdout_audit.parquet")
    return pd.read_parquet(BytesIO(raw))


@st.cache_data(show_spinner=False)
def load_zone_map_template() -> str:
    """Reads the Model Audit zone-map HTML template, inlining its zone-paths JS."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    html = (assets_dir / "model_audit_map.html").read_text(encoding="utf-8")
    js = (assets_dir / "zone-paths.js").read_text(encoding="utf-8")
    return html.replace(
        '<script src="./zone-paths.js"></script>',
        f'<script>{js}</script>',
    )


@st.cache_data(show_spinner=False)
def load_latency_map_template() -> str:
    """Reads the Latency Test zone-map HTML template, inlining its zone-paths JS."""
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    html = (assets_dir / "latency_test_map.html").read_text(encoding="utf-8")
    js = (assets_dir / "zone-paths.js").read_text(encoding="utf-8")
    return html.replace(
        '<script src="./zone-paths.js"></script>',
        f'<script>{js}</script>',
    )
