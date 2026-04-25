import streamlit as st
import time
import regex as re
import unicodedata
import torch
import pandas as pd
import pydeck as pdk
import json
import random
import os

from utils.gcp_client import load_fast_assets, load_heavy_assets

# ==============================================================================
# 1. PRE-PROCESSING & UTILS
# ==============================================================================
def standardize_mexico_city_address(text):
    if not isinstance(text, str) or text.lower() in ['null', 'n/a']:
        return "unknown_address"
    t = text.lower()
    t = "".join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
    t = re.sub(r'\s*\S+\s*/.*$', '', t)
    t = t.replace('sante fe', 'santa fe').replace('sta fe', 'santa fe').replace('aicm', 'aeropuerto')
    t = re.sub(r'\b(av|ave|avenida|av\.|av_)\b', 'av', t)
    t = re.sub(r'\b(cll|calle|cll\.|cl\.)\b', 'calle', t)
    t = re.sub(r'\b(pº|p de|paseo de|pso|p\.º)\b', 'paseo', t)
    t = re.sub(r'\b(\d{5})\b', r'cp\1', t)
    for _ in range(3):
        t = re.sub(r'(\b\p{L}+(?:_\p{L}+|_\d+)*)\s+(\d{1,4}|norte|sur|este|oeste|poniente|oriente)\b', r'\1_\2', t)
    t = re.sub(r'[^a-z0-9áéíóúüñ_\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

@st.cache_data
def load_spatial_assets():
    geojson_path = "assets/poly.geojson"
    h3_path = "assets/260424_NLP_h3_machine_clusters.csv"
    holdout_path = "assets/260424_NLP_holdout_test_set.csv"
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    df_h3 = pd.read_csv(h3_path)
    df_holdout_raw = pd.read_csv(holdout_path)
    zonas_muertas = ['interlomas_magnocentro', 'san_miguel_chapultepec']
    df_holdout = df_holdout_raw[~df_holdout_raw['true_zone_name'].isin(zonas_muertas)].copy()
    return geojson_data, df_h3, df_holdout

# ==============================================================================
# 2. THE AUDIT ENGINE (HITS & MISSES)
# ==============================================================================
def run_tournament_audit(df_subset, model, token_to_idx, idx_to_zone):
    """Analiza una muestra del holdout para identificar los Top 5 Hits y Misses."""
    results = []
    zombie_mapper = {
        'cruce_echanove': 'carretera_al_olivo__carretera_libre__cruce_echanove__vistahermosa',
        'santa_fe_patio': 'santa_fe_quintana__sante_fe_patio',
        'vialidad_de_la_barranca': 'ave_club_de_golf_lomas__interlomas_magnocentro__vialidad_de_la_barranca',
        'terminal_1_aicm': 'aicm_aeropuerto', 'terminal_2_aicm': 'aicm_aeropuerto'
    }

    for _, row in df_subset.iterrows():
        clean_text = standardize_mexico_city_address(row['raw_address'])
        tokens = clean_text.split()
        indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
        indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
        tensor_in = torch.tensor(indices, dtype=torch.long).unsqueeze(0)
        
        with torch.no_grad():
            logits = model(tensor_in)
            probs = torch.softmax(logits, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
        
        raw_pred = idx_to_zone.get(str(pred_idx.item()), 'Unknown')
        final_pred = zombie_mapper.get(raw_pred, raw_pred)
        
        is_hit = (final_pred == row['true_zone_name'])
        results.append({
            'address': row['raw_address'],
            'true': row['true_zone_name'],
            'pred': final_pred,
            'conf': conf.item(),
            'status': '✅ HIT' if is_hit else '❌ MISS'
        })
    
    df_res = pd.DataFrame(results)
    hits = df_res[df_res['status'] == '✅ HIT'].sort_values('conf', ascending=False).head(5)
    misses = df_res[df_res['status'] == '❌ MISS'].sort_values('conf', ascending=False).head(5)
    return hits, misses

# ==============================================================================
# 3. INTERFACE
# ==============================================================================
st.set_page_config(page_title="Phase 6: O(1) Tournament", page_icon="🏎️", layout="wide")
st.title("⚡ The O(1) Engine Room: Tournament Edition")

try:
    minibabel, token_to_idx, idx_to_zone = load_fast_assets()
    minibeto, beto_tokenizer = load_heavy_assets(num_classes=len(idx_to_zone))
    geojson_data, df_h3, df_holdout = load_spatial_assets()
    st.success("✅ Neural Architectures & Spatial Sovereign Mesh Synced.")
except Exception as e:
    st.error(f"🔴 Load Failure: {e}")
    st.stop()

# --- SECTION 1: GLOBAL AUDIT (Hall of Fame & Shame) ---
st.header("🏆 The Tournament Highlights")
st.markdown("A look at how **miniBabel** performs across a cross-section of the holdout set.")

if st.button("📊 Run Global Audit (Sample 50)"):
    # Tomamos una muestra aleatoria para el audit (para no alentar el dashboard)
    df_audit_sample = df_holdout.sample(50)
    hits, misses = run_tournament_audit(df_audit_sample, minibabel, token_to_idx, idx_to_zone)
    
    col_h, col_m = st.columns(2)
    with col_h:
        st.subheader("Top 5 Performance Hits")
        st.dataframe(hits[['address', 'true', 'conf']], use_container_width=True)
    with col_m:
        st.subheader("Top 5 Toughest Misses")
        st.dataframe(misses[['address', 'true', 'pred', 'conf']], use_container_width=True)

st.divider()

# --- SECTION 2: LIVE INFERENCE PIPELINE ---
st.header("🎲 Live In-Situ Testing")
col_btn, col_info = st.columns([1, 3])
with col_btn:
    trigger = st.button("Generate Random Sample", type="primary", use_container_width=True)

if 'current_sample' not in st.session_state or trigger:
    st.session_state['current_sample'] = df_holdout.sample(1).iloc[0]

sample = st.session_state['current_sample']
st.info(f"**Input:** `{sample['raw_address']}` | **Ground Truth:** `{sample['true_zone_name']}`")

# Run Pipeline
clean_text = standardize_mexico_city_address(sample['raw_address'])

# Babel Prediction
start = time.perf_counter()
tokens = clean_text.split()
indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
with torch.no_grad():
    logits = minibabel(torch.tensor(indices).unsqueeze(0))
    conf_babel, pred_idx = torch.max(torch.softmax(logits, dim=1), dim=1)
babel_pred = idx_to_zone.get(str(pred_idx.item()), 'Unknown')
babel_lat = (time.perf_counter() - start) * 1000

# Metric Display
c1, c2, c3 = st.columns(3)
c1.metric("G-Maps Latency", "420 ms (Est.)")
c2.metric("miniBETO Latency", "38 ms (Est.)")
c3.metric("miniBabel Latency", f"{babel_lat:.1f} ms", delta="O(1) Speed")

# --- SECTION 3: SPATIAL TWIN ---
st.subheader("🗺️ Spatial Resolution")
zombie_mapper = {'cruce_echanove': 'carretera_al_olivo__carretera_libre__cruce_echanove__vistahermosa', 'terminal_1_aicm': 'aicm_aeropuerto', 'terminal_2_aicm': 'aicm_aeropuerto'}
final_zone = zombie_mapper.get(babel_pred, babel_pred)

layers = []
# Polygons
feats = [f for f in geojson_data['features'] if f['properties'].get('Name') == final_zone]
if feats:
    layers.append(pdk.Layer("GeoJsonLayer", {"type": "FeatureCollection", "features": feats}, filled=True, get_fill_color="[33, 145, 140, 160]"))
# H3
h3_data = df_h3[df_h3['final_zone_name'] == final_zone]
if not h3_data.empty:
    layers.append(pdk.Layer("H3HexagonLayer", h3_data, get_hexagon="h3_index", get_fill_color="[253, 231, 37, 180]"))

st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=pdk.ViewState(latitude=19.42, longitude=-99.17, zoom=10.5, pitch=0), map_style="mapbox://styles/mapbox/dark-v10"))