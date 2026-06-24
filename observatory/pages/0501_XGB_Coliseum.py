import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import joblib
import time
import io
from google.cloud import storage
from components.styles import GLOBAL_CSS


# ==============================================================================
# 1. CONFIGURACIÓN, ESTÉTICA Y QUANTUM SYNC (BLOQUE MAESTRO UNIFICADO)
# ==============================================================================
st.set_page_config(layout="wide", page_title="XGBoost Tournament: Human vs AI")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown("Proyect Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
        st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
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

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
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
# 3. PAGE LAYOUT
# ==============================================================================
st.markdown("# XGBoost Tournament: Human vs AI")
st.markdown("""
<div style='font-size:0.95rem;color:#475569;line-height:1.7;max-width:860px;margin-bottom:24px;'>
Phase 5 documents the transition from descriptive discovery to a predictive inference engine.
The objective: synthesize a model capable of replicating the agent's decision policy with high fidelity —
and then beat it.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["The Science", "The Coliseum", "The Coliseum (Legacy)"])

with tab1:
    st.markdown("""
<style>
.ci-stepper { display:flex; align-items:flex-start; gap:0; margin:18px 0 28px 0; }
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
  font-size:0.60rem; color:#94a3b8;
  text-align:center; margin-top:2px; line-height:1.3;
}
.ci-step:hover .ci-step-label { color:#21918c; }
[data-baseweb="tab-panel"] [data-baseweb="tab-list"] { display:none !important; }
[data-baseweb="tab-panel"] [data-baseweb="tab-border"] { display:none !important; }
.ci-step.ci-active .ci-dot {
  background:#21918c !important; border-color:#21918c !important; color:#fff !important;
}
.ci-step.ci-active .ci-step-label { color:#21918c !important; font-weight:700; }
</style>
<div class="ci-stepper">
  <div class="ci-step ci-active">
    <div class="ci-dot">P1</div>
    <div class="ci-step-label">Feature Selection</div>
    <div class="ci-step-sub">MI + Chi-squared audit</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P2</div>
    <div class="ci-step-label">Model Tournament</div>
    <div class="ci-step-sub">5-trial algorithmic tournament</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P3</div>
    <div class="ci-step-label">Cognitive Cascade</div>
    <div class="ci-step-sub">Hierarchical architecture</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P4</div>
    <div class="ci-step-label">Bias-Variance Tradeoff</div>
    <div class="ci-step-sub">Lightweight champion emerges</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P5</div>
    <div class="ci-step-label">SHAPs</div>
    <div class="ci-step-sub">Behavioral DNA decoded</div>
  </div>
</div>
""", unsafe_allow_html=True)

    components.html("""
<script>
setTimeout(function() {
  var steps = window.parent.document.querySelectorAll('.ci-step');
  var allTabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');

  function setActive(idx) {
    steps.forEach(function(s) { s.classList.remove('ci-active'); });
    if (steps[idx]) steps[idx].classList.add('ci-active');
  }

  var initIdx = 0;
  for (var j = 3; j < allTabs.length; j++) {
    if (allTabs[j].getAttribute('aria-selected') === 'true') { initIdx = j - 3; break; }
  }
  setActive(initIdx);

  steps.forEach(function(step, i) {
    step.addEventListener('click', function() {
      var target = allTabs[i + 3];
      if (target) {
        var sy = window.parent.scrollY;
        target.click();
        setActive(i);
        setTimeout(function() { window.parent.scrollTo(0, sy); }, 50);
        setTimeout(function() { window.parent.scrollTo(0, sy); }, 300);
      }
    });
  });
}, 300);
</script>
""", height=0)

    sci1, sci2, sci3, sci4, sci5 = st.tabs([
        "Feature Selection",
        "Model Tournament",
        "Cognitive Cascade",
        "Bias-Variance Tradeoff",
        "SHAPs",
    ])

    with sci1:
        st.markdown("""
<style>
.step-row    { display: flex; gap: 0; align-items: stretch; margin-bottom: 0; }
.step-spine  { display: flex; flex-direction: column; align-items: center; width: 44px; flex-shrink: 0; }
.step-circle { width: 30px; height: 30px; border-radius: 50%;
               color: #fff; font-size: 12px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 1; }
.step-line   { width: 2px; background: rgba(150,150,150,0.2); flex: 1; min-height: 16px; }
.step-body   { flex: 1; padding: 0 0 48px 12px; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 2px; padding-top: 6px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.6; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)
        _, col = st.columns([1, 11])
        with col:
            st.markdown("""
<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>1</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>Noise &amp; Metadata Purge</div>
    <div class='step-why'>Identifiers, timestamps, and target-leaking columns removed. Establishes the clean observation space before any statistical audit.</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>2</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>Correlation Doppelgangers</div>
    <div class='step-why'>Pearson correlation matrix audit. Features with r &gt; 0.85 flagged; the lower-MI duplicate pruned to eliminate multicollinearity before Lasso.</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>3</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>Lasso Regularization</div>
    <div class='step-why'>L1 penalty drives irrelevant coefficients to exactly zero. Survivors confirm predictive signal under linear constraints — setting the ceiling for what non-linear models must beat.</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>4</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>PCA</div>
    <div class='step-why'>Principal Component Analysis compresses the surviving 41-feature set into orthogonal components retaining 90% of variance. Eliminates residual multicollinearity for linear and Bayesian estimators.</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#164e4b'>★</div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#164e4b'>Tri-League Architecture</div>
    <div class='step-why'>Three feature representations advance to the tournament: League A (PCA, 19 components — control group), League B (raw curated, 20 features — interpretability mandate), League C (curated PCA, 12 components — mathematical purity). Every algorithm is benchmarked across all three.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    with sci2:
        pass

    with sci3:
        pass

    with sci4:
        pass

    with sci5:
        pass

with tab2:
    pass

with tab3:
    st.markdown("### The Coliseum: Hierarchical Flow")

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

    # --- SIMULATION ENGINE ---
    if st.session_state.arena_running and len(df_session) > 0:
        idx = st.session_state.arena_idx
        row = df_session.iloc[idx]

        fare = float(row['upfront_fare'])
        pickup_m = int(float(row['time_to_pickup_sec'] or 0)/60)
        trip_m = int(float(row['est_trip_time_sec'] or 0)/60)
        base_info = f"${fare:.0f} | {pickup_m}m | {trip_m}m | {str(row['final_zone_name'])[:10]}"
        q_class = f"quantum-link-{idx}"

        badge_match = "<span class='badge-agreed'>🤝 MATCH</span>"
        badge_hum = "<span class='badge-human'>👤 HUM</span>"
        badge_ai = "<span class='badge-ai'>🤖 AI</span>"

        h_l1, ai_l1 = row['human_l1_bucket'], row['ai_l1_bucket']
        gem_template = f"<div class='offer-gem {{extra_class}} {q_class}'>{{badge}} {base_info}</div>"

        if row['is_l1_match']:
            gem = gem_template.format(
                extra_class="nuance-gem" if h_l1 == "THE_NUANCED_REST" else "",
                badge=badge_match
            )
            st.session_state.towers_l1[h_l1].append(gem)
        else:
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

        l2_gem = f"<div class='offer-gem nuance-gem {q_class}'>{base_info}</div>"

        if h_l1 == "THE_NUANCED_REST":
            h_dec = row['human_decision']
            if h_dec in st.session_state.towers_l2["human"]:
                st.session_state.towers_l2["human"][h_dec].append(l2_gem)
                if h_dec == "ACCEPTED": st.session_state.bank['human'] += fare

        if ai_l1 == "THE_NUANCED_REST":
            for mod, col in [("full", "ai_l2_full_decision"), ("light", "ai_l2_spartan_decision")]:
                dec = row[col]
                if dec in st.session_state.towers_l2[mod]:
                    st.session_state.towers_l2[mod][dec].append(l2_gem)
                    if dec == "ACCEPTED": st.session_state.bank[mod] += fare

        if idx < len(df_session) - 1:
            st.session_state.arena_idx += 1
            time.sleep(1.0 / speed_mult)
            st.rerun()
        else:
            st.session_state.arena_running = False
            st.balloons()

    # --- PLACEHOLDER DE PENDIENTES ---
    st.info("Pending: Time in Session Counter, Auditoria de Discrepancias, asegurar que el hover jale bien, stop tournament, otros.")
