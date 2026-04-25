import streamlit as st
import time
import requests
import regex as re
import unicodedata
import torch
import pydeck as pdk
import json
import random
import io
from google.cloud import storage
from pathlib import Path
import pandas as pd

# IMPORTAMOS DEL BACKEND
from utils.gcp_client import load_fast_assets, load_heavy_assets

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Phase 6: O(1) Engine Room", page_icon="⚡", layout="wide")

# ==========================================
# FUNCIÓN: CARGA DE ASSETS (LA QUE FALTABA)
# ==========================================
@st.cache_data
def load_production_assets():
    """Jala la malla soberana y el test set directamente de la nube y local."""
    # A. Ruta al GeoJSON Local
    geojson_path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # B. Conexión a GCS para CSVs
    KEY_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    client = storage.Client.from_service_account_json(str(KEY_PATH))
    bucket = client.bucket("pienza-streamlit")
    
    def get_gcs_df(blob_name):
        blob = bucket.blob(blob_name)
        buffer = io.BytesIO()
        blob.download_to_file(buffer)
        buffer.seek(0)
        return pd.read_csv(buffer)

    # Nombres exactos de tus archivos en el Bucket
    df_h3 = get_gcs_df("260424_NLP_h3_machine_clusters.csv")
    df_holdout_raw = get_gcs_df("260424_NLP_holdout_test_set.csv")
    
    # FILTRO DE SEGURIDAD
    zonas_muertas = ['interlomas_magnocentro', 'san_miguel_chapultepec']
    df_holdout = df_holdout_raw[~df_holdout_raw['true_zone_name'].isin(zonas_muertas)].copy()
    
    return geojson_data, df_h3, df_holdout

# ==========================================
# PHASE 2: LINGUISTIC PIPELINE (Hard-Cut)
# ==========================================
def standardize_mexico_city_address(text, debug=False):
    if not isinstance(text, str) or text.lower() in ['null', 'n/a']:
        return "unknown_address", {}

    t = text.lower()
    t = "".join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
    states = {"raw": t}

    # 1. HARD-CUT (The Guillotine)
    t = re.sub(r'\s*\S+\s*/.*$', '', t)
    states["post_cut"] = t

    # 2. Heuristics & Grammar
    t = t.replace('sante fe', 'santa fe').replace('sta fe', 'santa fe').replace('aicm', 'aeropuerto')
    t = re.sub(r'\b(av|ave|avenida|av\.|av_)\b', 'av', t)
    t = re.sub(r'\b(cll|calle|cll\.|cl\.)\b', 'calle', t)
    t = re.sub(r'\b(pº|p de|paseo de|pso|p\.º)\b', 'paseo', t)

    # 3. Zip Codes
    t = re.sub(r'\b(\d{5})\b', r'cp\1', t)
    states["post_grammar_zip"] = t

    # 4. Soldering
    for _ in range(3):
        t = re.sub(r'(\b\p{L}+(?:_\p{L}+|_\d+)*)\s+(\d{1,4}|norte|sur|este|oeste|poniente|oriente)\b', r'\1_\2', t)
    states["post_fusion"] = t

    # 5. Purge
    t = re.sub(r'[^a-z0-9áéíóúüñ_\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    states["final"] = t

    if debug:
        return t, states
    return t

# ==========================================
# INFERENCE LOGIC (Google Maps)
# ==========================================
def get_google_maps_latency(address: str):
    api_key = st.secrets.get("GCP_API_KEY", "")
    if not api_key: return "API Key Missing", 0.0
    formatted_address = requests.utils.quote(f"{address}, CDMX, Mexico")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
    
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        latency = (time.perf_counter() - start_time) * 1000
        if response.status_code == 200 and response.json()['status'] == 'OK':
            return response.json()['results'][0]['formatted_address'], latency
        return "API Error", latency
    except:
        return "Network Timeout", (time.perf_counter() - start_time) * 1000

# ==========================================
# UI RENDERING & ENGINE INITIALIZATION
# ==========================================
# Initialize session state for address logging
if 'address_history' not in st.session_state:
    st.session_state['address_history'] = []

st.title("⚡ The O(1) Engine Room")

# --- MANUAL CACHE OVERRIDE ---
if st.button("🔄 Force Clear Cache", type="secondary"):
    st.cache_resource.clear()
    st.cache_data.clear()
    st.success("RAM cleared! Click 'Execute Pipeline' to pull fresh models.")
    st.rerun()

st.markdown("Benchmarking the Latency-Precision Frontier. Watch the architectural trade-offs unfold in real-time.")

# ==========================================
# 3. INITIALIZATION (NLP + SPATIAL)
# ==========================================
try:
    # 1. Carga de Motores NLP (Singleton Cache)
    minibabel, token_to_idx, idx_to_zone = load_fast_assets()
    minibeto, beto_tokenizer = load_heavy_assets(num_classes=len(idx_to_zone))
    
    # 2. Carga de Activos de Producción (La función que pegaste en la Parte 1)
    geojson_data, df_h3, df_holdout = load_production_assets()
    
    st.success("✅ Neural Engines & Spatial Sovereign Mesh Armed and Loaded.")
except Exception as e:
    st.error(f"🔴 Critical Load Failure: {e}")
    st.stop()

st.divider()


# ==========================================
# 4. TOURNAMENT HIGHLIGHTS (HITS & MISSES)
# ==========================================
st.subheader("🏆 Tournament Highlights: Model Audit")
st.markdown("Auditing **miniBabel** performance across the firewalled holdout set.")

# Función auxiliar para auditoría rápida
def get_audit_results(df_test, model, token_to_idx, idx_to_zone):
    results = []
    zombie_mapper = {
        'cruce_echanove': 'carretera_al_olivo__carretera_libre__cruce_echanove__vistahermosa',
        'santa_fe_patio': 'santa_fe_quintana__sante_fe_patio',
        'vialidad_de_la_barranca': 'ave_club_de_golf_lomas__interlomas_magnocentro__vialidad_de_la_barranca',
        'terminal_1_aicm': 'aicm_aeropuerto', 
        'terminal_2_aicm': 'aicm_aeropuerto'
    }
    
    # Tomamos una muestra representativa
    sample_df = df_test.sample(min(100, len(df_test)))
    
    for _, row in sample_df.iterrows():
        clean = standardize_mexico_city_address(row['raw_address'])
        tokens = clean.split()
        indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
        indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
        
        with torch.no_grad():
            tensor_in = torch.tensor(indices).unsqueeze(0)
            logits = model(tensor_in)
            probs = torch.softmax(logits, dim=1)
            conf, pred_idx = torch.max(probs, dim=1)
        
        # 1. Obtener predicción cruda
        raw_pred = idx_to_zone.get(str(pred_idx.item()), 'Unknown')
        
        # 2. Aplicar mapper a AMBOS (Predicción y Verdad) para que coincidan
        final_pred = zombie_mapper.get(raw_pred, raw_pred).strip().lower()
        actual_truth = zombie_mapper.get(row['true_zone_name'], row['true_zone_name']).strip().lower()
        
        # 3. Comparación robusta
        is_hit = (final_pred == actual_truth)
        
        results.append({
            'Address': row['raw_address'][:40] + "...", # Recortado para la tabla
            'True Zone': actual_truth,
            'Predicted': final_pred,
            'Conf': conf.item(),
            'Status': '✅ HIT' if is_hit else '❌ MISS'
        })
    return pd.DataFrame(results)

if st.button("📊 Run Precision Audit"):
    df_res = get_audit_results(df_holdout, minibabel, token_to_idx, idx_to_zone)
    col_h, col_m = st.columns(2)
    with col_h:
        st.write("**Top 5 Confidence Hits**")
        st.dataframe(df_res[df_res['Status'] == '✅ HIT'].sort_values('Conf', ascending=False).head(5), hide_index=True)
    with col_m:
        st.write("**Toughest Strategic Misses**")
        st.dataframe(df_res[df_res['Status'] == '❌ MISS'].sort_values('Conf', ascending=False).head(5), hide_index=True)

st.divider()




col_input, _ = st.columns([2, 1])
with col_input:
    raw_address = st.text_input("Raw Edge String (Try typos, missing zip codes, or noise):", value="Paseo de la Reforma 222 / Roma Norte")

if st.button("🚀 Execute Pipeline", type="primary"):
    
    # 1. PHASE 2: LINGUISTIC PIPELINE (Preprocessing)
    clean_text, states = standardize_mexico_city_address(raw_address, debug=True)
    
    st.subheader("Phase 2: The Linguistic Guillotine")
    st.code(f"""
    1. Raw Input:   {states['raw']}
    2. Hard-Cut:    {states['post_cut']}
    3. Zip/Grammar: {states['post_grammar_zip']}
    4. Soldered:    {states['post_fusion']}
    5. Final Array: [{clean_text}]
    """, language="text")

    st.divider()

    # 2. PHASE 3: THE TOURNAMENT (Inference)
    st.subheader("Phase 3: The Inference Waterfall")
    
    # --- Execute Google Maps ---
    gmap_res, gmap_lat = get_google_maps_latency(raw_address)
    
    # --- Execute miniBETO ---
    start_beto = time.perf_counter()
    encoded = beto_tokenizer(clean_text, return_tensors='pt', max_length=64, padding='max_length', truncation=True)
    with torch.no_grad():
        logits_beto = minibeto(encoded['input_ids'], encoded['attention_mask'])
        probs_beto = torch.softmax(logits_beto, dim=1)
        conf_beto, pred_idx_beto = torch.max(probs_beto, dim=1)
    beto_lat = (time.perf_counter() - start_beto) * 1000
    beto_res_label = f"{idx_to_zone.get(str(pred_idx_beto.item()), 'Unknown')} ({conf_beto.item():.1%} Conf)"

    # --- Execute miniBabel ---
    start_babel = time.perf_counter()
    tokens = clean_text.split()
    indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
    indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
    tensor_in = torch.tensor(indices, dtype=torch.long).unsqueeze(0)
    with torch.no_grad():
        logits_babel = minibabel(tensor_in)
        probs_babel = torch.softmax(logits_babel, dim=1)
        conf_babel, pred_idx_babel = torch.max(probs_babel, dim=1)
    babel_lat = (time.perf_counter() - start_babel) * 1000
    babel_res_label = f"{idx_to_zone.get(str(pred_idx_babel.item()), 'Unknown')} ({conf_babel.item():.1%} Conf)"

    # 3. DISPLAY CURRENT RESULTS (The 3 Columns)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🌐 Google Maps API**")
        st.metric("Latency", f"{gmap_lat:.1f} ms")
        st.info(gmap_res)

    with col2:
        st.markdown("**🧠 miniBETO (FP16)**")
        st.metric("Latency", f"{beto_lat:.1f} ms")
        st.success(beto_res_label)

    with col3:
        st.markdown("**🏎️ miniBabel**")
        st.metric("Latency", f"{babel_lat:.1f} ms", delta=f"{(gmap_lat/babel_lat):.1f}x faster", delta_color="normal")
        st.success(babel_res_label)

    # 4. STATE PERSISTENCE (Log to History)
    new_entry = {
        "address": raw_address,
        "gmaps": {"lat": gmap_lat, "res": gmap_res},
        "beto": {"lat": beto_lat, "res": beto_res_label},
        "babel": {"lat": babel_lat, "res": babel_res_label},
        "timestamp": time.strftime("%H:%M:%S")
    }
    st.session_state['address_history'].insert(0, new_entry)

st.divider()
st.subheader("📜 Live Session Audit Trail")

if st.session_state['address_history']:
    for i, entry in enumerate(st.session_state['address_history']):
        with st.container(border=True):
            cols = st.columns([2, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"**{len(st.session_state['address_history']) - i}. Input:** `{entry['address']}`")
                st.caption(f"Captured at {entry['timestamp']}")
            
            with cols[1]:
                st.markdown("**🌐 G-Maps**")
                st.caption(f"{entry['gmaps']['lat']:.1f}ms")
                st.write(f"_{entry['gmaps']['res']}_")
                
            with cols[2]:
                st.markdown("**🧠 BETO**")
                st.caption(f"{entry['beto']['lat']:.1f}ms")
                st.write(entry['beto']['res'])
                
            with cols[3]:
                # miniBabel is highlighted as the efficiency champion
                st.markdown("**🏎️ Babel**")
                st.caption(f":green[{entry['babel']['lat']:.1f}ms]")
                st.write(f"**{entry['babel']['res']}**")

    if st.button("🗑️ Clear Audit Log"):
        st.session_state['address_history'] = []
        st.rerun()
else:
    st.info("The Engine Room is idling. Execute the pipeline to populate the audit log.")

st.divider()
st.info(f""" map displaying the points of the resuls, Sugiero esto: 



top 5 HITT top 5 miss miniBETO

top 5 HITT top 5 miss miniBabel



y luego usando un RANDOM del holdout test, continuamos con el pipeline que ya tenemos de 

GOOGLE vs beto vs babel

 """)