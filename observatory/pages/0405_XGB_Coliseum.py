import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import io
from google.cloud import storage, bigquery

# ==========================================
# 1. CONFIGURACIÓN Y ESTÉTICA "VISTIBLE"
# ==========================================
st.set_page_config(layout="wide", page_title="Pienza Coliseum")

# --- A. ESTILOS BASE Y COMPONENTES OPUS ---
base_css = """
<style>
    /* 1. Estilos Originales */
    .offer-gem {
        background-color: #ffffff; border-left: 4px solid #21918c;
        padding: 4px 8px; margin-bottom: 3px; border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 10px; line-height: 1.2; 
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
        color: #121212;
    }
    .nuance-gem {
        border-left: 4px solid #f5a623 !important;
        background-color: #fff9e6 !important;
        font-weight: bold;
    }
    .tower-label { 
        font-weight: bold; font-size: 11px; text-align: center; 
        color: white; background-color: #440154; 
        padding: 5px; border-radius: 5px 5px 0 0;
    }
    .bucket { 
        background-color: #f8f9fa; border: 1px solid #ddd;
        border-radius: 0 0 5px 5px; padding: 5px; 
        min-height: 200px; max-height: 350px; overflow-y: auto;
        display: flex; flex-direction: column-reverse;
    }
    .agent-header {
        text-align: center; font-weight: 800; font-size: 14px;
        padding: 8px; background: #21918c; color: white; border-radius: 8px;
        margin-bottom: 5px;
    }
    
    /* 2. Diseño del Scrollbar (Opus Theme) */
    .bucket::-webkit-scrollbar { width: 6px; }
    .bucket::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 0 0 5px 0; }
    .bucket::-webkit-scrollbar-thumb { background: #21918c; border-radius: 4px; }
    .bucket::-webkit-scrollbar-thumb:hover { background: #440154; }

    /* 3. Badges Cuánticos */
    .badge-agreed { background-color: #2ca02c; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
    .badge-human { background-color: #440154; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
    .badge-ai { background-color: #21918c; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
</style>
"""

KEY_PATH = "/workspaces/pienza/observatory/service-account.json"

# --- B. MAGIA CSS: EL HILO CUÁNTICO (HOVER DINÁMICO) ---
# Usamos Python para escribir 150 reglas CSS automáticas
max_ofertas = 150
hover_css = "<style>\n"
for i in range(max_ofertas):
    hover_css += f"""
    body:has(.quantum-link-{i}:hover) .quantum-link-{i} {{
        box-shadow: 0px 0px 12px 2px #f5a623 !important;
        border-left: 6px solid #f5a623 !important;
        background-color: #fffce6 !important;
        transform: scale(1.03);
        transition: all 0.2s ease-in-out;
        z-index: 10;
        cursor: crosshair;
    }}
    """
hover_css += "</style>"

# --- C. INYECCIÓN A STREAMLIT ---
st.markdown(base_css, unsafe_allow_html=True)
st.markdown(hover_css, unsafe_allow_html=True)

# --- PERSISTENCIA DE ESTADO ---
if 'arena_idx' not in st.session_state: st.session_state.arena_idx = 0
if 'arena_running' not in st.session_state: st.session_state.arena_running = False
if 'bank' not in st.session_state: st.session_state.bank = {"human": 0.0, "full": 0.0, "light": 0.0}

# Layer 1 Buckets (Added Nuanced Rest)
if 'towers_l1' not in st.session_state:
    st.session_state.towers_l1 = {
        "THE_NUANCED_REST": [], # <--- NEW BUCKET
        "Long Pickup Time": [], 
        "Low Profitability": [], 
        "Dropoff: Non-Operational": [], 
        "Dropoff: Proxy Zone": []
    }
if 'towers_l2' not in st.session_state:
    st.session_state.towers_l2 = {
        "human": {"ACCEPTED": [], "Expected Value Gamble": [], "Strategic Mismatch": []},
        "full": {"ACCEPTED": [], "Expected Value Gamble": [], "Strategic Mismatch": []},
        "light": {"ACCEPTED": [], "Expected Value Gamble": [], "Strategic Mismatch": []}
    }



# ========================================== 
# 2. CARGA DE ACTIVOS (REEMPLAZADA POR PARQUET)
# ========================================== 
@st.cache_data 
def load_tournament_ledger(): 
    client = storage.Client.from_service_account_json(KEY_PATH) 
    bucket = client.bucket("pienza-streamlit") 
    blob = bucket.blob("260419_resultados_torneo.parquet") 
    buffer = io.BytesIO() 
    blob.download_to_file(buffer) 
    buffer.seek(0) 
    df = pd.read_parquet(buffer)
    # Asegurar orden cronológico
    if 'offer_timestamp' in df.columns:
        df['offer_timestamp'] = pd.to_datetime(df['offer_timestamp'])
        df = df.sort_values('offer_timestamp')
    return df

# 🔥 AQUÍ NACE df_master (DEBE IR ANTES DE LA SECCIÓN 3)
df_master = load_tournament_ledger()

# ========================================== 
# 3. ARENA UI 
# ========================================== 
st.title("🏟️ The Coliseum: Hierarchical Flow") 

# Controls 
c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([2, 2, 1]) 

# --- CAMBIO 1: Todas las sesiones + "ALL SESSIONS" ---
lista_sesiones = ["ALL SESSIONS"] + sorted(df_master['session_fk'].dropna().unique().tolist())
sid = c_ctrl1.selectbox("Choose Shift:", lista_sesiones) 

# --- CAMBIO 2: Saltos discretos y hasta 20x ---
speed_mult = c_ctrl2.slider("Simulation Speed", 1, 20, 1, step=1) 

# --- CAMBIO 3: Lógica para correr todo o filtrar ---
if sid == "ALL SESSIONS":
    df_session = df_master.copy().reset_index(drop=True)
else:
    df_session = df_master[df_master['session_fk'] == sid].reset_index(drop=True)

if c_ctrl3.button("🚀 START TOURNAMENT", use_container_width=True): 
    st.session_state.arena_idx = 0 
    st.session_state.bank = {"human": 0.0, "full": 0.0, "light": 0.0} 
    st.session_state.trips = {"human": 0, "full": 0, "light": 0} 
    st.session_state.hours = {"human": 0.0, "full": 0.0, "light": 0.0} 
    st.session_state.towers_l1 = {k: [] for k in st.session_state.towers_l1} 
    st.session_state.towers_l2 = {ag: {k: [] for k in st.session_state.towers_l2[ag]} for ag in st.session_state.towers_l2} 
    st.session_state.arena_running = True

# Metrics
st.markdown("---")
l1, l2, l3 = st.columns(3)
l1.metric("👤 Human Bank", f"${st.session_state.bank['human']:,.2f}")
l2.metric("🤖 Full Model Bank", f"${st.session_state.bank['full']:,.2f}")
l3.metric("🛡️ Lightweight Bank", f"${st.session_state.bank['light']:,.2f}")

# --- LAYER 1: 5 BUCKETS ---
st.markdown("### 1. Layer 1: The Bouncer Junction (Triage)")
t1_cols = st.columns(5) # 5 Columns for Triage
l1_keys = ["THE_NUANCED_REST", "Long Pickup Time", "Low Profitability", "Dropoff: Non-Operational", "Dropoff: Proxy Zone"]

for i, key in enumerate(l1_keys):
    with t1_cols[i]:
        label_style = "background-color:#21918c" if key == "THE_NUANCED_REST" else ""
        st.markdown(f'<div class="tower-label" style="{label_style}">{key}</div>', unsafe_allow_html=True)
        items = st.session_state.towers_l1.get(key, [])
        # Build gem HTML
        gem_html = ""
        for it in items[-12:]:
            css_class = "offer-gem nuance-gem" if key == "THE_NUANCED_REST" else "offer-gem"
            gem_html += f"<div class='{css_class}'>{it}</div>"
        st.markdown(f'<div class="bucket">{gem_html}</div>', unsafe_allow_html=True)

# --- LAYER 2: STRATEGIST DUEL ---
st.markdown("---")
st.markdown("### 2. Layer 2: Strategic Strategist Duel (Nuanced Only)")
duel_cols = st.columns(3)
agents = ["human", "full", "light"]
titles = ["👤 HUMAN AGENT", "🤖 FULL FEATURE MODEL", "🛡️ LIGHTWEIGHT MODEL"]

for i, ag in enumerate(agents):
    with duel_cols[i]:
        st.markdown(f'<div class="agent-header">{titles[i]}</div>', unsafe_allow_html=True)
        sub_c = st.columns(3)
        for j, buck in enumerate(["ACCEPTED", "Expected Value Gamble", "Strategic Mismatch"]):
            with sub_c[j]:
                st.markdown(f'<div style="font-size:9px; text-align:center; font-weight:bold;">{buck.split()[-1].upper()}</div>', unsafe_allow_html=True)
                it_l2 = st.session_state.towers_l2[ag][buck]
                gem_html_l2 = "".join([f"<div class='offer-gem nuance-gem'>{it}</div>" for it in it_l2[-12:]])
                st.markdown(f'<div class="bucket" style="min-height:150px;">{gem_html_l2}</div>', unsafe_allow_html=True)

# ========================================== 
# 4. SIMULATION ENGINE (THE QUANTUM REALITY) 
# ========================================== 
if st.session_state.arena_running and len(df_session) > 0: 
    idx = st.session_state.arena_idx 
    row = df_session.iloc[idx] 
    
    fare = float(row['upfront_fare'])
    trip_hrs = float(row['est_trip_time_sec']) / 3600.0

    # Base Physics Metadata 
    base_gem = f"${fare:.0f} | {int(row['time_to_pickup_sec']/60)}m | {int(row['est_trip_time_sec']/60)}m | {str(row['final_zone_name'])[:10]}" 
    
    # --------------------------------------------------------- 
    # 1. TRANSLATE TO LAYER 1 REALITIES (LÍNEA DIRECTA DEL PARQUET)
    # --------------------------------------------------------- 
    human_l1_bucket = row['human_l1_bucket']
    ai_l1_bucket = row['ai_l1_bucket']

    # --------------------------------------------------------- 
    # 2. LAYER 1 VISUAL PLACEMENT (THE QUANTUM SPLIT) 
    # --------------------------------------------------------- 
    base_gem_html = f"<span class='quantum-link-{idx}' style='display:block;'>{{badge}} {base_gem}</span>" 
    if row['is_l1_match']: 
        gem_html = base_gem_html.format(badge="<span class='badge-agreed'>🤝 MATCH</span>") 
        if human_l1_bucket in st.session_state.towers_l1: 
            st.session_state.towers_l1[human_l1_bucket].append(gem_html) 
    else: 
        gem_human = base_gem_html.format(badge="<span class='badge-human'>👤 HUM</span>") 
        if human_l1_bucket in st.session_state.towers_l1: 
            st.session_state.towers_l1[human_l1_bucket].append(gem_human) 
        
        gem_ai = base_gem_html.format(badge="<span class='badge-ai'>🤖 AI</span>") 
        if ai_l1_bucket in st.session_state.towers_l1: 
            st.session_state.towers_l1[ai_l1_bucket].append(gem_ai) 
            
    # --------------------------------------------------------- 
    # 3. TRIGGER TOAST & HUMAN BANK (Independent + Limite Físico)
    # --------------------------------------------------------- 
    if human_l1_bucket == "THE_NUANCED_REST" or ai_l1_bucket == "THE_NUANCED_REST": 
        st.toast(f"💎 GEMA DETECTED: {base_gem}", icon="🔥") 
        time.sleep(1.0) 
        
    if row['human_decision'] == "ACCEPTED" and st.session_state.trips['human'] < 70: 
        st.session_state.bank['human'] += fare
        st.session_state.hours['human'] += trip_hrs
        st.session_state.trips['human'] += 1
        
    # --------------------------------------------------------- 
    # 4. LAYER 2 ROUTING (Independent Timelines) 
    # --------------------------------------------------------- 
    # Human Timeline 
    if human_l1_bucket == "THE_NUANCED_REST": 
        st.session_state.towers_l2["human"][row['human_decision']].append(base_gem) 
        
    # AI Timeline (Only executes if the AI Bouncer actually passed it) 
    if ai_l1_bucket == "THE_NUANCED_REST": 
        # Full Model 
        full_label = row['ai_l2_full_decision']
        st.session_state.towers_l2["full"][full_label].append(base_gem) 
        if full_label == "ACCEPTED" and st.session_state.trips['full'] < 70: 
            st.session_state.bank["full"] += fare
            st.session_state.hours['full'] += trip_hrs
            st.session_state.trips['full'] += 1
            
        # Light Model 
        light_label = row['ai_l2_spartan_decision']
        st.session_state.towers_l2["light"][light_label].append(base_gem) 
        if light_label == "ACCEPTED" and st.session_state.trips['light'] < 70: 
            st.session_state.bank["light"] += fare
            st.session_state.hours['light'] += trip_hrs
            st.session_state.trips['light'] += 1
            
    # --------------------------------------------------------- 
    # PROGRESSION 
    # --------------------------------------------------------- 
    if idx < len(df_session) - 1: 
        st.session_state.arena_idx += 1 
        time.sleep(1.0 / speed_mult) 
        st.rerun() 
    else: 
        st.session_state.arena_running = False 
        st.balloons()