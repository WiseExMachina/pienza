import streamlit as st

st.set_page_config(layout="wide", page_title="Foundations | Pienza", page_icon="🏗️")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown("Proyect Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0002_Foundations.py", label="Foundations")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox")
        st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping & The Efficient Frontier")
        st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
        st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("Archive")
        st.page_link("pages/9000_Project_Strategy_and_Scope.py", label="Project Strategy and Scope")
        st.page_link("pages/9000_Acquisition_and_Ground_Truth.py", label="Acquisition and Ground Truth")
        st.page_link("pages/9000_mock.py", label="WIP mock")
        st.page_link("pages/9000_found2.py", label="Found2")
        st.page_link("pages/9000_Foundations_and_Architecture.py", label="Foundations & Architecture")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button(
                "📄 Download 91-Page Report (PDF)",
                data=pdf_data,
                file_name="Project_Pienza_Full_Report.pdf",
                mime="application/pdf"
            )
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span {
    font-family: 'Inter', sans-serif !important;
}
h1 {
    font-size: 36px !important;
    font-weight: 400 !important;
    color: #121212;
    letter-spacing: -1px;
}
h2 {
    font-size: 22px !important;
    font-weight: 600 !important;
    color: #21918c;
    letter-spacing: -0.5px;
}
h3 {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #21918c;
}
p, li {
    color: #555;
    font-size: 0.9rem;
    line-height: 1.7;
}
.placeholder-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 48px 32px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    color: #aaa;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
}
.placeholder-card span {
    font-size: 2rem;
    display: block;
    margin-bottom: 12px;
    color: #ccc;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Foundations")
st.markdown("Infrastructure, ingestion pipelines, and telemetry simulation underpinning Project Pienza.")
st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📖 Intro & Timeline", "🔄 Data Ingestion Pipelines", "🎮 GTS Telemetry Simulator"])

with tab1:
    st.markdown("## Intro & Timeline")
    st.markdown("""
<style>
.story-section { border-left: 3px solid #21918c; padding-left: 20px; margin-bottom: 32px; }
.story-section p { font-size: 0.88rem; color: #555; line-height: 1.75; margin: 0; }
.story-pill {
    display: inline-block;
    background: #f0fafa;
    border: 1px solid #21918c;
    color: #21918c;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.story-footnote {
    font-size: 0.75rem;
    color: #999;
    margin-top: 10px;
    font-style: italic;
}
.story-footnote a { color: #21918c; text-decoration: none; }
.story-footnote a:hover { text-decoration: underline; }
.fn-wrap {
    display: inline-block;
    position: relative;
}
.fn-mark {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    color: #21918c;
    vertical-align: super;
    cursor: default;
    border-bottom: 1px dotted #21918c;
}
.fn-wrap .fn-tooltip {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: #ffffff;
    color: #555;
    font-size: 0.78rem;
    line-height: 1.5;
    border: 1px solid #21918c;
    border-radius: 8px;
    padding: 10px 14px;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    transition: opacity 0.2s ease;
    z-index: 9999;
}
.fn-wrap .fn-tooltip::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #21918c;
}
.fn-wrap:hover .fn-tooltip {
    visibility: visible;
    opacity: 1;
}
</style>

<div class="story-section">
  <span class="story-pill">Scope & Constraints</span>
  <p>
    Pienza explicitly rejects reverse-engineering proprietary pricing algorithms — a statistically unfeasible objective given a boutique, single-agent dataset. The analytical lens is reoriented toward <strong>the sole variable under absolute agent control: the decision itself</strong>.<span class="fn-wrap"><span class="fn-mark">†</span><span class="fn-tooltip">Bounded by the ITESM Data Science Certificate, the project allowed exploration across behavioral economics and generative AI — with one inviolable constraint: Reinforcement Learning was out of scope. The Markov scaffolding built in Phase 6 was designed precisely to make that next step possible.</span></span>
  </p>
</div>

<div class="story-section">
  <span class="story-pill">Initial Hypothesis</span>
  <p>
    A pilot study (N ≈ 150, Jul–Aug 2025) observed a Payout Spread of 75–85 % of Base Fare. The hypothesis: time savings incur an implicit fare penalty. A benchmark comparison falsified this — Simple Linear Regression dominated all ML models and no meaningful non-linear signal was found. Scaling the regression approach would demand thousands of completed trips at prohibitive operational cost.<span class="fn-wrap"><span class="fn-mark">†</span><span class="fn-tooltip">During Phase 3 (Exploratory Analysis), the Payout Spread inquiry was revisited and formally resolved via Causal Inference — modeling the platform's inelastic Integrity Buffer and baseline heteroscedasticity. → <a href="/Causal_Inference" target="_self" style="color:#21918c;text-decoration:none;">Causal Inference</a></span></span>
  </p>
</div>

<div class="story-section">
  <span class="story-pill">Pivot to Classification</span>
  <p>
    Regression abandoned. Research objective redefined from <em>price prediction</em> to <em>behavior cloning</em>. Incorporating the Negative Class (rejected offers) resolved data scarcity and exposed the full decision boundary — enabling XGBoost to model the agent's non-linear acceptance policy.
  </p>
</div>

<div class="story-section">
  <span class="story-pill">Target Feature: Multiclass Classification</span>
  <p>
    The problem is defined as a <strong>multiclass classification</strong> task. Each rejected offer is assigned a single, mutually exclusive label representing the primary reason for rejection across a three-tiered triage: geospatial feasibility, economic viability, and strategic alignment. Acceptance is implicit — a <code>NULL</code> label signals the absence of any objection. A binary accept/reject formulation was kept as a fallback in case the multiclass approach failed.
  </p>
</div>

<style>
.target-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 8px;
    margin-bottom: 8px;
}
.target-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: all 0.25s ease;
}
.target-card:hover {
    border-color: #21918c;
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,0.07);
}
.target-card.null-card {
    border-style: dashed;
    border-color: #ccc;
    background: #fafafa;
}
.target-card.null-card:hover {
    border-color: #21918c;
    border-style: dashed;
}
.target-tier {
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #aaa;
    margin-bottom: 4px;
}
.target-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #21918c;
    font-family: 'Courier New', monospace;
    margin-bottom: 6px;
}
.target-desc {
    font-size: 0.78rem;
    color: #555;
    line-height: 1.5;
}
</style>

<div class="target-grid">
  <div class="target-card">
    <div class="target-tier">Tier 1 — Geospatial</div>
    <div class="target-label">dropoff_non_operational</div>
    <div class="target-desc">Destination lies within a pre-defined zone outside the operational area.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 1 — Geospatial</div>
    <div class="target-label">dropoff_proxy</div>
    <div class="target-desc">Destination is outside the primary zone but acceptable if aligned with a homecoming vector toward <em>Anzures</em>.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 2 — Economic</div>
    <div class="target-label">low_profitability</div>
    <div class="target-desc">Offer fails baseline EPH requirements relative to estimated duration.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 2 — Economic</div>
    <div class="target-label">long_pickup_time</div>
    <div class="target-desc">Uncompensated pickup time exceeds tolerance; threshold relaxes during extreme gridlock.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 3 — Strategic</div>
    <div class="target-label">strategic_mismatch</div>
    <div class="target-desc">High-value offer rejected due to unfavorable routing context (e.g., <em>Santa Fe → Polanco</em> during Friday peak gridlock).</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 3 — Strategic</div>
    <div class="target-label">expected_value_gamble</div>
    <div class="target-desc">Viable offer rejected based on the probabilistic expectation of a superior imminent event.</div>
  </div>
  <div class="target-card null-card">
    <div class="target-tier">Implicit</div>
    <div class="target-label">NULL</div>
    <div class="target-desc">Absence of objection signals an accepted offer.</div>
  </div>
</div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("## Data Ingestion Pipelines")
    st.markdown("""
    <div class="placeholder-card">
        <span>🔄</span>
        <strong>Placeholder — Data Ingestion Pipelines</strong><br/>
        Architecture diagrams, pipeline schemas, and ingestion flow documentation will live here.
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("## GTS Telemetry Simulator")
    st.markdown("""
    <div class="placeholder-card">
        <span>🎮</span>
        <strong>Placeholder — GTS Telemetry Simulator</strong><br/>
        Interactive telemetry generation controls and live output preview will live here.
    </div>
    """, unsafe_allow_html=True)
