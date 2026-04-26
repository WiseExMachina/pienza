import pandas as pd
from google.cloud import storage
from io import BytesIO
import os
import streamlit as st
import json
import torch
import torch.nn as nn
import math

# --- 1. HYGIENE & CONFIG ---
# Eliminamos transformers porque ya no cargamos a la bestia de 110M de parámetros
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".streamlit/service-account.json"

# ==========================================
# GCP CONNECTIVITY UTILS
# ==========================================

@st.cache_data(show_spinner="Decrypting GCP Telemetry...")
def fetch_parquet_from_gcp(bucket_name: str, file_name: str) -> pd.DataFrame:
    """
    Fetches a Parquet file securely from a GCP bucket.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        parquet_bytes = blob.download_as_bytes()
        return pd.read_parquet(BytesIO(parquet_bytes))
    except Exception as e:
        st.error(f"Failed to connect to GCP Vault: {e}")
        return pd.DataFrame()

def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
    """
    Downloads physical ML artifacts (.pth, .json) to local /tmp storage.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
    except Exception as e:
        st.error(f"Failed to download {source_blob_name} from GCP: {e}")
        raise e

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
            d_model=d_model, nhead=nhead, dim_feedforward=256, dropout=dropout, batch_first=True
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

# ==========================================
# RESOURCE LOADERS (The Single Source of Truth)
# ==========================================

@st.cache_resource(show_spinner="Initializing O(1) miniBabel Engine...")
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
        
    # Inicialización del modelo (Ajustado a los hiperparámetros de entrenamiento)
    model = ZoneClassifierTransformer(
        vocab_size=len(token_to_idx), 
        num_classes=len(idx_to_zone),
        d_model=256,
        nhead=8
    )
    model.load_state_dict(torch.load(babel_path, map_location="cpu"))
    model.eval()
    
    return model, token_to_idx, idx_to_zone