import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import io
from google.cloud import storage


# ==============================================================================
# 1. CONFIGURACIÓN, ESTÉTICA Y QUANTUM SYNC (BLOQUE MAESTRO UNIFICADO)
# ==============================================================================
st.set_page_config(layout="wide", page_title="XGBoost Tournament: Human vs AI")

# --- A. EL SNIPER SCRIPT (VERSIÓN FORCE CENTER) ---
quantum_scroll_js = """
<script>
const syncQuantumScroll = () => {
    const gems = document.querySelectorAll('[class*="quantum-link-"]');
    
    gems.forEach(gem => {
        gem.addEventListener('mouseenter', function() {
            const quantumClass = Array.from(this.classList).find(c => c.startsWith('quantum-link-'));
            if (!quantumClass) return;

            const siblings = document.querySelectorAll('.' + quantumClass);
            siblings.forEach(sib => {
                if (sib !== this) {
                    const bucket = sib.closest('.bucket');
                    if (bucket) {
                        // CÁLCULO DE POSICIÓN RELATIVA
                        // Restamos el offset del bucket para que la gema quede en el centro visual
                        const targetPos = sib.offsetTop - bucket.offsetTop - (bucket.clientHeight / 2) + (sib.clientHeight / 2);
                        
                        bucket.scrollTo({
                            top: targetPos,
                            behavior: 'smooth'
                        });
                    }
                }
            });
        });
    });
};

// Reiniciar el listener cada vez que Streamlit actualice el DOM
const observer = new MutationObserver(syncQuantumScroll);
observer.observe(document.body, { childList: true, subtree: true });
</script>
"""

# --- B. ESTILOS BASE (OPUS THEME) ---
base_css = """
<style>
    .offer-gem {
        background-color: #ffffff; border-left: 4px solid #21918c;
        padding: 4px 8px; margin-bottom: 3px; border-radius: 4px;
        font-family: 'Courier New', monospace; font-size: 10px; line-height: 1.2; 
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1); color: #121212;
        transition: all 0.2s ease;
    }
    .nuance-gem { border-left: 4px solid #f5a623 !important; background-color: #fff9e6 !important; font-weight: bold; }
    .tower-label { font-weight: bold; font-size: 11px; text-align: center; color: white; background-color: #440154; padding: 5px; border-radius: 5px 5px 0 0; }
    
    .bucket { 
        background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 0 0 5px 5px; padding: 5px; 
        height: 350px !important; overflow-y: auto !important; 
        display: flex; flex-direction: column; /* Dirección natural para el auto-scroll */
    }
    
    .agent-header { text-align: center; font-weight: 800; font-size: 14px; padding: 8px; background: #21918c; color: white; border-radius: 8px; margin-bottom: 5px; }
    .bucket::-webkit-scrollbar { width: 6px; }
    .bucket::-webkit-scrollbar-thumb { background: #21918c; border-radius: 4px; }
    
    .badge-agreed { background-color: #2ca02c; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
    .badge-human { background-color: #440154; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
    .badge-ai { background-color: #21918c; color: white; padding: 2px 4px; border-radius: 3px; font-size: 8px; margin-right: 4px; font-weight: bold; }
</style>
"""

# --- C. HILO CUÁNTICO (HOVER DINÁMICO) ---
max_ofertas = 150
hover_css = "<style>\n"
for i in range(max_ofertas):
    hover_css += f"""
    body:has(.quantum-link-{i}:hover) .quantum-link-{i} {{
        box-shadow: 0px 0px 15px 3px #f5a623 !important;
        border-left: 8px solid #f5a623 !important;
        background-color: #fffce6 !important;
        transform: scale(1.04);
        z-index: 99;
    }}
    """
hover_css += "</style>"

st.markdown(base_css, unsafe_allow_html=True)
st.markdown(hover_css, unsafe_allow_html=True)
st.markdown(quantum_scroll_js, unsafe_allow_html=True)



# ==============================================================================
# 2. LÓGICA DE DATOS Y ESTADO
# ==============================================================================
KEY_PATH = "/workspaces/pienza/observatory/.streamlit/service-account.json"

if 'arena_idx' not in st.session_state: st.session_state.arena_idx = 0
if 'arena_running' not in st.session_state: st.session_state.arena_running = False
if 'bank' not in st.session_state: st.session_state.bank = {"human": 0.0, "full": 0.0, "light": 0.0}
if 'trips' not in st.session_state: st.session_state.trips = {"human": 0, "full": 0, "light": 0}

if 'towers_l1' not in st.session_state:
    st.session_state.towers_l1 = {k: [] for k in ["THE_NUANCED_REST", "Long Pickup Time", "Low Profitability", "Dropoff: Non-Operational", "Dropoff: Proxy Zone"]}
if 'towers_l2' not in st.session_state:
    st.session_state.towers_l2 = {ag: {k: [] for k in ["ACCEPTED", "Expected Value Gamble", "Strategic Mismatch"]} for ag in ["human", "full", "light"]}

@st.cache_data 
def load_tournament_ledger(): 
    client = storage.Client.from_service_account_json(KEY_PATH) 
    bucket = client.bucket("pienza-streamlit") 
    blob = bucket.blob("260420_resultados_torneo_iter2v3.parquet") 
    buffer = io.BytesIO() 
    blob.download_to_file(buffer) 
    buffer.seek(0) 
    df = pd.read_parquet(buffer)
    if 'offer_timestamp' in df.columns:
        df['offer_timestamp'] = pd.to_datetime(df['offer_timestamp'])
        df = df.sort_values('offer_timestamp')
    return df

df_master = load_tournament_ledger()

# ==============================================================================
# 3. ARENA UI
# ==============================================================================
st.title("🏟️ The Coliseum: Hierarchical Flow") 

c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([2, 2, 1]) 
lista_sesiones = ["ALL SESSIONS"] + sorted(df_master['session_fk'].dropna().unique().tolist())
sid = c_ctrl1.selectbox("Choose Shift:", lista_sesiones) 
speed_mult = c_ctrl2.slider("Simulation Speed", 1, 20, 5, step=1) 

if sid == "ALL SESSIONS":
    df_session = df_master.copy().reset_index(drop=True)
else:
    df_session = df_master[df_master['session_fk'] == sid].reset_index(drop=True)

if c_ctrl3.button("🚀 START TOURNAMENT", use_container_width=True): 
    st.session_state.arena_idx = 0 
    st.session_state.bank = {k: 0.0 for k in st.session_state.bank}
    st.session_state.trips = {k: 0 for k in st.session_state.trips}
    st.session_state.towers_l1 = {k: [] for k in st.session_state.towers_l1} 
    st.session_state.towers_l2 = {ag: {k: [] for k in st.session_state.towers_l2[ag]} for ag in st.session_state.towers_l2} 
    st.session_state.arena_running = True

st.markdown("---")
l1, l2, l3 = st.columns(3)
l1.metric("👤 Human Bank", f"${st.session_state.bank['human']:,.2f}")
l2.metric("🤖 Full Model Bank", f"${st.session_state.bank['full']:,.2f}")
l3.metric("🛡️ Lightweight Bank", f"${st.session_state.bank['light']:,.2f}")

# --- LAYER 1 RENDER ---
st.markdown("### 1. Layer 1: The Bouncer Junction")
t1_cols = st.columns(5)
l1_keys = list(st.session_state.towers_l1.keys())

for i, key in enumerate(l1_keys):
    with t1_cols[i]:
        st.markdown(f'<div class="tower-label" style="{"background-color:#21918c" if key == "THE_NUANCED_REST" else ""}">{key}</div>', unsafe_allow_html=True)
        # Mostramos los últimos 30 para tener qué scrollear
        gem_html = "".join(st.session_state.towers_l1[key][-30:])
        st.markdown(f'<div class="bucket">{gem_html}</div>', unsafe_allow_html=True)

# --- LAYER 2 RENDER ---
st.markdown("---")
st.markdown("### 2. Layer 2: Strategic Strategist Duel")
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
                gem_html_l2 = "".join(st.session_state.towers_l2[ag][buck][-30:])
                st.markdown(f'<div class="bucket" style="height:250px !important;">{gem_html_l2}</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. SIMULATION ENGINE
# ==============================================================================
if st.session_state.arena_running and len(df_session) > 0: 
    idx = st.session_state.arena_idx 
    row = df_session.iloc[idx] 
    
    # --- 0. CORE MATH & METADATA ---
    fare = float(row['upfront_fare'])
    pickup_m = int(float(row['time_to_pickup_sec'] or 0)/60)
    trip_m = int(float(row['est_trip_time_sec'] or 0)/60)
    base_info = f"${fare:.0f} | {pickup_m}m | {trip_m}m | {str(row['final_zone_name'])[:10]}" 
    q_class = f"quantum-link-{idx}"

    # --- 1. DEFINICIÓN DE BADGES ORIGINALES (HTML) ---
    badge_match = "<span class='badge-agreed'>🤝 MATCH</span>"
    badge_hum = "<span class='badge-human'>👤 HUM</span>"
    badge_ai = "<span class='badge-ai'>🤖 AI</span>"

    # --- 2. LÓGICA DE ASIGNACIÓN LAYER 1 (BOUNCER) ---
    h_l1, ai_l1 = row['human_l1_bucket'], row['ai_l1_bucket']
    gem_template = f"<div class='offer-gem {{extra_class}} {q_class}'>{{badge}} {base_info}</div>"

    if row['is_l1_match']: 
        # Match Perfecto
        gem = gem_template.format(
            extra_class="nuance-gem" if h_l1 == "THE_NUANCED_REST" else "", 
            badge=badge_match
        )
        st.session_state.towers_l1[h_l1].append(gem) 
    else: 
        # Mismatch (Gemas Espejadas)
        gem_h = gem_template.format(
            extra_class="nuance-gem" if h_l1 == "THE_NUANCED_REST" else "", 
            badge=badge_hum
        )
        st.session_state.towers_l1[h_l1].append(gem_h) 
        
        gem_ai = gem_template.format(
            extra_class="nuance-gem" if ai_l1 == "THE_NUANCED_REST" else "", 
            badge=badge_ai
        )
        st.session_state.towers_l1[ai_l1].append(gem_ai) 
            
    # --- 3. LÓGICA LAYER 2 (STRATEGIST DUEL) ---
    l2_gem = f"<div class='offer-gem nuance-gem {q_class}'>{base_info}</div>"
    
    # Human Strategist
    if h_l1 == "THE_NUANCED_REST":
        h_dec = row['human_decision']
        if h_dec in st.session_state.towers_l2["human"]:
            st.session_state.towers_l2["human"][h_dec].append(l2_gem)
            if h_dec == "ACCEPTED": st.session_state.bank['human'] += fare
    
    # AI Models (Full & Light)
    if ai_l1 == "THE_NUANCED_REST":
        for mod, col in [("full", "ai_l2_full_decision"), ("light", "ai_l2_spartan_decision")]:
            dec = row[col]
            if dec in st.session_state.towers_l2[mod]:
                st.session_state.towers_l2[mod][dec].append(l2_gem)
                if dec == "ACCEPTED": st.session_state.bank[mod] += fare

    # --- 4. AVANCE Y CONTROL ---
    if idx < len(df_session) - 1: 
        st.session_state.arena_idx += 1 
        time.sleep(1.0 / speed_mult) 
        st.rerun() 
    else: 
        st.session_state.arena_running = False 
        st.balloons()

# --- PLACEHOLDER DE PENDIENTES ---
st.info("Pending: Time in Session Counter, Auditoría de Discrepancias, asegurar que el hover jale bien, stop tournament, otros.")
