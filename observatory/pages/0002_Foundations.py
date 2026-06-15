import datetime
import time
import pandas as pd
import plotly.express as px
import altair as alt
import streamlit as st
import streamlit.components.v1 as components
from components.styles import GLOBAL_CSS

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
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Page-specific overrides
st.markdown("""
<style>
h2 { font-size: 22px !important; font-weight: 600 !important; letter-spacing: -0.5px; }
h3 { font-size: 16px !important; font-weight: 600 !important; }
p, li { color: #555; font-size: 0.9rem; line-height: 1.7; }

/* GTS Simulator — device frame */
.sim-wrapper { display: flex; justify-content: center; padding: 12px 0 20px; }
.sim-device {
    width: 290px;
    background: #ffffff;
    border-radius: 28px;
    border: 7px solid #1a1a1a;
    padding: 0 14px 14px;
    box-shadow: 0 18px 40px rgba(0,0,0,0.18), inset 0 0 0 1px rgba(255,255,255,0.08);
    font-family: 'Inter', sans-serif !important;
}
.sim-notch {
    width: 68px; height: 6px;
    background: #1a1a1a;
    border-radius: 0 0 5px 5px;
    margin: 0 auto 16px;
}
.sim-header {
    text-align: center; color: #888;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    padding-bottom: 10px; margin-bottom: 12px;
    border-bottom: 1px solid #eee;
}
.sim-home {
    width: 80px; height: 3px;
    background: #1a1a1a; border-radius: 2px;
    margin: 14px auto 0; opacity: 0.25;
}
#timer-display {
    font-family: 'Courier New', monospace;
    font-size: 22px; font-weight: bold; color: #dc3545;
    text-align: center; margin: 8px 0; background: #fff5f5;
    padding: 6px; border-radius: 10px; border: 1px solid #ffc1c1;
}
div.stButton > button, div[data-testid="stPopover"] > button {
    width: 100%; border-radius: 10px !important; padding: 12px !important;
    font-weight: 700 !important; font-size: 13px !important;
    text-transform: none !important; border: none !important;
    transition: all 0.2s ease;
}
.summary-card {
    background-color: #f8f9fa; border: 1px solid #ddd;
    border-radius: 12px; padding: 15px; margin-top: 15px;
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
tab1, tab2, tab3, tab4 = st.tabs(["📖 Introduction", "📅 Timeline", "🔄 Data Ingestion Pipelines", "🎮 GTS Telemetry Simulator"])

with tab1:
    st.markdown("## Introduction")
    st.markdown("""
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

with tab3:
    st.markdown("## Data Ingestion Pipelines")
    st.markdown("""
    <div class="placeholder-card">
        <span>🔄</span>
        <strong>Placeholder — Data Ingestion Pipelines</strong><br/>
        Architecture diagrams, pipeline schemas, and ingestion flow documentation will live here.
    </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown("## GTS Telemetry Simulator")
    st.markdown("""
    This module simulates the **Engine 1** mobile experience. It demonstrates the "One-Touch" state transitions and the logic used to calculate operational KPIs in the field.
    """)

    # ── SESSION STATE ────────────────────────────────────────────────────────
    if 'sim_active' not in st.session_state:
        st.session_state.sim_active = False
    if 'sim_log' not in st.session_state:
        st.session_state.sim_log = []
    if 'start_time_dt' not in st.session_state:
        st.session_state.start_time_dt = None
    if 'show_t1' not in st.session_state:
        st.session_state.show_t1 = False
    if 'show_t4' not in st.session_state:
        st.session_state.show_t4 = False
    if 'show_summary' not in st.session_state:
        st.session_state.show_summary = False

    # ── LOGIC ────────────────────────────────────────────────────────────────
    def log_sim_event(status, ride_id, upfront=0.0, realized=0.0):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_cdmx = now_utc - datetime.timedelta(hours=6)
        st.session_state.sim_log.insert(0, {
            "raw_ts": time.time(),
            "serverTimestamp (MEX)": now_cdmx.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "clientTimestamp (UTC)": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rideID": ride_id,
            "eventType": status,
            "latitude": 19.4326,
            "longitude": -99.1332,
            "addressText": "Zócalo, Mexico City",
            "upfrontFare": float(upfront),
            "realizedFare": float(realized)
        })

    def calculate_summary():
        if not st.session_state.sim_log:
            return None
        df = pd.DataFrame(st.session_state.sim_log).sort_values("raw_ts")
        total_up = df["upfrontFare"].sum()
        total_re = df["realizedFare"].sum()
        spread = (total_re / total_up) * 100 if total_up > 0 else 0
        durs = {"Looking": 0, "Driving": 0, "Waiting": 0, "On Ride": 0}
        for i in range(len(df) - 1):
            delta = df.iloc[i + 1]["raw_ts"] - df.iloc[i]["raw_ts"]
            etype = df.iloc[i]["eventType"]
            if "T0" in etype:   durs["Looking"] += delta
            elif "T1" in etype: durs["Driving"] += delta
            elif "T2" in etype: durs["Waiting"] += delta
            elif "T3" in etype: durs["On Ride"] += delta
        return {"up": total_up, "re": total_re, "spread": spread, "times": durs}

    # ── JS: color buttons + style the column as the phone frame ─────────────
    components.html("""
    <script>
    function applyStyles() {
        const doc = window.parent.document;

        // 1. Color T0–T4 buttons by text
        doc.querySelectorAll('button').forEach(btn => {
            const t = btn.innerText.trim();
            if      (t.startsWith('T0:')) { btn.style.setProperty('background-color','#007BFF','important'); btn.style.setProperty('color','white','important'); }
            else if (t.startsWith('T1:')) { btn.style.setProperty('background-color','#FFC107','important'); btn.style.setProperty('color','black','important'); }
            else if (t.startsWith('T2:')) { btn.style.setProperty('background-color','#FD7E14','important'); btn.style.setProperty('color','white','important'); }
            else if (t.startsWith('T3:')) { btn.style.setProperty('background-color','#17A2B8','important'); btn.style.setProperty('color','white','important'); }
            else if (t.startsWith('T4:')) { btn.style.setProperty('background-color','#28A745','important'); btn.style.setProperty('color','white','important'); }
            else if (t.startsWith('■')) { btn.style.setProperty('background-color','#adb5bd','important'); btn.style.setProperty('color','white','important'); }
        });

        // 2. Find the stColumn containing T0 and style it as the phone frame
        const t0 = Array.from(doc.querySelectorAll('button')).find(b => b.innerText.trim().startsWith('T0:'));
        if (t0) {
            let col = t0;
            while (col && col.getAttribute('data-testid') !== 'stColumn') col = col.parentElement;
            if (col) {
                col.style.setProperty('background', 'white', 'important');
                col.style.setProperty('border', '7px solid #1a1a1a', 'important');
                col.style.setProperty('border-radius', '28px', 'important');
                col.style.setProperty('box-shadow', '0 18px 40px rgba(0,0,0,0.18)', 'important');
                col.style.setProperty('padding', '0 14px 20px', 'important');
                col.style.setProperty('max-width', '390px', 'important');
                col.style.setProperty('margin', '0 auto', 'important');
            }
        }
    }
    setTimeout(applyStyles, 150);
    setInterval(applyStyles, 800);
    </script>
    """, height=0)

    # ── UI ───────────────────────────────────────────────────────────────────
    active = st.session_state.sim_active
    col_l, col_m, col_r = st.columns([0.7, 2, 0.7])

    with col_m:
        # Notch + header at top of the phone-framed column
        st.markdown("""
        <div class="sim-notch"></div>
        <div class="sim-header">Geotimestamps GTS-4</div>
        """, unsafe_allow_html=True)

        # Session control
        if not active:
            if st.button("▶  Start Session", type="primary", use_container_width=True):
                st.session_state.sim_active = True
                st.session_state.start_time_dt = time.time()
                st.session_state.sim_log = []
                st.rerun()
        else:
            if st.button("■  End Session", use_container_width=True):
                st.session_state.sim_active = False
                st.session_state.show_summary = True
                st.rerun()

        # Timer — live when active, static placeholder when not
        if active:
            components.html(f"""
            <div id="timer-display" style="font-family:'Courier New',monospace;font-size:22px;font-weight:bold;
                 color:#dc3545;text-align:center;margin:8px 0;background:#fff5f5;
                 padding:6px;border-radius:10px;border:1px solid #ffc1c1;">00:00:00:000</div>
            <script>
            (function() {{
                const start = {st.session_state.start_time_dt} * 1000;
                const el = document.getElementById('timer-display');
                function update() {{
                    const d = Date.now() - start;
                    const h = Math.floor(d/3600000).toString().padStart(2,'0');
                    const m = Math.floor((d%3600000)/60000).toString().padStart(2,'0');
                    const s = Math.floor((d%60000)/1000).toString().padStart(2,'0');
                    const ms = Math.floor(d%1000).toString().padStart(3,'0');
                    el.innerHTML = h+":"+m+":"+s+":"+ms;
                    requestAnimationFrame(update);
                }}
                update();
            }})();
            </script>
            """, height=60)
        else:
            st.markdown("""<div style="font-family:'Courier New',monospace;font-size:22px;font-weight:bold;
                color:#ccc;text-align:center;margin:8px 0;background:#fafafa;
                padding:6px;border-radius:10px;border:1px solid #eee;">
                00:00:00:000</div>""", unsafe_allow_html=True)

        # Ride ID + T0–T4 — always visible, disabled until session starts
        default_ride_id = datetime.datetime.now().strftime("%y%m%d") + "-01"
        ride_id = st.text_input("Daily Ride ID:", value=default_ride_id, disabled=not active)

        if st.button("T0: Looking for rides", disabled=not active, use_container_width=True):
            log_sim_event("T0: Looking for rides", ride_id)

        if st.button("T1: Ride Accepted, Driving to Pickup", disabled=not active, use_container_width=True):
            st.session_state.show_t1 = not st.session_state.show_t1
        if st.session_state.show_t1 and active:
            with st.form("form_t1", clear_on_submit=True):
                u_fare_raw = st.text_input("Upfront Fare ($)", placeholder="e.g. 85")
                if st.form_submit_button("Confirm T1", use_container_width=True):
                    log_sim_event("T1: Ride Accepted, Driving to Pickup", ride_id, upfront=float(u_fare_raw or 0))
                    st.session_state.show_t1 = False
                    st.rerun()

        if st.button("T2: Waiting for passenger", disabled=not active, use_container_width=True):
            log_sim_event("T2: Waiting for passenger", ride_id)

        if st.button("T3: Ride Started", disabled=not active, use_container_width=True):
            log_sim_event("T3: Ride Started", ride_id)

        if st.button("T4: Ride completed", disabled=not active, use_container_width=True):
            st.session_state.show_t4 = not st.session_state.show_t4
        if st.session_state.show_t4 and active:
            with st.form("form_t4", clear_on_submit=True):
                r_fare_raw = st.text_input("Realized Fare ($)", placeholder="e.g. 72")
                if st.form_submit_button("Confirm T4", use_container_width=True):
                    log_sim_event("T4: Ride completed", ride_id, realized=float(r_fare_raw or 0))
                    st.session_state.show_t4 = False
                    st.rerun()

        # Home indicator — bottom of phone frame
        st.markdown('<div class="sim-home"></div>', unsafe_allow_html=True)

    # Post-session summary — modal dialog
    @st.dialog("Session Summary")
    def show_summary():
        stats = calculate_summary()
        if stats:
            st.write(f"**Total Upfront:** ${stats['up']:.2f}")
            st.write(f"**Total Realized:** ${stats['re']:.2f}")
            st.write(f"**Net Spread:** {stats['spread']:.2f}%")
            st.divider()
            for k, v in stats['times'].items():
                st.write(f"⏱ **{k}:** {time.strftime('%H:%M:%S', time.gmtime(v))}")
            st.divider()
            if st.button("Clear Log", use_container_width=True):
                st.session_state.sim_log = []
                st.rerun()

    if not active and st.session_state.sim_log and st.session_state.show_summary:
        st.session_state.show_summary = False
        show_summary()

    # Live telemetry table
    if st.session_state.sim_log:
        st.markdown("#### Real-time Telemetry Buffer (Backend)")
        df_table = pd.DataFrame(st.session_state.sim_log).drop(columns=['raw_ts'])
        st.dataframe(df_table, use_container_width=True, hide_index=True, height=180)
        components.html("""
        <script>
        function forceScrollbar() {
            const doc = window.parent.document;
            doc.querySelectorAll('[data-testid="stDataFrame"] *').forEach(el => {
                const style = window.parent.getComputedStyle(el);
                if (style.overflowX === 'auto' || style.overflowX === 'hidden') {
                    el.style.setProperty('overflow-x', 'scroll', 'important');
                    el.style.setProperty('scrollbar-width', 'thin', 'important');
                    el.style.setProperty('scrollbar-color', '#21918c #f1f1f1', 'important');
                }
            });
        }
        setTimeout(forceScrollbar, 300);
        setTimeout(forceScrollbar, 800);
        </script>
        """, height=0)

    st.divider()

    # ── OPERATIONAL NOTES ────────────────────────────────────────────────────
    st.markdown("## Operational Resilience & Edge Case Notes")
    st.markdown("""
<div class="story-section">
  <span class="story-pill">Atomic Persistence</span>
  <p>Data is not "dumped" in a single batch at the end of a session. Every state transition (T0–T4) is captured as an atomic event and queued immediately for backend synchronization. Even if a session is never formally ended, every captured data point is preserved.</p>
</div>

<div class="story-section">
  <span class="story-pill">Session Boundary</span>
  <p>Operational shifts typically conclude at <strong>T0 (Searching)</strong> after the final drop-off. For consistency, this trailing deadhead period was pruned — the final engineered record always terminates with a <strong>T4 (Completed Ride)</strong>.</p>
</div>

<div class="story-section">
  <span class="story-pill">Redundancy & Deduplication</span>
  <p>To minimize cognitive load during high-stress driving, the agent would "Double-Tap" a state if unsure whether a transition had logged. The architecture prioritizes <strong>Capture over Cleanliness</strong> — duplicate entries and out-of-order clicks are pruned programmatically during the Post-Session Reconciliation Protocol.</p>
</div>

<div class="story-section">
  <span class="story-pill">Financial Ground Truth</span>
  <p>All fares entered in the field are treated as <strong>"High-Confidence Drafts."</strong> Every entry is audited back-home against: (1) <strong>Engine 2 Visual Artifacts</strong> for Upfront Quoted Fares, and (2) <strong>Platform Activity History</strong> for Realized Net Fares.</p>
</div>

<div class="story-section">
  <span class="story-pill">Temporal Fidelity</span>
  <p>The system captures natural "Idle Gaps" between T4 (Completion) and the subsequent T0 (New Search). If a chained offer was accepted, the next state after T4 would be T1 rather than T0 — the exact acceptance timestamp is lost in the main log but captured by the OCR Engine via screenshot.</p>
</div>
    """, unsafe_allow_html=True)

    st.caption("Simulator Version: GTS-4.0")

with tab2:
    import plotly.graph_objects as go

    st.markdown("## Project Timeline")

    PHASES = [
        {
            "phase": "Phase 1", "label": "Acquisition & Ground Truth",
            "arch_short": "OCR<br>+<br>Sheets",
            "date_range": "Aug 22 – Oct 1, 2025",
            "detail": "High-fidelity manual capture of operational data via the bespoke GTS Webapp. Establishment of the target variable and the primary contextual ride attributes.",
            "bullets": ["GTS Webapp", "Dual OCR Engine", "Target variable definition", "Ride attributes schema"],
            "start": "2025-08-22", "end": "2025-10-01",
        },
        {
            "phase": "Phase 2", "label": "Data Engineering & Architecture",
            "arch_short": "SQLite<br>+<br>Colab",
            "date_range": "Oct 2 – Nov 20, 2025",
            "detail": "Transition to a relational database (pienza.db) and Star Schema design. Implementation of automated OCR pipelines and normalization protocols. Creation of the stateful engineered_features table.",
            "bullets": ["Star Schema design", "Idempotent ETL pipeline", "OCR automation", "engineered_features table"],
            "start": "2025-10-02", "end": "2025-11-20",
        },
        {
            "phase": "Phase 3", "label": "Exploratory Analysis & Causal Inference",
            "arch_short": "SQLite<br>+<br>Colab",
            "date_range": "Nov 21 – Dec 3, 2025",
            "detail": "Diagnostic audit of marketplace physics and rational search time boundaries. Causal modeling of baseline heteroscedasticity and quantification of the platform's inelastic Integrity Buffer.",
            "bullets": ["Marketplace physics audit", "Optimal stopping boundary", "Integrity Buffer quantification", "Heteroscedasticity causal model"],
            "start": "2025-11-21", "end": "2025-12-03",
        },
        {
            "phase": "Phase 4", "label": "Unsupervised Learning & Geo-Remediation",
            "arch_short": "SQLite<br>+<br>Colab",
            "date_range": "Dec 4, 2025 – Jan 2, 2026",
            "detail": "Application of HDBSCAN for zone discovery and surgical coordinate cleaning using hand-crafted heuristic polygons. Generation of the Silver Palette geo-semantic attributes.",
            "bullets": ["HDBSCAN zone discovery", "Heuristic polygon cleaning", "Silver Palette attributes", "44 geo-semantic clusters"],
            "start": "2025-12-04", "end": "2026-01-02",
        },
        {
            "phase": "Phase 5", "label": "Supervised Imitation Learning",
            "arch_short": "SQLite<br>+<br>Colab",
            "date_range": "Jan 3 – Jan 12, 2026",
            "detail": "Model evaluation tournament and implementation of the Cognitive Cascade hierarchical architecture for the champion model.",
            "bullets": ["Model tournament", "Cognitive Cascade architecture", "Hierarchical XGBoost champion", "Binary + multiclass evaluation"],
            "start": "2026-01-03", "end": "2026-01-12",
        },
        {
            "phase": "Phase 6", "label": "Generative Moonshots",
            "arch_short": "BigQuery<br>+<br>Colab",
            "date_range": "Jan 13 – Mar 31, 2026",
            "detail": "O(1) neural spatial inference and cGAN manifold synthesis. Formulation of the internal Mobility Tensor to establish the Markov Decision Process (MDP) baseline for autonomous routing.",
            "bullets": ["O(1) NLP spatial inference", "cGAN · 1M-row synthesis", "Mobility Tensor formulation", "MDP scaffold for autonomy"],
            "start": "2026-01-13", "end": "2026-03-31",
        },
        {
            "phase": "Phase 7 ✦", "label": "Streamlit: Pienza Observatory",
            "arch_short": "BigQuery<br>+<br>VS Code",
            "date_range": "Apr 1, 2026 – present",
            "detail": "Migration from Colab notebooks to a production-ready development environment. The research pipeline now runs entirely within GitHub Codespaces and VS Code — enabling live model interrogation, iterative Observatory builds, and a stable, reproducible workspace with full BigQuery connectivity.",
            "bullets": ["GitHub Codespaces", "VS Code", "BigQuery live queries", "Streamlit Observatory"],
            "start": "2026-04-01", "end": "2026-05-31",
        },
    ]

    df_phases = pd.DataFrame(PHASES)
    df_phases["Start"] = pd.to_datetime(df_phases["start"])
    df_phases["End"]   = pd.to_datetime(df_phases["end"])

    COLORS = ["#0d4a47", "#21918c", "#2db3ad", "#47c4be", "#6dcfca", "#9eddd9", "#c8eeec"]

    # ── Ribbon chart ──────────────────────────────────────────────────────
    META_GROUPS = [
        {
            "label": "Acquisition", "start": "2025-08-22", "end": "2025-10-01",
            "color": "#0d4a47",
            "hover": "<b>Phase 1</b><br>Manual field capture via GTS Webapp",
        },
        {
            "label": "Engineering /<br>Statistics", "start": "2025-10-02", "end": "2025-12-03",
            "color": "#21918c",
            "hover": "<b>Phases 2–3</b><br>Relational DB · ETL · Causal Inference",
        },
        {
            "label": "Classical ML", "start": "2025-12-04", "end": "2026-01-12",
            "color": "#2db3ad",
            "hover": "<b>Phases 4–5</b><br>HDBSCAN geo-remediation · XGBoost imitation learning",
        },
        {
            "label": "Deep Learning", "start": "2026-01-13", "end": "2026-03-31",
            "color": "#47c4be",
            "hover": "<b>Phase 6</b><br>O(1) NLP · cGAN · Mobility Tensor · MDP<br><i>† Iterative correction of past phases applied throughout</i>",
        },
        {
            "label": "Streamlit", "start": "2026-04-01", "end": "2026-05-31",
            "color": "#6dcfca",
            "hover": "<b>Phase 7</b><br>Pienza Observatory — production deployment",
        },
    ]

    fig = go.Figure()

    # Phase ribbon (y 0.35–0.65)
    for i, (_, row) in enumerate(df_phases.iterrows()):
        s = row["Start"].timestamp() * 1000
        e = row["End"].timestamp() * 1000
        mid_ts = (s + e) / 2
        fig.add_trace(go.Scatter(
            x=[s, e, e, s, s],
            y=[0.35, 0.35, 0.65, 0.65, 0.35],
            fill="toself",
            fillcolor=COLORS[i],
            line=dict(color="white", width=2),
            mode="lines",
            hovertemplate=(
                f"<b>{row['phase']}: {row['label']}</b><br>"
                f"{row['date_range']}<br>"
                f"Arch: {row['arch_short'].replace('<br>', ' ')}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        fig.add_annotation(
            x=mid_ts, y=0.50, xref="x", yref="y",
            text=f"<b>{row['phase']}</b>",
            showarrow=False, font=dict(size=9, color="white"),
            xanchor="center", yanchor="middle",
        )
        fig.add_annotation(
            x=mid_ts, y=0.22, xref="x", yref="y",
            text=row["arch_short"],
            showarrow=False, font=dict(size=8, color="#21918c"),
            xanchor="center",
        )

    # Meta-group labels above ribbon — full-width line with centered text
    for g in META_GROUPS:
        gs = pd.Timestamp(g["start"]).timestamp() * 1000
        ge = pd.Timestamp(g["end"]).timestamp() * 1000
        gm = (gs + ge) / 2
        fig.add_shape(
            type="line",
            x0=gs, x1=ge, y0=0.88, y1=0.88,
            xref="x", yref="y",
            line=dict(color="#bbb", width=1),
        )
        fig.add_annotation(
            x=gm, y=0.88, xref="x", yref="y",
            text=f"<b>{g['label']}</b>",
            showarrow=False,
            font=dict(size=9, color="#555"),
            xanchor="center", yanchor="middle",
            bgcolor="white", borderpad=3,
            hovertext=g["hover"],
        )


    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=260,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(
            type="date", showgrid=False,
            tickformat="%b %Y", tickfont=dict(size=11, color="#555"),
            range=[pd.Timestamp("2025-08-15").timestamp()*1000,
                   pd.Timestamp("2026-06-01").timestamp()*1000],
        ),
        yaxis=dict(visible=False, range=[0.05, 1.05]),
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Vertical story with arrows ────────────────────────────────────────
    st.markdown("""
<style>
.phase-story { max-width: 760px; margin: 0 auto; }
.phase-card {
    display: flex; gap: 20px; align-items: flex-start;
    background: #fff; border: 1px solid #e8e8e8;
    border-left: 4px solid var(--phase-color);
    border-radius: 10px; padding: 18px 20px;
    margin: 0 0 0 0;
}
.phase-badge-num {
    flex-shrink: 0;
    width: 40px; height: 40px;
    background: var(--phase-color);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 14px;
}
.phase-card-body { flex: 1; }
.phase-card-title { font-weight: 700; font-size: 0.95rem; color: #121212; margin-bottom: 2px; }
.phase-card-meta { font-size: 0.78rem; color: #888; margin-bottom: 8px; }
.phase-card-meta .arch-tag {
    display: inline-block; background: #f0faf9; color: #21918c;
    border: 1px solid #c2e8e5; border-radius: 4px;
    padding: 1px 6px; font-size: 0.72rem; font-weight: 600;
    margin-left: 8px;
}
.phase-card-desc { font-size: 0.85rem; color: #555; line-height: 1.65; margin-bottom: 10px; }
.phase-bullets { display: flex; flex-wrap: wrap; gap: 6px; }
.phase-bullet {
    background: #f5f5f5; border-radius: 20px;
    padding: 3px 10px; font-size: 0.75rem; color: #444;
}
.phase-arrow {
    text-align: center; color: #ccc; font-size: 22px;
    margin: 6px 0; line-height: 1;
    user-select: none;
}
</style>
""", unsafe_allow_html=True)

    phase_html = '<div class="phase-story">'
    for i, (_, row) in enumerate(df_phases.iterrows()):
        color = COLORS[i]
        bullets_html = "".join(f'<span class="phase-bullet">{b}</span>' for b in row["bullets"])
        phase_html += f"""
<div class="phase-card" style="--phase-color:{color}">
  <div class="phase-badge-num">{i+1}</div>
  <div class="phase-card-body">
    <div class="phase-card-title">{row['label']}</div>
    <div class="phase-card-meta">{row['date_range']} <span class="arch-tag">{row['arch_short'].replace('<br>', ' ')}</span></div>
    <div class="phase-card-desc">{row['detail']}</div>
    <div class="phase-bullets">{bullets_html}</div>
  </div>
</div>
"""
        if i < len(df_phases) - 1:
            phase_html += '<div class="phase-arrow">↓</div>'

    phase_html += '</div>'
    st.markdown(phase_html, unsafe_allow_html=True)
