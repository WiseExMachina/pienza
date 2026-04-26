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

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Phase 6: O(1) Engine Room", page_icon="⚡", layout="wide")

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
    df_h3_master = get_gcs_df("260425_h3_sovereign_mesh_master.csv")
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
    t = re.sub(r'\s*\S+\s*/.*$', '', t)
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

# ==========================================
# 3. INITIALIZATION (NLP + SPATIAL)
# ==========================================
try:
    # 1. Carga de Motores NLP (Singleton Cache)
    if 'minibabel' not in st.session_state:
        st.session_state['minibabel'], st.session_state['token_to_idx'], st.session_state['idx_to_zone'] = load_babel_assets()
    
    # 2. Carga de Activos (Guardarlos en session_state para que vivan siempre)
    if 'geojson_data' not in st.session_state:
        st.session_state['geojson_data'], st.session_state['df_h3_master'], st.session_state['df_holdout'] = load_production_assets()
        st.session_state['df_audit'] = load_parity_audit()
        st.success("✅ Neural Engines & Spatial Sovereign Mesh Armed and Loaded.")

except Exception as e:
    st.error(f"🔴 Critical Load Failure: {e}")
    st.stop()

# Alias cortos para que tu código de abajo no truene
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
    """Ofusca números excepto CPs de 5 dígitos (1 -> *, 22 -> **, etc)"""
    import re
    if not isinstance(text, str): return text
    # Busca bloques de números: si tienen longitud 5 se quedan, si no, asteriscos
    return re.sub(r'\d+', lambda m: m.group(0) if len(m.group(0)) == 5 else '*' * len(m.group(0)), text)

def style_conf(val):
    """Versión minimalista de confianza"""
    if val > 0.9: return f"{int(val*100)}% ✨"
    if val > 0.7: return f"{int(val*100)}% ⚡"
    return f"{int(val*100)}% 🧊"

# --- 2. INITIALIZE SESSION STATES ---
if 'hits_view' not in st.session_state: st.session_state['hits_view'] = 'top'
if 'misses_view' not in st.session_state: st.session_state['misses_view'] = 'top'

if not df_audit.empty:
    # Definimos anchos quirúrgicos para forzar espacio a la dirección
    table_config = {
        "address": st.column_config.TextColumn("Urban String (Obfuscated)", width="large"),
        "true_name": st.column_config.TextColumn("Truth", width="small"),
        "babel_pred_name": st.column_config.TextColumn("Predicted", width="small"),
        "formatted_conf": st.column_config.TextColumn("C.", width="small") # "C." para ahorrar espacio
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
    
    # Aplicar transformaciones
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
    
    # Aplicar transformaciones
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
    
    # 4. ROBUST COMPARISON (THE SOVEREIGN EQUALITY)
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
    
    # STEP 1: RAW VS TRUTH (Industrial Box)
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

    # STEP 2: LINGUISTIC PIPELINE (Dense Code Blocks)
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
    
    # Extraemos info necesaria
    current_pred = scan['babel']['res'].split(" (")[0]
    current_truth = scan['truth']
    google_coords = scan['gmaps'].get('coords') # Asegúrate que esto se guarde en session_state
    
    render_sovereign_map(current_pred, current_truth, google_coords, df_h3_master, geojson_data)
    
    # Leyenda explicativa
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