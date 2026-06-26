import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import io
from google.cloud import storage
from components.styles import GLOBAL_CSS
from utils.bq_client import fetch_data_from_bq


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
    <div class="ci-step-label">SHAPs</div>
    <div class="ci-step-sub">Behavioral DNA decoded</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P5</div>
    <div class="ci-step-label">Bias-Variance Tradeoff</div>
    <div class="ci-step-sub">Lightweight champion emerges</div>
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
        "SHAPs",
        "Bias-Variance Tradeoff",
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
        st.markdown("""
<div style='margin-bottom:32px;'>
  <div style='font-size:0.85rem;color:#777;line-height:1.6;margin-bottom:4px;font-family:Inter,sans-serif;font-weight:400;'>Five algorithms entered the arena in sequence, each benchmarked across all three feature leagues. This multi-trial framework is designed to capture the baseline predictive signal before introducing non-linear complexity.</div>
  <div style='display:flex;gap:28px;margin-top:14px;justify-content:center;'>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#94a3b8;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>Training</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>Weeks 1 &#8211; 5</div>
    </div>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#94a3b8;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>OOT Holdout</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>Week 6</div>
    </div>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#94a3b8;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>Scoring Metric</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>F1-Macro</div>
    </div>
  </div>
</div>
<div style='border:1px solid rgba(0,0,0,0.07);border-radius:8px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;font-size:0.59rem;font-weight:700;color:#94a3b8;letter-spacing:0.6px;padding:8px 14px;background:#f8fafc;border-bottom:1px solid rgba(0,0,0,0.06);'>
    <span>TRIAL</span><span>ALGORITHM</span><span>TRAINING</span><span style='color:#64748b;'>A-LEAGUE</span><span style='color:#21918c;'>B-LEAGUE</span><span>C-LEAGUE</span>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;'>1 &nbsp;floor</span>
    <span style='font-size:0.72rem;color:#334155;'>Gaussian NB</span>
    <span style='font-size:0.68rem;color:#94a3b8;'>Chronological</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.257</span><div style='height:3px;background:#64748b;border-radius:2px;width:33.8%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.257</span><div style='height:3px;background:#21918c;border-radius:2px;width:33.8%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#94a3b8;'>0.256</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:33.6%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;'>2 &nbsp;linear</span>
    <span style='font-size:0.72rem;color:#334155;'>Logistic Regression</span>
    <span style='font-size:0.68rem;color:#94a3b8;'>Time-Series Split</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.482</span><div style='height:3px;background:#64748b;border-radius:2px;width:63.3%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.514</span><div style='height:3px;background:#21918c;border-radius:2px;width:67.5%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#94a3b8;'>0.490</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:64.4%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;'>3 &nbsp;theoretical</span>
    <span style='font-size:0.72rem;color:#334155;'>Logistic Reg (k-fold)</span>
    <span style='font-size:0.68rem;color:#94a3b8;'>Stratified K-Fold</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.687</span><div style='height:3px;background:#64748b;border-radius:2px;width:90.3%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.716</span><div style='height:3px;background:#21918c;border-radius:2px;width:94.1%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#94a3b8;'>0.691</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:90.8%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#94a3b8;'>4 &nbsp;scout</span>
    <span style='font-size:0.72rem;color:#334155;'>Decision Tree</span>
    <span style='font-size:0.68rem;color:#94a3b8;'>Time-Series Split</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.336</span><div style='height:3px;background:#64748b;border-radius:2px;width:44.2%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.474</span><div style='height:3px;background:#21918c;border-radius:2px;width:62.3%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#94a3b8;'>0.373</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:49.0%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);background:rgba(33,145,140,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#21918c;font-weight:700;'>5 &nbsp;champion</span>
    <span style='font-size:0.72rem;color:#334155;font-weight:600;'>XGBoost</span>
    <span style='font-size:0.68rem;color:#21918c;font-weight:600;'>Stratified K-Fold</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.760</span><div style='height:3px;background:#64748b;border-radius:2px;width:99.9%;margin-top:3px;opacity:0.5;'></div></div>
    <div style='background:rgba(33,145,140,0.10);border-radius:4px;padding:3px 6px;'><span style='font-family:monospace;font-size:0.72rem;color:#21918c;font-weight:700;'>0.761 &#9733;</span><div style='height:3px;background:#21918c;border-radius:2px;width:100%;margin-top:3px;'></div></div>
    <span style='font-family:monospace;font-size:0.70rem;color:#cbd5e1;font-style:italic;'>retired</span>
  </div>
</div>
<div style='margin-top:10px;font-size:0.65rem;color:#94a3b8;font-style:italic;'>C-League retired at Trial 4 &#8212; PCA compression discards the variance XGBoost needs to split on.</div>
<div style='margin-top:56px;margin-bottom:56px;display:flex;align-items:center;gap:20px;justify-content:center;'>
  <div style='flex-shrink:0;text-align:center;'>
    <div style='font-family:monospace;font-size:2.4rem;font-weight:700;color:#21918c;line-height:1;'>0.761</div>
    <div style='font-size:0.58rem;font-weight:700;color:#94a3b8;letter-spacing:1px;margin-top:4px;'>F1-MACRO</div>
  </div>
  <div style='width:1px;height:48px;background:rgba(33,145,140,0.2);flex-shrink:0;'></div>
  <div>
    <div style='font-size:0.88rem;font-weight:700;color:#164e4b;margin-bottom:3px;'>XGBoost &nbsp;&#183;&nbsp; B-League (Curated Raw)</div>
    <div style='font-size:0.75rem;color:#94a3b8;line-height:1.6;'>OOT Holdout (W1&#8211;5 train, W6 test) &nbsp;&#183;&nbsp; Advances to Phase 3 as the behavioral cloning backbone.</div>
  </div>
</div>
<div style='margin-top:52px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:14px 16px;'>
  <div style='font-size:0.72rem;font-weight:700;color:#21918c;margin-bottom:8px;'>The State vs. Time Dilemma</div>
  <div style='font-size:0.88rem;color:#334155;line-height:1.7;'>Strict time-splits on a 5-week dataset risk severe data starvation. However, because the foundational feature matrix already encoded temporal context and agent memory, every observation acts as an independent operational state. This existing architecture renders chronological ordering mathematically redundant, allowing Stratified K-Fold to maximize training volume without data leakage &#8212; strictly validated by a Week 6 out-of-time holdout.</div>
</div>
""", unsafe_allow_html=True)

        # ── Class distribution by week heatmap ──────────────────────────────
        _SQL_CLASS_DIST = """
        WITH weekly AS (
            SELECT
                CAST(FLOOR(DATE_DIFF(DATE(CAST(ml.offer_timestamp AS TIMESTAMP)), DATE '2024-08-22', DAY) / 7) + 1 AS INT64) AS week_num,
                COALESCE(rp.reason_primary_description, 'accepted') AS reason,
                COUNT(*) AS n
            FROM `645009831643.pienza_mini.v_ML_Supervised` ml
            LEFT JOIN `645009831643.pienza_mini.reason_primary` rp
                ON rp.reason_primary_id = ml.reason_primary_fk
            WHERE COALESCE(rp.reason_primary_description, '') != 'system_logic_failure'
            GROUP BY 1, 2
        )
        SELECT week_num, reason, n FROM weekly ORDER BY week_num, reason
        """
        _df_dist = fetch_data_from_bq(_SQL_CLASS_DIST)

        if not _df_dist.empty:
            _pivot = _df_dist.pivot(index="reason", columns="week_num", values="n").fillna(0)
            _weeks = sorted(_pivot.columns.tolist())
            _reasons = _pivot.index.tolist()
            _pct = _pivot.div(_pivot.sum(axis=0), axis=1) * 100
            _week_headers = "".join([
                f"<span style='font-size:0.59rem;font-weight:700;color:#94a3b8;letter-spacing:0.5px;text-align:center;'>{'W6 OOT' if w == _weeks[-1] else f'W{i+1}'}</span>"
                for i, w in enumerate(_weeks)
            ])
            _grid_cols = f"1fr repeat({len(_weeks)}, 52px)"
            _rows_html = ""
            for reason in _reasons:
                _cells = ""
                for i, w in enumerate(_weeks):
                    pct = _pct.loc[reason, w]
                    n = int(_pivot.loc[reason, w])
                    is_oot = (w == _weeks[-1])
                    opacity = max(0.08, pct / 100)
                    bg = f"rgba(148,163,184,{opacity:.2f})" if is_oot else f"rgba(33,145,140,{opacity:.2f})"
                    border = "border-left:1px dashed rgba(0,0,0,0.10);" if is_oot else ""
                    _cells += (
                        f"<div style='text-align:center;padding:4px 2px;background:{bg};border-radius:3px;{border}'>"
                        f"<div style='font-family:monospace;font-size:0.65rem;color:#334155;font-weight:600;'>{pct:.0f}%</div>"
                        f"<div style='font-family:monospace;font-size:0.55rem;color:#94a3b8;'>{n}</div>"
                        f"</div>"
                    )
                _rows_html += (
                    f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:4px;align-items:center;padding:1px 0;border-top:1px solid rgba(0,0,0,0.04);'>"
                    f"<span style='font-family:monospace;font-size:0.65rem;color:#64748b;'>{reason}</span>"
                    f"{_cells}</div>"
                )
            _totals_cells = ""
            for i, w in enumerate(_weeks):
                total_n = int(_pivot[w].sum())
                is_oot = (w == _weeks[-1])
                border = "border-left:1px dashed rgba(0,0,0,0.10);" if is_oot else ""
                _totals_cells += (
                    f"<div style='text-align:center;padding:4px 2px;{border}'>"
                    f"<div style='font-family:monospace;font-size:0.65rem;color:#334155;font-weight:700;'>{total_n:,}</div>"
                    f"</div>"
                )
            _totals_row = (
                f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:4px;align-items:center;padding:1px 0;border-top:1px solid rgba(0,0,0,0.12);margin-top:2px;'>"
                f"<span style='font-family:monospace;font-size:0.60rem;color:#94a3b8;font-weight:700;letter-spacing:0.5px;'>TOTAL</span>"
                f"{_totals_cells}</div>"
            )
            _heatmap_html = (
                f"<div style='margin-top:56px;font-size:0.85rem;color:#777;line-height:1.6;font-family:Inter,sans-serif;font-weight:400;'>A temporal breakdown of the target variables confirms the structural integrity of the dataset. Tracking class distribution across the six-week horizon validates that the agent&#8217;s decision policy does not suffer from fundamental concept drift, safely clearing the path for K-Fold shuffling.</div>"
                f"<div style='margin-top:28px;border-top:1px solid rgba(0,0,0,0.06);padding-top:20px;max-width:820px;margin-left:auto;margin-right:auto;'>"
                f"<div style='font-size:0.59rem;font-weight:700;color:#94a3b8;letter-spacing:1.5px;margin-bottom:10px;'>CLASS DISTRIBUTION BY WEEK &nbsp;&#8212;&nbsp; REASON PRIMARY</div>"
                f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:4px;padding:0 0 6px;'><span></span>{_week_headers}</div>"
                f"{_rows_html}{_totals_row}"
                f"<div style='margin-top:8px;font-size:0.65rem;color:#94a3b8;font-style:italic;'>W6 = OOT holdout, unseen during training. Minority class shift across weeks motivates Stratified K-Fold over strict time-splits.</div>"
                f"</div>"
            )
            st.markdown(_heatmap_html, unsafe_allow_html=True)

    with sci3:
        import json as _json

        _mono  = _json.load(open("/workspaces/pienza/data/dumped_files/0508_monolith_metrics.json"))
        _casc  = _json.load(open("/workspaces/pienza/data/dumped_files/0509_cascade_metrics.json"))
        _l1    = _casc["layer1"]
        _l2    = _casc["layer2"]

        # ── Intro + comparison banner (always visible, above tabs) ────────────
        st.markdown("""
<div style='font-size:0.85rem;color:#777;line-height:1.6;font-family:Inter,sans-serif;font-weight:400;margin-bottom:32px;'>
This section shows how a monolithic class architecture fails because deterministic noise acts as a "gravitational well," cannibalizing nuanced decisions. The Cognitive Cascade resolves this through a dual-layer hierarchy: Layer 1 isolates deterministic rejections, clearing a noise-free subset for Layer 2 to decode the agent's true strategic intent.
</div>
<style>
.bento-card {
  background:#fff;
  border:1px solid #e2e8f0;
  border-left:3px solid #21918c;
  border-radius:10px;
  padding:14px 16px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  cursor: default;
}
.bento-card:hover {
  box-shadow: 0 6px 24px rgba(33,145,140,0.13);
  transform: translateY(-2px);
}
</style>
<div style='display:grid;grid-template-columns:1fr auto 2fr;align-items:center;gap:0;margin-bottom:36px;'>
  <div class='bento-card'>
    <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>Monolith</div>
    <div style='font-size:0.55rem;color:#94a3b8;margin-bottom:6px;'>Single Stage · 7 Classes</div>
    <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
      <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.61</div>
      <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
    </div>
    <div style='display:flex;gap:5px;flex-wrap:wrap;'>
      <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.941</span>
      <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 76%</span>
    </div>
  </div>
  <div style='padding:0 14px;color:#cbd5e1;font-size:1rem;text-align:center;'>→</div>
  <div class='bento-card'>
    <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>Cognitive Cascade</div>
    <div style='display:grid;grid-template-columns:1fr 1px 1fr;gap:0;'>
      <div style='padding-right:16px;'>
        <div style='font-size:0.55rem;color:#94a3b8;margin-bottom:6px;'>Layer 1 · 5 Classes</div>
        <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
          <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.76</div>
          <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
        </div>
        <div style='display:flex;gap:5px;flex-wrap:wrap;'>
          <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.941</span>
          <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 81%</span>
        </div>
      </div>
      <div style='background:#e2e8f0;'></div>
      <div style='padding-left:16px;'>
        <div style='font-size:0.55rem;color:#94a3b8;margin-bottom:6px;'>Layer 2 · 3 Classes</div>
        <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
          <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.91</div>
          <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
        </div>
        <div style='display:flex;gap:5px;flex-wrap:wrap;'>
          <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.981</span>
          <span style='font-size:0.58rem;font-weight:600;color:#94a3b8;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 91%</span>
        </div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        if "c3_selected" not in st.session_state:
            st.session_state["c3_selected"] = "Monolith"

        _c3_active = st.session_state["c3_selected"]

        _mono_active = _c3_active == "Monolith"
        st.markdown(f"""
<style>
.c3-seg {{
  display:inline-flex; border-radius:999px; background:#f1f5f9;
  padding:4px; gap:0; margin-bottom:28px; border:1px solid #e2e8f0;
}}
.c3-seg-btn {{
  padding:5px 16px; border-radius:999px; font-size:0.72rem; font-weight:600;
  cursor:pointer; transition:all 0.18s ease; user-select:none;
  white-space:nowrap; color:#64748b; background:transparent;
}}
.c3-seg-btn:hover {{ color:#21918c; }}
.c3-seg-active {{
  background:#21918c; color:#ffffff !important;
  box-shadow:0 2px 8px rgba(33,145,140,0.30);
}}
</style>
<div class="c3-seg">
  <div class="c3-seg-btn {'c3-seg-active' if _mono_active else ''}" id="c3card-mono">Monolith</div>
  <div class="c3-seg-btn {'c3-seg-active' if not _mono_active else ''}" id="c3card-casc">Cognitive Cascade</div>
</div>
""", unsafe_allow_html=True)

        if st.button("mono", key="btn_c3_mono"):
            st.session_state["c3_selected"] = "Monolith"
            st.rerun()
        if st.button("casc", key="btn_c3_casc"):
            st.session_state["c3_selected"] = "Cognitive Cascade"
            st.rerun()



        _c3_view = st.session_state["c3_selected"]

        if _c3_view == "Monolith":
            _mono_cm     = _mono["confusion_matrix"]
            _mono_labels = _mono["labels"]
            _n = len(_mono_labels)
            _row_sums = [sum(_mono_cm[i]) for i in range(_n)]

            # Build cell rows — fixed columns so cells stay compact regardless of screen width
            _label_map = {"non_operational": "dropoff non operational"}
            _cw = 66
            _grid_cols = f"130px " + " ".join([f"{_cw}px"] * _n)
            _rows_html = ""
            for i in range(_n):
                _rt = _row_sums[i] if _row_sums[i] > 0 else 1
                _display_lbl = _label_map.get(_mono_labels[i], _mono_labels[i]).replace('_', ' ')
                _rows_html += f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:3px;margin-bottom:3px;'>"
                _rows_html += f"<div style='font-size:0.56rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;white-space:normal;word-break:break-word;line-height:1.3;'>{_display_lbl}</div>"
                for j in range(_n):
                    _val = _mono_cm[i][j]
                    _pct = _val / _rt
                    _diag = (i == j)
                    if _diag:
                        _alpha = max(0.14, _pct * 0.85)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#fff" if _pct > 0.45 else "#21918c"
                        _fw = "700"
                    elif _val == 0:
                        _bg = "#f8fafc"; _tc = "#e2e8f0"; _fw = "400"
                    else:
                        _alpha = max(0.04, _pct * 0.35)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#94a3b8"; _fw = "500"
                    _green_lbl = {"non_operational","proxy_zone","low_profitability","long_pickup"}
                    _red_lbl   = {"strategic_mismatch","expected_value_gamble","accepted"}
                    if _diag and _mono_labels[i] in _green_lbl:
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#22c55e;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>✓</span>"
                    elif _diag and _mono_labels[i] in _red_lbl:
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#ef4444;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>✗</span>"
                    else:
                        _icon = ""
                    _rows_html += f"<div style='background:{_bg};border-radius:4px;text-align:center;padding:16px 0;position:relative;'>{_icon}<div style='font-size:0.85rem;color:{_tc};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
                _rows_html += "</div>"

            # Bottom class labels row (empty first cell to offset row-label column)
            _bot = f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:3px;margin-top:4px;'>"
            _bot += "<div></div>"
            for _lbl in _mono_labels:
                _bot += f"<div style='font-size:0.56rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.3;'>{_label_map.get(_lbl, _lbl).replace('_',' ')}</div>"
            _bot += "</div>"

            # "Predicted" axis label centered under the data columns only
            _pred_label = f"<div style='display:grid;grid-template-columns:{_grid_cols};margin-top:8px;'>"
            _pred_label += "<div></div>"
            _pred_label += f"<div style='grid-column:2/{_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div>"
            _pred_label += "</div>"

            _cr = _mono["classification_report"]
            _sm = _cr["strategic_mismatch"]
            _ev = _cr["expected_value_gamble"]
            _ac = _cr["accepted"]
            _sm_t2 = round((1 - _sm["recall"]) * 100)
            _sm_t1 = round((1 - _sm["precision"]) * 100)
            _ev_t2 = round((1 - _ev["recall"]) * 100)
            _ev_t1 = round((1 - _ev["precision"]) * 100)
            _ac_t2 = round((1 - _ac["recall"]) * 100)
            _ac_t1 = round((1 - _ac["precision"]) * 100)

            st.markdown(f"""
<div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:40px;'>Monolith Confusion Matrix · W6 OOT Holdout</div>
<div style='padding-bottom:90px;'>
<div style='width:fit-content;margin:0 auto;transform:scale(1.15) translateX(-70px);transform-origin:top center;'><div style='display:flex;gap:8px;align-items:center;'>
  <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
  <div>
    {_rows_html}
    {_bot}
    {_pred_label}
  </div>
</div></div>
</div>
""", unsafe_allow_html=True)

            st.markdown("""<div style='margin-top:40px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:14px 18px;'>
  <div style='font-size:0.62rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Diagnostic</div>
  <div style='font-size:0.82rem;color:#334155;line-height:1.7;'>While deterministic rejections achieve high separation (&gt;80% recall), the nuanced classes severely underperform. Due to the high similarity in their feature spaces, the model defaults to a "lazy" information gain strategy: it absorbs these complex, minority decisions into the <code style='font-size:0.75rem;background:rgba(33,145,140,0.12);padding:1px 5px;border-radius:3px;'>dropoff_non_operational</code> majority class instead of executing the deep splits required to isolate them.</div>
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:16px;margin-top:40px;'>Autopsy Report</div>
<div style='margin:0 auto;max-width:780px;border:1px solid rgba(33,145,140,0.2);border-radius:8px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:140px 1fr 1fr 1fr;'>
    <div style='background:#f8fafc;padding:10px 14px;border-bottom:1px solid rgba(33,145,140,0.12);'></div>
    <div style='background:#f8fafc;padding:10px 14px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.58rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Strategic Mismatch</div>
    <div style='background:#f8fafc;padding:10px 14px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.58rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Expected Value Gamble</div>
    <div style='background:#f8fafc;padding:10px 14px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.58rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Accepted</div>
    <div style='padding:14px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.78rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type II</div>
      <div style='font-size:0.76rem;color:#94a3b8;margin-top:2px;'>False Negative</div>
    </div>
    <div style='padding:14px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:#21918c;line-height:1;'>{_sm_t2}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>undetected</div>
    </div>
    <div style='padding:14px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:#21918c;line-height:1;'>{_ev_t2}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>undetected</div>
    </div>
    <div style='padding:14px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:#21918c;line-height:1;'>{_ac_t2}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>undetected</div>
    </div>
    <div style='padding:14px;'>
      <div style='font-size:0.78rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type I</div>
      <div style='font-size:0.76rem;color:#94a3b8;margin-top:2px;'>False Positive</div>
    </div>
    <div style='padding:14px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_sm_t1}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>false alarms</div>
    </div>
    <div style='padding:14px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_ev_t1}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>false alarms</div>
    </div>
    <div style='padding:14px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.6rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_ac_t1}%</div>
      <div style='font-size:0.60rem;color:#94a3b8;margin-top:4px;'>false alarms</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            st.markdown("""
<div style='margin-top:28px;font-size:0.85rem;color:#777;line-height:1.6;font-family:Inter,sans-serif;font-weight:400;'>
  A simultaneous collapse across both Type I and Type II metrics confirms a complete failure to map mathematical boundaries. With up to 96% of critical events undetected and severe false-alarm rates when triggered, the model isn&#8217;t inferring complex intent&#8202;&#8212;&#8202;it is simply guessing blindly.
</div>
<div style='margin-top:32px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:0.72rem;color:#94a3b8;font-family:monospace;text-align:center;'>
  Monolith &middot; F1-macro 0.61 &middot; <span style='color:#b91c1c;'>✗ architecture insufficient</span> &nbsp;&mdash;&mdash;&mdash;&nbsp; proceeding to Cognitive Cascade <span style='color:#21918c;'>→</span>
</div>
""", unsafe_allow_html=True)


        elif _c3_view == "Cognitive Cascade":
            st.markdown("""<div style='font-size:0.85rem;color:#777;line-height:1.6;font-family:Inter,sans-serif;font-weight:400;margin-bottom:32px;'>
In this hierarchical architecture, Layer 1 collapses the overlapping minority classes into a single <code>nuanced_rest</code> bucket. Recalled observations from this bucket then pass to Layer 2 to decode the agent&#8217;s final decision policy.
</div>""", unsafe_allow_html=True)

            # ── Section 2: Cascade Architecture diagram ────────────────────────────
            st.markdown("""
<div style='display:flex;justify-content:center;margin-bottom:48px;'>
<div style='display:grid;grid-template-columns:auto auto auto;gap:0;align-items:center;'>
  <div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>
    <div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>
      <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 1</div>
    </div>
    <div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>dropoff_non_operational</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>proxy_zone</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>low_profitability</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>long_pickup</div>
      <div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;'>→ nuanced_rest</div>
    </div>
  </div>
  <div style='display:flex;flex-direction:column;align-items:center;gap:3px;padding:0 16px;'>
    <div style='font-size:0.55rem;font-weight:700;color:#94a3b8;'>19.4%</div>
    <div style='color:#21918c;font-size:1.1rem;'>→</div>
  </div>
  <div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>
    <div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>
      <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 2</div>
    </div>
    <div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>accepted</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>strategic_mismatch</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>expected_value_gamble</div>
    </div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

            # ── Sections 3 + 4: L1 and L2 side by side ───────────────────────────
            _l1_cm = _l1["confusion_matrix"]
            _l1_labels = _l1["labels"]
            _l1_n = len(_l1_labels)
            _l1_row_sums = [sum(_l1_cm[i]) for i in range(_l1_n)]
            _l1_cw = 76
            _l1_grid_cols = f"90px " + " ".join([f"{_l1_cw}px"] * _l1_n)
            _l1_rows_html = ""
            for i in range(_l1_n):
                _rt = _l1_row_sums[i] if _l1_row_sums[i] > 0 else 1
                _l1_lmap = {"non_operational": "dropoff non operational"}
                _display_lbl = _l1_lmap.get(_l1_labels[i], _l1_labels[i]).replace('_', ' ')
                _l1_rows_html += f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};gap:3px;margin-bottom:3px;'>"
                _l1_rows_html += f"<div style='font-size:0.56rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;white-space:normal;word-break:break-word;line-height:1.3;'>{_display_lbl}</div>"
                for j in range(_l1_n):
                    _val = _l1_cm[i][j]
                    _pct = _val / _rt
                    _diag = (i == j)
                    if _diag:
                        _alpha = max(0.14, _pct * 0.85)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#fff" if _pct > 0.45 else "#21918c"
                        _fw = "700"
                    elif _val == 0:
                        _bg = "#f8fafc"; _tc = "#e2e8f0"; _fw = "400"
                    else:
                        _alpha = max(0.04, _pct * 0.35)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#94a3b8"; _fw = "500"
                    if _diag and _l1_labels[i] == "nuanced_rest":
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#f59e0b;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>→</span>"
                    elif _diag:
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#22c55e;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>✓</span>"
                    else:
                        _icon = ""
                    _l1_rows_html += f"<div style='background:{_bg};border-radius:4px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;'>{_icon}<div style='font-size:0.85rem;color:{_tc};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
                _l1_rows_html += "</div>"
            _l1_bot = f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};gap:3px;margin-top:4px;'><div></div>"
            for _lbl in _l1_labels:
                _l1_bot += f"<div style='font-size:0.56rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.3;'>{_lbl.replace('_',' ')}</div>"
            _l1_bot += "</div>"
            _l1_pred = f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};margin-top:8px;'><div></div><div style='grid-column:2/{_l1_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div></div>"

            _l2_cm = _l2["confusion_matrix"]
            _l2_labels = _l2["labels"]
            _l2_n = len(_l2_labels)
            _l2_row_sums = [sum(_l2_cm[i]) for i in range(_l2_n)]
            _l2_cw = 76
            _l2_grid_cols = f"90px " + " ".join([f"{_l2_cw}px"] * _l2_n)
            _l2_rows_html = ""
            for i in range(_l2_n):
                _rt = _l2_row_sums[i] if _l2_row_sums[i] > 0 else 1
                _display_lbl = _l2_labels[i].replace('_', ' ')
                _l2_rows_html += f"<div style='display:grid;grid-template-columns:{_l2_grid_cols};gap:3px;margin-bottom:3px;'>"
                _l2_rows_html += f"<div style='font-size:0.56rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;white-space:normal;word-break:break-word;line-height:1.3;'>{_display_lbl}</div>"
                for j in range(_l2_n):
                    _val = _l2_cm[i][j]
                    _pct = _val / _rt
                    _diag = (i == j)
                    if _diag:
                        _alpha = max(0.14, _pct * 0.85)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#fff" if _pct > 0.45 else "#21918c"
                        _fw = "700"
                    elif _val == 0:
                        _bg = "#f8fafc"; _tc = "#e2e8f0"; _fw = "400"
                    else:
                        _alpha = max(0.04, _pct * 0.35)
                        _bg = f"rgba(33,145,140,{_alpha:.2f})"
                        _tc = "#94a3b8"; _fw = "500"
                    if _diag:
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#22c55e;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>✓</span>"
                    else:
                        _icon = ""
                    _l2_rows_html += f"<div style='background:{_bg};border-radius:4px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;'>{_icon}<div style='font-size:0.85rem;color:{_tc};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
                _l2_rows_html += "</div>"
            _l2_bot = f"<div style='display:grid;grid-template-columns:{_l2_grid_cols};gap:3px;margin-top:4px;'><div></div>"
            for _lbl in _l2_labels:
                _l2_bot += f"<div style='font-size:0.56rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.3;'>{_lbl.replace('_',' ')}</div>"
            _l2_bot += "</div>"
            _l2_pred = f"<div style='display:grid;grid-template-columns:{_l2_grid_cols};margin-top:8px;'><div></div><div style='grid-column:2/{_l2_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div></div>"

            st.markdown(f"""
<div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;'>Cognitive Cascade · Theoretical Ceiling</div>
<div style='font-size:0.82rem;color:#777;line-height:1.6;font-family:Inter,sans-serif;font-weight:400;margin-bottom:24px;'>Layer 2 was evaluated in strict isolation using 100% of the ground-truth nuanced holdout. This prevents selection bias and establishes the theoretical performance ceiling of the Nuance Engine before introducing cascading errors from Layer 1.</div>
<div style='display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:center;padding-bottom:90px;'>
  <div>
    <div><div style='display:flex;gap:2px;align-items:center;'>
      <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
      <div>{_l1_rows_html}{_l1_bot}{_l1_pred}</div>
    </div></div>
  </div>
  <div style='display:flex;align-items:center;justify-content:center;'>
    <div style='width:32px;height:32px;border-radius:999px;background:rgba(33,145,140,0.10);display:flex;align-items:center;justify-content:center;'>
      <span style='color:#21918c;font-size:1rem;line-height:1;'>→</span>
    </div>
  </div>
  <div>
    <div><div style='display:flex;gap:2px;align-items:center;'>
      <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#94a3b8;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
      <div>{_l2_rows_html}{_l2_bot}{_l2_pred}</div>
    </div></div>
  </div>
</div>""", unsafe_allow_html=True)

            # ── Final callout ──────────────────────────────────────────────────────
            st.markdown("""
<div style='margin-top:48px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:14px 16px;'>
  <div style='font-size:0.72rem;font-weight:700;color:#21918c;margin-bottom:8px;'>The Architecture as the Answer</div>
  <div style='font-size:0.88rem;color:#334155;line-height:1.7;'>The monolith&#8217;s failure was not a data problem or a hyperparameter problem &#8212; it was a structural one. No amount of tuning resolves a 7:1 class imbalance when a dominant class shares feature space with a minority class. The Cognitive Cascade does not fight the gravity well. It sidesteps it entirely.</div>
</div>""", unsafe_allow_html=True)

        components.html("""<script>
setTimeout(function() {
  var doc = window.parent.document;
  var cardMono = doc.getElementById('c3card-mono');
  var cardCasc = doc.getElementById('c3card-casc');
  var btns = doc.querySelectorAll('button');
  var btnMono = null, btnCasc = null;
  btns.forEach(function(b) {
    var t = b.innerText.trim();
    if (t === 'mono') btnMono = b;
    if (t === 'casc') btnCasc = b;
  });
  if (btnMono) {
    var wrap = btnMono.closest('[data-testid="stElementContainer"]') || btnMono.parentElement;
    if (wrap) wrap.style.display = 'none';
    if (cardMono) cardMono.addEventListener('click', function() { btnMono.click(); });
  }
  if (btnCasc) {
    var wrap2 = btnCasc.closest('[data-testid="stElementContainer"]') || btnCasc.parentElement;
    if (wrap2) wrap2.style.display = 'none';
    if (cardCasc) cardCasc.addEventListener('click', function() { btnCasc.click(); });
  }
}, 400);
</script>""", height=1)

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
