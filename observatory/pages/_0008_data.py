"""Data literals and pure helpers used by 0008_The_Quest_to_O1_NLP.py (Layer 1 extraction)."""

import base64
import json
import math
import os
from pathlib import Path

import pandas as pd
import streamlit as st
import torch
import torch.nn as nn

from utils.gcp_client import download_from_gcs, fetch_bytes_from_gcs


# ==========================================
# NEURAL ARCHITECTURE: miniBabel (Transformer)
# ==========================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class ZoneClassifierTransformer(nn.Module):
    def __init__(self, vocab_size, num_classes, d_model=256, nhead=8, num_layers=2, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=d_model * 2, dropout=dropout, batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(d_model * 2, num_classes)
        self.d_model = d_model

    def forward(self, x):
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        avg_pool = x.mean(dim=1)
        max_pool, _ = x.max(dim=1)
        fused_features = torch.cat((avg_pool, max_pool), dim=1)
        fused_features = self.dropout(fused_features)
        return self.classifier(fused_features)


@st.cache_resource(show_spinner="Initializing miniBabel...")
def load_babel_assets():
    """
    Downloads and instantiates the lightweight miniBabel model.
    """
    BUCKET_NAME = "pienza-streamlit"
    os.makedirs("/tmp/pienza_models", exist_ok=True)

    token_path = "/tmp/pienza_models/token_to_idx.json"
    zone_path = "/tmp/pienza_models/idx_to_zone.json"
    babel_path = "/tmp/pienza_models/babel.pth"

    # Descarga de artefactos
    download_from_gcs(BUCKET_NAME, "260422_token_to_idx.json", token_path)
    download_from_gcs(BUCKET_NAME, "260423__idx_to_zone_to_semantics.json", zone_path)
    download_from_gcs(BUCKET_NAME, "260422_pienza_babel_champion.pth", babel_path)

    with open(token_path, 'r', encoding='utf-8') as f:
        token_to_idx = json.load(f)
    with open(zone_path, 'r', encoding='utf-8') as f:
        idx_to_zone = json.load(f)

    # Model initialization (matches the training-time hyperparameters)
    model = ZoneClassifierTransformer(
        vocab_size=len(token_to_idx),
        num_classes=len(idx_to_zone),
        d_model=256,
        nhead=8
    )
    model.load_state_dict(torch.load(babel_path, map_location="cpu", weights_only=True))
    model.eval()

    return model, token_to_idx, idx_to_zone


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
