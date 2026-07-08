import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import io
from components.styles import GLOBAL_CSS
from utils.bq_client import fetch_data_from_bq
from utils.gcp_client import _storage_client, fetch_bytes_from_gcs
from config import FAVICON


# ==============================================================================
# 1. CONFIGURACIÓN, ESTÉTICA Y QUANTUM SYNC (BLOQUE MAESTRO UNIFICADO)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Human vs AI: Behavioral Cloning", page_icon=FAVICON)

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
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big")
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
            pdf_data = fetch_bytes_from_gcs("pienza-streamlit", "Pienza_Papers.pdf")
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except Exception:
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
    /* Gray minimal slider for threshold simulator */
    [data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
        background-color: #94a3b8 !important;
        border-color: #94a3b8 !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] div[data-testid="stThumbValue"] {
        color: #64748b !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child > div:first-child {
        background-color: #cbd5e1 !important;
    }
    [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child > div:nth-child(2) {
        background-color: #94a3b8 !important;
    }
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
    client = _storage_client()
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
<div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;">
This phase documents the transition from descriptive discovery to a predictive inference engine.
The objective: synthesize a model capable of replicating the agent's decision policy with high fidelity —
and then beat it.
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["The Science", "Model Playoffs"])

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
  font-size:0.60rem; color:#64748b;
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
    <div class="ci-step-label">Architecture Design</div>
    <div class="ci-step-sub">Monolith vs Cascade</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P4</div>
    <div class="ci-step-label">Precision-Recall Tradeoff</div>
    <div class="ci-step-sub">Threshold Tuning</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P5</div>
    <div class="ci-step-label">SHAPs</div>
    <div class="ci-step-sub">Behavioral DNA decoded</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P6</div>
    <div class="ci-step-label">Bias-Variance Tradeoff</div>
    <div class="ci-step-sub">Lightweight model emerges</div>
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
  for (var j = 2; j < allTabs.length; j++) {
    if (allTabs[j].getAttribute('aria-selected') === 'true') { initIdx = j - 2; break; }
  }
  setActive(initIdx);

  steps.forEach(function(step, i) {
    step.addEventListener('click', function() {
      var target = allTabs[i + 2];
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

    sci1, sci2, sci3, sci4, sci5, sci6 = st.tabs([
        "Feature Selection",
        "Model Tournament",
        "Cognitive Cascade",
        "Threshold Calibrator",
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
<div style='font-size:0.90rem;color:#64748b;line-height:1.7;max-width:860px;margin-bottom:28px;'>
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
    <div style='margin-top:12px;font-size:0.75rem;color:#64748b;'>4,765 rows × 105 columns &nbsp;·&nbsp; 49 columns dropped</div>
    <div style='margin-top:10px;display:flex;flex-direction:column;gap:6px;'>
      <div style='display:flex;align-items:center;border-left:3px solid #21918c;padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#64748b;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Text &amp; Metadata</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>offer_id &nbsp;·&nbsp; feature_id &nbsp;·&nbsp; session_fk &nbsp;·&nbsp; ocr_fk</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+15</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>image_content_hash<br>dropoff_address<br>dropoff_ambiguity<br>dropoff_hdbscan_name<br>pickup_ambiguity<br>pickup_address<br>dropoff_polygon_name<br>offer_timestamp<br>comment_1<br>comment_2<br>special_note_raw<br>inferred_agent_bearing<br>is_imputed<br>record_status_fk<br>interpolation_quality_fk</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.6);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#64748b;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Leakage (EDA)</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_EDA &nbsp;·&nbsp; eph_realized_EDA &nbsp;·&nbsp; is_spread_downgrade_EDA &nbsp;·&nbsp; traffic_volatility_index_eda</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+6</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>eph_complete_index_EDA<br>eph_complete_label_EDA<br>eph_realized_index_EDA<br>eph_realized_label_EDA<br>is_total_cycle_downgrade_EDA<br>realized_traffic_index</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.4);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#64748b;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Leakage (Target)</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>offer_action_fk &nbsp;·&nbsp; reason_primary_fk &nbsp;·&nbsp; outcome_fk &nbsp;·&nbsp; post_offer_status_fk</span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.25);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#64748b;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Geo Coordinates</span>
        <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>pickup_lat &nbsp;·&nbsp; pickup_lon &nbsp;·&nbsp; dropoff_lat &nbsp;·&nbsp; dropoff_lon</span>
        <span class='fn-wrap' style='margin-left:auto;'><span class='fn-mark'>+2</span><span class='fn-tooltip' style='font-family:monospace;font-size:0.68rem;line-height:1.8;width:210px;right:0;left:auto;transform:none;'>inferred_agent_lat<br>inferred_agent_lon</span></span>
      </div>
      <div style='display:flex;align-items:center;border-left:3px solid rgba(33,145,140,0.1);padding:7px 12px;gap:12px;'>
        <span style='font-size:0.65rem;font-weight:700;color:#64748b;width:120px;flex-shrink:0;letter-spacing:0.5px;'>Manual Overrides</span>
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
      <div style='font-size:0.75rem;color:#64748b;margin-bottom:6px;'>4,765 rows × 56 columns &nbsp;·&nbsp; audit on 46 numerical &nbsp;·&nbsp; 5 dropped</div>
      <div style='display:grid;grid-template-columns:1fr 1fr 64px;gap:0;font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'>
        <span>DROPPED</span><span>SURVIVOR</span><span style='text-align:right;'>r</span>
      </div>
      <div style='border-left:3px solid #21918c;margin-top:4px;display:flex;flex-direction:column;'>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_direct <span style='color:#64748b;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_direct_index &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_operational <span style='color:#64748b;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_operational_index &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_realized_ML <span style='color:#64748b;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_realized_index_ML &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;border-bottom:1px solid rgba(0,0,0,0.04);'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_ML <span style='color:#64748b;'>(raw)</span> &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>eph_complete_index_ML &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;text-align:right;'>1.00</span>
        </div>
        <div style='display:grid;grid-template-columns:1fr 1fr 64px;padding:5px 12px;'>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>time_in_session_sec &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;'>cycle_cumulative_net_earnings &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span>
          <span style='font-family:monospace;font-size:0.68rem;color:#64748b;text-align:right;'>0.92</span>
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
        try:
            _lasso = _json.loads(_storage_client().bucket("pienza-streamlit").blob("lasso_liga_a.json").download_as_text())
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
                    f"<span style='font-family:monospace;font-size:0.65rem;color:#64748b;text-align:right;'>{c:.3f}</span>"
                    f"</div>"
                    for f, c in _top8
                )
                + "</div>"
            )
    
            _rest_tooltip = "<br>".join(
                f"{f} <span style='color:#64748b;'>({c:.3f})</span>"
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
        <div style='margin-top:12px;font-size:0.75rem;color:#64748b;'>4,765 rows × 51 columns &nbsp;·&nbsp; L1 audit on 41 numerical &nbsp;·&nbsp; C = 0.05</div>
        <div style='margin-top:10px;display:flex;gap:24px;align-items:start;'>
          <div style='flex:2;min-width:0;'>
            <div style='display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) 48px;gap:0 8px;font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'>
          <span>SURVIVOR</span><span>COEF</span><span style='text-align:right;'>val</span>
            </div>
            {_top8_html}
            <div style='padding:6px 12px;'>{_rest_pill}</div>
          </div>
          <div style='flex:1;min-width:0;'>
            <div style='font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'>CASUALTIES ({_n_cas})</div>
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
        <div style='margin-top:10px;font-size:0.75rem;color:#64748b;font-style:italic;'>Run 0501_PCA_allfeat.ipynb to populate results.</div>
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
        <div style='font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;'>Cumulative variance</div>
        <div style='display:flex;align-items:center;gap:8px;'>
          <div style='width:160px;height:8px;background:#e2e8f0;border-radius:4px;overflow:hidden;'>
        <div style='width:90%;height:100%;background:#21918c;border-radius:4px;'></div>
          </div>
          <span style='font-family:monospace;font-size:0.72rem;color:#21918c;font-weight:700;'>90%</span>
        </div>
        <div style='font-size:0.68rem;color:#64748b;margin-top:2px;'>captured by 12 of 20 components</div>
      </div>
      <div style='display:flex;flex-direction:column;gap:6px;'>
        <div style='font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:2px;'>Compression</div>
        <div style='font-family:monospace;font-size:0.72rem;color:#64748b;'>20 features &nbsp;→&nbsp; <span style='color:#21918c;font-weight:700;'>12 components</span></div>
        <div style='font-size:0.68rem;color:#64748b;'>40% dimensionality reduction</div>
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
      <div style='font-size:0.75rem;color:#64748b;margin-bottom:4px;'>10 categorical</div>
      <div style='border-left:3px solid #21918c;'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'><span>SPATIAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_h3_hex_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:100%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.967</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>83,801</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_polygon_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:70.7%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.684</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>69,959</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>dropoff_hdbscan_id &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:41.4%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.400</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>8,806</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>final_zone_id &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span> <span class='fn-wrap fn-left'><span class='fn-mark' style='font-size:0.65rem;color:#000;font-weight:900;cursor:default;border-bottom:none;'>ⓘ</span><span class='fn-tooltip' style='font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:220px;left:0;transform:none;'>A geospatial coalescence of manual polygons and HDBSCAN clusters. Selected over H3 hex grids to preserve domain explainability and prevent overfitting.</span></span></span><div style='height:5px;background:#21918c;border-radius:3px;width:69.4%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.671</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>24.9</span></div>
      </div>
      <div style='border-left:3px solid rgba(33,145,140,0.5);'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'><span>TEMPORAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>hour_of_day &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:100%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.071</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>257.9</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>day_of_week &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:35.2%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.025</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>101.2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>day_type &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:21.1%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.015</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>30.2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>time_of_day_block &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:12.7%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.009</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>38.9</span></div>
      </div>
      <div style='border-left:3px solid rgba(33,145,140,0.25);'>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;gap:3px 8px;font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.5px;padding:4px 12px;'><span>CONTEXTUAL</span><span></span><span style='text-align:right;'>MI</span><span style='text-align:right;'>CHI2</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>heuristic_flag_context &nbsp;<span style='color:#f59e0b;font-size:0.6rem;'>&#9888;</span> <span class='fn-wrap fn-left'><span class='fn-mark' style='font-size:0.65rem;color:#000;font-weight:900;cursor:default;border-bottom:none;'>ⓘ</span><span class='fn-tooltip' style='font-family:sans-serif;font-size:0.73rem;line-height:1.6;width:250px;left:0;transform:none;'>The dominant signal in early SHAP audits. Constitutes expert-encoded bias (data leakage); retained here strictly to establish the baseline for the algorithmic tournament.</span></span></span><div style='height:5px;background:#f59e0b;border-radius:3px;width:100%;opacity:0.6;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.302</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>8,472</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>product_category_fk &nbsp;<span style='color:#22c55e;font-size:0.6rem;'>✓</span></span><div style='height:5px;background:#21918c;border-radius:3px;width:10.9%;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.033</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>182.4</span></div>
        <div style='display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,0.9fr) 44px 56px;align-items:center;gap:3px 8px;padding:4px 12px;border-top:1px solid rgba(0,0,0,0.04);'><span style='font-family:monospace;font-size:0.68rem;color:#64748b;display:flex;align-items:center;gap:4px;'>driver_state_at_request_fk &nbsp;<span style='color:#ef4444;font-size:0.6rem;'>✕</span></span><div style='height:5px;background:rgba(100,116,139,0.25);border-radius:3px;width:1%;min-width:3px;'></div><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>0.003</span><span style='font-family:monospace;font-size:0.62rem;color:#64748b;text-align:right;'>18.9</span></div>
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
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Wide Set:Control Group</div>
        <div style='font-size:0.75rem;color:#64748b;line-height:1.5;'>Validates that expert pruning did not destroy latent signal.</div>
      </div>
      <div style='flex:1;min-width:180px;'>
        <span style='display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:1px;
          padding:3px 10px;border-radius:4px;background:rgba(33,145,140,0.10);
          color:#21918c;border:1px solid rgba(33,145,140,0.3);margin-bottom:8px;'>B-LEAGUE</span>
        <div style='font-size:0.72rem;color:#21918c;font-weight:600;margin-bottom:4px;'>20 numerical + 5 categorical</div>
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Curated:Raw</div>
        <div style='font-size:0.75rem;color:#64748b;line-height:1.5;'>Expert-selected raw scaled variables — preserves geometric splits for tree models.</div>
      </div>
      <div style='flex:1;min-width:180px;'>
        <span style='display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:1px;
          padding:3px 10px;border-radius:4px;background:rgba(33,145,140,0.10);
          color:#21918c;border:1px solid rgba(33,145,140,0.3);margin-bottom:8px;'>C-LEAGUE</span>
        <div style='font-size:0.72rem;color:#21918c;font-weight:600;margin-bottom:4px;'>12 components + 5 categorical</div>
        <div style='font-size:0.80rem;font-weight:600;color:#334155;margin-bottom:2px;'>Curated:PCA</div>
        <div style='font-size:0.75rem;color:#64748b;line-height:1.5;'>Orthogonal projection of B-League designed for linear and Bayesian purity.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='background:#FFFF00;border:3px solid #FFD700;padding:12px 18px;margin-top:32px;font-size:0.85rem;font-weight:700;color:#000;'>PENDING: reordenar Text &amp; Metadata</div>", unsafe_allow_html=True)

    with sci2:
        st.markdown("""
<div style='margin-bottom:32px;'>
  <div style='font-size:0.85rem;color:#777;line-height:1.6;margin-bottom:4px;font-family:'Source Sans Pro',sans-serif;font-weight:400;'>Five algorithms entered the arena in sequence, each benchmarked across all three feature leagues. This multi-trial framework is designed to capture the baseline predictive signal before introducing non-linear complexity.</div>
  <div style='display:flex;gap:28px;margin-top:14px;justify-content:center;'>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>Training</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>Weeks 1 &#8211; 5</div>
    </div>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>OOT Holdout</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>Week 6</div>
    </div>
    <div style='border-left:3px solid #21918c;padding:6px 12px;background:rgba(33,145,140,0.04);border-radius:0 6px 6px 0;'>
      <div style='font-size:0.58rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:2px;'>Scoring Metric</div>
      <div style='font-size:0.72rem;font-weight:600;color:#334155;'>F1-Macro</div>
    </div>
  </div>
</div>
<div style='border:1px solid rgba(0,0,0,0.07);border-radius:8px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;font-size:0.59rem;font-weight:700;color:#64748b;letter-spacing:0.6px;padding:8px 14px;background:#f8fafc;border-bottom:1px solid rgba(0,0,0,0.06);'>
    <span>TRIAL</span><span>ALGORITHM</span><span>TRAINING</span><span style='color:#64748b;'>A-LEAGUE</span><span style='color:#21918c;'>B-LEAGUE</span><span>C-LEAGUE</span>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#64748b;'>1 &nbsp;floor</span>
    <span style='font-size:0.72rem;color:#334155;'>Gaussian NB</span>
    <span style='font-size:0.68rem;color:#64748b;'>Chronological</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.257</span><div style='height:3px;background:#64748b;border-radius:2px;width:33.8%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.257</span><div style='height:3px;background:#21918c;border-radius:2px;width:33.8%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.256</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:33.6%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#64748b;'>2 &nbsp;linear</span>
    <span style='font-size:0.72rem;color:#334155;'>Logistic Regression</span>
    <span style='font-size:0.68rem;color:#64748b;'>Time-Series Split</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.482</span><div style='height:3px;background:#64748b;border-radius:2px;width:63.3%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.514</span><div style='height:3px;background:#21918c;border-radius:2px;width:67.5%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.490</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:64.4%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#64748b;'>3 &nbsp;theoretical</span>
    <span style='font-size:0.72rem;color:#334155;'>Logistic Reg (k-fold)</span>
    <span style='font-size:0.68rem;color:#64748b;'>Stratified K-Fold</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.687</span><div style='height:3px;background:#64748b;border-radius:2px;width:90.3%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.716</span><div style='height:3px;background:#21918c;border-radius:2px;width:94.1%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.691</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:90.8%;margin-top:3px;opacity:0.5;'></div></div>
  </div>
  <div style='display:grid;grid-template-columns:100px 1fr 150px 108px 108px 108px;gap:0 8px;align-items:center;padding:9px 14px;border-top:1px solid rgba(0,0,0,0.04);'>
    <span style='font-family:monospace;font-size:0.62rem;color:#64748b;'>4 &nbsp;scout</span>
    <span style='font-size:0.72rem;color:#334155;'>Decision Tree</span>
    <span style='font-size:0.68rem;color:#64748b;'>Time-Series Split</span>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.336</span><div style='height:3px;background:#64748b;border-radius:2px;width:44.2%;margin-top:3px;opacity:0.5;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#21918c;'>0.474</span><div style='height:3px;background:#21918c;border-radius:2px;width:62.3%;margin-top:3px;opacity:0.4;'></div></div>
    <div><span style='font-family:monospace;font-size:0.72rem;color:#64748b;'>0.373</span><div style='height:3px;background:#94a3b8;border-radius:2px;width:49.0%;margin-top:3px;opacity:0.5;'></div></div>
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
<div style='margin-top:10px;font-size:0.65rem;color:#64748b;font-style:italic;'>C-League retired at Trial 4 &#8212; PCA compression discards the variance XGBoost needs to split on.</div>
<div style='margin-top:56px;margin-bottom:56px;display:flex;align-items:center;gap:20px;justify-content:center;'>
  <div style='flex-shrink:0;text-align:center;'>
    <div style='font-family:monospace;font-size:2.4rem;font-weight:700;color:#21918c;line-height:1;'>0.761</div>
    <div style='font-size:0.58rem;font-weight:700;color:#64748b;letter-spacing:1px;margin-top:4px;'>F1-MACRO</div>
  </div>
  <div style='width:1px;height:48px;background:rgba(33,145,140,0.2);flex-shrink:0;'></div>
  <div>
    <div style='font-size:0.88rem;font-weight:700;color:#164e4b;margin-bottom:3px;'>XGBoost &nbsp;&#183;&nbsp; B-League (Curated Raw)</div>
    <div style='font-size:0.75rem;color:#64748b;line-height:1.6;'>OOT Holdout (W1&#8211;5 train, W6 test) &nbsp;&#183;&nbsp; Advances to Phase 3 as the behavioral cloning backbone.</div>
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
                f"<span style='font-size:0.59rem;font-weight:700;color:#64748b;letter-spacing:0.5px;text-align:center;'>{'W6 OOT' if w == _weeks[-1] else f'W{i+1}'}</span>"
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
                        f"<div style='font-family:monospace;font-size:0.55rem;color:#64748b;'>{n}</div>"
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
                f"<span style='font-family:monospace;font-size:0.60rem;color:#64748b;font-weight:700;letter-spacing:0.5px;'>TOTAL</span>"
                f"{_totals_cells}</div>"
            )
            _heatmap_html = (
                f"<div style='margin-top:56px;font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;'>A temporal breakdown of the target variables confirms the structural integrity of the dataset. Tracking class distribution across the six-week horizon validates that the agent&#8217;s decision policy does not suffer from fundamental concept drift, safely clearing the path for K-Fold shuffling.</div>"
                f"<div style='margin-top:28px;border-top:1px solid rgba(0,0,0,0.06);padding-top:20px;max-width:820px;margin-left:auto;margin-right:auto;'>"
                f"<div style='font-size:0.59rem;font-weight:700;color:#64748b;letter-spacing:1.5px;margin-bottom:10px;'>CLASS DISTRIBUTION BY WEEK &nbsp;&#8212;&nbsp; REASON PRIMARY</div>"
                f"<div style='display:grid;grid-template-columns:{_grid_cols};gap:4px;padding:0 0 6px;'><span></span>{_week_headers}</div>"
                f"{_rows_html}{_totals_row}"
                f"<div style='margin-top:8px;font-size:0.65rem;color:#64748b;font-style:italic;'>W6 = OOT holdout, unseen during training. Minority class shift across weeks motivates Stratified K-Fold over strict time-splits.</div>"
                f"</div>"
            )
            st.markdown(_heatmap_html, unsafe_allow_html=True)

    with sci3:
        import json as _json

        _client = _storage_client()
        _bucket = _client.bucket("pienza-streamlit")
        _mono = _json.loads(_bucket.blob("0508_monolith_metrics.json").download_as_text())
        _casc = _json.loads(_bucket.blob("0509_cascade_metrics.json").download_as_text())
        _l1    = _casc["layer1"]
        _l2    = _casc["layer2"]

        # ── Intro + comparison banner (always visible, above tabs) ────────────
        st.markdown("""
<div style='font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;margin-bottom:32px;'>
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
    <div style='font-size:0.55rem;color:#64748b;margin-bottom:6px;'>Single Stage:7 Classes</div>
    <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
      <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.61</div>
      <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
    </div>
    <div style='display:flex;gap:5px;flex-wrap:wrap;'>
      <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.941</span>
      <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 76%</span>
    </div>
  </div>
  <div style='padding:0 14px;color:#cbd5e1;font-size:1rem;text-align:center;'>→</div>
  <div class='bento-card'>
    <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;'>Cognitive Cascade</div>
    <div style='display:grid;grid-template-columns:1fr 1px 1fr;gap:0;'>
      <div style='padding-right:16px;'>
        <div style='font-size:0.55rem;color:#64748b;margin-bottom:6px;'>Layer 1:5 Classes</div>
        <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
          <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.76</div>
          <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
        </div>
        <div style='display:flex;gap:5px;flex-wrap:wrap;'>
          <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.941</span>
          <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 81%</span>
        </div>
      </div>
      <div style='background:#e2e8f0;'></div>
      <div style='padding-left:16px;'>
        <div style='font-size:0.55rem;color:#64748b;margin-bottom:6px;'>Layer 2:3 Classes</div>
        <div style='display:flex;align-items:baseline;gap:6px;margin-bottom:10px;'>
          <div style='font-family:monospace;font-size:1.8rem;font-weight:700;color:#64748b;line-height:1;'>0.91</div>
          <div style='font-size:0.55rem;font-weight:700;color:#b0bec5;letter-spacing:1px;text-transform:uppercase;'>F1-Macro</div>
        </div>
        <div style='display:flex;gap:5px;flex-wrap:wrap;'>
          <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>AUC 0.981</span>
          <span style='font-size:0.58rem;font-weight:600;color:#64748b;background:#f1f5f9;border-radius:999px;padding:2px 9px;'>Acc 91%</span>
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

        st.markdown('<div class="c3-hidden-btns">', unsafe_allow_html=True)
        if st.button("mono", key="btn_c3_mono"):
            st.session_state["c3_selected"] = "Monolith"
            st.rerun()
        if st.button("casc", key="btn_c3_casc"):
            st.session_state["c3_selected"] = "Cognitive Cascade"
            st.rerun()
        st.markdown('</div><style>.c3-hidden-btns{display:none!important;}</style>', unsafe_allow_html=True)



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

            # "nuanced →" bracket under the 3 nuanced columns
            _nuanced_cols = ["strategic_mismatch", "expected_value_gamble", "accepted"]
            _nc_positions = [i for i, l in enumerate(_mono_labels) if l in _nuanced_cols]
            if _nc_positions:
                _cw_mono       = 66    # px por columna del monolito
                _nc_offset_px  = 0     # ← ajuste fino en px (positivo = derecha, negativo = izquierda)
                _nc_margin     = 130 + min(_nc_positions) * _cw_mono + _nc_offset_px
                _nc_width      = len(_nc_positions) * _cw_mono
                _nuanced_bracket = (
                    f"<div style='margin-top:4px;margin-left:{_nc_margin}px;width:{_nc_width}px;"
                    f"display:flex;align-items:center;gap:4px;'>"
                    f"<div style='flex:1;height:1px;background:rgba(100,116,139,0.3);margin-left:40px;'></div>"
                    f"<span style='font-size:0.52rem;font-weight:700;color:#64748b;letter-spacing:0.8px;"
                    f"text-transform:uppercase;white-space:nowrap;'>nuanced</span>"
                    f"<div style='flex:1;height:1px;background:rgba(100,116,139,0.3);'></div>"
                    f"</div>"
                )
            else:
                _nuanced_bracket = ""

            # "Predicted" axis label centered under the data columns only
            _pred_label = f"<div style='display:grid;grid-template-columns:{_grid_cols};margin-top:8px;'>"
            _pred_label += "<div></div>"
            _pred_label += f"<div style='grid-column:2/{_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div>"
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
<div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:40px;'>Monolith Confusion Matrix:W6 OOT Holdout</div>
<div style='padding-bottom:90px;'>
<div style='width:fit-content;margin:0 auto;transform:scale(1.15) translateX(-70px);transform-origin:top center;'><div style='display:flex;gap:8px;align-items:center;'>
  <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
  <div>
    {_rows_html}
    {_bot}
    {_nuanced_bracket}
    {_pred_label}
  </div>
</div></div>
</div>
""", unsafe_allow_html=True)

            st.markdown("""<div style='margin-top:40px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:14px 18px;'>
  <div style='font-size:0.62rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Diagnostic</div>
  <div style='font-size:0.82rem;color:#334155;line-height:1.7;'>Due to the high similarity in the feature space of the nuanced classes, the model defaults to a "lazy" information gain strategy: it absorbs these complex, minority decisions into the <code style='font-size:0.75rem;background:rgba(33,145,140,0.12);padding:1px 5px;border-radius:3px;'>dropoff_non_operational</code> majority class instead of executing the deep splits required to isolate them.</div>
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div style='font-size:0.65rem;font-weight:600;color:#64748b;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:16px;margin-top:40px;border-left:2px solid rgba(33,145,140,0.3);padding-left:8px;'>Autopsy Report</div>
<div style='display:flex;justify-content:center;'><div style='display:inline-block;border:1px solid rgba(33,145,140,0.2);border-radius:6px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:100px 1fr 1fr 1fr;'>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);'></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Strategic Mismatch</div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Expected Value Gamble</div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Accepted</div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.62rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type II</div>
      <div style='font-size:0.58rem;color:#94a3b8;margin-top:1px;'>False Negative</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_sm_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_ev_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_ac_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;'>
      <div style='font-size:0.62rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type I</div>
      <div style='font-size:0.58rem;color:#94a3b8;margin-top:1px;'>False Positive</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_sm_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_ev_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_ac_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
  </div>
</div></div>
""", unsafe_allow_html=True)

            st.markdown("""
<div style='margin-top:28px;font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;'>
  A simultaneous collapse across both Type I and Type II metrics confirms a complete failure to map mathematical boundaries. With up to 96% of critical events undetected and severe false-alarm rates when triggered, the model isn&#8217;t inferring complex intent&#8202;&#8212;&#8202;it is simply guessing blindly.
</div>
<div style='margin-top:32px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:0.72rem;color:#64748b;font-family:monospace;text-align:center;'>
  Monolith &middot; F1-macro 0.61 &middot; <span style='color:#b91c1c;'>✗ architecture insufficient</span> &nbsp;&mdash;&mdash;&mdash;&nbsp; proceeding to Cognitive Cascade <span style='color:#21918c;'>→</span>
</div>
""", unsafe_allow_html=True)


        elif _c3_view == "Cognitive Cascade":
            st.markdown("""<div style='font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;margin-bottom:32px;'>
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
    <div style='font-size:0.55rem;font-weight:700;color:#64748b;'>19.4%</div>
    <div style='color:#21918c;font-size:1.1rem;'>→</div>
  </div>
  <div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>
    <div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>
      <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 2</div>
    </div>
    <div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>strategic_mismatch</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>expected_value_gamble</div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;'>accepted</div>
    </div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

            # ── Sections 3 + 4: L1 and L2 side by side ───────────────────────────
            # Canonical display order: mirrors Layer 1 box order (logical, matches monolith)
            # dropoff_non_op → proxy_zone → low_profitability → long_pickup → nuanced_rest
            _L1_CANONICAL = ["dropoff_non_operational", "dropoff_proxy_zone", "low_profitability", "long_pickup_time", "the_nuanced_rest"]
            _l1_cm_raw = _l1["confusion_matrix"]
            _l1_labels_raw = _l1["labels"]
            _l1_idx = [_l1_labels_raw.index(c) for c in _L1_CANONICAL if c in _l1_labels_raw]
            _l1_labels = [_l1_labels_raw[i] for i in _l1_idx]
            _l1_cm = [[_l1_cm_raw[r][c] for c in _l1_idx] for r in _l1_idx]
            _l1_n = len(_l1_labels)
            _l1_row_sums = [sum(_l1_cm[i]) for i in range(_l1_n)]
            _l1_cw = 76
            _l1_grid_cols = f"90px " + " ".join([f"{_l1_cw}px"] * _l1_n)
            _l1_rows_html = ""
            for i in range(_l1_n):
                _rt = _l1_row_sums[i] if _l1_row_sums[i] > 0 else 1
                _l1_display = {"the_nuanced_rest": "nuanced rest"}
                _display_lbl = _l1_display.get(_l1_labels[i], _l1_labels[i]).replace('_', ' ')
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
                    if _diag and _l1_labels[i] == "the_nuanced_rest":
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#f59e0b;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>→</span>"
                    elif _diag:
                        _icon = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#22c55e;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>✓</span>"
                    else:
                        _icon = ""
                    _l1_rows_html += f"<div style='background:{_bg};border-radius:4px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;'>{_icon}<div style='font-size:0.85rem;color:{_tc};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
                _l1_rows_html += "</div>"
            _l1_bot = f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};gap:3px;margin-top:4px;'><div></div>"
            for _lbl in _l1_labels:
                _l1_display_b = {"the_nuanced_rest": "nuanced rest"}
                _l1_bot += f"<div style='font-size:0.56rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.3;'>{_l1_display_b.get(_lbl, _lbl).replace('_',' ')}</div>"
            _l1_bot += "</div>"
            # "nuanced →" bracket over the last 4 columns (all except col 1 which is nuanced_rest itself)
            _l1_nuanced_bracket = (
                f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};margin-top:6px;'>"
                f"<div></div>"
                f"<div style='grid-column:2/{_l1_n+2};display:flex;align-items:center;gap:4px;padding:0 2px;'>"
                f"<div style='flex:1;height:1px;background:rgba(100,116,139,0.3);'></div>"
                f"<span style='font-size:0.52rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>nuanced →</span>"
                f"<div style='flex:1;height:1px;background:rgba(100,116,139,0.3);'></div>"
                f"</div></div>"
            )
            _l1_pred = f"<div style='display:grid;grid-template-columns:{_l1_grid_cols};margin-top:8px;'><div></div><div style='grid-column:2/{_l1_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div></div>"

            # Canonical L2 order: matches monolith column order for cognitive consistency
            _L2_CANONICAL = ["strategic_mismatch", "expected_value_gamble", "accepted"]
            _l2_cm_raw = _l2["confusion_matrix"]
            _l2_labels_raw = _l2["labels"]
            _l2_idx = [_l2_labels_raw.index(c) for c in _L2_CANONICAL if c in _l2_labels_raw]
            _l2_labels = [_l2_labels_raw[i] for i in _l2_idx]
            _l2_cm = [[_l2_cm_raw[r][c] for c in _l2_idx] for r in _l2_idx]
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
            _l2_pred = f"<div style='display:grid;grid-template-columns:{_l2_grid_cols};margin-top:8px;'><div></div><div style='grid-column:2/{_l2_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div></div>"

            st.markdown(f"""
<div style='font-size:0.82rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;margin-bottom:24px;'>Layer 2 was evaluated in strict isolation using 100% of the ground-truth nuanced holdout. This prevents selection bias and establishes the theoretical performance ceiling of the Nuance Engine before introducing cascading errors from Layer 1.</div>
<div style='display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:center;padding-bottom:25px;'>
  <div>
    <div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Layer 1</div>
    <div style='display:flex;gap:2px;align-items:center;'>
      <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
      <div>{_l1_rows_html}{_l1_bot}{_l1_pred}</div>
    </div>
  </div>
  <div style='display:flex;align-items:center;justify-content:center;'>
    <div style='width:32px;height:32px;border-radius:999px;background:rgba(33,145,140,0.10);display:flex;align-items:center;justify-content:center;'>
      <span style='color:#21918c;font-size:1rem;line-height:1;'>→</span>
    </div>
  </div>
  <div>
    <div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Layer 2</div>
    <div style='display:flex;gap:2px;align-items:center;'>
      <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
      <div>{_l2_rows_html}{_l2_bot}{_l2_pred}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            # ── Cascade Autopsy Report ─────────────────────────────────────────────
            _l1_cr  = _l1["classification_report"]
            _l2_cr  = _l2["classification_report"]
            _nr     = _l1_cr.get("the_nuanced_rest", {})
            _c_sm   = _l2_cr.get("strategic_mismatch", {})
            _c_ev   = _l2_cr.get("expected_value_gamble", {})
            _c_ac   = _l2_cr.get("accepted", {})
            _nr_t2  = round((1 - _nr.get("recall", 1))     * 100)
            _nr_t1  = round((1 - _nr.get("precision", 1))  * 100)
            _csm_t2 = round((1 - _c_sm.get("recall", 1))   * 100)
            _csm_t1 = round((1 - _c_sm.get("precision", 1))* 100)
            _cev_t2 = round((1 - _c_ev.get("recall", 1))   * 100)
            _cev_t1 = round((1 - _c_ev.get("precision", 1))* 100)
            _cac_t2 = round((1 - _c_ac.get("recall", 1))   * 100)
            _cac_t1 = round((1 - _c_ac.get("precision", 1))* 100)
            _mono_cr      = _mono["classification_report"]
            _m_sm_r       = round(_mono_cr.get("strategic_mismatch",    {}).get("recall", 0) * 100)
            _m_ev_r       = round(_mono_cr.get("expected_value_gamble", {}).get("recall", 0) * 100)
            _m_ac_r       = round(_mono_cr.get("accepted",              {}).get("recall", 0) * 100)
            _l2_min_recall = min(100 - _csm_t2, 100 - _cev_t2, 100 - _cac_t2)
            st.markdown(f"""
<div style='margin-top:0;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:14px 18px;margin-bottom:20px;'>
  <div style='font-size:0.62rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Diagnostic</div>
  <div style='font-size:0.82rem;color:#334155;line-height:1.7;'>Shattering the monolith&#8217;s baseline of {_m_sm_r}%, {_m_ev_r}%, and {_m_ac_r}%, Layer 2 achieves a theoretical recall ceiling of &gt;{_l2_min_recall}% across all three nuanced classes.</div>
</div>
<div style='font-size:0.65rem;font-weight:600;color:#64748b;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:16px;margin-top:40px;border-left:2px solid rgba(33,145,140,0.3);padding-left:8px;'>Autopsy Report</div>
<div style='display:flex;justify-content:center;'><div style='display:inline-block;border:1px solid rgba(33,145,140,0.2);border-radius:6px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:100px 1fr 1fr 1fr 1fr;'>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);'></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Nuanced Rest &nbsp;<span style='font-size:0.50rem;color:#94a3b8;font-weight:500;letter-spacing:0;'>L1</span></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:2px solid rgba(33,145,140,0.35);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Strategic Mismatch &nbsp;<span style='font-size:0.50rem;color:#94a3b8;font-weight:500;letter-spacing:0;'>L2</span></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Expected Value Gamble &nbsp;<span style='font-size:0.50rem;color:#94a3b8;font-weight:500;letter-spacing:0;'>L2</span></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Accepted &nbsp;<span style='font-size:0.50rem;color:#94a3b8;font-weight:500;letter-spacing:0;'>L2</span></div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.62rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type II</div>
      <div style='font-size:0.58rem;color:#94a3b8;margin-top:1px;'>False Negative</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_nr_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:2px solid rgba(33,145,140,0.35);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_csm_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_cev_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_cac_t2}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>undetected</div>
    </div>
    <div style='padding:8px 10px;'>
      <div style='font-size:0.62rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;'>Type I</div>
      <div style='font-size:0.58rem;color:#94a3b8;margin-top:1px;'>False Positive</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_nr_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
    <div style='padding:8px 10px;border-left:2px solid rgba(33,145,140,0.35);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_csm_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_cev_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.6);line-height:1;'>{_cac_t1}%</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:2px;'>false alarms</div>
    </div>
  </div>
</div></div>
""", unsafe_allow_html=True)

            st.markdown("""
<div style='margin-top:28px;font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;'>
  This autopsy validates the hierarchical pivot. Layer&#160;1&#8217;s controlled 31% signal loss acts as a necessary firewall, driving Layer&#160;2&#8217;s false alarms and undetected rates down from 96% to single digits.
</div>
<div style='margin-top:32px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:0.72rem;color:#64748b;font-family:monospace;text-align:center;'>
  Cognitive Cascade &middot; theoretical ceiling established &middot; <span style='color:#21918c;'>✓ cascade architecture validated</span> &nbsp;&mdash;&mdash;&mdash;&nbsp; next phase: threshold tuning <span style='color:#21918c;'>→</span>
</div>
""", unsafe_allow_html=True)





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
        # ── Threshold Simulator ───────────────────────────────────────────────
        st.markdown("""
<div style='font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;margin-bottom:24px;'>To simulate real-world production, this interactive module enables tuning Layer&#160;1&#8217;s <code style='font-size:0.82rem;background:rgba(33,145,140,0.08);color:#21918c;padding:1px 5px;border-radius:3px;'>nuanced_rest</code> recall threshold, visualizing exactly what survives the initial filter to feed Layer&#160;2.</div>
""", unsafe_allow_html=True)

        @st.cache_data(show_spinner=False)
        def _load_sim_parquet_v3():
            from io import BytesIO
            _b = _storage_client().bucket("pienza-streamlit")
            return pd.read_parquet(BytesIO(_b.blob("0509_sim_proba.parquet").download_as_bytes()))

        _df_sim = _load_sim_parquet_v3()

        if "sim_thresh_pct" not in st.session_state:
            st.session_state["sim_thresh_pct"] = 50

        _thresh_pct = st.session_state["sim_thresh_pct"]
        _T = _thresh_pct / 100

        st.markdown("<div style='font-size:0.52rem;font-weight:600;color:#21918c;letter-spacing:1.5px;text-transform:uppercase;font-family:monospace;margin-bottom:4px;'>Layer 1:nuanced_rest classification threshold</div>", unsafe_allow_html=True)
        st.slider(
            label="threshold",
            label_visibility="collapsed",
            key="sim_thresh_pct",
            min_value=1, max_value=99, step=1, format="%d%%",
            help="Adjusts the probability cutoff at which Layer 1 routes an observation to Layer 2 as nuanced_rest. At 50% (sklearn default) the behavior matches the static matrices above. Lower = more signal captured, more noise introduced."
        )

        import re as _re2
        def _norm(s): return _re2.sub(r'[^\w]+', '_', str(s)).strip('_').lower()

        _l1_other_cols = ["dropoff_non_operational", "dropoff_proxy_zone", "long_pickup_time", "low_profitability"]
        _pred_l1 = _df_sim[_l1_other_cols].idxmax(axis=1).copy()
        _pred_l1[_df_sim["the_nuanced_rest"] >= _T] = "the_nuanced_rest"

        _SIM_L1_ORDER = ["dropoff_non_operational", "dropoff_proxy_zone", "low_profitability", "long_pickup_time", "the_nuanced_rest"]
        _sim_l1_ytrue = _df_sim["y_true_l1"].apply(_norm)
        _sim_l1_cm = [
            [int(((_sim_l1_ytrue == tc) & (_pred_l1 == pc)).sum()) for pc in _SIM_L1_ORDER]
            for tc in _SIM_L1_ORDER
        ]
        _sim_l1_n = len(_SIM_L1_ORDER)
        _sim_l1_row_sums = [sum(r) for r in _sim_l1_cm]
        _sim_l1_display = {"the_nuanced_rest": "nuanced rest"}
        _sim_l1_cw = 96
        _sim_l1_grid = f"110px " + " ".join([f"{_sim_l1_cw}px"] * _sim_l1_n)

        _sim_l1_rows = ""
        for i, tc in enumerate(_SIM_L1_ORDER):
            _rt = _sim_l1_row_sums[i] or 1
            _lbl = _sim_l1_display.get(tc, tc).replace("_", " ")
            _sim_l1_rows += f"<div style='display:grid;grid-template-columns:{_sim_l1_grid};gap:3px;margin-bottom:3px;'>"
            _sim_l1_rows += f"<div style='font-size:0.56rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;white-space:normal;word-break:break-word;line-height:1.3;'>{_lbl}</div>"
            for j, pc in enumerate(_SIM_L1_ORDER):
                _val = _sim_l1_cm[i][j]; _pct = _val / _rt; _diag = (i == j)
                if _diag:
                    _alpha = max(0.14, _pct * 0.85)
                    _bg = f"rgba(33,145,140,{_alpha:.2f})"; _tc2 = "#fff" if _pct > 0.45 else "#21918c"; _fw = "700"
                elif _val == 0:
                    _bg = "#f8fafc"; _tc2 = "#e2e8f0"; _fw = "400"
                else:
                    _bg = f"rgba(33,145,140,{max(0.04,_pct*0.35):.2f})"; _tc2 = "#94a3b8"; _fw = "500"
                if _diag and tc == "the_nuanced_rest":
                    _ico = "<span style='position:absolute;top:-8px;right:-6px;font-size:0.75rem;color:#f59e0b;background:#fff;border-radius:999px;line-height:1;padding:2px;box-shadow:0 1px 3px rgba(0,0,0,0.12);'>→</span>"
                else:
                    _ico = ""
                _border = "box-shadow:0 0 0 2px rgba(245,158,11,0.55);" if (_diag and tc == "the_nuanced_rest") else ""
                _sim_l1_rows += f"<div style='background:{_bg};border-radius:4px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;{_border}'>{_ico}<div style='font-size:0.85rem;color:{_tc2};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
            _sim_l1_rows += "</div>"
        _sim_l1_bot = f"<div style='display:grid;grid-template-columns:{_sim_l1_grid};gap:3px;margin-top:4px;'><div></div>"
        for _lbl in _SIM_L1_ORDER:
            _sim_l1_bot += f"<div style='font-size:0.56rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.3;'>{_sim_l1_display.get(_lbl,_lbl).replace('_',' ')}</div>"
        _sim_l1_bot += "</div>"
        _sim_l1_pred = f"<div style='display:grid;grid-template-columns:{_sim_l1_grid};margin-top:8px;'><div></div><div style='grid-column:2/{_sim_l1_n+2};text-align:center;font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;'>Predicted</div></div>"

        _SIM_L2_ORDER  = ["strategic_mismatch", "expected_value_gamble", "accepted"]
        _routed_mask   = (_pred_l1 == "the_nuanced_rest") & _df_sim["y_true_l2"].notna()
        _df_routed     = _df_sim[_routed_mask]
        _pred_l2       = _df_routed[[f"l2_{c}" for c in _SIM_L2_ORDER]].idxmax(axis=1).str.replace("l2_", "", regex=False)
        _ytrue_l2_sim  = _df_routed["y_true_l2"].apply(_norm)
        _sim_l2_cm     = [
            [int(((_ytrue_l2_sim == tc) & (_pred_l2 == pc)).sum()) for pc in _SIM_L2_ORDER]
            for tc in _SIM_L2_ORDER
        ]
        _sim_l2_n        = len(_SIM_L2_ORDER)
        _sim_l2_row_sums = [sum(r) for r in _sim_l2_cm]
        _sm_cw  = 52
        _sm_lw  = 70
        _sim_l2_grid = f"{_sm_lw}px " + " ".join([f"{_sm_cw}px"] * _sim_l2_n)

        _sim_l2_rows = ""
        for i, tc in enumerate(_SIM_L2_ORDER):
            _rt = _sim_l2_row_sums[i] or 1
            _sim_l2_rows += f"<div style='display:grid;grid-template-columns:{_sim_l2_grid};gap:2px;margin-bottom:2px;'>"
            _sim_l2_rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:6px;align-self:center;white-space:normal;word-break:break-word;line-height:1.2;'>{tc.replace('_',' ')}</div>"
            for j, pc in enumerate(_SIM_L2_ORDER):
                _val = _sim_l2_cm[i][j]; _pct = _val / _rt; _diag = (i == j)
                if _diag:
                    _bg = f"rgba(33,145,140,{max(0.14,_pct*0.85):.2f})"; _tc2 = "#fff" if _pct > 0.45 else "#21918c"; _fw = "700"
                elif _val == 0:
                    _bg = "#f8fafc"; _tc2 = "#e2e8f0"; _fw = "400"
                else:
                    _bg = f"rgba(33,145,140,{max(0.04,_pct*0.35):.2f})"; _tc2 = "#94a3b8"; _fw = "500"
                _sim_l2_rows += f"<div style='background:{_bg};border-radius:3px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;'><div style='font-size:0.72rem;color:{_tc2};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
            _sim_l2_rows += "</div>"
        _sim_l2_bot  = f"<div style='display:grid;grid-template-columns:{_sim_l2_grid};gap:2px;margin-top:4px;'><div></div>"
        _sim_l2_bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.2;'>{l.replace('_',' ')}</div>" for l in _SIM_L2_ORDER)
        _sim_l2_bot += "</div>"
        _sim_l2_pred = f"<div style='display:grid;grid-template-columns:{_sim_l2_grid};margin-top:6px;'><div></div><div style='grid-column:2/{_sim_l2_n+2};text-align:center;font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>Predicted</div></div>"

        _fp_mask       = (_pred_l1 == "the_nuanced_rest") & (_sim_l1_ytrue != "the_nuanced_rest")
        _df_fp         = _df_sim[_fp_mask]
        _fp_count      = len(_df_fp)
        _FP_ROW_ORDER  = ["dropoff_non_operational", "dropoff_proxy_zone", "low_profitability", "long_pickup_time"]
        _pred_fp_l2    = _df_fp[[f"l2_{c}" for c in _SIM_L2_ORDER]].fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False)
        _ytrue_fp      = _sim_l1_ytrue[_fp_mask]
        _sim_fp_display = {"dropoff_non_operational": "non operational", "dropoff_proxy_zone": "proxy zone",
                           "low_profitability": "low profit", "long_pickup_time": "long pickup"}
        _sim_fp_cm     = [
            [int(((_ytrue_fp == tc) & (_pred_fp_l2 == pc)).sum()) for pc in _SIM_L2_ORDER]
            for tc in _FP_ROW_ORDER
        ]
        _sim_fp_row_sums = [sum(r) for r in _sim_fp_cm]

        _sim_fp_rows = ""
        for i, tc in enumerate(_FP_ROW_ORDER):
            _rt = _sim_fp_row_sums[i] or 1
            _lbl = _sim_fp_display.get(tc, tc)
            _sim_fp_rows += f"<div style='display:grid;grid-template-columns:{_sm_lw}px {' '.join([f'{_sm_cw}px']*_sim_l2_n)};gap:2px;margin-bottom:2px;'>"
            _sim_fp_rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:6px;align-self:center;white-space:normal;word-break:break-word;line-height:1.2;'>{_lbl}</div>"
            for j, pc in enumerate(_SIM_L2_ORDER):
                _val = _sim_fp_cm[i][j]; _pct = _val / _rt
                if _val == 0:
                    _bg = "#f8fafc"; _tc2 = "#e2e8f0"; _fw = "400"
                else:
                    _bg = f"rgba(100,116,139,{max(0.08,_pct*0.55):.2f})"; _tc2 = "#1e293b"; _fw = "500"
                _sim_fp_rows += f"<div style='background:{_bg};border-radius:3px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;'><div style='font-size:0.72rem;color:{_tc2};font-weight:{_fw};'>{_pct*100:.0f}%</div></div>"
            _sim_fp_rows += "</div>"

        _sim_fp_grid = f"{_sm_lw}px " + " ".join([f"{_sm_cw}px"] * _sim_l2_n)
        _sim_fp_bot  = f"<div style='display:grid;grid-template-columns:{_sim_fp_grid};gap:2px;margin-top:4px;'><div></div>"
        _sim_fp_bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.2;'>{l.replace('_',' ')}</div>" for l in _SIM_L2_ORDER)
        _sim_fp_bot += "</div>"
        _sim_fp_pred = f"<div style='display:grid;grid-template-columns:{_sim_fp_grid};margin-top:6px;'><div></div><div style='grid-column:2/{_sim_l2_n+2};text-align:center;font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>L2 Predicted</div></div>"

        _nr_routed = int(_routed_mask.sum())
        _nr_total  = int((_sim_l1_ytrue == "the_nuanced_rest").sum())

        st.markdown(f"""
<div style='display:flex;align-items:center;gap:0;margin-bottom:28px;justify-content:center;'>
  <div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>
    <div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>
      <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 1</div>
    </div>
    <div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;display:flex;justify-content:space-between;'>
        <span>total holdout</span><span style='font-weight:700;color:#64748b;'>{len(_df_sim)}</span>
      </div>
      <div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'>
        <span>→ nuanced_rest</span><span>{_nr_routed + _fp_count}</span>
      </div>
    </div>
  </div>
  <div style='display:flex;flex-direction:column;align-items:center;gap:3px;padding:0 16px;'>
    <div style='font-size:0.55rem;font-weight:700;color:#64748b;'>{round(_nr_routed/len(_df_sim)*100,1)}%</div>
    <div style='color:#21918c;font-size:1.1rem;'>→</div>
  </div>
  <div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>
    <div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>
      <div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 2</div>
    </div>
    <div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>
      <div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'>
        <span>true nuanced</span><span>{_nr_routed}</span>
      </div>
      <div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;font-weight:600;display:flex;justify-content:space-between;'>
        <span>false positives</span><span>{_fp_count}</span>
      </div>
    </div>
  </div>
</div>
<div style='display:grid;grid-template-columns:1fr auto 1fr;gap:24px;align-items:start;padding-bottom:25px;'>
  <div>
    <div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Layer 1</div>
    <div style='display:flex;gap:2px;align-items:center;'>
      <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.62rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
      <div>{_sim_l1_rows}{_sim_l1_bot}{_sim_l1_pred}</div>
    </div>
  </div>
  <div style='align-self:start;display:flex;align-items:center;justify-content:center;padding-top:96px;'>
    <div style='width:32px;height:32px;border-radius:999px;background:rgba(33,145,140,0.10);display:flex;align-items:center;justify-content:center;'>
      <span style='color:#21918c;font-size:1rem;line-height:1;'>→</span>
    </div>
  </div>
  <div style='display:flex;flex-direction:column;gap:0;align-items:start;'>
    <div>
      <div style='font-size:0.72rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Layer 2</div>
      <div style='display:flex;gap:2px;align-items:center;'>
        <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;white-space:nowrap;align-self:center;'>Real</div>
        <div>{_sim_l2_rows}{_sim_l2_bot}{_sim_l2_pred}</div>
      </div>
    </div>
    <div style='display:flex;align-items:center;padding-left:138px;margin-top:6px;margin-bottom:6px;'>
      <div style='width:24px;height:24px;border-radius:999px;background:rgba(100,116,139,0.10);display:flex;align-items:center;justify-content:center;'>
        <span style='color:#64748b;font-size:0.8rem;line-height:1;'>↓</span>
      </div>
    </div>
    <div>
      <div style='font-size:0.72rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>L1 False Positives:Routed to L2</div>
      <div style='display:flex;gap:2px;align-items:center;'>
        <div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;white-space:nowrap;align-self:center;'>L1 Real</div>
        <div>{_sim_fp_rows}{_sim_fp_bot}{_sim_fp_pred}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── Accepted class tracking table ─────────────────────────────────────
        import re as _re3
        def _norm2(s): return _re3.sub(r'[^\w]+', '_', str(s)).strip('_').lower()

        _l2_cols = ["l2_strategic_mismatch", "l2_expected_value_gamble", "l2_accepted"]
        _l2_pred_all = _df_sim[_l2_cols].fillna(0).idxmax(axis=1).str.replace("l2_", "").apply(_norm2)

        _true_accepted_mask = _df_sim["y_true_l2"].apply(_norm2) == "accepted"
        _a1_total = int(_true_accepted_mask.sum())

        _accepted_offer_ids = _df_sim.loc[_true_accepted_mask, "offer_id"].tolist()
        _ids_sql = ", ".join([f"'{x}'" for x in _accepted_offer_ids])

        @st.cache_data(show_spinner=False)
        def _load_realized_fares(ids_key: str) -> dict:
            _q = f"""
            SELECT offer_id, realized_fare
            FROM `645009831643.pienza_mini.v_mission_dossier`
            WHERE offer_id IN ({ids_key})
              AND realized_fare IS NOT NULL
            """
            _df = fetch_data_from_bq(_q)
            return dict(zip(_df["offer_id"], _df["realized_fare"]))

        _fare_map = _load_realized_fares(_ids_sql)
        _a1_earnings = sum(_fare_map.get(oid, 0) for oid in _accepted_offer_ids)

        def _accepted_breakdown(pred_l1_series):
            _routed = pred_l1_series == "the_nuanced_rest"
            _ta_routed = _true_accepted_mask & _routed
            _n_routed  = int(_ta_routed.sum())
            _l2p = _l2_pred_all[_ta_routed]
            _fp_routed = _routed & ~_true_accepted_mask & _df_sim["y_true_l2"].isna()
            _phantom = int((_l2_pred_all[_fp_routed] == "accepted").sum())
            _correct_ids = _df_sim.loc[_ta_routed & (_l2_pred_all == "accepted"), "offer_id"].tolist()
            _earn_correct = sum(_fare_map.get(oid, 0) for oid in _correct_ids)
            _phantom_uf   = _df_sim.loc[_fp_routed & (_l2_pred_all == "accepted"), "upfront_fare"]
            _earn_phantom = float((6.31 + 0.79 * _phantom_uf).sum())
            return {
                "routed":        _n_routed,
                "correct":       int((_l2p == "accepted").sum()),
                "to_sm":         int((_l2p == "strategic_mismatch").sum()),
                "to_ev":         int((_l2p == "expected_value_gamble").sum()),
                "phantom":       _phantom,
                "earn_correct":  _earn_correct,
                "earn_phantom":  _earn_phantom,
                "earn_total":    _earn_correct + _earn_phantom,
            }

        _pred_l1_50 = _df_sim[_l1_other_cols].idxmax(axis=1).copy()
        _pred_l1_50[_df_sim["the_nuanced_rest"] >= 0.5] = "the_nuanced_rest"
        _a2 = _accepted_breakdown(_pred_l1_50)
        _a3 = _accepted_breakdown(_pred_l1)

        def _pct(n, d): return f"({round(n/d*100)}%)" if d > 0 else ""

        _ai_ne_human_a2 = _a2["to_sm"] + _a2["to_ev"] + _a2["phantom"]
        _ai_ne_human_a3 = _a3["to_sm"] + _a3["to_ev"] + _a3["phantom"]

        st.markdown(f"""
<div style='margin-top:16px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0;padding:14px 18px;'>
  <div style='font-size:0.62rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Precision–Recall Tradeoff</div>
  <div style='font-size:0.82rem;color:#334155;line-height:1.7;'>Pushing the threshold toward 100% maximizes conditional precision in Layer 2 at the cost of a recall collapse, allowing very few offers to pass the initial filter. Conversely, pushing it toward 0% preserves recall but introduces a high volume of False Positives into Layer 2, degrading the decision boundaries required to resolve strategic intent.</div>
</div>
<div style='margin-top:32px;font-size:0.85rem;color:#777;line-height:1.6;font-family:'Source Sans Pro',sans-serif;font-weight:400;margin-bottom:20px;'>To measure the real-world impact of this tradeoff, the scorecard below translates classification thresholds into financial outcomes, comparing the AI's dynamic yield against the human baseline.</div>
<div style='display:flex;justify-content:center;'><div style='display:inline-block;border:1px solid rgba(33,145,140,0.2);border-radius:6px;overflow:hidden;'>
  <div style='display:grid;grid-template-columns:200px 160px 160px 160px;'>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;'>Accepted</div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Human <span style='font-size:0.58rem;color:#94a3b8;font-weight:500;letter-spacing:0;text-transform:none;'>Ground Truth</span></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.65rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>AI <span style='font-size:0.58rem;color:#94a3b8;font-weight:500;letter-spacing:0;text-transform:none;'>Default Threshold</span></div>
    <div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:2px solid rgba(33,145,140,0.4);text-align:center;font-size:0.65rem;font-weight:700;color:#21918c;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>AI <span style='font-size:0.58rem;color:#21918c;font-weight:500;letter-spacing:0;text-transform:none;'>Active:{_thresh_pct}%</span></div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.72rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Human Only</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_a1_total}</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#94a3b8;line-height:1;'>—</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:2px solid rgba(33,145,140,0.4);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#94a3b8;line-height:1;'>—</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.72rem;font-weight:700;color:#21918c;text-transform:uppercase;letter-spacing:0.5px;'>Human = AI</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:1px;'>both accepted</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#94a3b8;line-height:1;'>—</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='display:flex;align-items:baseline;justify-content:center;gap:4px;'><span style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_a2["correct"]}</span><span style='font-size:0.55rem;color:#94a3b8;'>{_pct(_a2["correct"],_a2["routed"])}</span></div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:2px solid rgba(33,145,140,0.4);text-align:center;'>
      <div style='display:flex;align-items:baseline;justify-content:center;gap:4px;'><span style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>{_a3["correct"]}</span><span style='font-size:0.55rem;color:#94a3b8;'>{_pct(_a3["correct"],_a3["routed"])}</span></div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'>
      <div style='font-size:0.72rem;font-weight:700;color:rgba(33,145,140,0.55);text-transform:uppercase;letter-spacing:0.5px;'>AI ≠ Human</div>
      <div style='font-size:0.52rem;color:#94a3b8;margin-top:1px;'>AI accepted, human rejected</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#94a3b8;line-height:1;'>—</div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='display:flex;align-items:baseline;justify-content:center;gap:4px;'><span style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.55);line-height:1;'>{_ai_ne_human_a2}</span><span style='font-size:0.55rem;color:#94a3b8;'>{_pct(_ai_ne_human_a2,_a1_total)}</span></div>
    </div>
    <div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:2px solid rgba(33,145,140,0.4);text-align:center;'>
      <div style='display:flex;align-items:baseline;justify-content:center;gap:4px;'><span style='font-family:monospace;font-size:1.15rem;font-weight:700;color:rgba(33,145,140,0.55);line-height:1;'>{_ai_ne_human_a3}</span><span style='font-size:0.55rem;color:#94a3b8;'>{_pct(_ai_ne_human_a3,_a1_total)}</span></div>
    </div>
    <div style='position:relative;padding:8px 10px;'>
      <div style='font-size:0.72rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Cumulative earnings</div>
      <span class='fn-wrap' style='position:absolute;top:6px;right:8px;'><span class='fn-mark' style='color:#21918c;font-size:0.6rem;'>ⓘ</span><span class='fn-tooltip' style='width:380px;white-space:normal;font-family:sans-serif;font-size:0.73rem;line-height:1.7;text-transform:none;letter-spacing:0;font-weight:400;color:#334155;'><strong>Imputation method (AI ≠ Human trips)</strong><br>Human earnings are verified realized fares. Non-realized AI fares are estimated via the Causal Inference polynomial model at ΔT = 1.0:<br><br><span style='font-family:monospace;font-size:0.78rem;background:rgba(33,145,140,0.08);padding:4px 8px;border-radius:4px;display:block;white-space:nowrap;'>F̂(ΔT=1) = 6.31 + 0.79:Upfront Fare</span></span></span>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>${_a1_earnings:,.0f}</div>
    </div>
    <div style='padding:8px 10px;border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>${_a2["earn_total"]:,.0f}</div>
    </div>
    <div style='padding:8px 10px;border-left:2px solid rgba(33,145,140,0.4);text-align:center;'>
      <div style='font-family:monospace;font-size:1.15rem;font-weight:700;color:#21918c;line-height:1;'>${_a3["earn_total"]:,.0f}</div>
    </div>
  </div>
</div></div>
<div style='margin-top:40px;background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0;padding:14px 18px;'>
  <div style='font-size:0.62rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Simulator scope caveat</div>
  <div style='font-size:0.82rem;color:#334155;line-height:1.6;'>Both mathematical extremes would fail in real-world operations. While very low thresholds imply a volume that breaks physical transit constraints, extreme high thresholds starve the agent of operational volume, leaving them with too few viable options to generate meaningful earnings.</div>
</div>
<div style='margin-top:32px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:0.72rem;color:#64748b;font-family:monospace;text-align:center;'>
  Cognitive Cascade &middot; <span style='color:#21918c;'>✓ behavioral cloning · success</span> &nbsp;&mdash;&mdash;&mdash;&nbsp; proceeding to Decode Behavioral DNA <span style='color:#21918c;'>→</span>
</div>
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;padding:12px 16px;margin-top:16px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;color:#cc6600;'>⚠ PENDING — Layout experiment</span><br><br>
  Jugar con el orden de matrices: idea: mover la matriz de FP hacia abajo y colocar la tabla de Accepted en el espacio vacío que quedaría a la derecha de L1 (actualmente ocupado por el layout de L2+FP). Esto pondría la narrativa de earnings directamente al lado de la acción de L1, sin hacer scroll.
</div>
""", unsafe_allow_html=True)

    with sci5:
        # ── Load SHAP data ────────────────────────────────────────────────────
        @st.cache_data(show_spinner=False)
        def _load_shap_l1():
            from io import BytesIO
            return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("0509_shap_l1_nuanced.parquet").download_as_bytes()))

        @st.cache_data(show_spinner=False)
        def _load_shap_l2():
            from io import BytesIO
            return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("0509_shap_l2.parquet").download_as_bytes()))

        _df_shap_l1 = _load_shap_l1()
        _df_shap_l2 = _load_shap_l2()

        # ── Clean labels — snake_case, strip implementation suffixes ─────────
        _LABEL_CLEAN = {
            # L1
            "time_to_pickup_sec":                   "time_to_pickup",
            "upfront_fare":                         "upfront_fare",
            "log_upfront_fare":                     "upfront_fare",
            "eph_operational_index":                "eph_operational_index",
            "est_trip_time_sec":                    "est_trip_time",
            "historical_rolling_avg_traffic_index": "rolling_avg_traffic_index",
            "traffic_index_base_120":               "traffic_index_base_120",
            "traffic_volatility_index_ml":          "traffic_volatility_index",
            "log_traffic_volatility_index_ml":      "traffic_volatility_index",
            "log_traffic_index_base_120":           "traffic_index_base_120",
            "time_since_last_offer":                "time_since_last_offer",
            "consecutive_rejects":                  "consecutive_rejects",
            "session_progress_ratio":               "session_progress_ratio",
            "hour_of_day_7":                        "hour_of_day: 7am",
            "hour_of_day_8":                        "hour_of_day: 8am",
            "hour_of_day_13":                       "hour_of_day: 1pm",
            "day_of_week_Wednesday":                "day_of_week: wednesday",
            "day_of_week_Thursday":                 "day_of_week: thursday",
            "product_category_fk_3":                "category: business_comfort",
            # L2
            "log_total_accumulated_deadhead_sec":   "accumulated_deadhead",
            "log_cycle_cumulative_net_earnings":    "cycle_cumulative_earnings",
            "log_est_trip_time_sec":                "est_trip_time",
            "dispatch_lead_time_sec":               "dispatch_lead_time",
            "home_vector_alignment_score":          "home_vector_alignment",
            "cycle_avg_dtp_km":                     "cycle_avg_dtp_km",
            "cycle_ttp_dtp_ratio":                  "cycle_ttp_dtp_ratio",
            "cycle_rolling_avg_spread":             "cycle_rolling_avg_spread",
            "cycle_std_dtp_km":                     "cycle_std_dtp_km",
            "eph_complete_index_ML":                "eph_complete_index",
            "category: comfort":                    "category: comfort",
            "category: business_comfort":           "category: business_comfort",
            "Zona: santa_fe_ibero":                 "zona: santa_fe_ibero",
            "dropoff: Unassigned Area":             "dropoff: unassigned",
            "dropoff: roma_condesa_2":              "dropoff: roma_condesa_2",
            "dropoff: tamarindos":                  "dropoff: tamarindos",
            "dropoff: terminal_1_aicm":             "dropoff: terminal_1_aicm",
            "dropoff: terminal_2_aicm":             "dropoff: terminal_2_aicm",
            "dropoff: juarez_soho_house":           "dropoff: juarez_soho_house",
            "dropoff: lomas_verdes":                "dropoff: lomas_verdes",
        }

        def _clean_label(raw):
            if raw in _LABEL_CLEAN:
                return _LABEL_CLEAN[raw]
            # strip common implementation suffixes
            import re as _re_lbl
            s = str(raw)
            s = _re_lbl.sub(r'^log_', '', s)
            s = _re_lbl.sub(r'_sec$', '', s)
            s = _re_lbl.sub(r'_ml$', '', s)
            s = _re_lbl.sub(r'_fk$', '', s)
            return s

        _df_shap_l1["label_clean"] = _df_shap_l1["label"].apply(_clean_label)
        _df_shap_l2["label_clean"] = _df_shap_l2["label"].apply(_clean_label)
        _df_shap_l1["color"] = _df_shap_l1["directional_impact"].apply(lambda x: "#21918c" if x >= 0 else "#c8d0d8")
        _df_shap_l2["color"] = _df_shap_l2["directional_impact"].apply(lambda x: "#21918c" if x >= 0 else "#c8d0d8")
        _df_shap_l1["direction"] = _df_shap_l1["directional_impact"].apply(lambda x: "Motor ↑" if x >= 0 else "Brake ↓")
        _df_shap_l2["direction"] = _df_shap_l2["directional_impact"].apply(lambda x: "Motor ↑" if x >= 0 else "Brake ↓")

        import plotly.graph_objects as go

        def _interp_color(t, c_light, c_dark):
            def _hex(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
            r1, g1, b1 = _hex(c_light)
            r2, g2, b2 = _hex(c_dark)
            return f"rgb({int(r1+(r2-r1)*t)},{int(g1+(g2-g1)*t)},{int(b1+(b2-b1)*t)})"

        def _shap_chart(df, title, x_domain=None, x_title=None, x_title_right=None):
            df = df.sort_values("mean_abs_shap", ascending=True).copy()
            _dom = x_domain or [-0.30, 0.30]
            _norm = (df["mean_abs_shap"] - df["mean_abs_shap"].min()) / \
                    (df["mean_abs_shap"].max() - df["mean_abs_shap"].min() + 1e-9)
            _colors = [
                _interp_color(t, "#b2dbd9", "#21918c") if v >= 0 else _interp_color(t, "#e8eaed", "#8896a5")
                for t, v in zip(_norm, df["directional_impact"])
            ]
            fig = go.Figure(go.Bar(
                x=df["directional_impact"],
                y=df["label_clean"],
                orientation="h",
                marker=dict(color=_colors, line=dict(width=0), cornerradius=4),
                hovertemplate="<b>%{y}</b><br>Impact: %{x:.3f}<extra></extra>",
            ))
            _annotations = []
            if x_title:
                _annotations.append(dict(
                    x=0, y=-0.14, xref="paper", yref="paper",
                    text=f"<b>{x_title}</b>",
                    showarrow=False, xanchor="left",
                    font=dict(size=12, color="#8896a5", family="Inter"),
                ))
            if x_title_right:
                _annotations.append(dict(
                    x=1, y=-0.14, xref="paper", yref="paper",
                    text=f"<b>{x_title_right}</b>",
                    showarrow=False, xanchor="right",
                    font=dict(size=12, color="#21918c", family="Inter"),
                ))
            fig.update_layout(
                paper_bgcolor="#fafafa",
                plot_bgcolor="#fafafa",
                font=dict(family="Inter", color="#475569", size=12),
                annotations=_annotations,
                margin=dict(l=0, r=20, t=40, b=72),
                title=dict(text=title, font=dict(size=13, color="#334155"), x=0),
                xaxis=dict(
                    range=_dom,
                    zeroline=True, zerolinecolor="#cbd5e1", zerolinewidth=1,
                    showgrid=False, tickfont=dict(size=10, color="#94a3b8"),
                    title=dict(text="mean SHAP value", font=dict(size=10, color="#94a3b8"), standoff=4),
                ),
                yaxis=dict(
                    showgrid=True, gridcolor="#dde3ea", gridwidth=1, griddash="dot",
                    tickfont=dict(size=11, color="#475569"), title=None,
                ),
                height=560,
            )
            return fig

        # ── L1 chart ──────────────────────────────────────────────────────────
        st.markdown("""
<p style='font-size:0.84rem;color:#475569;line-height:1.65;margin-bottom:20px;'>This SHAP analysis decodes the behavioral logic of the cascade — first, what separates a deterministic rejection from a nuanced offer at Layer 1, then how each of the three strategic outcomes is weighted at Layer 2. Each bar reflects the mean contribution of a feature to that classification decision.</p>
<div style='margin-top:8px;margin-bottom:4px;font-size:1.1rem;font-weight:700;color:#21918c;font-family:'Source Sans Pro',sans-serif;'>Layer 1 · nuanced_rest class</div>
""", unsafe_allow_html=True)
        st.plotly_chart(_shap_chart(_df_shap_l1, "What drives nuanced_rest classification", x_domain=[-0.55, 0.35], x_title="← deterministic rejections", x_title_right="nuanced_rest · passes to L2 →"), use_container_width=True)

        # ── L1 insight — editorial callout ────────────────────────────────────
        st.markdown("""
<div style='border-left:3px solid #21918c;background:rgba(33,145,140,0.07);padding:14px 18px;border-radius:0;margin-top:4px;margin-bottom:24px;'>
<span style='font-size:0.82rem;color:#334155;line-height:1.65;'>High baseline congestion pushes offers into the Nuanced category — the agent actively hunts high-friction market states to secure high EPH rides. Yet friction and risk are not the same thing: while known traffic is desired, unpredicted risk is not. High <code>traffic_volatility_index</code> signals margin erosion and drives immediate rejection.</span>
</div>
""", unsafe_allow_html=True)

        # ── L2 carousel ───────────────────────────────────────────────────────
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown("""
<div style='margin-bottom:4px;font-size:1.1rem;font-weight:700;color:#21918c;font-family:'Source Sans Pro',sans-serif;'>Layer 2 · strategic classes</div>
""", unsafe_allow_html=True)

        _L2_ORDER   = ["Strategic Mismatch", "Expected Value Gamble", "ACCEPTED"]
        _L2_CLASSES = _L2_ORDER
        _L2_LABELS   = {
            "ACCEPTED":             "Accepted",
            "Expected Value Gamble":"Expected Value Gamble",
            "Strategic Mismatch":   "Strategic Mismatch",
        }
        _L2_TITLES = {
            "ACCEPTED":             "What drives the agent to Accept",
            "Expected Value Gamble":"What drives Expected Value Gamble",
            "Strategic Mismatch":   "What drives Strategic Mismatch",
        }
        _L2_DOMAINS = {
            "ACCEPTED":             [-0.30, 0.50],
            "Expected Value Gamble":[-0.40, 0.30],
            "Strategic Mismatch":   [-0.35, 0.30],
        }
        _L2_XTITLE_LEFT = {
            "ACCEPTED":             "← pulls towards nuanced rejection",
            "Expected Value Gamble":"← pulls towards nuanced rejection",
            "Strategic Mismatch":   "← pulls towards nuanced rejection",
        }
        _L2_XTITLE_RIGHT = {
            "ACCEPTED":             "drives acceptance →",
            "Expected Value Gamble":"drives the gamble →",
            "Strategic Mismatch":   "forces strategic mismatch →",
        }

        if "shap_l2_class" not in st.session_state:
            st.session_state["shap_l2_class"] = _L2_CLASSES[0]

        _active_l2 = st.session_state["shap_l2_class"]

        # Selector chips
        _chip_html = "<div style='display:flex;gap:8px;margin-bottom:16px;'>"
        for _cls in _L2_CLASSES:
            _is_active = (_cls == _active_l2)
            _chip_html += f"""<div style='padding:5px 14px;border-radius:999px;border:1px solid {'#21918c' if _is_active else '#e2e8f0'};background:{'rgba(33,145,140,0.10)' if _is_active else '#fff'};font-size:0.72rem;font-weight:{'700' if _is_active else '500'};color:{'#21918c' if _is_active else '#94a3b8'};'>{_L2_LABELS.get(_cls, _cls)}</div>"""
        _chip_html += "</div>"
        st.markdown(_chip_html, unsafe_allow_html=True)

        # Hidden buttons for interactivity
        _cols_l2 = st.columns(len(_L2_CLASSES))
        for _ci, _cls in enumerate(_L2_CLASSES):
            if _cols_l2[_ci].button(_L2_LABELS.get(_cls, _cls), key=f"shap_l2_btn_{_ci}", use_container_width=True):
                st.session_state["shap_l2_class"] = _cls
                st.rerun()
        _btn_labels = [_L2_LABELS.get(_cls, _cls) for _cls in _L2_CLASSES]
        import streamlit.components.v1 as _cv1
        _cv1.html(f"""<script>
(function wire() {{
    const labels = {_btn_labels};
    const doc = window.parent.document;

    // find hidden buttons
    const btnMap = {{}};
    doc.querySelectorAll('button').forEach(btn => {{
        const t = btn.innerText.trim();
        if (labels.includes(t)) btnMap[t] = btn;
    }});

    // find chip divs (divs whose sole text matches a label)
    const chips = [];
    doc.querySelectorAll('div').forEach(div => {{
        if (labels.includes(div.innerText.trim()) && div.children.length === 0) chips.push(div);
    }});

    if (Object.keys(btnMap).length < labels.length || chips.length < labels.length) {{
        setTimeout(wire, 50); return;
    }}

    // hide buttons
    labels.forEach(l => {{
        const el = btnMap[l].closest('[data-testid="stButton"]');
        if (el) el.style.display = 'none';
    }});

    // wire chip clicks → button clicks
    chips.forEach(chip => {{
        const label = chip.innerText.trim();
        chip.style.cursor = 'pointer';
        chip.addEventListener('click', () => {{ if (btnMap[label]) btnMap[label].click(); }});
    }});
}})();
</script>""", height=0)

        # Chart for active class
        _df_active = _df_shap_l2[_df_shap_l2["class_name"] == _active_l2].copy()
        st.plotly_chart(_shap_chart(_df_active, _L2_TITLES.get(_active_l2, _active_l2),
            x_domain=_L2_DOMAINS.get(_active_l2, [-0.30, 0.30]),
            x_title=_L2_XTITLE_LEFT.get(_active_l2),
            x_title_right=_L2_XTITLE_RIGHT.get(_active_l2),
        ), use_container_width=True)

        if _active_l2 == "ACCEPTED":
            st.markdown("""
<div style='border-left:3px solid #21918c;background:rgba(33,145,140,0.07);padding:14px 18px;border-radius:0;margin-top:4px;margin-bottom:8px;'>
<span style='font-size:0.82rem;color:#334155;line-height:1.65;'>Acceptance is driven by clean economics above all — <code>eph_operational_index</code> and <code>upfront_fare</code> dominate: the agent accepts when the money is unambiguously good. As expected, <code>accumulated_deadhead</code> also drives acceptance — deep into an unpaid stretch, the agent grows less selective to stop the bleeding.</span>
</div>
""", unsafe_allow_html=True)

        if _active_l2 == "Expected Value Gamble":
            st.markdown("""
<div style='border-left:3px solid #21918c;background:rgba(33,145,140,0.07);padding:14px 18px;border-radius:0;margin-top:4px;margin-bottom:8px;'>
<span style='font-size:0.82rem;color:#334155;line-height:1.65;'>The strongest brake on the gamble is <code>accumulated_deadhead</code> — the more unpaid time already sunk into the cycle, the less willing the agent is to bet. Notably, <code>upfront_fare</code> also pulls toward caution: the gamble isn't a naive "chase the high fare" reflex, but a context-aware bet weighed against time already spent.</span>
</div>
""", unsafe_allow_html=True)

        if _active_l2 == "Strategic Mismatch":
            st.markdown("""
<div style='border-left:3px solid #21918c;background:rgba(33,145,140,0.07);padding:14px 18px;border-radius:0;margin-top:4px;margin-bottom:8px;'>
<span style='font-size:0.82rem;color:#334155;line-height:1.65;'>As a session advances (<code>session_progress_ratio</code>) and daily financial targets are secured (<code>cycle_cumulative_earnings</code>), the agent abandons pure revenue maximization for an exit strategy. Trips that pull the driver away from their baseline zone (a negative <code>home_vector_alignment</code>) aggressively trigger a mismatch rejection, as the driver refuses to be dragged further away at the end of their day.</span>
</div>
""", unsafe_allow_html=True)

    with sci6:

        @st.cache_data(show_spinner=False)
        def _load_lc_l1():
            from io import BytesIO
            return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_learning_curve_L1.parquet").download_as_bytes()))

        @st.cache_data(show_spinner=False)
        def _load_lc_l2():
            from io import BytesIO
            return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_learning_curve_L2.parquet").download_as_bytes()))

        @st.cache_data(show_spinner=False)
        def _load_lc_spartan():
            from io import BytesIO
            return pd.read_parquet(BytesIO(_storage_client().bucket("pienza-streamlit").blob("260505_0509_spartan_learning_curve.parquet").download_as_bytes()))

        _df_lc_l1      = _load_lc_l1()
        _df_lc_l2      = _load_lc_l2()
        _df_lc_spartan = _load_lc_spartan()

        def _prep_lc(df):
            tc = [c for c in df.columns if c.startswith("train_s_")]
            vc = [c for c in df.columns if c.startswith("test_s_")]
            return df.assign(
                train_mean = df[tc].mean(axis=1),
                val_mean   = df[vc].mean(axis=1),
                val_std    = df[vc].std(axis=1),
            )

        _lc1 = _prep_lc(_df_lc_l1)
        _lc2 = _prep_lc(_df_lc_l2)
        _lcs = _prep_lc(_df_lc_spartan)

        def _lc_chart(df, title, show_stats=True):
            import plotly.graph_objects as _go
            fig = _go.Figure()
            # train — slate
            fig.add_trace(_go.Scatter(
                x=df["train_sizes"], y=df["train_mean"],
                name="Train", mode="lines+markers",
                line=dict(color="#8896a5", width=2, dash="dot"),
                marker=dict(size=4, color="#8896a5"),
            ))
            # val band
            fig.add_trace(_go.Scatter(
                x=pd.concat([df["train_sizes"], df["train_sizes"][::-1]]),
                y=pd.concat([df["val_mean"] + df["val_std"], (df["val_mean"] - df["val_std"])[::-1]]),
                fill="toself", fillcolor="rgba(33,145,140,0.08)",
                line=dict(color="rgba(255,255,255,0)"), showlegend=False, hoverinfo="skip",
            ))
            # val — teal
            fig.add_trace(_go.Scatter(
                x=df["train_sizes"], y=df["val_mean"],
                name="Validation", mode="lines+markers",
                line=dict(color="#21918c", width=2),
                marker=dict(size=5, color="#21918c"),
            ))
            fig.update_layout(
                title=dict(text=title, font=dict(size=11, color="#21918c", family="Inter"), x=0),
                paper_bgcolor="#fafafa", plot_bgcolor="#fafafa",
                font=dict(family="Inter", size=11, color="#475569"),
                xaxis=dict(title="training samples", showgrid=False,
                           tickfont=dict(size=10, color="#94a3b8"),
                           title_font=dict(size=10, color="#94a3b8")),
                yaxis=dict(title="F1-Macro", range=[0, 1.05], gridcolor="#e2e8f0", griddash="dot",
                           zeroline=False, tickfont=dict(size=10, color="#94a3b8"),
                           title_font=dict(size=10, color="#94a3b8")),
                legend=dict(orientation="h", y=-0.22, x=0, font=dict(size=11, color="#475569"),
                            bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=0, r=10, t=40, b=64),
                height=320,
            )
            if show_stats:
                _tr = df["train_mean"].iloc[-1]
                _vl = df["val_mean"].iloc[-1]
                _gp = _tr - _vl
                fig.add_annotation(
                    x=1, y=0, xref="paper", yref="paper", xanchor="right", yanchor="bottom",
                    text=f"<span style='color:#8896a5;'>train</span> {_tr:.2f} &nbsp; <span style='color:#21918c;'>val</span> {_vl:.2f} &nbsp; <span style='color:#475569;'>gap</span> {_gp:.2f}",
                    showarrow=False, font=dict(size=11, family="Inter"), align="right",
                    bgcolor="rgba(250,250,250,0.85)", borderpad=4,
                )
            return fig

        # ── L1 healthy ─────────────────────────────────────────────────────────
        st.markdown("""
<div style='margin:8px 0 16px;padding:0 4px;'>
  <div style='font-size:0.85rem;font-weight:700;letter-spacing:2.5px;color:#94a3b8;text-transform:uppercase;margin-bottom:6px;'>Layer 1 · learning curve</div>
  <div style='height:1px;background:linear-gradient(to right,rgba(33,145,140,0.35),transparent);'></div>
</div>
<p style='font-size:0.84rem;color:#475569;line-height:1.65;margin-bottom:12px;'>With ~3,000 training samples, Layer 1 converges cleanly. Train and validation curves close in steadily — no memorization, no collapse. A gap of 0.15 at full data is healthy for a real-world behavioral model.</p>
""", unsafe_allow_html=True)
        st.plotly_chart(_lc_chart(_lc1, "L1 Bouncer · learning curve"), use_container_width=True)

        # ── L2 problem intro ───────────────────────────────────────────────────
        st.markdown("""
<div style='margin:32px 0 16px;padding:0 4px;'>
  <div style='font-size:0.85rem;font-weight:700;letter-spacing:2.5px;color:#94a3b8;text-transform:uppercase;margin-bottom:6px;'>Layer 2 · the overfitting problem</div>
  <div style='height:1px;background:linear-gradient(to right,rgba(33,145,140,0.35),transparent);'></div>
</div>
<p style='font-size:0.84rem;color:#475569;line-height:1.65;margin-bottom:20px;'>Layer 2 memorized the training set — a textbook high-variance failure. With only ~600 samples, the model learns noise. The solution: a lightweight model of 6 features, selected for behavioral meaning over raw performance. The gap collapses from 0.24 to 0.11 at the cost of ~0.09 in validation score — a deliberate tradeoff favoring generalization.</p>
""", unsafe_allow_html=True)

        # ── 6 lightweight features — stepper ──────────────────────────────────
        st.markdown("""
<div style='display:flex;justify-content:center;margin-bottom:24px;'><div style='display:flex;gap:0;max-width:320px;width:100%;'>

  <!-- stepper spine -->
  <div style='display:flex;flex-direction:column;align-items:center;margin-right:16px;flex-shrink:0;'>
    <div style='width:34px;height:34px;border-radius:50%;background:#21918c;display:flex;align-items:center;justify-content:center;'>
      <span style='color:#fff;font-size:0.95rem;font-weight:700;line-height:1;font-family:'Source Sans Pro',sans-serif;'>L</span>
    </div>
    <div style='width:1px;background:#d1d5db;flex:1;margin-top:4px;'></div>
  </div>

  <!-- content -->
  <div style='padding-top:6px;padding-bottom:20px;'>
    <div style='font-size:0.68rem;font-weight:700;color:#21918c;letter-spacing:1.4px;text-transform:uppercase;margin-bottom:12px;'>Lightweight Feature Set</div>
    <div style='border-left:3px solid #21918c;padding-left:14px;display:flex;flex-direction:column;gap:6px;'>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>session_progress_ratio</span>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>total_accumulated_deadhead_sec</span>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>cycle_rolling_avg_spread</span>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>eph_operational_index</span>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>cycle_cumulative_net_earnings</span>
      <span style='font-family:monospace;font-size:0.68rem;color:#94a3b8;'>home_vector_alignment_score</span>
    </div>
  </div>

</div></div>
""", unsafe_allow_html=True)

        # ── learning curves side by side ───────────────────────────────────────
        _col_l2, _col_sp = st.columns(2)
        with _col_l2:
            st.plotly_chart(_lc_chart(_lc2, "L2 Full · 25+ features"), use_container_width=True)
        with _col_sp:
            st.plotly_chart(_lc_chart(_lcs, "L2 Lightweight · 6 features"), use_container_width=True)

        # ── comparison table ───────────────────────────────────────────────────
        st.markdown("""
<div style='margin-top:12px;font-family:'Source Sans Pro',sans-serif;'>
  <table style='width:auto;border-collapse:collapse;line-height:1.2;margin:0 auto;'>
    <thead>
      <tr style='background:#f8fafc;'>
        <th style='padding:4px 8px;text-align:left;white-space:nowrap;border-bottom:1px solid rgba(33,145,140,0.12);'></th>
        <th style='padding:4px 8px;text-align:center;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);font-weight:normal;white-space:nowrap;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>Train F1</span>
        </th>
        <th style='padding:4px 8px;text-align:center;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);font-weight:normal;white-space:nowrap;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>Val F1</span>
        </th>
        <th style='padding:4px 8px;text-align:center;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);font-weight:normal;white-space:nowrap;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>Gap</span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style='padding:4px 8px;border-bottom:1px solid #f1f5f9;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>Layer 1</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#21918c;'>0.97</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#64b5b1;'>0.82</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#475569;'>0.15</span>
          <span style='font-size:0.58rem;font-weight:600;color:#21918c;margin-left:3px;'>healthy</span>
        </td>
      </tr>
      <tr>
        <td style='padding:4px 8px;border-bottom:1px solid #f1f5f9;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>L2 Full</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#21918c;'>0.94</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#64b5b1;'>0.70</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-bottom:1px solid #f1f5f9;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#475569;'>0.24</span>
          <span style='font-size:0.58rem;font-weight:600;color:#f59e0b;margin-left:3px;'>overfit</span>
        </td>
      </tr>
      <tr>
        <td style='padding:4px 8px;'>
          <span style='font-size:0.58rem;font-weight:700;color:#334155;letter-spacing:1.2px;text-transform:uppercase;'>L2 Lightweight</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#21918c;'>0.72</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#64b5b1;'>0.61</span>
        </td>
        <td style='padding:4px 8px;text-align:center;border-left:1px solid rgba(33,145,140,0.12);'>
          <span style='font-size:0.75rem;font-weight:700;color:#475569;'>0.11</span>
          <span style='font-size:0.58rem;font-weight:600;color:#21918c;margin-left:3px;'>generalizes</span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style='border-left:3px solid #21918c;background:rgba(33,145,140,0.07);padding:14px 18px;border-radius:0;margin-top:20px;'>
<span style='font-size:0.82rem;color:#334155;line-height:1.65;'>While the initial model suffered from high variance, the lightweight iteration corrects this at the cost of increased bias, trading complexity for generalization. This ensures the learned decision policy remains robust across diverse operational states.</span>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style='margin-top:32px;border-top:1px solid #e2e8f0;padding-top:14px;font-size:0.72rem;color:#64748b;font-family:monospace;text-align:center;'>
  Behavioral Cloning &middot; <span style='color:#21918c;'>✓ dimensionality reduction · success</span> &nbsp;&mdash;&mdash;&mdash;&nbsp; proceeding to Sensitivity Analysis <span style='color:#21918c;'>→</span>
</div>
""", unsafe_allow_html=True)

with tab2:
    from io import BytesIO as _BytesIO2

    # ── Load parquets ─────────────────────────────────────────────────────────
    @st.cache_data(show_spinner=False)
    def _po_load_full():
        return pd.read_parquet(_BytesIO2(_storage_client().bucket("pienza-streamlit").blob("0509_sim_proba.parquet").download_as_bytes()))

    @st.cache_data(show_spinner=False)
    def _po_load_light():
        return pd.read_parquet(_BytesIO2(_storage_client().bucket("pienza-streamlit").blob("0509_spartan_proba.parquet").download_as_bytes()))

    @st.cache_data(show_spinner=False)
    def _po_load_mono():
        return pd.read_parquet(_BytesIO2(_storage_client().bucket("pienza-streamlit").blob("0508_monolith_proba.parquet").download_as_bytes()))

    _po_full  = _po_load_full()
    _po_light = _po_load_light()
    _po_mono  = _po_load_mono()

    # ── Human baseline ────────────────────────────────────────────────────────
    _po_h_mask  = _po_mono["y_true"] == "accepted"
    _po_h_total = int(_po_h_mask.sum())
    _po_h_ids   = _po_mono.loc[_po_h_mask, "offer_id"].tolist()

    # ── Realized fare map (BQ) ────────────────────────────────────────────────
    @st.cache_data(show_spinner=False)
    def _po_load_fares(ids_key: str) -> dict:
        _q = f"""
        SELECT offer_id, realized_fare
        FROM `645009831643.pienza_mini.v_mission_dossier`
        WHERE offer_id IN ({ids_key})
          AND realized_fare IS NOT NULL
        """
        return dict(zip(*[fetch_data_from_bq(_q)[c].tolist() for c in ["offer_id", "realized_fare"]]))

    _po_fare_map = _po_load_fares(", ".join([f"'{x}'" for x in _po_h_ids]))
    _po_h_earn   = sum(_po_fare_map.get(oid, 0) for oid in _po_h_ids)

    # ── Breakdown helper ──────────────────────────────────────────────────────
    def _po_breakdown(df, pred_mask, true_mask, no_gt_mask=None):
        both     = pred_mask & true_mask
        ai_only  = pred_mask & ~true_mask
        # estimate earnings only on L1 FPs (no ground truth), matching sci4 methodology
        earn_fp  = ai_only if no_gt_mask is None else (ai_only & no_gt_mask)
        earn_b   = sum(_po_fare_map.get(oid, 0) for oid in df.loc[both, "offer_id"])
        earn_ai  = float((6.31 + 0.79 * df.loc[earn_fp, "upfront_fare"]).sum())
        return {
            "human_eq_ai": int(both.sum()),
            "ai_ne_human": int(ai_only.sum()),
            "earn":        earn_b + earn_ai,
        }

    # ── Monolith ──────────────────────────────────────────────────────────────
    _mono_cols      = [c for c in _po_mono.columns if c.startswith("mono_")]
    _mono_pred_acc  = _po_mono[_mono_cols].idxmax(axis=1) == "mono_accepted"
    _mono_true_acc  = _po_mono["y_true"] == "accepted"
    _mb = _po_breakdown(_po_mono, _mono_pred_acc, _mono_true_acc)

    # ── CC Full (default 50%) ─────────────────────────────────────────────────
    _po_l1_det   = ["dropoff_non_operational", "dropoff_proxy_zone", "long_pickup_time", "low_profitability"]
    _full_l1     = _po_full[_po_l1_det].idxmax(axis=1).copy()
    _full_l1[_po_full["the_nuanced_rest"] >= 0.5] = "the_nuanced_rest"
    _full_routed = _full_l1 == "the_nuanced_rest"
    _full_l2     = pd.Series("_", index=_po_full.index)
    _full_l2[_full_routed] = (
        _po_full.loc[_full_routed, ["l2_strategic_mismatch", "l2_expected_value_gamble", "l2_accepted"]]
        .fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False)
    )
    _full_pred_acc  = _full_l2 == "accepted"
    _full_true_acc  = _po_full["offer_id"].isin(_po_h_ids)
    _full_no_gt     = _po_full["y_true_l2"].isna()
    _fb = _po_breakdown(_po_full, _full_pred_acc, _full_true_acc, no_gt_mask=_full_no_gt)

    # ── CC Lightweight (default 50%) ──────────────────────────────────────────
    _light_l1    = _po_light[_po_l1_det].idxmax(axis=1).copy()
    _light_l1[_po_light["the_nuanced_rest"] >= 0.5] = "the_nuanced_rest"
    _light_routed = _light_l1 == "the_nuanced_rest"
    _light_l2    = pd.Series("_", index=_po_light.index)
    _light_l2[_light_routed] = (
        _po_light.loc[_light_routed, ["spartan_l2_strategic_mismatch", "spartan_l2_expected_value_gamble", "spartan_l2_accepted"]]
        .fillna(0).idxmax(axis=1).str.replace("spartan_l2_", "", regex=False)
    )
    _light_pred_acc = _light_l2 == "accepted"
    _light_true_acc = _po_light["offer_id"].isin(_po_h_ids)
    _light_no_gt    = _po_light["y_true_l2"].isna()
    _lb = _po_breakdown(_po_light, _light_pred_acc, _light_true_acc, no_gt_mask=_light_no_gt)

    # ── Winner detection ──────────────────────────────────────────────────────
    _po_earnings = {"human": _po_h_earn, "mono": _mb["earn"], "full": _fb["earn"], "light": _lb["earn"]}
    _po_winner   = max(_po_earnings, key=_po_earnings.get)

    def _pct_po(n, d): return f"({round(n/d*100)}%)" if d > 0 else ""

    def _col_header(key, label, sublabel):
        is_win  = _po_winner == key
        bg      = "rgba(33,145,140,0.07)" if is_win else "#f8fafc"
        bdr     = "border-left:2px solid #21918c;" if is_win else "border-left:1px solid rgba(33,145,140,0.12);"
        color   = "#21918c" if is_win else "#64748b"
        sub_col = "#21918c" if is_win else "#94a3b8"
        crown   = " ★" if is_win else ""
        return (
            f"<div style='background:{bg};padding:6px 10px;"
            f"border-bottom:1px solid rgba(33,145,140,0.12);{bdr}"
            f"text-align:center;font-size:0.65rem;font-weight:700;color:{color};"
            f"letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>"
            f"{label}{crown} <span style='font-size:0.58rem;color:{sub_col};font-weight:500;"
            f"letter-spacing:0;text-transform:none;'>{sublabel}</span></div>"
        )

    def _cell(key, val, muted=False):
        is_win  = _po_winner == key
        bdr     = "border-left:2px solid rgba(33,145,140,0.4);" if is_win else "border-left:1px solid rgba(33,145,140,0.12);"
        color   = "rgba(33,145,140,0.55)" if muted else ("#21918c" if not muted else "#21918c")
        return f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);{bdr}text-align:center;'>{val}</div>"

    def _num(val, muted=False, size="0.88rem"):
        color = "rgba(33,145,140,0.55)" if muted else "#21918c"
        return f"<span style='font-family:monospace;font-size:{size};font-weight:700;color:{color};line-height:1;'>{val}</span>"

    def _num_kpi(val):
        return _num(val, size="1.0rem")

    def _num_pct(n, d, muted=False):
        return f"<div style='display:flex;align-items:baseline;justify-content:center;gap:4px;'>{_num(n, muted)}<span style='font-size:0.52rem;color:#94a3b8;'>{_pct_po(n,d)}</span></div>"

    _dash = "<div style='font-family:monospace;font-size:0.88rem;font-weight:700;color:#94a3b8;line-height:1;'>—</div>"
    _kpi_bg   = "background:rgba(33,145,140,0.04);"
    _grid_cols = "195px 125px 125px 125px 125px;"

    # pre-compute all HTML fragments to keep the markdown call flat (no blank lines / comments)
    _hdr_mono  = _col_header("mono",  "Monolith",       "Flat Multiclass")
    _hdr_full  = _col_header("full",  "CC Full",        "L1 + L2 Champion")
    _hdr_light = _col_header("light", "CC Lightweight", "L1 + L2 Spartan")

    _row_ho_mono  = _cell("mono",  _dash)
    _row_ho_full  = _cell("full",  _dash)
    _row_ho_light = _cell("light", _dash)

    _row_eq_mono  = _cell("mono",  _num_pct(_mb["human_eq_ai"], _po_h_total))
    _row_eq_full  = _cell("full",  _num_pct(_fb["human_eq_ai"], _po_h_total))
    _row_eq_light = _cell("light", _num_pct(_lb["human_eq_ai"], _po_h_total))

    _row_ne_mono  = _cell("mono",  _num_pct(_mb["ai_ne_human"], _po_h_total, muted=True))
    _row_ne_full  = _cell("full",  _num_pct(_fb["ai_ne_human"], _po_h_total, muted=True))
    _row_ne_light = _cell("light", _num_pct(_lb["ai_ne_human"], _po_h_total, muted=True))

    _earn_bdr_h     = "1px solid rgba(33,145,140,0.12)"
    _earn_bdr_mono  = "2px solid rgba(33,145,140,0.4)" if _po_winner == "mono"  else "1px solid rgba(33,145,140,0.12)"
    _earn_bdr_full  = "2px solid rgba(33,145,140,0.4)" if _po_winner == "full"  else "1px solid rgba(33,145,140,0.12)"
    _earn_bdr_light = "2px solid rgba(33,145,140,0.4)" if _po_winner == "light" else "1px solid rgba(33,145,140,0.12)"

    _num_h     = _num_kpi(f"${_po_h_earn:,.0f}")
    _num_mono  = _num_kpi(f"${_mb['earn']:,.0f}")
    _num_full  = _num_kpi(f"${_fb['earn']:,.0f}")
    _num_light = _num_kpi(f"${_lb['earn']:,.0f}")

    # static: total accepted & avg per ride
    _tot_h     = _po_h_total
    _tot_mono  = _mb["human_eq_ai"] + _mb["ai_ne_human"]
    _tot_full  = _fb["human_eq_ai"] + _fb["ai_ne_human"]
    _tot_light = _lb["human_eq_ai"] + _lb["ai_ne_human"]

    def _avg(earn, total): return f"${earn/total:,.2f}" if total > 0 else "—"

    def _stat_row_total(bdr_mono, bdr_full, bdr_light):
        return (
            "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Total Accepted</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>human=AI + AI≠human</div></div>"
            f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num(_tot_h)}</div>"
            f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{bdr_mono};text-align:center;'>{_num(_tot_mono)}</div>"
            f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{bdr_full};text-align:center;'>{_num(_tot_full)}</div>"
            f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{bdr_light};text-align:center;'>{_num(_tot_light)}</div>"
        )

    def _stat_row_avg(earn_h, earn_mono, earn_full, earn_light, tot_mono, tot_full, tot_light, bdr_mono, bdr_full, bdr_light):
        return (
            "<div style='padding:8px 10px;background:rgba(33,145,140,0.04);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Avg / Accepted Ride</div></div>"
            f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num_kpi(_avg(earn_h, _tot_h))}</div>"
            f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{bdr_mono};text-align:center;'>{_num_kpi(_avg(earn_mono, tot_mono))}</div>"
            f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{bdr_full};text-align:center;'>{_num_kpi(_avg(earn_full, tot_full))}</div>"
            f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{bdr_light};text-align:center;'>{_num_kpi(_avg(earn_light, tot_light))}</div>"
        )

    _scorecard_html = (
        "<div style='font-size:0.85rem;color:#777;line-height:1.6;margin-bottom:28px;margin-top:8px;'>"
        "Four contenders. Same 780-offer holdout. One financial outcome. The scorecard below measures each model's accepted decisions against the human ground truth — translating classification behavior into realized earnings."
        "</div>"
        "<div style='display:flex;justify-content:center;'>"
        "<div style='display:inline-block;border:1px solid rgba(33,145,140,0.2);border-radius:6px;overflow:hidden;'>"
        "<div style='display:grid;grid-template-columns:195px 125px 125px 125px 125px;'>"
        "<div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;'>Accepted</div>"
        "<div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Human <span style='font-size:0.55rem;color:#94a3b8;font-weight:500;letter-spacing:0;text-transform:none;'>Ground Truth</span></div>"
        f"{_hdr_mono}{_hdr_full}{_hdr_light}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Human Only</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num(_po_h_total)}</div>"
        f"{_row_ho_mono}{_row_ho_full}{_row_ho_light}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#21918c;text-transform:uppercase;letter-spacing:0.5px;'>Human = AI</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>both accepted</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_dash}</div>"
        f"{_row_eq_mono}{_row_eq_full}{_row_eq_light}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:rgba(33,145,140,0.55);text-transform:uppercase;letter-spacing:0.5px;'>AI ≠ Human</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>AI accepted, human rejected</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_dash}</div>"
        f"{_row_ne_mono}{_row_ne_full}{_row_ne_light}"
        + _stat_row_total(_earn_bdr_mono, _earn_bdr_full, _earn_bdr_light)
        + "<div style='position:relative;padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Cumulative Earnings</div>"
        "<span class='fn-wrap' style='position:absolute;top:6px;right:8px;'><span class='fn-mark' style='color:#21918c;font-size:0.6rem;'>&#9432;</span>"
        "<span class='fn-tooltip' style='width:340px;white-space:normal;font-family:sans-serif;font-size:0.73rem;line-height:1.7;text-transform:none;letter-spacing:0;font-weight:400;color:#334155;'><strong>Imputation method (AI ≠ Human trips)</strong><br>Human earnings are verified realized fares. Non-realized AI fares are estimated via the Causal Inference polynomial model at ΔT = 1.0:<br><br><span style='font-family:monospace;font-size:0.78rem;background:rgba(33,145,140,0.08);padding:4px 8px;border-radius:4px;display:block;white-space:nowrap;'>F&#770;(ΔT=1) = 6.31 + 0.79 × Upfront Fare</span></span></span></div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_earn_bdr_h};text-align:center;'>{_num_h}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_earn_bdr_mono};text-align:center;'>{_num_mono}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_earn_bdr_full};text-align:center;'>{_num_full}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_earn_bdr_light};text-align:center;'>{_num_light}</div>"
        + _stat_row_avg(_po_h_earn, _mb["earn"], _fb["earn"], _lb["earn"], _tot_mono, _tot_full, _tot_light, _earn_bdr_mono, _earn_bdr_full, _earn_bdr_light)
        + "</div></div></div>"
        "<div style='margin-top:12px;text-align:center;font-size:0.58rem;color:#94a3b8;'>"
        "All models evaluated on the same 780-offer week-6 holdout · threshold fixed at 50% (default) · ★ highest earner"
        "</div>"
    )
    # ── 1. Slider ─────────────────────────────────────────────────────────────
    if "po_thresh_pct" not in st.session_state:
        st.session_state["po_thresh_pct"] = 50
    st.markdown("<div style='font-size:0.52rem;font-weight:600;color:#21918c;letter-spacing:1.5px;text-transform:uppercase;font-family:monospace;margin-bottom:4px;'>threshold — P(accepted) for Monolith · P(nuanced_rest) for CC</div>", unsafe_allow_html=True)
    st.slider(
        label="po_threshold",
        label_visibility="collapsed",
        key="po_thresh_pct",
        min_value=1, max_value=99, step=1, format="%d%%",
        help="Monolith: minimum P(accepted) to classify as accepted. CC Full/Lightweight: minimum P(nuanced_rest) to route to L2."
    )

    _po_T            = st.session_state["po_thresh_pct"] / 100
    _po_thresh_label = f"{st.session_state['po_thresh_pct']}%"

    # ── Monolith dynamic (threshold on mono_accepted probability) ─────────────
    _mono_acc_col  = "mono_accepted"
    _mono_pred_dyn = (
        (_po_mono[_mono_cols].idxmax(axis=1) == _mono_acc_col) |
        (_po_mono[_mono_acc_col] >= _po_T)
    )
    # threshold logic: accepted if P(accepted) >= T, else argmax of remaining
    _mono_pred_dyn = _po_mono[_mono_acc_col] >= _po_T
    _mono_true_acc_dyn = _po_mono["y_true"] == "accepted"
    _mono_dyn_tp = int((_mono_pred_dyn & _mono_true_acc_dyn).sum())
    _mono_dyn_fn = int((~_mono_pred_dyn & _mono_true_acc_dyn).sum())
    _mono_dyn_fp = int((_mono_pred_dyn & ~_mono_true_acc_dyn).sum())
    _mono_dyn_tn = int((~_mono_pred_dyn & ~_mono_true_acc_dyn).sum())
    _mono_dyn_total_acc = _mono_dyn_tp + _mono_dyn_fp

    # ── 2. Bento routing cards (CC Full, dynamic) ─────────────────────────────
    _po_l1_dyn = _po_full[_po_l1_det].idxmax(axis=1).copy()
    _po_l1_dyn[_po_full["the_nuanced_rest"] >= _po_T] = "the_nuanced_rest"

    # CC Full routing stats (dynamic)
    _po_routed_mask  = (_po_l1_dyn == "the_nuanced_rest") & _po_full["y_true_l2"].notna()
    _po_fp_mask      = (_po_l1_dyn == "the_nuanced_rest") & _po_full["y_true_l2"].isna()
    _po_nr_routed    = int(_po_routed_mask.sum())
    _po_fp_count     = int(_po_fp_mask.sum())
    _po_total_routed = _po_nr_routed + _po_fp_count
    _po_pct_routed   = round(_po_total_routed / len(_po_full) * 100, 1)

    # CC Lightweight routing stats (same dynamic L1 as CC Full — L1 is shared)
    _pl_routed_mask  = (_po_l1_dyn == "the_nuanced_rest") & _po_light["y_true_l2"].notna()
    _pl_fp_mask      = (_po_l1_dyn == "the_nuanced_rest") & _po_light["y_true_l2"].isna()
    _pl_nr_routed    = int(_pl_routed_mask.sum())
    _pl_fp_count     = int(_pl_fp_mask.sum())
    _pl_total_routed = _pl_nr_routed + _pl_fp_count
    _pl_pct_routed   = round(_pl_total_routed / len(_po_light) * 100, 1)

    def _bento_col(label, total_holdout, total_routed, pct_routed, nr_routed, fp_count):
        return (
            f"<div style='display:flex;flex-direction:column;align-items:center;gap:0;'>"
            f"<div style='text-align:center;font-size:0.58rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;'>{label}</div>"
            "<div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>"
            "<div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'><div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 1</div></div>"
            "<div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>"
            f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;display:flex;justify-content:space-between;'><span>total holdout</span><span style='font-weight:700;color:#64748b;'>{total_holdout}</span></div>"
            f"<div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'><span>→ nuanced_rest</span><span>{total_routed}</span></div>"
            "</div></div>"
            f"<div style='display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0;'><div style='color:#21918c;font-size:1.1rem;'>↓</div><div style='font-size:0.55rem;font-weight:700;color:#64748b;'>{pct_routed}%</div></div>"
            "<div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>"
            "<div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'><div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Recall Autopsy</div></div>"
            "<div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>"
            f"<div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'><span>true nuanced</span><span>{nr_routed}</span></div>"
            f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;font-weight:600;display:flex;justify-content:space-between;'><span>false positives</span><span>{fp_count}</span></div>"
            "</div></div></div>"
        )

    # shared trunk (L1 is identical for both cascade variants)
    _routing_html = (
        "<div style='display:flex;flex-direction:column;align-items:center;margin-bottom:0;'>"
        "<div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:220px;'>"
        "<div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 1 &mdash; Shared</div>"
        "<div style='font-size:0.46rem;color:#94a3b8;margin-top:2px;'>identical for CC Full &amp; CC Lightweight</div>"
        "</div>"
        "<div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>"
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;display:flex;justify-content:space-between;'><span>total holdout</span><span style='font-weight:700;'>{len(_po_full)}</span></div>"
        f"<div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'><span>→ nuanced_rest</span><span>{_po_total_routed}</span></div>"
        "</div></div>"
        f"<div style='display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0;'><div style='color:#21918c;font-size:1.1rem;'>↓</div><div style='font-size:0.55rem;font-weight:700;color:#64748b;'>{_po_pct_routed}%</div></div>"
        "</div>"
    )
    # routing_html kept for reference but replaced by 3-col grid below

    # ── shared norm helper (used by all matrices below) ───────────────────────
    import re as _re_po
    def _po_norm(s): return _re_po.sub(r'[^\w]+', '_', str(s)).strip('_').lower()
    _po_l1_ytrue = _po_full["y_true_l1"].apply(_po_norm)

    # ── L1 binary confusion (nuanced_rest vs not) ─────────────────────────────
    _l1_tp = int(((_po_l1_dyn == "the_nuanced_rest") & (_po_l1_ytrue == "the_nuanced_rest")).sum())
    _l1_fp = int(((_po_l1_dyn == "the_nuanced_rest") & (_po_l1_ytrue != "the_nuanced_rest")).sum())
    _l1_fn = int(((_po_l1_dyn != "the_nuanced_rest") & (_po_l1_ytrue == "the_nuanced_rest")).sum())
    _l1_tn = int(((_po_l1_dyn != "the_nuanced_rest") & (_po_l1_ytrue != "the_nuanced_rest")).sum())

    _l1_2x2 = [[_l1_tp, _l1_fn], [_l1_fp, _l1_tn]]
    _l1_cw  = 72; _l1_lw = 90
    _l1_2x2_grid = f"{_l1_lw}px {_l1_cw}px {_l1_cw}px"
    _l1_row_labels = ["nuanced_rest", "not nuanced"]
    _l1_col_labels = ["nuanced_rest", "not nuanced"]
    _l1_cell_meta  = [
        [("TP", "#21918c", f"rgba(33,145,140,{max(0.14,_l1_tp/780*0.85):.2f})"),
         ("FN", "#64748b", "rgba(100,116,139,0.10)")],
        [("FP", "#64748b", "rgba(100,116,139,0.10)"),
         ("TN", "#475569", f"rgba(33,145,140,{max(0.06,_l1_tn/780*0.4):.2f})")],
    ]
    _l1_2x2_rows = ""
    for i, rl in enumerate(_l1_row_labels):
        _l1_2x2_rows += f"<div style='display:grid;grid-template-columns:{_l1_2x2_grid};gap:3px;margin-bottom:3px;'>"
        _l1_2x2_rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;'>{rl}</div>"
        for j in range(2):
            _v = _l1_2x2[i][j]; _tag, _tc2, _bg2 = _l1_cell_meta[i][j]
            _l1_bdr = "border:2px solid rgba(245,158,11,0.45);" if _tag == "FP" else "border:2px solid transparent;"
            _l1_2x2_rows += (
                f"<div style='background:{_bg2};border-radius:4px;aspect-ratio:1;{_l1_bdr}"
                f"display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;'>"
                f"<div style='font-size:0.80rem;font-weight:700;color:{_tc2};'>{_v}</div>"
                f"<div style='font-size:0.42rem;font-weight:700;color:{_tc2};opacity:0.7;letter-spacing:0.5px;'>{_tag}</div>"
                f"</div>"
            )
        _l1_2x2_rows += "</div>"
    _l1_2x2_bot  = f"<div style='display:grid;grid-template-columns:{_l1_2x2_grid};gap:3px;margin-top:4px;'><div></div>"
    _l1_2x2_bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;'>{l}</div>" for l in _l1_col_labels)
    _l1_2x2_bot += "</div>"
    _l1_2x2_pred = f"<div style='display:grid;grid-template-columns:{_l1_2x2_grid};margin-top:5px;'><div></div><div style='grid-column:2/4;text-align:center;font-size:0.48rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>Predicted</div></div>"
    _l1_real     = "<div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.46rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;align-self:center;'>Actual</div>"

    _l1_shared_note = (
        "<div style='display:flex;flex-direction:column;align-items:center;justify-content:center;width:220px;gap:6px;'>"
        "<div style='background:rgba(33,145,140,0.06);border:1px dashed rgba(33,145,140,0.3);border-radius:10px;padding:12px 16px;text-align:center;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Shared Layer 1</div>"
        "<div style='font-size:0.52rem;color:#64748b;line-height:1.5;'>CC Full and CC Lightweight share the same L1 model.<br>These numbers are identical for both cascade variants.</div>"
        "</div>"
        "</div>"
    )
    _l1_2x2_html = (
        "<div style='display:flex;justify-content:center;gap:40px;margin:20px 0 8px;'>"
        "<div style='display:flex;flex-direction:column;align-items:center;gap:6px;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>L1 Binary Confusion &mdash; Both Cascade Variants</div>"
        f"<div style='display:flex;gap:6px;align-items:center;'>{_l1_real}<div>{_l1_2x2_rows}{_l1_2x2_bot}{_l1_2x2_pred}</div></div>"
        "</div>"
        "</div>"
        "<div style='display:flex;justify-content:center;margin:4px 0 20px;'>"
        "<svg width='340' height='60' xmlns='http://www.w3.org/2000/svg'>"
        "<line x1='170' y1='0' x2='170' y2='20' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='60' y1='20' x2='280' y2='20' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='60' y1='20' x2='60' y2='44' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='280' y1='20' x2='280' y2='44' stroke='#21918c' stroke-width='1.5'/>"
        "<polygon points='60,44 55,38 65,38' fill='#21918c'/>"
        "<polygon points='280,44 275,38 285,38' fill='#21918c'/>"
        "<text x='60' y='58' text-anchor='middle' font-size='8' font-weight='700' fill='#21918c' font-family='monospace' letter-spacing='1'>CC FULL</text>"
        "<text x='280' y='58' text-anchor='middle' font-size='8' font-weight='700' fill='#21918c' font-family='monospace' letter-spacing='1'>CC LIGHTWEIGHT</text>"
        "</svg>"
        "</div>"
    )
    @st.cache_data(show_spinner=False)
    def _po_l1_sweep(_df_f, _df_l):
        _l1_det   = ["dropoff_non_operational", "dropoff_proxy_zone", "long_pickup_time", "low_profitability"]
        _l1_base  = _df_f[_l1_det].idxmax(axis=1)
        _l1_ytrue = _df_f["y_true_l1"].str.lower().str.replace(r"[^\w]+", "_", regex=True).str.strip("_")
        _l2_ytrue_f = _df_f["y_true_l2"].str.lower().str.replace(r"[^\w]+", "_", regex=True).str.strip("_")
        _l2_ytrue_l = _df_l["y_true_l2"].str.lower().str.replace(r"[^\w]+", "_", regex=True).str.strip("_")
        rows = []
        for t in range(1, 100):
            _l1_dyn  = _l1_base.copy()
            _l1_dyn[_df_f["the_nuanced_rest"] >= t / 100] = "the_nuanced_rest"
            _routed  = _l1_dyn == "the_nuanced_rest"
            _l1_fp   = int((_routed & (_l1_ytrue != "the_nuanced_rest")).sum())
            _has_gt_f = _routed & _df_f["y_true_l2"].notna()
            _has_gt_l = _routed & _df_l["y_true_l2"].notna()
            _pred_f  = (_df_f[["l2_strategic_mismatch","l2_expected_value_gamble","l2_accepted"]]
                        .fillna(0).idxmax(axis=1).str.replace("l2_","",regex=False))
            _pred_l  = (_df_l[["spartan_l2_strategic_mismatch","spartan_l2_expected_value_gamble","spartan_l2_accepted"]]
                        .fillna(0).idxmax(axis=1).str.replace("spartan_l2_","",regex=False))
            _tp_f = int((_routed & (_pred_f == "accepted") & _has_gt_f & (_l2_ytrue_f == "accepted")).sum())
            _tp_l = int((_routed & (_pred_l == "accepted") & _has_gt_l & (_l2_ytrue_l == "accepted")).sum())
            rows.append({"t": t, "l1_fp": _l1_fp, "l2_tp_full": _tp_f, "l2_tp_light": _tp_l})
        return pd.DataFrame(rows)

    _l1_sw = _po_l1_sweep(_po_full, _po_light)

    import plotly.graph_objects as _go_l1sw
    _cur_t_sw    = st.session_state["po_thresh_pct"]
    _cur_tp_f_sw = int(_l1_sw.loc[_l1_sw["t"] == _cur_t_sw, "l2_tp_full"].iloc[0])
    _cur_tp_l_sw = int(_l1_sw.loc[_l1_sw["t"] == _cur_t_sw, "l2_tp_light"].iloc[0])
    _cur_fp_sw   = int(_l1_sw.loc[_l1_sw["t"] == _cur_t_sw, "l1_fp"].iloc[0])

    _fig_l1sw = _go_l1sw.Figure()
    _fig_l1sw.add_trace(_go_l1sw.Scatter(
        x=_l1_sw["t"], y=_l1_sw["l2_tp_full"],
        mode="lines", name="TP accepted · CC Full",
        line=dict(color="#21918c", width=2),
        hovertemplate="t=%{x}%<br>TP Full=%{y}<extra></extra>",
    ))
    _fig_l1sw.add_trace(_go_l1sw.Scatter(
        x=_l1_sw["t"], y=_l1_sw["l2_tp_light"],
        mode="lines", name="TP accepted · CC Lightweight",
        line=dict(color="#21918c", width=2, dash="dot"),
        hovertemplate="t=%{x}%<br>TP Light=%{y}<extra></extra>",
    ))
    _fig_l1sw.add_trace(_go_l1sw.Scatter(
        x=_l1_sw["t"], y=_l1_sw["l1_fp"],
        mode="lines", name="FP non-nuanced (L1, shared)",
        line=dict(color="#94a3b8", width=2),
        hovertemplate="t=%{x}%<br>L1 FP=%{y}<extra></extra>",
    ))
    _fig_l1sw.add_shape(type="line", xref="x", yref="paper",
        x0=_cur_t_sw, x1=_cur_t_sw, y0=0, y1=1,
        line=dict(color="#94a3b8", width=1, dash="dot"))
    _fig_l1sw.add_annotation(x=_cur_t_sw, y=_cur_tp_f_sw,
        text=f"  Full={_cur_tp_f_sw}", showarrow=False,
        font=dict(size=9, color="#21918c"), xanchor="left", yanchor="middle")
    _fig_l1sw.add_annotation(x=_cur_t_sw, y=_cur_tp_l_sw,
        text=f"  Light={_cur_tp_l_sw}", showarrow=False,
        font=dict(size=9, color="#21918c"), xanchor="left", yanchor="bottom")
    _fig_l1sw.add_annotation(x=_cur_t_sw, y=_cur_fp_sw,
        text=f"  FP={_cur_fp_sw}", showarrow=False,
        font=dict(size=9, color="#94a3b8"), xanchor="left", yanchor="middle")
    _fig_l1sw.update_layout(
        xaxis=dict(title="threshold (%)", tickfont=dict(size=8), gridcolor="#f1f5f9", range=[10, 95]),
        yaxis=dict(title="count", tickfont=dict(size=8), gridcolor="#f1f5f9", range=[0, 70]),
        legend=dict(font=dict(size=8), orientation="h", y=-0.25),
        margin=dict(l=40, r=10, t=10, b=40),
        height=320, plot_bgcolor="#fafafa", paper_bgcolor="white",
    )

    # ── CC Full confusion matrices (L2 + FP) ─────────────────────────────────
    _PO_L2_ORDER  = ["strategic_mismatch", "expected_value_gamble", "accepted"]

    # Layer 2 matrix — true nuanced rows routed correctly
    _po_routed_l2_mask = (_po_l1_dyn == "the_nuanced_rest") & _po_full["y_true_l2"].notna()
    _po_df_routed      = _po_full[_po_routed_l2_mask]
    _po_pred_l2        = _po_df_routed[[f"l2_{c}" for c in _PO_L2_ORDER]].fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False)
    _po_ytrue_l2       = _po_df_routed["y_true_l2"].apply(_po_norm)
    _po_l2_cm          = [
        [int(((_po_ytrue_l2 == tc) & (_po_pred_l2 == pc)).sum()) for pc in _PO_L2_ORDER]
        for tc in _PO_L2_ORDER
    ]
    _po_l2_row_sums = [sum(r) for r in _po_l2_cm]

    _po_sm_cw = 52; _po_sm_lw = 82
    _po_l2_grid = f"{_po_sm_lw}px " + " ".join([f"{_po_sm_cw}px"] * 3)

    _po_l2_rows = ""
    for i, tc in enumerate(_PO_L2_ORDER):
        _rt = _po_l2_row_sums[i] or 1
        _po_l2_rows += f"<div style='display:grid;grid-template-columns:{_po_l2_grid};gap:2px;margin-bottom:2px;'>"
        _po_l2_rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:6px;align-self:center;white-space:normal;word-break:break-word;line-height:1.2;'>{tc.replace('_',' ')}</div>"
        for j, pc in enumerate(_PO_L2_ORDER):
            _val = _po_l2_cm[i][j]; _pct = _val / _rt; _diag = (i == j)
            if _diag:
                _bg2 = f"rgba(33,145,140,{max(0.14,_pct*0.85):.2f})"; _tc2 = "#fff" if _pct > 0.45 else "#21918c"; _fw2 = "700"
            elif _val == 0:
                _bg2 = "#f8fafc"; _tc2 = "#e2e8f0"; _fw2 = "400"
            else:
                _bg2 = f"rgba(33,145,140,{max(0.04,_pct*0.35):.2f})"; _tc2 = "#94a3b8"; _fw2 = "500"
            _po_l2_rows += f"<div style='background:{_bg2};border-radius:3px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;'><div style='font-size:0.72rem;color:{_tc2};font-weight:{_fw2};'>{_pct*100:.0f}%</div></div>"
        _po_l2_rows += "</div>"
    _po_l2_bot = f"<div style='display:grid;grid-template-columns:{_po_l2_grid};gap:2px;margin-top:4px;'><div></div>"
    _po_l2_bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.2;'>{l.replace('_',' ')}</div>" for l in _PO_L2_ORDER)
    _po_l2_bot += "</div>"
    _po_l2_pred = f"<div style='display:grid;grid-template-columns:{_po_l2_grid};margin-top:6px;'><div></div><div style='grid-column:2/5;text-align:center;font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>Predicted</div></div>"

    # FP matrix — L1 false positives routed to L2
    _PO_FP_ROW_ORDER = ["dropoff_non_operational", "dropoff_proxy_zone", "low_profitability", "long_pickup_time"]
    _po_fp_mask      = (_po_l1_dyn == "the_nuanced_rest") & (_po_l1_ytrue != "the_nuanced_rest")
    _po_df_fp        = _po_full[_po_fp_mask]
    _po_ytrue_fp     = _po_l1_ytrue[_po_fp_mask]
    _po_pred_fp_l2   = _po_df_fp[[f"l2_{c}" for c in _PO_L2_ORDER]].fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False)
    _po_fp_display   = {"dropoff_non_operational": "non operational", "dropoff_proxy_zone": "proxy zone",
                        "low_profitability": "low profit", "long_pickup_time": "long pickup"}
    _po_fp_cm        = [
        [int(((_po_ytrue_fp == tc) & (_po_pred_fp_l2 == pc)).sum()) for pc in _PO_L2_ORDER]
        for tc in _PO_FP_ROW_ORDER
    ]
    _po_fp_row_sums = [sum(r) for r in _po_fp_cm]

    _po_fp_rows = ""
    for i, tc in enumerate(_PO_FP_ROW_ORDER):
        _rt = _po_fp_row_sums[i] or 1
        _lbl = _po_fp_display.get(tc, tc)
        _po_fp_rows += f"<div style='display:grid;grid-template-columns:{_po_l2_grid};gap:2px;margin-bottom:2px;'>"
        _po_fp_rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:6px;align-self:center;white-space:normal;word-break:break-word;line-height:1.2;'>{_lbl}</div>"
        for j, pc in enumerate(_PO_L2_ORDER):
            _val = _po_fp_cm[i][j]; _pct = _val / _rt
            if _val == 0:
                _bg2 = "#f8fafc"; _tc2 = "#e2e8f0"; _fw2 = "400"
            else:
                _bg2 = f"rgba(100,116,139,{max(0.08,_pct*0.55):.2f})"; _tc2 = "#1e293b"; _fw2 = "500"
            _po_fp_rows += f"<div style='background:{_bg2};border-radius:3px;text-align:center;aspect-ratio:1;display:flex;align-items:center;justify-content:center;'><div style='font-size:0.72rem;color:{_tc2};font-weight:{_fw2};'>{_pct*100:.0f}%</div></div>"
        _po_fp_rows += "</div>"
    _po_fp_bot = f"<div style='display:grid;grid-template-columns:{_po_l2_grid};gap:2px;margin-top:4px;'><div></div>"
    _po_fp_bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;word-break:break-word;line-height:1.2;'>{l.replace('_',' ')}</div>" for l in _PO_L2_ORDER)
    _po_fp_bot += "</div>"
    _po_fp_pred = f"<div style='display:grid;grid-template-columns:{_po_l2_grid};margin-top:6px;'><div></div><div style='grid-column:2/5;text-align:center;font-size:0.50rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>L2 Predicted</div></div>"

    _po_real_label = "<div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.46rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;align-self:center;'>Real</div>"
    _po_l1real_label = "<div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.46rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;align-self:center;'>L1 Real</div>"

    _po_matrices_html = (
        "<div style='display:flex;justify-content:center;margin:28px 0 36px;'>"
        "<div style='display:flex;flex-direction:column;gap:32px;'>"
        "<div>"
        "<div style='font-size:0.60rem;font-weight:700;color:#21918c;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;'>Layer 2</div>"
        f"<div style='display:flex;gap:6px;align-items:center;'>{_po_real_label}<div>{_po_l2_rows}{_po_l2_bot}{_po_l2_pred}</div></div>"
        "</div>"
        "<div>"
        "<div style='font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;'>L1 False Positives · Routed to L2</div>"
        f"<div style='display:flex;gap:6px;align-items:center;'>{_po_l1real_label}<div>{_po_fp_rows}{_po_fp_bot}{_po_fp_pred}</div></div>"
        "</div>"
        "</div></div>"
    )
    # ── L2 data: CC Full ──────────────────────────────────────────────────────
    _po_l2_tp = int(((_po_pred_l2 == "accepted") & (_po_ytrue_l2 == "accepted")).sum())
    _po_l2_fn = int(((_po_pred_l2 != "accepted") & (_po_ytrue_l2 == "accepted")).sum())
    _po_l2_fp = int(((_po_pred_l2 == "accepted") & (_po_ytrue_l2 != "accepted")).sum())
    _po_l2_tn = int(((_po_pred_l2 != "accepted") & (_po_ytrue_l2 != "accepted")).sum())
    _po_l2_fp_accepted = int((_po_df_fp[[f"l2_{c}" for c in _PO_L2_ORDER]].fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False) == "accepted").sum())
    _po_l2_n_true = int(_po_routed_l2_mask.sum())

    # ── L2 data: CC Lightweight ───────────────────────────────────────────────
    _PLW_L2_COLS  = ["spartan_l2_strategic_mismatch", "spartan_l2_expected_value_gamble", "spartan_l2_accepted"]
    _po_lw_routed_mask = (_po_l1_dyn == "the_nuanced_rest") & _po_light["y_true_l2"].notna()
    _po_lw_df_routed   = _po_light[_po_lw_routed_mask]
    _po_lw_pred_l2     = _po_lw_df_routed[_PLW_L2_COLS].fillna(0).idxmax(axis=1).str.replace("spartan_l2_", "", regex=False)
    _po_lw_ytrue_l2    = _po_lw_df_routed["y_true_l2"].apply(_po_norm)
    _po_lw_df_fp       = _po_light[(_po_l1_dyn == "the_nuanced_rest") & (_po_l1_ytrue != "the_nuanced_rest")]
    _po_lw_tp = int(((_po_lw_pred_l2 == "accepted") & (_po_lw_ytrue_l2 == "accepted")).sum())
    _po_lw_fn = int(((_po_lw_pred_l2 != "accepted") & (_po_lw_ytrue_l2 == "accepted")).sum())
    _po_lw_fp = int(((_po_lw_pred_l2 == "accepted") & (_po_lw_ytrue_l2 != "accepted")).sum())
    _po_lw_tn = int(((_po_lw_pred_l2 != "accepted") & (_po_lw_ytrue_l2 != "accepted")).sum())
    _po_lw_fp_accepted = int((_po_lw_df_fp[_PLW_L2_COLS].fillna(0).idxmax(axis=1).str.replace("spartan_l2_", "", regex=False) == "accepted").sum())
    _po_lw_n_true = int(_po_lw_routed_mask.sum())

    # ── 2×2 binary confusion: CC Full + CC Lightweight side by side ───────────
    def _po_build_2x2(tp, fn, fp, tn, n_total, fp_acc, highlight=()):
        # highlight: tuple of cell tags to outline in orange e.g. ("TP", "FP")
        _cw = 72; _lw = 90
        _grid = f"{_lw}px {_cw}px {_cw}px"
        _rl = ["accepted", "not accepted"]
        _cl = ["accepted", "not accepted"]
        _meta = [
            [("TP", "#21918c", f"rgba(33,145,140,{max(0.14,tp/n_total*0.85):.2f})"),
             ("FN", "#64748b", "rgba(100,116,139,0.10)")],
            [("FP", "#64748b", "rgba(100,116,139,0.10)"),
             ("TN", "#475569", f"rgba(33,145,140,{max(0.06,tn/n_total*0.4):.2f})")],
        ]
        _vals = [[tp, fn], [fp, tn]]
        _rows = ""
        for i, rl in enumerate(_rl):
            _rows += f"<div style='display:grid;grid-template-columns:{_grid};gap:3px;margin-bottom:3px;'>"
            _rows += f"<div style='font-size:0.50rem;color:#64748b;font-weight:600;text-align:right;padding-right:8px;align-self:center;'>{rl}</div>"
            for j in range(2):
                _v = _vals[i][j]; _tag, _tc2, _bg2 = _meta[i][j]
                _border = "border:2px solid rgba(245,158,11,0.45);" if _tag in highlight else "border:2px solid transparent;"
                _rows += (
                    f"<div style='background:{_bg2};border-radius:4px;aspect-ratio:1;{_border}"
                    f"display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;'>"
                    f"<div style='font-size:0.80rem;font-weight:700;color:{_tc2};'>{_v}</div>"
                    f"<div style='font-size:0.42rem;font-weight:700;color:{_tc2};opacity:0.7;letter-spacing:0.5px;'>{_tag}</div>"
                    f"</div>"
                )
            _rows += "</div>"
        _bot = f"<div style='display:grid;grid-template-columns:{_grid};gap:3px;margin-top:4px;'><div></div>"
        _bot += "".join(f"<div style='font-size:0.46rem;font-weight:600;color:#64748b;text-align:center;'>{l}</div>" for l in _cl)
        _bot += "</div>"
        _pred = f"<div style='display:grid;grid-template-columns:{_grid};margin-top:5px;'><div></div><div style='grid-column:2/4;text-align:center;font-size:0.48rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>Predicted (Accepted?)</div></div>"
        _actual = "<div style='writing-mode:vertical-rl;transform:rotate(180deg);font-size:0.46rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;align-self:center;'>Actual</div>"
        _total_ai_neq = fp + fp_acc
        _recon = (
            f"<div style='margin-top:10px;font-size:0.48rem;color:#94a3b8;border-top:1px dashed #e2e8f0;padding-top:8px;'>"
            f"<div style='display:flex;justify-content:space-between;'><span>FP (over-accepted, ground truth)</span><span style='color:#64748b;font-weight:700;'>{fp}</span></div>"
            f"<div style='display:flex;justify-content:space-between;'><span>L1 FP &#8594; accepted by L2 (no GT)</span><span style='color:#64748b;font-weight:700;'>{fp_acc}</span></div>"
            f"<div style='display:flex;justify-content:space-between;border-top:1px solid #e2e8f0;margin-top:4px;padding-top:4px;font-weight:700;color:#64748b;'>"
            f"<span>Total AI&#8800;Human (accepted)</span><span style='color:#475569;'>{_total_ai_neq}</span></div>"
            f"</div>"
        )
        return f"<div style='display:flex;gap:6px;align-items:center;'>{_actual}<div>{_rows}{_bot}{_pred}{_recon}</div></div>"

    # ── Monolith card (row 1) ─────────────────────────────────────────────────
    _mono_card = (
        "<div style='display:flex;flex-direction:column;align-items:center;gap:8px;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>Monolith</div>"
        "<div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:200px;'>"
        "<div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;'>Single Layer</div>"
        "<div style='font-size:0.46rem;color:#94a3b8;margin-top:2px;'>P(accepted) ≥ threshold · no cascade</div>"
        "</div>"
        "<div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>"
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;display:flex;justify-content:space-between;'><span>total holdout</span><span style='font-weight:700;'>{len(_po_mono)}</span></div>"
        f"<div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'><span>→ predicted accepted</span><span>{_mono_dyn_tp + _mono_dyn_fp}</span></div>"
        "</div></div>"
        f"<div style='display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0;'><div style='color:#64748b;font-size:1.1rem;'>↓</div></div>"
        "</div>"
    )

    # ── Monolith matrix (row 2 — same level as CC Full/Lightweight) ───────────
    _mono_matrix = (
        "<div style='display:flex;flex-direction:column;align-items:center;gap:6px;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#64748b;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>Monolith · Binary Confusion</div>"
        + _po_build_2x2(_mono_dyn_tp, _mono_dyn_fn, _mono_dyn_fp, _mono_dyn_tn, int(_mono_true_acc_dyn.sum()), 0, highlight=("TP", "FP"))
        + "</div>"
    )

    # ── L1 shared bento (spans CC Full + CC Lightweight) ─────────────────────
    _l1_shared_bento = (
        "<div style='display:flex;flex-direction:column;align-items:center;gap:0;'>"
        "<div style='background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;padding:0;overflow:hidden;width:220px;'>"
        "<div style='padding:8px 12px;border-bottom:1px solid #f1f5f9;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;'>Layer 1 &mdash; Shared</div>"
        "<div style='font-size:0.46rem;color:#94a3b8;margin-top:2px;'>identical for CC Full &amp; CC Lightweight</div>"
        "</div>"
        "<div style='padding:8px 10px;display:flex;flex-direction:column;gap:4px;'>"
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#64748b;display:flex;justify-content:space-between;'><span>total holdout</span><span style='font-weight:700;'>{len(_po_full)}</span></div>"
        f"<div style='background:rgba(33,145,140,0.08);border:1px solid rgba(33,145,140,0.3);border-radius:6px;padding:5px 10px;font-size:0.6rem;color:#21918c;font-weight:700;display:flex;justify-content:space-between;'><span>→ nuanced_rest</span><span>{_po_total_routed}</span></div>"
        "</div></div>"
        f"<div style='display:flex;flex-direction:column;align-items:center;gap:2px;padding:6px 0;'>"
        f"<div style='color:#21918c;font-size:1.1rem;'>↓</div>"
        f"<div style='font-size:0.55rem;font-weight:700;color:#64748b;'>{_po_pct_routed}%</div></div>"
        # L1 matrix inline (no outer centering wrapper)
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;text-align:center;'>L1 Binary Confusion</div>"
        f"<div style='display:flex;gap:6px;align-items:center;'>{_l1_real}<div>{_l1_2x2_rows}{_l1_2x2_bot}{_l1_2x2_pred}</div></div>"
        # SVG bifurcation
        "<div style='margin:4px 0 8px;'>"
        "<svg width='340' height='60' xmlns='http://www.w3.org/2000/svg'>"
        "<line x1='170' y1='0' x2='170' y2='20' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='60' y1='20' x2='280' y2='20' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='60' y1='20' x2='60' y2='44' stroke='#21918c' stroke-width='1.5'/>"
        "<line x1='280' y1='20' x2='280' y2='44' stroke='#21918c' stroke-width='1.5'/>"
        "<polygon points='60,44 55,38 65,38' fill='#21918c'/>"
        "<polygon points='280,44 275,38 285,38' fill='#21918c'/>"
        "<text x='60' y='58' text-anchor='middle' font-size='8' font-weight='700' fill='#21918c' font-family='monospace' letter-spacing='1'>CC FULL</text>"
        "<text x='280' y='58' text-anchor='middle' font-size='8' font-weight='700' fill='#21918c' font-family='monospace' letter-spacing='1'>CC LIGHTWEIGHT</text>"
        "</svg>"
        "</div>"
        "</div>"
    )

    # ── L2 CC Full bento ──────────────────────────────────────────────────────
    _l2_full_bento = (
        "<div style='display:flex;flex-direction:column;align-items:center;gap:6px;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>CC Full · Binary Confusion</div>"
        + _po_build_2x2(_po_l2_tp, _po_l2_fn, _po_l2_fp, _po_l2_tn, _po_l2_n_true, _po_l2_fp_accepted, highlight=("TP",))
        + "</div>"
    )

    # ── L2 CC Lightweight bento ───────────────────────────────────────────────
    _l2_lw_bento = (
        "<div style='display:flex;flex-direction:column;align-items:center;gap:6px;'>"
        "<div style='font-size:0.55rem;font-weight:700;color:#21918c;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>CC Lightweight · Binary Confusion</div>"
        + _po_build_2x2(_po_lw_tp, _po_lw_fn, _po_lw_fp, _po_lw_tn, _po_lw_n_true, _po_lw_fp_accepted, highlight=("TP",))
        + "</div>"
    )

    # ── 3-column CSS grid layout ──────────────────────────────────────────────
    _po_grid_html = (
        "<div style='display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-rows:auto auto;gap:24px 32px;align-items:start;margin:24px 0 32px;'>"
        # row 1 col 1: Monolith card (pinned to top, does not stretch)
        f"<div style='display:flex;justify-content:center;align-self:start;'>{_mono_card}</div>"
        # row 1 col 2+3: L1 shared trunk
        f"<div style='grid-column:2/4;display:flex;justify-content:center;'>{_l1_shared_bento}</div>"
        # row 2 col 1: Monolith matrix
        f"<div style='display:flex;justify-content:center;align-self:start;'>{_mono_matrix}</div>"
        # row 2 col 2: CC Full L2
        f"<div style='display:flex;justify-content:center;'>{_l2_full_bento}</div>"
        # row 2 col 3: CC Lightweight L2
        f"<div style='display:flex;justify-content:center;'>{_l2_lw_bento}</div>"
        "</div>"
    )
    st.markdown(_po_grid_html, unsafe_allow_html=True)

    _sw_empty, _sw_chart = st.columns([1, 2])
    with _sw_chart:
        st.plotly_chart(_fig_l1sw, use_container_width=True)

    # ── 3. Static scorecard (all models at 50%) ───────────────────────────────
    st.markdown(_scorecard_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:40px;border-top:1px solid #e2e8f0;padding-top:32px;'></div>", unsafe_allow_html=True)

    # ── Dynamic scorecard (CC Full + CC Lightweight respond to slider) ────────
    _dyn_routed = _po_l1_dyn == "the_nuanced_rest"

    _po_l2_dyn = pd.Series("_", index=_po_full.index)
    _po_l2_dyn[_dyn_routed] = (
        _po_full.loc[_dyn_routed, ["l2_strategic_mismatch", "l2_expected_value_gamble", "l2_accepted"]]
        .fillna(0).idxmax(axis=1).str.replace("l2_", "", regex=False)
    )
    _dyn_pred_acc = _po_l2_dyn == "accepted"
    _dyn_b = _po_breakdown(_po_full, _dyn_pred_acc, _full_true_acc, no_gt_mask=_full_no_gt)



    _pl_l2_dyn = pd.Series("_", index=_po_light.index)
    _pl_l2_dyn[_dyn_routed] = (
        _po_light.loc[_dyn_routed, ["spartan_l2_strategic_mismatch", "spartan_l2_expected_value_gamble", "spartan_l2_accepted"]]
        .fillna(0).idxmax(axis=1).str.replace("spartan_l2_", "", regex=False)
    )
    _pl_dyn_pred_acc = _pl_l2_dyn == "accepted"
    _lb_dyn = _po_breakdown(_po_light, _pl_dyn_pred_acc, _light_true_acc, no_gt_mask=_light_no_gt)

    # winner among the dynamic column + static columns
    _dyn_earnings = {"human": _po_h_earn, "mono": _mb["earn"], "full": _dyn_b["earn"], "light": _lb_dyn["earn"]}
    _dyn_winner   = max(_dyn_earnings, key=_dyn_earnings.get)

    def _dyn_col_header(key, label, sublabel, is_active=False):
        is_win  = _dyn_winner == key
        bg      = "rgba(33,145,140,0.07)" if is_win else "#f8fafc"
        bdr     = "border-left:2px solid #21918c;" if is_win else "border-left:1px solid rgba(33,145,140,0.12);"
        color   = "#21918c" if is_win else "#64748b"
        sub_col = "#21918c" if is_win else "#94a3b8"
        crown   = " ★" if is_win else ""
        active_badge = f" <span style='font-size:0.5rem;background:#21918c;color:#fff;border-radius:3px;padding:1px 4px;vertical-align:middle;'>ACTIVE</span>" if is_active else ""
        return (
            f"<div style='background:{bg};padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);{bdr}"
            f"text-align:center;font-size:0.65rem;font-weight:700;color:{color};letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>"
            f"{label}{crown}{active_badge} <span style='font-size:0.58rem;color:{sub_col};font-weight:500;letter-spacing:0;text-transform:none;'>{sublabel}</span></div>"
        )

    def _dyn_cell(key, val):
        is_win = _dyn_winner == key
        bdr = "border-left:2px solid rgba(33,145,140,0.4);" if is_win else "border-left:1px solid rgba(33,145,140,0.12);"
        return f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);{bdr}text-align:center;'>{val}</div>"

    _dyn_earn_bdr_h     = "1px solid rgba(33,145,140,0.12)"
    _dyn_earn_bdr_mono  = "2px solid rgba(33,145,140,0.4)" if _dyn_winner == "mono"  else "1px solid rgba(33,145,140,0.12)"
    _dyn_earn_bdr_full  = "2px solid rgba(33,145,140,0.4)" if _dyn_winner == "full"  else "1px solid rgba(33,145,140,0.12)"
    _dyn_earn_bdr_light = "2px solid rgba(33,145,140,0.4)" if _dyn_winner == "light" else "1px solid rgba(33,145,140,0.12)"

    _num_dyn_full  = _num_kpi(f"${_dyn_b['earn']:,.0f}")
    _num_dyn_light = _num_kpi(f"${_lb_dyn['earn']:,.0f}")

    _dyn_tot_mono  = _mb["human_eq_ai"]    + _mb["ai_ne_human"]
    _dyn_tot_full  = _dyn_b["human_eq_ai"] + _dyn_b["ai_ne_human"]
    _dyn_tot_light = _lb_dyn["human_eq_ai"] + _lb_dyn["ai_ne_human"]

    _dyn_scorecard = (
        "<div style='display:flex;justify-content:center;'>"
        "<div style='display:inline-block;border:1px solid rgba(33,145,140,0.2);border-radius:6px;overflow:hidden;'>"
        "<div style='display:grid;grid-template-columns:195px 125px 125px 125px 125px;'>"
        "<div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;'>Accepted</div>"
        "<div style='background:#f8fafc;padding:6px 10px;border-bottom:1px solid rgba(33,145,140,0.12);border-left:1px solid rgba(33,145,140,0.12);text-align:center;font-size:0.60rem;font-weight:700;color:#64748b;letter-spacing:0.8px;text-transform:uppercase;white-space:nowrap;'>Human <span style='font-size:0.55rem;color:#94a3b8;font-weight:500;letter-spacing:0;text-transform:none;'>Ground Truth</span></div>"
        f"{_dyn_col_header('mono',  'Monolith',       '50% fixed')}"
        f"{_dyn_col_header('full',  'CC Full',        _po_thresh_label, is_active=True)}"
        f"{_dyn_col_header('light', 'CC Lightweight', _po_thresh_label, is_active=True)}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Human Only</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num(_po_h_total)}</div>"
        f"{_dyn_cell('mono', _dash)}{_dyn_cell('full', _dash)}{_dyn_cell('light', _dash)}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#21918c;text-transform:uppercase;letter-spacing:0.5px;'>Human = AI</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>both accepted</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_dash}</div>"
        f"{_dyn_cell('mono', _num_pct(_mb['human_eq_ai'], _po_h_total))}"
        f"{_dyn_cell('full', _num_pct(_dyn_b['human_eq_ai'], _po_h_total))}"
        f"{_dyn_cell('light', _num_pct(_lb_dyn['human_eq_ai'], _po_h_total))}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:rgba(33,145,140,0.55);text-transform:uppercase;letter-spacing:0.5px;'>AI ≠ Human</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>AI accepted, human rejected</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_dash}</div>"
        f"{_dyn_cell('mono', _num_pct(_mb['ai_ne_human'], _po_h_total, muted=True))}"
        f"{_dyn_cell('full', _num_pct(_dyn_b['ai_ne_human'], _po_h_total, muted=True))}"
        f"{_dyn_cell('light', _num_pct(_lb_dyn['ai_ne_human'], _po_h_total, muted=True))}"
        "<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Total Accepted</div><div style='font-size:0.50rem;color:#94a3b8;margin-top:1px;'>human=AI + AI≠human</div></div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num(_tot_h)}</div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{_dyn_earn_bdr_mono};text-align:center;'>{_num(_dyn_tot_mono)}</div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{_dyn_earn_bdr_full};text-align:center;'>{_num(_dyn_tot_full)}</div>"
        f"<div style='padding:7px 10px;border-bottom:1px solid rgba(33,145,140,0.08);border-left:{_dyn_earn_bdr_light};text-align:center;'>{_num(_dyn_tot_light)}</div>"
        "<div style='position:relative;padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Cumulative Earnings</div></div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_h};text-align:center;'>{_num_h}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_mono};text-align:center;'>{_num_mono}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_full};text-align:center;'>{_num_dyn_full}</div>"
        f"<div style='padding:8px 10px;border-bottom:1px solid rgba(33,145,140,0.08);background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_light};text-align:center;'>{_num_dyn_light}</div>"
        "<div style='padding:8px 10px;background:rgba(33,145,140,0.04);'><div style='font-size:0.62rem;font-weight:700;color:#334155;text-transform:uppercase;letter-spacing:0.5px;'>Avg / Accepted Ride</div></div>"
        f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:1px solid rgba(33,145,140,0.12);text-align:center;'>{_num_kpi(_avg(_po_h_earn, _tot_h))}</div>"
        f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_mono};text-align:center;'>{_num_kpi(_avg(_mb['earn'], _dyn_tot_mono))}</div>"
        f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_full};text-align:center;'>{_num_kpi(_avg(_dyn_b['earn'], _dyn_tot_full))}</div>"
        f"<div style='padding:8px 10px;background:rgba(33,145,140,0.04);border-left:{_dyn_earn_bdr_light};text-align:center;'>{_num_kpi(_avg(_lb_dyn['earn'], _dyn_tot_light))}</div>"
        "</div></div></div>"
        f"<div style='margin-top:12px;text-align:center;font-size:0.58rem;color:#94a3b8;'>CC Full &amp; CC Lightweight evaluated at {_po_thresh_label} threshold · Human &amp; Monolith fixed · ★ highest earner</div>"
    )
    st.markdown(_dyn_scorecard, unsafe_allow_html=True)

    # ── everything below this line removed (Threshold Sensitivity + post-its) ──
