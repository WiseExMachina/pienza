import streamlit as st
import time
import requests
import regex as re
import unicodedata
import torch
import json
import io
from google.cloud import storage
from pathlib import Path
import pandas as pd

# IMPORTAMOS SOLO LO NECESARIO (Babel)
from utils.gcp_client import load_babel_assets
from utils.bq_client import fetch_data_from_bq
from components.styles import GLOBAL_CSS
import threading as _threading

def _preload_babel():
    try:
        load_babel_assets()
    except Exception:
        pass

_threading.Thread(target=_preload_babel, daemon=True).start()


# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Phase 6: O(1) Engine Room", page_icon="⚡", layout="wide")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown("Project Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer")
        st.page_link("pages/0009_Generative_Moonshots.py", label="Generative Moonshots")
        st.markdown("---")
        st.markdown("**Archive**")
        st.page_link("pages/9001_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/9002_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/9003_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("# miniBabel: Custom NLP Transformer")
st.markdown(f"<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>A Real-Time Spatial Classifier — CDMX Address → Geographic Zone</h4>", unsafe_allow_html=True)
st.markdown("""
<div style='font-size:0.95rem;color:#64748b;line-height:1.7;max-width:860px;margin-bottom:24px;'>
While the geocoding pipeline used during the Unsupervised Phase works for offline research, it is too fragile for real-time production.
Relying on live external APIs while on the road is computationally expensive, introduces latency, and creates a critical point of failure.
<br><br>
What if geocoding could be bypassed entirely? Using a baseline of 4,000+ historically verified addresses, the routing problem was reframed as a direct Natural Language Processing task.
<b>miniBabel</b> is a custom, lightweight Transformer that learns the linguistic DNA of raw addresses to map them directly into operational zones.
By eliminating third-party APIs, it is optimized for fast, reliable, on-device (edge) execution.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 0. SESSION STATE INITIALIZATION (THE ANCHOR)
# ==========================================
if 'address_history' not in st.session_state:
    st.session_state['address_history'] = []

if 'hits_view' not in st.session_state: 
    st.session_state['hits_view'] = 'top'

if 'misses_view' not in st.session_state: 
    st.session_state['misses_view'] = 'top'

# ==========================================
# FUNCIÓN: CARGA DE ASSETS
# ==========================================
@st.cache_data
def load_production_assets():
    """Jala la malla soberana y el test set directamente de la nube y local."""
    # A. Ruta al GeoJSON Local
    geojson_path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # B. Conexión a GCS
    KEY_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    client = storage.Client.from_service_account_json(str(KEY_PATH))
    bucket = client.bucket("pienza-streamlit")
    
    def get_gcs_df(blob_name):
        blob = bucket.blob(blob_name)
        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)
        return pd.read_csv(buffer)

    # Carga del Master Mesh (H3) y Holdout
    df_h3_master = get_gcs_df("260425_h3_coalesced.csv")
    df_h3_master['h3_index'] = df_h3_master['h3_index'].astype(str)
    
    df_holdout_raw = get_gcs_df("260424_NLP_holdout_test_set.csv")
    
    # FILTRO DE SEGURIDAD
    zonas_muertas = ['interlomas_magnocentro', 'san_miguel_chapultepec']
    df_holdout = df_holdout_raw[~df_holdout_raw['true_zone_name'].isin(zonas_muertas)].copy()
    
    return geojson_data, df_h3_master, df_holdout

@st.cache_data(show_spinner="Syncing Parity Ledger from GCS...")
def load_parity_audit():
    """Descarga el Ledger de Paridad con los nombres ya resueltos."""
    try:
        KEY_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
        client = storage.Client.from_service_account_json(str(KEY_PATH))
        bucket = client.bucket("pienza-streamlit")
        blob = bucket.blob("260425_Pienza_Babel_Final_Parity_Audit.csv") 
        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)
        return pd.read_csv(buffer)
    except Exception as e:
        st.error(f"Failed to load Parity Audit: {e}")
        return pd.DataFrame()

# ==========================================
# PHASE 2: LINGUISTIC PIPELINE (Hard-Cut)
# ==========================================
def standardize_mexico_city_address(text):
    if not isinstance(text, str) or text.lower() in ['null', 'n/a']:
        return "unknown_address"
    t = text.lower()
    t = "".join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
    t = re.sub(r'\bs/n\b', '__SN__', t)
    t = re.sub(r'\s*\S+\s*/.*$', '', t)
    t = t.replace('__SN__', 's/n')
    t = t.replace('sante fe', 'santa fe').replace('sta fe', 'santa fe').replace('aicm', 'aeropuerto')
    t = re.sub(r'\b(av|ave|avenida|av\.|av_)\b', 'av', t)
    t = re.sub(r'\b(cll|calle|cll\.|cl\.)\b', 'calle', t)
    t = re.sub(r'\b(pº|p de|paseo de|pso|p\.º)\b', 'paseo', t)
    t = re.sub(r'\b(\d{5})\b', r'cp\1', t)
    for _ in range(3):
        t = re.sub(r'(\b\p{L}+(?:_\p{L}+|_\d+)*)\s+(\d{1,4}|norte|sur|este|oeste|poniente|oriente)\b', r'\1_\2', t)
    t = re.sub(r'[^a-z0-9áéíóúüñ_\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# ==========================================
# INFERENCE LOGIC (Google Maps)
# ==========================================
def get_google_maps_latency(address: str):
    api_key = st.secrets.get("GCP_API_KEY", "")
    if not api_key: return "API Key Missing", 0.0, None
    formatted_address = requests.utils.quote(f"{address}, CDMX, Mexico")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
    
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=5).json()
        latency = (time.perf_counter() - start_time) * 1000
        if response['status'] == 'OK':
            res = response['results'][0]
            coords = res['geometry']['location'] # {'lat': ..., 'lng': ...}
            return res['formatted_address'], latency, coords
        return "API Error", latency, None
    except:
        return "Network Timeout", (time.perf_counter() - start_time) * 1000, None

# ==========================================
# NUEVO: MOTOR DEL MAPA (Colócalo aquí)
# ==========================================
def render_sovereign_map(pred_name, true_name, google_coords, df_h3_master, geojson_data):
    import pydeck as pdk
    import copy

    # --- 1. NORMALIZACIÓN Y EXPLOSIÓN ---
    def norm(t):
        if not t: return ""
        t = "".join(c for c in unicodedata.normalize('NFKD', str(t).lower()) if not unicodedata.combining(c))
        return re.sub(r'[^a-z0-9]', '', t)

    def explode_and_norm(name_string):
        if not name_string: return set()
        # Divide por "__" y normaliza cada parte
        return {norm(p) for p in str(name_string).split("__")}

    true_set = explode_and_norm(true_name)
    pred_set = explode_and_norm(pred_name)
    is_hit = (norm(true_name) == norm(pred_name))

    # --- 2. CONFIGURACIÓN DE COLORES (RGBA) ---
    GHOST_POLY = [60, 60, 60, 40]       # Fondo oscuro
    GHOST_HEX  = [40, 40, 40, 30]       # Hexágonos apagados
    COLOR_HIT  = [76, 232, 215, 255]    # Teal Brillante (Hit)
    COLOR_MISS = [255, 75, 75, 255]     # Rojo Intenso (Miss)
    COLOR_GOOGLE = [255, 200, 0, 255]   # Amarillo (Pin)

    # --- 3. PROCESAR POLÍGONOS ---
    geojson_copy = copy.deepcopy(geojson_data)
    for feature in geojson_copy['features']:
        props = feature['properties']
        raw_name = props.get('zone_name') or props.get('Name') or props.get('name')
        z_name_norm = norm(raw_name)
        
        # Lógica: Si el polígono es parte del grupo objetivo, se ilumina
        if z_name_norm in true_set:
            feature['properties']['fill_color'] = COLOR_HIT if is_hit else COLOR_HIT
        elif z_name_norm in pred_set and not is_hit:
            feature['properties']['fill_color'] = COLOR_MISS
        else:
            feature['properties']['fill_color'] = GHOST_POLY

    # --- 4. PROCESAR HEXÁGONOS (H3) ---
    df_h3_copy = df_h3_master.copy()
    
    # Asegurar que h3_index sea string para evitar errores de render
    df_h3_copy['h3_index'] = df_h3_copy['h3_index'].astype(str)
    
    def get_hex_color(row_name):
        h_norm = norm(row_name)
        if h_norm in true_set: return COLOR_HIT if is_hit else COLOR_HIT
        if h_norm in pred_set and not is_hit: return COLOR_MISS
        return GHOST_HEX
            
    df_h3_copy['fill_color'] = df_h3_copy['final_zone_name'].apply(get_hex_color)

    # --- 5. CAPAS Y RENDER ---
    layers = [
        pdk.Layer(
            "GeoJsonLayer", geojson_copy, stroked=True, filled=True,
            get_line_color=[255, 255, 255, 50], line_width_min_pixels=1,
            get_fill_color="properties.fill_color",
        ),
        pdk.Layer(
            "H3HexagonLayer", df_h3_copy, get_hexagon="h3_index",
            stroked=False, filled=True, get_fill_color="fill_color",
            pickable=True
        )
    ]
    
    if google_coords:
        layers.append(pdk.Layer(
            "ScatterplotLayer", pd.DataFrame([google_coords]),
            get_position=["lng", "lat"], get_color=COLOR_GOOGLE,
            get_radius=200, pickable=True,
        ))

    view_state = pdk.ViewState(
        latitude=google_coords['lat'] if google_coords else 19.4288,
        longitude=google_coords['lng'] if google_coords else -99.1747,
        zoom=11.5, pitch=45
    )

    st.pydeck_chart(pdk.Deck(
        layers=layers, initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={"text": "Zone: {final_zone_name}"}
    ))

tab_science, tab_dashboard = st.tabs(["The Science", "Dashboard — miniBabel O(1) Engine"])

with tab_science:
    st.markdown("""
<style>
.ci-stepper { display:flex; align-items:flex-start; gap:0; margin:18px 0 6px 0; }
.ci-step {
  display:flex; flex-direction:column; align-items:center; flex:1;
  position:relative; cursor:pointer;
}
.ci-step:not(:last-child)::after {
  content:''; position:absolute; top:14px; left:calc(50% + 14px);
  width:calc(100% - 28px); height:2px; background:rgba(33,145,140,0.2); z-index:0;
}
.ci-dot {
  width:28px; height:28px; border-radius:50%;
  background:rgba(33,145,140,0.12); border:1.5px solid rgba(33,145,140,0.4);
  display:flex; align-items:center; justify-content:center;
  font-size:0.60rem; font-weight:700; color:#21918c;
  z-index:1; position:relative; flex-shrink:0;
  transition: background 0.15s, border-color 0.15s;
}
.ci-step:hover .ci-dot { background:rgba(33,145,140,0.22); border-color:#21918c; }
.ci-step-label {
  font-size:0.68rem; font-weight:600; color:#334155;
  text-align:center; margin-top:6px; line-height:1.3;
}
.ci-step-sub {
  font-size:0.60rem; color:#64748b;
  text-align:center; margin-top:2px; line-height:1.3;
}
.ci-step:hover .ci-step-label { color:#21918c; }
.ci-step.ci-active .ci-dot {
  background:#21918c !important; border-color:#21918c !important; color:#fff !important;
}
.ci-step.ci-active .ci-step-label { color:#21918c !important; font-weight:700; }
</style>
<div class="ci-stepper">
  <div class="ci-step ci-active">
    <div class="ci-dot">P1</div>
    <div class="ci-step-label">Custom miniBabel</div>
    <div class="ci-step-sub">Purpose-Built PyTorch Transformer</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P2</div>
    <div class="ci-step-label">State-of-the-Art Adaptation</div>
    <div class="ci-step-sub">BETO Fine-Tuning</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P3</div>
    <div class="ci-step-label">Model Audit</div>
    <div class="ci-step-sub">Hits &amp; Misses</div>
  </div>
</div>

<!-- P1: INTRO -->
<div style="font-size:0.95rem;color:#64748b;line-height:1.7;max-width:860px;margin:24px 0 20px;">
<b style="color:#121212;font-weight:600;font-size:0.95rem;">ZoneClassifierTransformer</b> is a custom encoder-only Transformer trained from scratch to resolve messy, human-written Mexico City dropoff addresses into one of 63 geographic zones — benchmarked live against the Google Maps Geocoding API inside the Observatory's Phase 6 diagnostic page.
</div>

<!-- P1: STAT GRID -->
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin:28px 0 8px;">
  <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
    <div style="font-size:0.72rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Vocabulary</div>
    <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">2,502</div>
    <div style="font-size:0.72rem; color:#888; margin-top:4px;">standardized tokens</div>
  </div>
  <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
    <div style="font-size:0.72rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Model Dim</div>
    <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">256</div>
    <div style="font-size:0.72rem; color:#888; margin-top:4px;">d_model · 8 heads × 2 layers</div>
  </div>
  <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
    <div style="font-size:0.72rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Zones Classified</div>
    <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">59</div>
    <div style="font-size:0.72rem; color:#888; margin-top:4px;">polygon + HDBSCAN clusters</div>
  </div>
  <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
    <div style="font-size:0.72rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Inference Latency</div>
    <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">&lt; 10ms</div>
    <div style="font-size:0.72rem; color:#888; margin-top:4px;">on-device, CPU</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── ARCHITECTURE EXPLAINER ───────────────────────────────────────────────
    _A = '#21918c'
    _XS = [20, 55, 90, 125, 160]
    _Y  = 62

    if 'arch_history' not in st.session_state:
        st.session_state['arch_history'] = []
    if 'arch_future' not in st.session_state:
        st.session_state['arch_future'] = []

    import random as _random
    from utils.gcp_client import fetch_parquet_from_gcp

    @st.cache_data(show_spinner=False)
    def _load_holdout_pool():
        from google.cloud import storage as _gcs
        from io import BytesIO as _BytesIO
        _client = _gcs.Client()
        _blob = _client.bucket("pienza-streamlit").blob("260702_minibabel_holdout_audit.parquet")
        df = pd.read_parquet(_BytesIO(_blob.download_as_bytes()))
        if df.empty:
            return pd.DataFrame()
        return df[['raw_address', 'real_zone_name']].dropna().reset_index(drop=True)

    def _fetch_random_address():
        pool = _load_holdout_pool()
        if pool.empty:
            return None, None
        row = pool.sample(1).iloc[0]
        return row['raw_address'], row['real_zone_name']

    def _run_inference(cleaned: str):
        if 'minibabel' not in st.session_state or 'token_to_idx' not in st.session_state:
            return '—', '—'
        try:
            mb = st.session_state['minibabel']
            t2i = st.session_state['token_to_idx']
            i2z = st.session_state['idx_to_zone']
            indices = [t2i.get(t, t2i.get('<unk>', 1)) for t in cleaned.split()]
            indices = indices[:30] + [t2i.get('<pad>', 0)] * max(0, 30 - len(indices))
            tensor_in = torch.tensor(indices, dtype=torch.long).unsqueeze(0)
            with torch.no_grad():
                logits = mb(tensor_in)
                probs = torch.softmax(logits, dim=1)
                conf, pred_idx = torch.max(probs, dim=1)
            zone = i2z.get(str(pred_idx.item()), 'unknown')
            return zone, f'{conf.item()*100:.0f}%'
        except Exception:
            return '—', '—'

    def _build_ex_from_address(raw: str, real_zone: str = None) -> dict:
        cleaned = standardize_mexico_city_address(raw)
        tokens_raw = cleaned.split()[:30]
        tokens = tokens_raw + ['<pad>'] * (30 - len(tokens_raw))
        soldered = tokens[0] if tokens else 'unknown'
        zone, confidence = _run_inference(cleaned)
        return {
            'ocrRaw':     f'"{raw}"',
            'ocrCleaned': cleaned,
            'ocrFixes':   'standardized via linguistic pipeline',
            'soldered':   soldered,
            'tokens':     tokens,
            'headQueries': tokens[:4],
            'headWeights': [[0.60,0.15,0.13,0.06,0.06],[0.14,0.58,0.14,0.07,0.07],[0.16,0.16,0.14,0.54,0.00],[0.16,0.16,0.52,0.08,0.08]],
            'zone': zone, 'confidence': confidence,
            'real_zone': real_zone or '—',
            'label': raw[:40] + ('…' if len(raw) > 40 else ''),
        }

    if 'arch_ex' not in st.session_state:
        addr, real_zone = _fetch_random_address()
        if addr:
            st.session_state['arch_ex'] = _build_ex_from_address(addr, real_zone)
        else:
            st.session_state['arch_ex'] = _build_ex_from_address('Paseo de la Reforma 222, Juárez, 06600 Cuauhtémoc')

    _EX = st.session_state['arch_ex']

    def _head_svg(n, query_label, weights, token_labels):
        import math as _math
        query_idx = token_labels.index(query_label) if query_label in token_labels else 0
        qx = _XS[query_idx]
        parts = []
        for i, w in enumerate(weights):
            if i == query_idx:
                bump = 10 + w * 26
                d = f"M {qx-7} {_Y-2} C {qx-15} {_Y-bump} {qx+15} {_Y-bump} {qx+7} {_Y-2}"
            else:
                x2, mid_x, mid_y = _XS[i], (qx+_XS[i])/2, _Y-26-w*46
                d = f"M {qx} {_Y} Q {mid_x} {mid_y} {x2} {_Y}"
            parts.append(f'<path d="{d}" fill="none" stroke="{_A}" stroke-width="{1+w*5:.1f}" opacity="{0.25+w*0.65:.2f}" stroke-linecap="round"/>')
        for i, lbl in enumerate(token_labels):
            r = 5.5 if i == query_idx else 4
            fill = _A if i == query_idx else '#ffffff'
            parts.append(f'<circle cx="{_XS[i]}" cy="{_Y}" r="{r}" fill="{fill}" stroke="{_A}" stroke-width="1.3"/>')
            parts.append(f'<text x="{_XS[i]}" y="76" font-size="7" font-family="Courier New,monospace" text-anchor="middle" fill="#888">{lbl[:9]}</text>')
        svg = ''.join(parts)
        return (f'<div style="border:1px solid #eaeaea;background:#f8f9fa;border-radius:8px;padding:8px 8px 6px;flex:1;min-width:140px;">'
                f'<svg viewBox="0 0 180 80" style="width:100%;height:auto;display:block;overflow:visible;">{svg}</svg>'
                f'<div style="font-size:10px;font-family:\'Courier New\',monospace;color:#555;text-align:center;margin-top:2px;">Head {n} · from "{query_label}"</div>'
                f'</div>')

    def _stage(num, title, desc, spec, sub_items, recap_html=None, is_last=False, state=None):
        rows = ''.join(
            f'<div style="display:flex;align-items:center;border-left:3px solid rgba(33,145,140,{it["opacity"]});padding:7px 12px;gap:12px;margin-bottom:4px;">'
            f'<span style="font-size:0.65rem;font-weight:700;color:#64748b;width:150px;flex-shrink:0;letter-spacing:0.5px;">{it["label"]}</span>'
            f'<span style="font-family:\'Courier New\',monospace;font-size:0.68rem;color:#64748b;">{it["value"]}</span>'
            f'</div>' for it in sub_items)
        recap = f'<div style="font-size:0.85rem;color:#333;margin-top:12px;">{recap_html}</div>' if recap_html else ''
        state_strip = (
            f'<div style="margin-top:14px;margin-left:auto;max-width:62%;border-left:3px solid {_A};border-radius:0 4px 4px 0;padding:8px 12px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
            f'<span style="font-family:\'Courier New\',monospace;font-size:0.75rem;font-weight:700;color:#334155;line-height:1.6;">{state}</span>'
            f'</div>'
        ) if state else ''
        line  = '' if is_last else '<div class="step-line"></div>'
        return (
            f'<div class="step-row">'
            f'<div class="step-spine"><div class="step-circle" style="background:{_A};">{num}</div>{line}</div>'
            f'<div class="step-body">'
            f'<div class="step-label" style="color:{_A};font-size:17px;">{title}</div>'
            f'<div class="step-why">{desc}</div>'
            f'<div style="font-size:0.75rem;color:#64748b;margin-bottom:10px;">{spec}</div>'
            f'<div style="display:flex;flex-direction:column;gap:2px;">{rows}</div>'
            f'{recap}{state_strip}</div></div>')

    def _conn():
        return (f'<div style="display:flex;flex-direction:column;align-items:center;padding:4px 0;">'
                f'<div style="width:2px;height:16px;background:rgba(150,150,150,0.2);"></div>'
                f'<div style="font-size:14px;color:{_A};line-height:1;margin-top:-1px;">▾</div></div>')

    ex = _EX
    _head_svgs = ''.join(_head_svg(i+1, ex['headQueries'][i], ex['headWeights'][i], ex['tokens'][:5]) for i in range(4))

    _ALL_ZONES = ['Aeropuerto AICM','Agwa Bezares / Reforma BNP','Ahuehuetes Norte / De Los Bosques','Ahuehuetes Sur','Anahuac 1 / Bahias / Frontera Polanco','Anzures','Ave Club de Golf Lomas / Interlomas Magnocentro / Vialidad De La Barranca','Barranca Del Muerto','Blvrd Anahuac / Universidad Anahuac','Bondojito ASF / Bosque 2 / Bosque 3','Bosque 1 / Campo Marte','Bosque Real / Lomas Country Club','Bosques Pabellon / El Olivo / Loma De La Palma','Carretera Al Olivo / Carretera Libre / Cruce Echánove / Vistahermosa','Carso Antara Miyana','Central Del Norte','Centro Historico','Cuajimalpa Centro','De Las Fuentes / Tecamachalco','Felix Cuevas','Fuentes Casino / Sedena / Tecamachalco','Haciendas San Fernando','Herradura Conscripto','Interlomas Haciendas / Jesus Del Monte','Interlomas Magnocentro','Irrigación / Polanco Uber HQ','Juarez Rosa','Juarez SoHo House','Lagos','Lomas Altas / Nodo Reforma Palmas / Reforma Regina','Lomas Barrilaco / Lomas Olimpo / Nodo Monte Libano','Lomas FC Cuernavaca','Lomas Prado Norte / Lomas Trastevere','Lomas Verdes','Lomas Virreyes','Napoles WTC','Observatorio','Palmas JP Morgan','Pedregal','Polanco 5','Polanco Gandhi','Polanco Grupo Mexico / Polanco Palacio','Polanco Parque Lincoln','Polanco Parroquia','Rios','Roma Condesa 1','Roma Condesa 2','San Angel Altavista','San Jeronimo Tizapan','Santa Fe ABC','Santa Fe Bosques De / Santa Fe Cumbres De / Santa Fe Tec','Santa Fe Centro Comercial','Santa Fe Colegios','Santa Fe Ibero','Santa Fe ITESM','Santa Fe Quintana / Sante Fe Patio','Sotelo San Esteban','Tamarindos','Viaducto Tlalpan']
    _SHOW_ZONES = ['Roma Condesa 1', 'Polanco Parque Lincoln', 'Santa Fe Centro Comercial', 'Aeropuerto Aicm', 'Centro Historico']
    _REST_ZONES = [z for z in _ALL_ZONES if z not in _SHOW_ZONES]
    def _to_snake(z): return z.lower().replace(' / ', '_').replace('/', '_').replace(' ', '_')
    _sorted_all = sorted(_ALL_ZONES)
    _all_tooltip_rows = ''.join(
        f'<div style="padding:3px 0;font-size:0.72rem;color:#1e293b;font-family:sans-serif;border-bottom:1px solid #e2e8f0;line-height:1.5;">{z}</div>'
        for z in _sorted_all
    )
    _more_tooltip = (
        f'<span class="fn-wrap" style="display:inline-block;vertical-align:middle;margin-left:6px;">'
        f'<span class="fn-mark" style="font-size:0.68rem;font-weight:700;border-bottom:none;">+{len(_ALL_ZONES) - len(_SHOW_ZONES)} more</span>'
        f'<span class="fn-tooltip" style="width:360px;left:0;right:auto;transform:none;font-family:sans-serif;">'
        f'<b style="color:#21918c;font-size:0.73rem;">All {len(_ALL_ZONES)} zones — alphabetical</b><br><br>'
        f'<div style="max-height:280px;overflow-y:auto;">{_all_tooltip_rows}</div>'
        f'</span></span>'
    )
    _zone_items = [{'label': _to_snake(z), 'value': '', 'opacity': 1.0 - i*0.14} for i, z in enumerate(_SHOW_ZONES)]
    _zone_recap = (
        f'<div style="margin-top:6px;">{_more_tooltip}</div>'
        f'<div style="margin-top:8px;font-size:0.72rem;color:#94a3b8;line-height:1.6;">'
        f'Zones with fewer than 25 offers were merged into aggregated labels (e.g. "Anahuac 1 / Bahias / Frontera Polanco") to ensure stratified sampling viability during training.'
        f'</div>'
    )
    _stage0 = _stage('0','Target Variable Definition',f'The model classifies each address into one of {len(_ALL_ZONES)} operational zones derived from polygon clustering and HDBSCAN spatial grouping on the full ride-offer dataset.',f'{len(_ALL_ZONES)} classes · P_ polygon zones · C_ HDBSCAN clusters',_zone_items,recap_html=_zone_recap)

    _pre = (
        _stage0 +
        _stage(1,'Raw OCR Capture','Ride offers were batch-processed through the Google Gemini Pro Vision API to extract raw dropoff address strings.','Gemini Pro Vision · batch processing',[],state=ex['ocrRaw']) +
        _stage(2,'Linguistic Standardization','Applies minimal standardization, deliberately keeping real-world address noise intact for the Transformer to resolve.','5 rule passes · Level 0 preprocessing, no learned weights',[{'label':'Label Truncation','value':'strips trailing zone pair appended in the address (e.g. "… condesa / roma", "… anzures / polanco")','opacity':1.0},{'label':'Accent & Unicode','value':'NFKD normalize · lowercase','opacity':0.8},{'label':'Prefix Unification','value':'av/avenida → av · cll/calle → calle','opacity':0.62},{'label':'Postal Code Isolation','value':r'\d{5} → cp#####','opacity':0.45},{'label':'Token Soldering','value':'street name + number → reforma_222 · street + cardinal → insurgentes_sur','opacity':0.3}],state=ex['ocrCleaned']) +
        _stage(3,'Token Embedding','Each token is mapped to a learned 256-dimensional vector.<span class="fn-wrap" style="margin-left:6px;"><span class="fn-mark" style="font-size:0.75rem;color:#21918c;font-weight:900;cursor:default;border-bottom:none;">ⓘ</span><span class="fn-tooltip" style="font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:340px;"><b style="color:#21918c;">Token Embedding Explained</b><br><br><b>Vocabulary (2,500):</b> Not the total dataset — a dictionary of the top 2,500 most frequent unique words. Dropping rare words forces the model to learn actual patterns instead of memorizing noise.<br><br><b>Special Tokens (2):</b><br>&lt;unk&gt;: Tags unseen words in production as "unknown" to prevent crashes.<br>&lt;pad&gt;: Fills shorter addresses with blank spaces so every input meets the strict 30-token length requirement.<br><br><b>Embedding Dim (256):</b> Translates each token into a 256-dimensional mathematical vector, mapping its "semantic DNA" — teaching the network that words like polanco and anzures are geographically related.</span></span>','nn.Embedding · scaled by √d_model before the encoder',[{'label':'Vocabulary','value':'2,502 tokens','opacity':1.0},{'label':'Embedding Dim','value':'256 (d_model)','opacity':0.7},{'label':'Output Shape','value':'[batch, 30] → [batch, 30, 256]','opacity':0.45}],recap_html=f'2,502 tokens (<b style="border-bottom:1px dotted {_A};">2,500 learned</b> + <b style="border-bottom:1px dotted {_A};">2 special</b>: &lt;pad&gt;, &lt;unk&gt;)',state=' '.join(f'[{t}]' for t in ex['tokens']) + ' → 256-dim vectors × 30') +
        _stage(4,'Positional Encoding','Sin/cos signals tell the model token order, capturing the exact structural sequence of the address.<span class="fn-wrap" style="margin-left:6px;"><span class="fn-mark" style="font-size:0.75rem;color:#21918c;font-weight:900;cursor:default;border-bottom:none;">ⓘ</span><span class="fn-tooltip" style="font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:340px;"><b style="color:#21918c;">Why does the shape stay 256-dim?</b><br><br>Instead of concatenating arrays (which would double the size to 512), the position values are added directly on top of the word embeddings element-by-element (e.g., X&#x2081; + P&#x2081;). This mathematically fuses semantic meaning with structural location into a single vector, keeping the model fast and lightweight.</span></span>','sinusoidal · fixed, non-learned · added element-wise',[{'label':'Function','value':'sin/cos(pos / 10000^(2i/d))','opacity':1.0},{'label':'Max Length','value':'30 tokens','opacity':0.7},{'label':'Output Shape','value':'[batch, 30, 256]','opacity':0.45}],is_last=True,state='embedding[i] + pos_enc[i]  →  [batch, 30, 256]  (order-aware)')
    )

    _post = (
        _stage(5,'Pooling & Regularization','Dual pooling compresses the encoder output into a fixed vector; dropout then regularizes it before classification.','mean-pool ⊕ max-pool → dropout(p=0.3)',[{'label':'Mean Pool','value':'256-dim · avg over sequence','opacity':1.0},{'label':'Max Pool','value':'256-dim · strongest signal','opacity':0.7},{'label':'Dropout','value':'p = 0.3 · curbs overfitting on 3.4k training set','opacity':0.45}],recap_html=f'512-dim fused vector (<b style="border-bottom:1px dotted {_A};">256 mean-pool</b> + <b style="border-bottom:1px dotted {_A};">256 max-pool</b>)',state='mean([h₁…h₃₀]) ⊕ max([h₁…h₃₀])  →  dropout(p=0.3)  →  [batch, 512]') +
        _stage(6,'Classification & Output','The fused vector is projected to 63 zone logits; softmax converts them to probabilities and argmax picks the winner.','Linear(512→63) → softmax → argmax',[{'label':'Output Classes','value':'59 zones (P_ polygon · C_ cluster ids)','opacity':1.0},{'label':'Decision Rule','value':'argmax(softmax(logits))','opacity':0.7},{'label':'Latency','value':'< 10ms, on-device','opacity':0.45}],is_last=True,state=f"[batch, 512]  →  Linear(512→63)  →  argmax<br><b style='font-size:0.82rem;color:#21918c;'>{ex['zone']}</b>  \xb7  {ex['confidence']}")
    )

    _enc = (
        f'<div style="position:relative;border:2px dashed {_A};border-radius:16px;padding:30px 24px 24px;background:rgba(33,145,140,0.03);margin-bottom:8px;">'
        f'<div style="position:absolute;top:-14px;left:24px;background:#fafafa;padding:0 10px;font-size:12px;font-weight:700;color:{_A};letter-spacing:0.3px;">TRANSFORMER ENCODER LAYER</div>'
        f'<div style="position:absolute;top:-14px;right:24px;background:{_A};color:#fff;border-radius:20px;padding:3px 12px;font-size:11px;font-weight:700;letter-spacing:0.3px;">🔁 Stacked × 2</div>'
        f'<div style="background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:20px 22px;box-shadow:0 4px 6px rgba(0,0,0,0.02);margin-bottom:10px;">'
        f'<div style="font-size:18px;font-weight:800;letter-spacing:0.3px;color:{_A};text-transform:uppercase;margin-bottom:10px;">Multi-Head Self-Attention</div>'
        f'<div style="font-size:13.5px;color:#555;line-height:1.65;margin-bottom:6px;">Every token attends to every other token in the address simultaneously. Each head learns to specialize so the full context is captured before any classification happens. <span style="color:#999;font-size:12px;">(Showing 4 of the 8 heads for simplicity)</span></div>'
        f'<div style="font-size:13px;color:#333;margin-bottom:14px;">8 heads · d_k = 32 each · scaled dot-product · Add &amp; Norm<span class="fn-wrap" style="margin-left:6px;"><span class="fn-mark" style="font-size:0.75rem;color:#21918c;font-weight:900;cursor:default;border-bottom:none;">ⓘ</span><span class="fn-tooltip" style="font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:360px;"><b style="color:#21918c;">How the Attention Layer "Thinks"</b><br><br><b>8 Heads (d_k = 32):</b> Instead of looking at the address from a single perspective, the 256-dim bandwidth is split into 8 independent "heads" (32 dimensions each), allowing them to analyze the text simultaneously from multiple angles.<br><br><b>Scaled Dot-Product:</b> It uses a matrix dot-product to multiply the vectors of all words against each other. This operation measures the alignment between tokens, calculating exactly how strongly every single word should "pay attention" to every other word to capture the full context.<br><br><b>Add &amp; Norm:</b> It adds the original word data back into the output (so the model doesn\'t forget the original tokens) and normalizes the numbers to keep the neural network stable and learning efficiently.</span></span></div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:4px;">{_head_svgs}</div>'
        f'<div style="font-size:10.5px;color:#999;margin-top:6px;line-height:1.4;">Teal node = the token doing the attending; arc thickness/opacity = attention weight onto each other token.</div>'
        f'</div>'
        f'<div style="display:flex;flex-direction:column;align-items:center;padding:2px 0;"><div style="width:2px;height:12px;background:#dddddd;"></div><div style="font-size:13px;color:{_A};line-height:1;margin-top:-1px;">▾</div></div>'
        f'<div style="background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:20px 22px;box-shadow:0 4px 6px rgba(0,0,0,0.02);">'
        f'<div style="font-size:18px;font-weight:800;letter-spacing:0.3px;color:{_A};text-transform:uppercase;margin-bottom:10px;">Position-wise Feed-Forward</div>'
        f'<div style="font-size:13.5px;color:#555;line-height:1.65;margin-bottom:6px;">Passes each token\'s 256-dim representation through a 256-dim hidden layer with a non-linear activation, giving the model room to combine attention outputs before the residual Add &amp; Norm.</div>'
        f'<div style="font-size:13px;color:#333;margin-bottom:14px;">Linear(256→256) → ReLU → Linear(256→256) · dropout 0.3 · Add &amp; Norm<span class="fn-wrap" style="margin-left:6px;"><span class="fn-mark" style="font-size:0.75rem;color:#21918c;font-weight:900;cursor:default;border-bottom:none;">&#9432;</span><span class="fn-tooltip" style="font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:360px;"><b style="color:#21918c;">The Feed-Forward Workflow</b><br><br><b>Projection:</b> The first Linear(256→256) layer projects the token through a same-sized hidden space, learning complex combinations of the input features through its adjustable weights.<br><br><b>Filtering:</b> The ReLU activation acts as a non-linear filter, zeroing out negative values (noise) and letting only the strongest signals pass through.<br><br><b>Compression:</b> The second Linear layer maps the refined data back to the standard 256 dimensions, applying another set of learned weights.<br><br><b>Regularization:</b> Dropout randomly disables 30% of connections to prevent the network from over-relying on specific signals.<br><br><b>Add &amp; Norm:</b> It adds the contextualized input back into the output (so the model doesn\'t forget the context it mapped during the Attention phase) and normalizes the numbers to keep the neural network stable and learning efficiently.</span></span></div>'
        f'<svg viewBox="0 0 620 100" style="width:100%;max-height:130px;display:block;overflow:visible;">'
        f'<text x="10" y="46" font-size="10" font-family="Courier New,monospace" fill="#888">x (256)</text>'
        f'<path d="M 62 42 L 84 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<path d="M 70 42 C 70 6 480 6 480 42" fill="none" stroke="{_A}" stroke-width="1.3" opacity="0.55"></path>'
        f'<rect x="84" y="30" width="92" height="26" rx="5" fill="#f8f9fa" stroke="#dddddd" stroke-width="1"></rect>'
        f'<text x="130" y="44" font-size="9.5" font-family="Inter,sans-serif" font-weight="700" text-anchor="middle" fill="#333">Linear</text>'
        f'<text x="130" y="54" font-size="8" font-family="Courier New,monospace" text-anchor="middle" fill="#888">256 → 256</text>'
        f'<path d="M 176 42 L 196 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<rect x="196" y="30" width="56" height="26" rx="5" fill="{_A}" opacity="0.1" stroke="{_A}" stroke-width="1"></rect>'
        f'<text x="224" y="47" font-size="9.5" font-family="Inter,sans-serif" font-weight="700" text-anchor="middle" fill="{_A}">ReLU</text>'
        f'<path d="M 252 42 L 272 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<rect x="272" y="30" width="92" height="26" rx="5" fill="#f8f9fa" stroke="#dddddd" stroke-width="1"></rect>'
        f'<text x="318" y="44" font-size="9.5" font-family="Inter,sans-serif" font-weight="700" text-anchor="middle" fill="#333">Linear</text>'
        f'<text x="318" y="54" font-size="8" font-family="Courier New,monospace" text-anchor="middle" fill="#888">256 → 256</text>'
        f'<path d="M 364 42 L 384 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<rect x="384" y="30" width="76" height="26" rx="5" fill="#f8f9fa" stroke="#dddddd" stroke-width="1"></rect>'
        f'<text x="422" y="44" font-size="9.5" font-family="Inter,sans-serif" font-weight="700" text-anchor="middle" fill="#333">Dropout</text>'
        f'<text x="422" y="54" font-size="8" font-family="Courier New,monospace" text-anchor="middle" fill="#888">p = 0.3</text>'
        f'<path d="M 460 42 L 480 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<circle cx="480" cy="42" r="9" fill="#ffffff" stroke="{_A}" stroke-width="1.3"></circle>'
        f'<text x="480" y="46" font-size="11" text-anchor="middle" fill="{_A}">+</text>'
        f'<path d="M 489 42 L 508 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<rect x="508" y="30" width="66" height="26" rx="5" fill="{_A}" opacity="0.12" stroke="{_A}" stroke-width="1"></rect>'
        f'<text x="541" y="47" font-size="9.5" font-family="Inter,sans-serif" font-weight="700" text-anchor="middle" fill="{_A}">Norm</text>'
        f'<path d="M 574 42 L 594 42" fill="none" stroke="#bbbbbb" stroke-width="1.3"></path>'
        f'<text x="608" y="46" font-size="10" font-family="Courier New,monospace" fill="#888">y</text>'
        f'<text x="275" y="90" font-size="9" font-family="Inter,sans-serif" text-anchor="middle" fill="#999">residual skip connection carries x forward to the Add step</text>'
        f'</svg>'
        f'</div></div>'
        f'<p style="font-size:10.5px;color:#999;margin:10px 0 0;line-height:1.5;">The [30, 256] input tensor passes through both Transformer layers, where linear weights are updated via backpropagation to map the underlying structure of the sequence. The output is a context-aware [30, 256] matrix, passed directly to the Dual Pooling Fusion for structural compression.</p>'
    )

    _lat = (
        f'<div style="margin-top:40px;">'
        f'<div style="font-size:0.95rem;font-weight:700;color:#94a3b8;letter-spacing:2px;margin-bottom:8px;text-transform:uppercase;"><span style="text-transform:none;">miniBabel</span> vs. BETO</div>'
        f'<div style="height:1px;background:linear-gradient(to right,rgba(33,145,140,0.3),transparent);margin-bottom:20px;"></div>'
        f'<div style="font-size:13.5px;color:#555;line-height:1.65;margin-bottom:20px;">Both models share the same dual-pooling classification head and achieve near-identical accuracy. The difference is everything else: BETO arrives pre-trained on the entire Spanish internet; miniBabel was built from scratch on 3,389 CDMX ride-offer records.</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">'

        f'<div style="background:#fff;border:2px solid {_A};border-radius:12px;padding:22px 24px;box-shadow:0 4px 6px rgba(0,0,0,0.02);">'
        f'<div style="font-size:13px;font-weight:700;color:{_A};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px;"><span style="text-transform:none;">miniBabel</span> <span style="font-size:10px;font-weight:600;">(custom · purpose built)</span></div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px 16px;">'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Accuracy</div><div style="font-size:20px;font-weight:800;color:{_A};letter-spacing:-0.5px;">84%</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Inference</div><div style="font-size:20px;font-weight:800;color:{_A};letter-spacing:-0.5px;">&lt; 10ms</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Parameters</div><div style="font-size:20px;font-weight:800;color:{_A};letter-spacing:-0.5px;">~1.46M</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Classifier Input</div><div style="font-size:20px;font-weight:800;color:{_A};letter-spacing:-0.5px;">512</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Vocab</div><div style="font-size:1.1rem;font-weight:700;color:{_A};">2,502 tokens<br><span style="font-size:0.75rem;font-weight:400;color:#aaa;">CDMX ride-offer corpus</span></div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Training</div><div style="font-size:1.1rem;font-weight:700;color:{_A};">From scratch<br><span style="font-size:0.75rem;font-weight:400;color:#aaa;">3,389 records · custom tokenizer</span></div></div>'
        f'</div></div>'

        f'<div style="background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:22px 24px;box-shadow:0 4px 6px rgba(0,0,0,0.02);">'
        f'<div style="font-size:13px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px;">BETO <span style="font-size:10px;font-weight:600;">(dccuchile/bert-base-spanish-wwm-cased)</span></div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px 16px;">'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Accuracy</div><div style="font-size:20px;font-weight:800;color:#121212;letter-spacing:-0.5px;">85%</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Inference</div><div style="font-size:20px;font-weight:800;color:#121212;letter-spacing:-0.5px;">~150ms</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Parameters</div><div style="font-size:20px;font-weight:800;color:#121212;letter-spacing:-0.5px;">~110M</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Classifier Input</div><div style="font-size:20px;font-weight:800;color:#121212;letter-spacing:-0.5px;">1,536</div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Vocab</div><div style="font-size:1.1rem;font-weight:700;color:#121212;">~31,000 tokens<br><span style="font-size:0.75rem;font-weight:400;color:#aaa;">general Spanish corpus</span></div></div>'
        f'<div><div style="font-size:0.68rem;font-weight:700;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Training</div><div style="font-size:1.1rem;font-weight:700;color:#121212;">Pre-trained + fine-tune<br><span style="font-size:0.75rem;font-weight:400;color:#aaa;">AdamW lr=2e-5, 25 epochs</span></div></div>'
        f'</div></div>'

        f'</div>'
        f'<div style="background:rgba(33,145,140,0.06);border-left:3px solid {_A};border-radius:0 6px 6px 0;padding:12px 16px;">'
        f'<div style="font-size:0.8rem;color:#334155;line-height:1.7;">A +1% accuracy gain does not justify 75x the parameter size. For real-time routing systems, miniBabel proves that hyper-specialized domain data beats the brute force of massive foundational models.</div>'
        f'</div>'
        f'</div>'
    )

    _step_css = """<style>
.step-row { display:flex; gap:0; align-items:stretch; margin-bottom:0; }
.step-spine { display:flex; flex-direction:column; align-items:center; width:44px; flex-shrink:0; }
.step-circle { width:30px; height:30px; border-radius:50%; color:#fff; font-size:12px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; z-index:1; }
.step-line { width:2px; background:rgba(150,150,150,0.2); flex:1; min-height:16px; }
.step-body { flex:1; padding:0 0 28px 12px; }
.step-label { font-size:17px; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:2px; padding-top:6px; }
.step-why { font-size:0.85rem; color:#777; line-height:1.6; margin-bottom:4px; }
</style>"""

    st.markdown(_step_css, unsafe_allow_html=True)
    st.markdown("""<style>
.st-key-arch_random_wrap { display:flex !important; justify-content:center !important; }
.st-key-arch_random_wrap button {
    background:rgba(33,145,140,0.07) !important;color:#21918c !important;
    border:1.3px solid #21918c !important;
    border-radius:999px !important;padding:0.45rem 1.2rem !important;
    font-weight:700 !important;font-size:0.78rem !important;letter-spacing:0.4px !important;
    transition:background 0.15s ease, transform 0.15s ease !important;
}
.st-key-arch_random_wrap button:hover { background:rgba(33,145,140,0.14) !important; transform:translateY(-1px); }
.st-key-arch_random_wrap button p { color:#21918c !important; }
.st-key-arch_nav_row > div[data-testid="stVerticalBlock"],
.st-key-arch_nav_row [data-testid="stVerticalBlock"] {
    display:flex !important; flex-direction:row !important;
    justify-content:center !important; gap:12px !important;
    align-items:center !important;
}
.st-key-arch_back_wrap button, .st-key-arch_fwd_wrap button {
    background:#fff !important;color:#21918c !important;
    border:1.3px solid #21918c !important;border-radius:50% !important;
    width:29px !important;height:29px !important;min-width:29px !important;
    padding:0 !important;font-weight:700 !important;font-size:0.8rem !important;
    display:flex !important;align-items:center !important;justify-content:center !important;
    margin:0 auto !important;transition:background 0.15s ease, transform 0.15s ease !important;
}
.st-key-arch_back_wrap button p, .st-key-arch_fwd_wrap button p { color:#21918c !important; margin:0 !important; }
.st-key-arch_back_wrap button:hover, .st-key-arch_fwd_wrap button:hover { background:rgba(33,145,140,0.08) !important; transform:translateY(-1px); }
.st-key-arch_back_wrap button:disabled, .st-key-arch_fwd_wrap button:disabled {
    border-color:#ddd !important;background:#fafafa !important;
}
.st-key-arch_back_wrap button:disabled p, .st-key-arch_fwd_wrap button:disabled p { color:#bbb !important; }
</style>""", unsafe_allow_html=True)

    _, _nav_outer = st.columns([1, 1])
    with _nav_outer:
        _can_back = len(st.session_state['arch_history']) > 0
        _can_fwd  = len(st.session_state['arch_future']) > 0
        _cb, _cc, _cf = st.columns([0.3, 2, 0.3])
        with _cb:
            with st.container(key='arch_back_wrap'):
                if st.button('←', key='arch_back', disabled=not _can_back):
                    st.session_state['arch_future'].append(st.session_state['arch_ex'])
                    st.session_state['arch_ex'] = st.session_state['arch_history'].pop()
                    st.rerun()
        with _cc:
            with st.container(key='arch_random_wrap'):
                if st.button('Generate Random Sample', key='arch_random'):
                    addr, real_zone = _fetch_random_address()
                    if addr:
                        st.session_state['arch_history'].append(st.session_state['arch_ex'])
                        st.session_state['arch_future'] = []
                        st.session_state['arch_ex'] = _build_ex_from_address(addr, real_zone)
                        st.rerun()
        with _cf:
            with st.container(key='arch_fwd_wrap'):
                if st.button('→', key='arch_fwd', disabled=not _can_fwd):
                    st.session_state['arch_history'].append(st.session_state['arch_ex'])
                    st.session_state['arch_ex'] = st.session_state['arch_future'].pop()
                    st.rerun()

    st.markdown(_pre + _conn() + _enc + _conn() + _post + _lat, unsafe_allow_html=True)

with tab_dashboard:

    # ==========================================
    # 3. INITIALIZATION (NLP + SPATIAL) — lazy, only when Dashboard tab is opened
    # ==========================================
    try:
        if 'minibabel' not in st.session_state:
            st.session_state['minibabel'], st.session_state['token_to_idx'], st.session_state['idx_to_zone'] = load_babel_assets()
        if 'geojson_data' not in st.session_state:
            st.session_state['geojson_data'], st.session_state['df_h3_master'], st.session_state['df_holdout'] = load_production_assets()
            st.session_state['df_audit'] = load_parity_audit()
    except Exception as e:
        st.error(f"🔴 Critical Load Failure: {e}")
        st.stop()

    minibabel = st.session_state['minibabel']
    token_to_idx = st.session_state['token_to_idx']
    idx_to_zone = st.session_state['idx_to_zone']
    geojson_data = st.session_state['geojson_data']
    df_h3_master = st.session_state['df_h3_master']
    df_audit = st.session_state['df_audit']

    st.divider()

    # ==========================================
    # TOURNAMENT HIGHLIGHTS: THE PARITY LEDGER
    # ==========================================
    st.subheader("🏆 Tournament Highlights: Model Audit")

    # --- 1. UTILS: OBFUSCATION & STYLING ---
    def obfuscate_urban_string(text):
        import re
        if not isinstance(text, str): return text
        return re.sub(r'\d+', lambda m: m.group(0) if len(m.group(0)) == 5 else '*' * len(m.group(0)), text)

    def style_conf(val):
        if val > 0.9: return f"{int(val*100)}% ✨"
        if val > 0.7: return f"{int(val*100)}% ⚡"
        return f"{int(val*100)}% 🧊"

    # --- 2. INITIALIZE SESSION STATES ---
    if 'hits_view' not in st.session_state: st.session_state['hits_view'] = 'top'
    if 'misses_view' not in st.session_state: st.session_state['misses_view'] = 'top'

    if not df_audit.empty:
        table_config = {
            "address": st.column_config.TextColumn("Urban String (Obfuscated)", width="large"),
            "true_name": st.column_config.TextColumn("Truth", width="small"),
            "babel_pred_name": st.column_config.TextColumn("Predicted", width="small"),
            "formatted_conf": st.column_config.TextColumn("C.", width="small")
        }
        display_cols = ['address', 'true_name', 'babel_pred_name', 'formatted_conf']

        # --- SECTION: HITS ---
        col_h_head, col_h_btn = st.columns([5, 1])
        with col_h_head:
            h_label = "🟢 Top Confidence Hits" if st.session_state['hits_view'] == 'top' else "🎲 Random Hits"
            st.markdown(f"##### {h_label}")
        with col_h_btn:
            if st.button("Generate Random", key="btn_hits"):
                st.session_state['hits_view'] = 'random'; st.rerun()

        hits_df = df_audit[df_audit['babel_hit'] == 1].copy()
        hits_display = hits_df.sort_values('babel_conf', ascending=False).head(5) if st.session_state['hits_view'] == 'top' else hits_df.sample(5)
        hits_display['address'] = hits_display['address'].apply(obfuscate_urban_string)
        hits_display['formatted_conf'] = hits_display['babel_conf'].apply(style_conf)
        st.dataframe(hits_display[display_cols], column_config=table_config, hide_index=True, use_container_width=True)

        # --- SECTION: MISSES ---
        col_m_head, col_m_btn = st.columns([5, 1])
        with col_m_head:
            m_label = "🔴 High-Confidence Misses" if st.session_state['misses_view'] == 'top' else "🎲 Random Misses"
            st.markdown(f"##### {m_label}")
        with col_m_btn:
            if st.button("Generate Random", key="btn_misses"):
                st.session_state['misses_view'] = 'random'; st.rerun()

        miss_df = df_audit[df_audit['babel_hit'] == 0].copy()
        miss_display = miss_df.sort_values('babel_conf', ascending=False).head(5) if st.session_state['misses_view'] == 'top' else miss_df.sample(5)
        miss_display['address'] = miss_display['address'].apply(obfuscate_urban_string)
        miss_display['formatted_conf'] = miss_display['babel_conf'].apply(style_conf)
        st.dataframe(miss_display[display_cols], column_config=table_config, hide_index=True, use_container_width=True)

        # --- RESET BUTTON ---
        if st.session_state['hits_view'] == 'random' or st.session_state['misses_view'] == 'random':
            if st.button("↩️ Reset to Tops"):
                st.session_state['hits_view'] = 'top'; st.session_state['misses_view'] = 'top'; st.rerun()

    st.divider()

    # ==========================================
    # 5. THE VERTICAL INFERENCE PIPELINE
    # ==========================================
    st.subheader("🚀 The O(1) Diagnostic Pipeline")
    st.markdown("""
    Trigger a real-time benchmarking race. This action selects a random record from the **Holdout Set**,
    processes it through the **Linguistic Guillotine**, and contrasts **Cloud API** vs. **Local Neural**.
    """)

    # --- TRIGGER: THE ENGINE START ---
    if st.button("🎲 Generate & Execute Random Tournament Scan", type="primary", use_container_width=True):
        # 1. SELECCIÓN ALEATORIA
        random_row = df_audit.sample(1).iloc[0]
        raw_address = str(random_row['address'])
        true_name = str(random_row['true_name'])

        # 2. DEBUG PIPELINE (Step-by-Step for UI)
        def run_debug_pipeline(text):
            steps = {}
            t = text.lower()
            t = "".join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
            steps["1. Unicode Normalization"] = t
            t = re.sub(r'\s*\S+\s*/.*$', '', t)
            steps["2. The Hard-Cut Guillotine"] = t
            t = t.replace('sante fe', 'santa fe').replace('sta fe', 'santa fe').replace('aicm', 'aeropuerto')
            t = re.sub(r'\b(av|ave|avenida|av\.|av_)\b', 'av', t)
            t = re.sub(r'\b(cll|calle|cll\.|cl\.)\b', 'calle', t)
            t = re.sub(r'\b(pº|p de|paseo de|pso|p\.º)\b', 'paseo', t)
            steps["3. Grammar & Heuristics"] = t
            t = re.sub(r'\b(\d{5})\b', r'cp\1', t)
            steps["4. Zip Code Isolation"] = t
            for _ in range(3):
                t = re.sub(r'(\b\p{L}+(?:_\p{L}+|_\d+)*)\s+(\d{1,4}|norte|sur|este|oeste|poniente|oriente)\b', r'\1_\2', t)
            steps["5. Token Soldering (Street + #)"] = t
            t = re.sub(r'[^a-z0-9áéíóúüñ_\s]', ' ', t)
            t = re.sub(r'\s+', ' ', t).strip()
            steps["6. Final Neural Signal"] = t
            return t, steps

        clean_text, pipeline_steps = run_debug_pipeline(raw_address)

        # 3. EXECUTION: GOOGLE VS BABEL
        gmap_res, gmap_lat, gmap_coords = get_google_maps_latency(raw_address)

        start_babel = time.perf_counter()
        tokens = clean_text.split()
        indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
        indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
        tensor_in = torch.tensor(indices, dtype=torch.long).unsqueeze(0)

        with torch.no_grad():
            logits = minibabel(tensor_in)
            probs = torch.softmax(logits, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)

        babel_lat = (time.perf_counter() - start_babel) * 1000
        pred_name = idx_to_zone.get(str(pred_idx.item()), 'Unknown')

        # 4. ROBUST COMPARISON
        def normalize_for_comparison(text):
            if not text: return ""
            t = "".join(c for c in unicodedata.normalize('NFKD', str(text).lower()) if not unicodedata.combining(c))
            return re.sub(r'[^a-z0-9]', '', t)

        is_hit = normalize_for_comparison(pred_name) == normalize_for_comparison(true_name)

        # 5. SAVE TO SESSION STATE
        st.session_state['active_scan'] = {
            "raw": raw_address,
            "obfuscated": obfuscate_urban_string(raw_address),
            "truth": true_name,
            "pipeline": pipeline_steps,
            "gmaps": {"res": gmap_res, "lat": gmap_lat, "coords": gmap_coords},
            "babel": {"res": pred_name, "lat": babel_lat, "conf": conf.item(), "hit": is_hit}
        }

        # 6. LOG TO AUDIT TRAIL
        st.session_state['address_history'].insert(0, {
            "address": obfuscate_urban_string(raw_address),
            "gmaps": gmap_res,
            "babel": f"{pred_name} ({'✅' if is_hit else '❌'})",
            "timestamp": time.strftime("%H:%M:%S")
        })

    # --- RENDER ENGINE ROOM (UI) ---
    if 'active_scan' in st.session_state:
        scan = st.session_state['active_scan']

        # STEP 1: RAW VS TRUTH
        st.markdown("### 1. Raw Input & Target Verification")
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; border-left: 5px solid #2e6b6b; border-right: 1px solid #ddd; border-top: 1px solid #ddd; border-bottom: 1px solid #ddd;">
                <p style="margin-bottom: 2px; font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Input Address:</p>
                <p style="margin-bottom: 10px; font-size: 15px; font-weight: bold;">{scan['obfuscated']}</p>
                <p style="margin-bottom: 2px; font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Target Ground Truth Class:</p>
                <p style="margin-bottom: 0px; font-size: 15px; font-weight: bold; color: #2e6b6b;">🎯 {scan['truth']}</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")

        # STEP 2: LINGUISTIC PIPELINE
        st.markdown("### 2. Hierarchical Linguistic Engineering")
        for step_name, step_val in scan['pipeline'].items():
            st.markdown(f"<p style='font-size: 12px; color: #888; margin-bottom: -5px; margin-top: 10px;'>{step_name}</p>", unsafe_allow_html=True)
            st.code(obfuscate_urban_string(step_val), language="text")
        st.divider()

        # STEP 3: LATENCY & INFERENCE TOURNAMENT
        st.markdown("### 3. Latency & Inference Tournament")
        col_api, col_neu = st.columns(2)

        with col_api:
            st.markdown("**🌐 Google Maps API (Cloud)**")
            st.metric("Latency", f"{scan['gmaps']['lat']:.1f} ms")
            st.caption(f"Result: {scan['gmaps']['res']}")

        with col_neu:
            st.markdown("**🏎️ miniBabel (Local Neural)**")
            st.metric(
                "Latency", f"{scan['babel']['lat']:.1f} ms",
                delta="✅ HIT" if scan['babel']['hit'] else "❌ MISS",
                delta_color="normal" if scan['babel']['hit'] else "inverse"
            )
            st.success(f"Result: {scan['babel']['res']} ({scan['babel']['conf']:.1%})")
        st.divider()

        # STEP 4: SPATIAL OVERLAY
        st.markdown("### 4. Spatial Sovereign Mesh (Neural Footprint)")
        current_pred = scan['babel']['res'].split(" (")[0]
        current_truth = scan['truth']
        google_coords = scan['gmaps'].get('coords')
        render_sovereign_map(current_pred, current_truth, google_coords, df_h3_master, geojson_data)
        st.markdown(f"""
        <div style="font-size: 12px; color: gray;">
            🟡 <b>Yellow Pin:</b> Geocoded Google Location<br>
            ⚪ <b>White Glow:</b> Target Ground Truth<br>
            ✨ <b>Teal Glow:</b> Neural Hit (Correct Prediction)<br>
            🔴 <b>Red Glow:</b> Neural Miss (Incorrect Prediction)
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # 6. LIVE SESSION AUDIT TRAIL
    # ==========================================
    st.subheader("📜 Live Session Audit Trail")
    if st.session_state['address_history']:
        for entry in st.session_state['address_history']:
            with st.container(border=True):
                cols = st.columns([2, 1, 1])
                cols[0].write(f"**{entry['address']}**")
                cols[1].write(f"🌐 {entry['gmaps']}")
                cols[2].write(f"🏎️ {entry['babel']}")

        if st.button("🗑️ Clear Audit Log"):
            st.session_state['address_history'] = []
            st.session_state.pop('active_scan', None)
            st.rerun()

    st.info("""generate random--- que cada boton solo altere su tabla, linguistic engineering -- ocupa mucho espacio, mapa -- que se vea cdmx, audit trail --mas plano y compacto otras columnas, ** el resultado de google maps tambien debe ser ofuscado los numeros **""") 