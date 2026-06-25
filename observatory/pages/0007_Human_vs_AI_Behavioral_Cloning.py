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
st.set_page_config(layout="wide", page_title="Human vs AI: Behavioral Cloning")

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
st.markdown("# Human vs AI: Behavioral Cloning")
st.markdown("""
<div style='font-size:0.95rem;color:#475569;line-height:1.7;max-width:860px;margin-bottom:24px;'>
This phase documents the transition from descriptive discovery to a predictive inference engine.
The objective: synthesize a model capable of replicating the agent's decision policy with high fidelity —
and then beat it.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["The Science", "The Coliseum", "The Coliseum (Legacy)"])

with tab1:
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
    <div class="ci-step-sub">Lasso + domain curation</div>
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
.step-body   { flex: 1; padding: 0 0 28px 12px; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 2px; padding-top: 6px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.6; margin-bottom: 4px; }
.fn-wrap.fn-below .fn-tooltip { bottom: auto; top: 130%; pointer-events: auto; }
.fn-wrap.fn-below .fn-tooltip::after { top: auto; bottom: 100%; border-top-color: transparent; border-bottom-color: #21918c; }
.fn-wrap.fn-below .fn-tooltip::before { content:''; position:absolute; bottom:100%; left:0; width:100%; height:12px; }
.fn-wrap.fn-left .fn-tooltip::after { left: 20px; transform: none; }
</style>
<div style='font-size:0.90rem;color:#475569;line-height:1.7;max-width:860px;margin-bottom:28px;'>
This pipeline follows an experimental design to evaluate three feature "Leagues" across linear and non-linear architectures. Linear estimators require orthogonal inputs to mitigate multicollinearity, while XGBoost leverages internal L1/L2 regularization to process raw feature physics. This framework ensures each algorithmic family is benchmarked against its optimal data representation.<span class='fn-wrap fn-below'><span class='fn-mark'>†</span><span class='fn-tooltip' style='width:260px;white-space:normal;font-family:sans-serif;font-size:0.73rem;line-height:1.6;text-transform:none;letter-spacing:0;font-weight:400;'>Unlike the <a href='/Feature_Store' target='_self' style='color:#21918c;'>Feature Store</a>, which exposes a distilled subset optimized for explainability, this pipeline serves as the absolute audit trail — logging every feature purged prior to modeling.</span></span>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class='step-row' style='margin-bottom:32px;'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>1</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body' style='padding-bottom:0;'>
    <div class='step-label' style='color:#21918c'>Noise &amp; Metadata Purge</div>
    <div class='step-why'>Identifiers, timestamps, and target-leaking columns removed. Establishes the clean observation space before any statistical audit.</div>
    <div style='margin-top:12px;font-size:0.75rem;color:#94a3b8;'>4,765 rows × 105 columns &nbsp;·&nbsp; 49 columns dropped</div>
    <div style='margin-top:10px;display:flex;flex-direction:column;gap:6px;'>
      <div style='display:flex;align-items:center;border-left:3px solid #21918c;padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#94a3b8;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Text &amp; Metadata</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>offer_id &nbsp;·&nbsp; feature_id &nbsp;·&nbsp; session_fk &nbsp;·&nbsp; ocr_fk</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+15</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>image_content_hash<br>dropoff_address<br>dropoff_ambiguity<br>dropoff_hdbscan_name<br>pickup_ambiguity<br>pickup_address<br>dropoff_polygon_name<br>offer_timestamp<br>comment_1<br>comment_2<br>special_note_raw<br>inferred_agent_bearing<br>is_imputed<br>record_status_fk<br>interpolation_quality_fk</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.6);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#94a3b8;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Leakage (EDA)</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_EDA &nbsp;·&nbsp; eph_realized_EDA &nbsp;·&nbsp; is_spread_downgrade_EDA &nbsp;·&nbsp; traffic_volatility_index_eda</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+6</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>eph_complete_index_EDA<br>eph_complete_label_EDA<br>eph_realized_index_EDA<br>eph_realized_label_EDA<br>is_total_cycle_downgrade_EDA<br>realized_traffic_index</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.4);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#94a3b8;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Leakage (Target)</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>offer_action_fk &nbsp;·&nbsp; reason_primary_fk &nbsp;·&nbsp; outcome_fk &nbsp;·&nbsp; post_offer_status_fk</span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.25);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#94a3b8;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Geo Coordinates</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>pickup_lat &nbsp;·&nbsp; pickup_lon &nbsp;·&nbsp; dropoff_lat &nbsp;·&nbsp; dropoff_lon</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+2</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>inferred_agent_lat<br>inferred_agent_lon</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.1);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#94a3b8;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Manual Overrides</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>rider_star_rating &nbsp;·&nbsp; rider_trip_count &nbsp;·&nbsp; is_exclusive &nbsp;·&nbsp; is_vip</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+6</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>is_teens<br>is_identity_verified<br>eph_direct_label<br>eph_operational_label<br>eph_realized_label_ML<br>eph_complete_label_ML</span></span>
      </div>
    </div>
    <div style='margin-top:10px;font-size:0.75rem;color:#21918c;font-weight:600;'>4,765 rows × 56 columns &nbsp;(<span class='fn-wrap fn-left'><span class='fn-mark' style='vertical-align:baseline;font-size:0.75rem;'>46 numerical</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:660px;left:0;transform:none;'><div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px 12px;'><span>upfront_fare</span><span>session_progress_ratio</span><span>cycle_cumulative_net_earnings</span><span>time_to_pickup_sec</span><span>inferred_agent_speed_mps</span><span>eph_direct</span><span>dist_to_pickup_km</span><span>traffic_index_base_120</span><span>eph_direct_index</span><span>est_trip_time_sec</span><span>time_since_last_offer</span><span>eph_operational</span><span>est_trip_dist_km</span><span>offer_density_10sec</span><span>eph_operational_index</span><span>is_surge</span><span>offer_density_30sec</span><span>is_operational_downgrade</span><span>surge_amount</span><span>offer_density_60sec</span><span>eph_realized_ML</span><span>is_turbo_plus</span><span>offer_density_180sec</span><span>eph_realized_index_ML</span><span>turbo_plus_amount</span><span>consecutive_rejects</span><span>is_spread_downgrade_ML</span><span>is_reservation</span><span>cycle_avg_dtp_km</span><span>eph_complete_ML</span><span>reservation_amount</span><span>cycle_std_dtp_km</span><span>eph_complete_index_ML</span><span>is_priority</span><span>cycle_ttp_dtp_ratio</span><span>is_total_cycle_downgrade_ML</span><span>priority_amount</span><span>dispatch_lead_time_sec</span><span>home_vector_alignment_score</span><span>is_long_trip</span><span>cycle_rolling_avg_spread</span><span>historical_rolling_avg_traffic_index</span><span>is_multiple_destinations</span><span>total_accumulated_deadhead_sec</span><span>traffic_volatility_index_ml</span></div></span></span> + <span class='fn-wrap'><span class='fn-mark' style='vertical-align:baseline;font-size:0.75rem;'>10 categorical</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:240px;'>hour_of_day<br>product_category_fk<br>driver_state_at_request_fk<br>day_of_week<br>time_of_day_block<br>day_type<br>dropoff_polygon_id<br>dropoff_h3_hex_id<br>dropoff_hdbscan_id<br>heuristic_flag_context</span></span>)</div>
  </div>
</div>

""", unsafe_allow_html=True)


        st.markdown("""
<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>2</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>Correlation Doppelgangers</div>
    <div class='step-why'>Pearson r &gt; 0.90 filter. Raw EPH values are dropped for normalized indices; time is absorbed into cumulative earnings, combining duration and yield in a single feature.</div>
    <div style='margin-top:12px;'>
      <div style='font-size:0.75rem;color:#94a3b8;margin-bottom:6px;'>4,765 rows × 56 columns &nbsp;·&nbsp; audit on 46 numerical &nbsp;·&nbsp; 5 dropped</div>
      <div style='display:grid;grid-template-columns:1fr 1fr 64px;gap:0;font-size:0.65rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'>
        <span>DROPPED</span><span>SURVIVOR</span><span style='text-align:right;'>r</span>
      </div>
      <div style='border-left:3px solid #21918c;margin-top:4px;display:flex;flex-direction:column;'>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_direct <span style='color:#94a3b8;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_direct_index &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_operational <span style='color:#94a3b8;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_operational_index &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_realized_ML <span style='color:#94a3b8;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_realized_index_ML &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_ML <span style='color:#94a3b8;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_index_ML &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>time_in_session_sec &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>cycle_cumulative_net_earnings &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;text-align:right;'>0.92</span>
        </div>
      </div>
      <div style='margin-top:8px;font-size:0.75rem;color:#21918c;font-weight:600;'>4,765 rows × 51 columns &nbsp;(<span class='fn-wrap fn-left'><span class='fn-mark' style='vertical-align:baseline;font-size:0.75rem;'>41 numerical</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:660px;left:0;transform:none;'><div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px 12px;'><span>upfront_fare</span><span>session_progress_ratio</span><span>cycle_cumulative_net_earnings</span><span>time_to_pickup_sec</span><span>inferred_agent_speed_mps</span><span>eph_direct_index</span><span>dist_to_pickup_km</span><span>traffic_index_base_120</span><span>eph_operational_index</span><span>est_trip_time_sec</span><span>time_since_last_offer</span><span>is_operational_downgrade</span><span>est_trip_dist_km</span><span>offer_density_10sec</span><span>eph_realized_index_ML</span><span>is_surge</span><span>offer_density_30sec</span><span>is_spread_downgrade_ML</span><span>surge_amount</span><span>offer_density_60sec</span><span>eph_complete_index_ML</span><span>is_turbo_plus</span><span>offer_density_180sec</span><span>is_total_cycle_downgrade_ML</span><span>turbo_plus_amount</span><span>consecutive_rejects</span><span>home_vector_alignment_score</span><span>is_reservation</span><span>cycle_avg_dtp_km</span><span>historical_rolling_avg_traffic_index</span><span>reservation_amount</span><span>cycle_std_dtp_km</span><span>traffic_volatility_index_ml</span><span>is_priority</span><span>cycle_ttp_dtp_ratio</span><span></span><span>priority_amount</span><span>dispatch_lead_time_sec</span><span></span><span>is_long_trip</span><span>cycle_rolling_avg_spread</span><span></span><span>is_multiple_destinations</span><span>total_accumulated_deadhead_sec</span><span></span></div></span></span> + <span class='fn-wrap'><span class='fn-mark' style='vertical-align:baseline;font-size:0.75rem;'>10 categorical</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:240px;'>hour_of_day<br>product_category_fk<br>driver_state_at_request_fk<br>day_of_week<br>time_of_day_block<br>day_type<br>dropoff_polygon_id<br>dropoff_h3_hex_id<br>dropoff_hdbscan_id<br>heuristic_flag_context</span></span>)</div>
    </div>
  </div>
</div>

<div style='display:flex;justify-content:flex-end;margin:12px 0 4px;'>
  <div style='font-family:monospace;font-size:0.72rem;color:#164e4b;line-height:1.6;text-align:right;'>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
    <div>└── ⎇ &nbsp;<span style='color:#1a6b67;font-weight:700;'>A-League</span></div>
    <div style='padding-left:2.2ch;color:#1a6b67;'>Control Group</div>
    <div style='padding-left:2.2ch;color:rgba(22,78,75,0.6);'>41 numerical + 10 categorical</div>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
  </div>
</div>

""", unsafe_allow_html=True)

        # --- STEP 3: LASSO (dynamic from notebook output) ---
        import json as _json, os as _os
        _lasso_path = _os.path.join(_os.path.dirname(__file__), '..', 'assets', 'lasso_liga_a.json')
        try:
            with open(_lasso_path) as _f:
                _lasso = _json.load(_f)
            _survivors = _lasso['survivors']   # {feature: coef}
            _casualties = _lasso['casualties'] # [feature, ...]
            _sorted = sorted(_survivors.items(), key=lambda x: x[1], reverse=True)
            _top8 = _sorted[:8]
            _rest = _sorted[8:]
            _max_coef = _top8[0][1] if _top8 else 1.0
    
            def _bar(coef, max_c):
                pct = coef / max_c * 100
                return f"<div style='height:6px;background:#21918c;border-radius:3px;width:{pct:.1f}%;min-width:3px;'></div>"
    
            _top8_html = (
                "<div style='border-left:3px solid #21918c;display:flex;flex-direction:column;'>"
                + "".join(
                    f"<div style='display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) 48px;align-items:center;gap:8px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>"
                    f"<span style='font-family:monospace;font-size:0.68rem;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{f} &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>"
                    f"{_bar(c, _max_coef)}"
                    f"<span style='font-family:monospace;font-size:0.65rem;color:#94a3b8;text-align:right;'>{c:.3f}</span>"
                    f"</div>"
                    for f, c in _top8
                )
                + "</div>"
            )
    
            _rest_tooltip = "<br>".join(
                f"{f} <span style='color:#94a3b8;'>({c:.3f})</span>"
                for f, c in _rest
            )
            _n_rest = len(_rest)
            _rest_pill = (
                f"<span class='fn-wrap'>"
                f"<span class='fn-mark' style='vertical-align:baseline;font-size:0.72rem;'>+{_n_rest} more</span>"
                f"<span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:340px;left:0;transform:none;'>{_rest_tooltip}</span>"
                f"</span>"
            )
    
            _cas_rows = (
                "<div style='border-left:3px solid rgba(33,145,140,0.5);display:flex;flex-direction:column;'>"
                + "".join(
                    f"<div style='padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>"
                    f"<span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:6px;white-space:nowrap;'>{f}<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>"
                    f"</div>"
                    for f in _casualties
                )
                + "</div>"
            )
    
            _n_surv = len(_survivors)
            _n_cas  = len(_casualties)
            _lasso_block = f"""
    <div class='step-row'>
      <div class='step-spine'>
        <div class='step-circle' style='background:#21918c'>3</div>
        <div class='step-line'></div>
      </div>
      <div class='step-body'>
        <div class='step-label' style='color:#21918c'>Lasso Regularization</div>
        <div class='step-why'>L1 penalty drives irrelevant coefficients to exactly zero. Survivors confirm predictive signal under linear constraints — setting the ceiling for what non-linear models must beat.</div>
        <div style='margin-top:12px;font-size:0.75rem;color:#94a3b8;'>4,765 rows × 51 columns &nbsp;·&nbsp; L1 audit on 41 numerical &nbsp;·&nbsp; C = 0.05</div>
        <div style='margin-top:10px;display:flex;gap:24px;align-items:start;'>
          <div style='flex:2;min-width:0;'>
            <div style='display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) 48px;gap:0 8px;font-size:0.65rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'>
          <span>SURVIVOR</span><span>COEF</span><span style='text-align:right;'>val</span>
            </div>
            {_top8_html}
            <div style='padding:6px 12px;'>{_rest_pill}</div>
          </div>
          <div style='flex:1;min-width:0;'>
            <div style='font-size:0.65rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'>CASUALTIES ({_n_cas})</div>
            {_cas_rows}
          </div>
        </div>
        <div style='margin-top:10px;font-size:0.75rem;color:#21918c;font-weight:600;'>4,765 rows × {_n_surv + 10} columns &nbsp;({_n_surv} numerical survivors + 10 categorical)</div>
        <div style='margin-top:14px;text-align:center;'>
          <svg width='10' height='14' viewBox='0 0 10 16' fill='none'><path d='M5 0v13M1 9l4 5 4-5' stroke='#21918c' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/></svg>
        </div>
        <div style='margin-top:4px;border-left:3px solid #21918c;background:rgba(33,145,140,0.05);border-radius:0 8px 8px 0;padding:12px 16px;'>
          <div style='font-size:0.65rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:6px;'>SME Override</div>
          <div style='font-size:0.78rem;color:#334155;line-height:1.65;'>
            Although Lasso ranks <code style='font-size:0.72rem;background:rgba(33,145,140,0.10);padding:1px 5px;border-radius:3px;'>est_trip_dist_km</code> 3rd, human expertise overrides it: EV economics eliminate fuel costs, shifting the primary operational constraint from distance to time. A final matrix of <span class='fn-wrap'><span class='fn-mark' style='vertical-align:baseline;font-size:0.78rem;font-weight:700;'>20 domain-curated features</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:300px;left:0;transform:none;'>upfront_fare<br>time_to_pickup_sec<br>est_trip_time_sec<br>is_multiple_destinations<br>session_progress_ratio<br>traffic_index_base_120<br>time_since_last_offer<br>offer_density_10sec<br>consecutive_rejects<br>cycle_avg_dtp_km<br>cycle_std_dtp_km<br>cycle_ttp_dtp_ratio<br>dispatch_lead_time_sec<br>cycle_rolling_avg_spread<br>total_accumulated_deadhead_sec<br>cycle_cumulative_net_earnings<br>eph_operational_index<br>home_vector_alignment_score<br>historical_rolling_avg_traffic_index<br>traffic_volatility_index_ml</span></span> was locked in and passed a secondary Lasso validation without casualties.
          </div>
        </div>
        <div style='margin-top:8px;font-size:0.75rem;color:#21918c;font-weight:600;'>4,765 rows × 30 columns &nbsp;(20 numerical + 10 categorical)</div>
      </div>
    </div>
    """
        except FileNotFoundError:
            _lasso_block = """
    <div class='step-row'>
      <div class='step-spine'>
        <div class='step-circle' style='background:#21918c'>3</div>
        <div class='step-line'></div>
      </div>
      <div class='step-body'>
        <div class='step-label' style='color:#21918c'>Lasso Regularization</div>
        <div class='step-why'>L1 penalty drives irrelevant coefficients to exactly zero. Survivors confirm predictive signal under linear constraints — setting the ceiling for what non-linear models must beat.</div>
        <div style='margin-top:10px;font-size:0.75rem;color:#94a3b8;font-style:italic;'>Run 0501_PCA_allfeat.ipynb to populate results.</div>
      </div>
    </div>
    """
        st.markdown(_lasso_block, unsafe_allow_html=True)

        st.markdown("""
<div style='display:flex;justify-content:flex-end;margin:12px 0 4px;'>
  <div style='font-family:monospace;font-size:0.72rem;color:#164e4b;line-height:1.6;text-align:right;'>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
    <div>└── ⎇ &nbsp;<span style='color:#1a6b67;font-weight:700;'>B-League</span></div>
    <div style='padding-left:2.2ch;color:#1a6b67;'>Curated Raw</div>
    <div style='padding-left:2.2ch;color:rgba(22,78,75,0.6);'>20 numerical + 10 categorical</div>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>4</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>PCA</div>
    <div class='step-why'>Principal Component Analysis compresses the 20-feature set into orthogonal components, eliminating residual multicollinearity for linear and Bayesian estimators.</div>
    <div style='margin-top:12px;display:flex;gap:24px;align-items:center;justify-content:center;'>
      <div style='display:flex;flex-direction:column;gap:4px;'>
        <div style='font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;'>Cumulative variance</div>
        <div style='display:flex;align-items:center;gap:8px;'>
          <div style='width:160px;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;'>
        <div style='width:90%;height:100%;background:#21918c;border-radius:4px;'></div>
          </div>
          <span style='font-family:monospace;font-size:0.72rem;color:#21918c;font-weight:700;'>90%</span>
        </div>
        <div style='font-size:0.68rem;color:#94a3b8;margin-top:2px;'>captured by 12 of 20 components</div>
      </div>
      <div style='display:flex;flex-direction:column;gap:6px;'>
        <div style='font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;'>Compression</div>
        <div style='font-family:monospace;font-size:0.72rem;color:#64748b;'>20 features &nbsp;→&nbsp; <span style='color:#21918c;font-weight:700;'>12 components</span></div>
        <div style='font-size:0.68rem;color:#94a3b8;'>40% dimensionality reduction</div>
      </div>
    </div>
    <div style='margin-top:10px;font-size:0.75rem;color:#21918c;font-weight:600;'>4,765 rows × 22 columns &nbsp;(12 components + 10 categorical)</div>
  </div>
</div>

<div style='display:flex;justify-content:flex-end;margin:10px 0 4px;padding-right:0;'>
  <div style='font-family:monospace;font-size:0.72rem;color:#164e4b;line-height:1.6;text-align:right;'>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
    <div>└── ⎇ &nbsp;<span style='color:#1a6b67;font-weight:700;'>C-League</span></div>
    <div style='padding-left:2.2ch;color:#1a6b67;'>Curated PCA</div>
    <div style='padding-left:2.2ch;color:rgba(22,78,75,0.6);'>12 components + 10 categorical</div>
    <div style='color:rgba(22,78,75,0.4);'>│</div>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c;font-size:15px;'>&#8853;</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#21918c'>Categorical Curation</div>
    <div class='step-why'>Selection driven by Mutual Information + Chi&#178; validated against human domain expertise.</div>
    <div style='margin-top:12px;display:flex;flex-direction:column;gap:4px;'>
      <div style='font-size:0.75rem;color:#94a3b8;margin-bottom:4px;'>10 categorical</div>
      <div style='border-left:3px solid #21918c;'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'><span>SPATIAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_h3_hex_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:100%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.967</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>83,801</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_polygon_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:70.7%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.684</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>69,959</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_hdbscan_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:41.4%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.400</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>8,806</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>final_zone_id &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span> <span class='fn-wrap fn-left'><span class='fn-mark' style='font-size:0.65rem;color:#000;font-weight:900;cursor:default;border-bottom:none;'>ⓘ</span><span class='fn-tooltip' style='font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:220px;left:0;transform:none;'>A geospatial coalescence of manual polygons and HDBSCAN clusters. Selected over H3 hex grids to preserve domain explainability and prevent overfitting.</span></span></span><div style='height:5px;background:#21918c;border-radius:3px;width:69.4%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.671</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>24.9</span></div>
      </div>
      <div style='border-left:3px solid rgba(33,145,140,0.5);'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'><span>TEMPORAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>hour_of_day &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:100%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.071</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>257.9</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>day_of_week &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:35.2%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.025</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>101.2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>day_type &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:21.1%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.015</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>30.2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>time_of_day_block &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:12.7%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.009</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>38.9</span></div>
      </div>
      <div style='border-left:3px solid rgba(33,145,140,0.25);'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;padding:4px 12px;'><span>CONTEXTUAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>heuristic_flag_context &nbsp;<span style='color:#f59e0b;font-size:0.6rem;'>&#9888;</span> <span class='fn-wrap fn-left'><span class='fn-mark' style='font-size:0.65rem;color:#000;font-weight:900;cursor:default;border-bottom:none;'>ⓘ</span><span class='fn-tooltip' style='font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:250px;left:0;transform:none;'>The dominant signal in early SHAP audits. Constitutes expert-encoded bias (data leakage); retained here strictly to establish the baseline for the algorithmic tournament.</span></span></span><div style='height:5px;background:#f59e0b;border-radius:3px;width:100%;opacity:0.6;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.302</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>8,472</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>product_category_fk &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:10.9%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.033</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>182.4</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>driver_state_at_request_fk &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:1%;min-width:3px;'></div><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>0.003</span><span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;text-align:right;'>18.9</span></div>
      </div>
    </div>
    <div style='margin-top:10px;font-size:0.75rem;color:#21918c;font-weight:600;'>5 categorical survivors</div>
  </div>
</div>

<div style='display:flex;align-items:center;gap:16px;margin:28px 0 20px;padding:0 4px;'>
  <div style='flex:1;height:1px;background:linear-gradient(to right,transparent,rgba(22,78,75,0.25));'></div>
  <div style='display:flex;align-items:center;gap:8px;'>
    <span style='font-size:0.55rem;color:rgba(22,78,75,0.35);letter-spacing:3px;'>✦</span>
    <span style='font-size:0.60rem;font-weight:700;letter-spacing:2.5px;color:rgba(22,78,75,0.45);text-transform:uppercase;'>Tri-League Convergence</span>
    <span style='font-size:0.55rem;color:rgba(22,78,75,0.35);letter-spacing:3px;'>✦</span>
  </div>
  <div style='flex:1;height:1px;background:linear-gradient(to left,transparent,rgba(22,78,75,0.25));'></div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#164e4b'>★</div>
  </div>
  <div class='step-body'>
    <div class='step-label' style='color:#164e4b'>Tri-League Architecture</div>
    <div class='step-why'>Three feature representations advance to the tournament. Every algorithm is benchmarked across all three.</div>
    <div style='display:flex;gap:20px;margin-top:12px;flex-wrap:wrap;'>
      <div style='flex:1;min-width:180px;'>
        <span style='display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:1px;
          padding:3px 10px;border-radius:4px;background:rgba(33,145,140,0.10);
          color:#21918c;border:1px solid rgba(33,145,140,0.3);margin-bottom:8px;'>A-LEAGUE</span>
        <div style='font-size:0.72rem;color:#21918c;font-weight:600;margin-bottom:4px;'>41 numerical + 5 categorical</div>
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Wide Set · Control Group</div>
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.5;'>Validates that expert pruning did not destroy latent signal.</div>
      </div>
      <div style='flex:1;min-width:180px;'>
        <span style='display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:1px;
          padding:3px 10px;border-radius:4px;background:rgba(33,145,140,0.10);
          color:#21918c;border:1px solid rgba(33,145,140,0.3);margin-bottom:8px;'>B-LEAGUE</span>
        <div style='font-size:0.72rem;color:#21918c;font-weight:600;margin-bottom:4px;'>20 numerical + 5 categorical</div>
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Curated · Raw</div>
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.5;'>Expert-selected raw scaled variables — preserves geometric splits for tree models.</div>
      </div>
      <div style='flex:1;min-width:180px;'>
        <span style='display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:1px;
          padding:3px 10px;border-radius:4px;background:rgba(33,145,140,0.10);
          color:#21918c;border:1px solid rgba(33,145,140,0.3);margin-bottom:8px;'>C-LEAGUE</span>
        <div style='font-size:0.72rem;color:#21918c;font-weight:600;margin-bottom:4px;'>12 components + 5 categorical</div>
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Curated · PCA</div>
        <div style='font-size:0.75rem;color:#94a3b8;line-height:1.5;'>Orthogonal projection of B-League designed for linear and Bayesian purity.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='background:#FFFF00;border:3px solid #FFD700;padding:12px 18px;margin-top:32px;font-size:0.85rem;font-weight:700;color:#000;'>PENDING: reordenar Text &amp; Metadata</div>", unsafe_allow_html=True)



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
