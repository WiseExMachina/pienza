import base64
import datetime
import pathlib
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from components.styles import GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Foundations | Pienza", page_icon="🏗️")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown("Project Pienza")
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
tab1, tab2, tab3 = st.tabs(["📖 Introduction", "📅 Timeline", "🔄 Data Ingestion Pipelines"])

with tab1:
    st.markdown("## Introduction")
    st.markdown("""
<div class="story-section">
  <span class="story-pill">Scope & Constraints</span>
  <p>
    Pienza explicitly rejects reverse-engineering proprietary pricing algorithms — a statistically unfeasible objective given a boutique, single-agent dataset. The analytical lens is reoriented toward <strong>the sole variable under absolute agent control: the decision itself</strong>.<span class="fn-wrap"><span class="fn-mark">†</span><span class="fn-tooltip">Built alongside the ITESM Data Science Certificate, the project allowed exploration across behavioral economics and generative AI — with one strict constraint: Reinforcement Learning was out of scope. The Markov scaffolding built in Phase 6 was designed precisely to make that next step possible.</span></span>
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
    With regression abandoned, the research objective redefined from <em>price prediction</em> to <em>behavior cloning</em>. Incorporating the Negative Class (rejected offers) resolved data scarcity and exposed the full decision boundary — enabling XGBoost to model the agent's non-linear acceptance policy.
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
    subtab1, subtab2, subtab3 = st.tabs(["📋 Acquisition & Ground Truth", "🎮 Engine 1: Telemetry Simulator", "📷 Engine 2: Gemini OCR"])

    with subtab1:
        st.markdown("""
<div class="story-section">
  <span class="story-pill">Acquisition Context</span>
  <p>
    Project Pienza models the decision policy of an expert agent rather than a system in a learning phase. Prior to data collection, the subject had completed 24 months of field operations, concluding the <em>Exploration</em> stage of the Reinforcement Learning cycle. Utilizing the framework of Hopfield Networks, the agent's decision policy is modeled as a "cooled" system settled into a stable local minimum — an <em>attractor state</em>. This equilibrium represents an optimization contingent on the agent's specific constraints: geographic preferences, risk tolerance, and physical endurance. The resulting dataset provides a high-fidelity record of a <strong>converged exploitation policy</strong>.
  </p>
  <p>
    Project Pienza utilizes a proprietary, <strong>dual-engine acquisition ecosystem</strong> to overcome the data sparsity inherent in third-party platform exports. The primary acquisition campaign was executed over a strict 6-week observation window (August 22 – October 1, 2025), digitizing the agent's operational reality in real-time.
  </p>
</div>
""", unsafe_allow_html=True)

        with st.expander("Engine 1 — Operational Telemetry: GTS Webapp", expanded=True):
            st.markdown("""
To establish the ground truth of completed missions, a bespoke Progressive Web Application (PWA) designated as the **Geotimestamps (GTS) Webapp** was deployed. The interface was optimized for low-cognitive-load fieldwork, functioning as a "One-Touch Timestamping" instrument while maintaining resilience through a production-grade stack (Netlify Frontend, Google Sheets Backend).

**Lifecycle Mapping Protocol (T0–T4).** The system logs five critical state transitions with geospatial precision:

| Event | State | Capture |
|---|---|---|
| T0 | Search — idle, seeking offers | Timestamp + coordinates |
| T1 | Acceptance — offer accepted, en route | Quoted upfront fare |
| T2 | Arrival — at pickup, waiting | Timestamp + coordinates |
| T3 | In-Progress — mission started | Timestamp |
| T4 | Completion — mission finalized | Realized net fare |

**Output (`trip_events`):** A verified timeline of physical state transitions and realized financial outcomes (N ≈ 350 completed trips).
            """)

        with st.expander("Engine 2 — Total Offer Stream: OCR Pipeline", expanded=True):
            st.markdown("""
To neutralize **Survivorship Bias**, the system must capture the full decision boundary — specifically the Rejected Offers (*The Negative Class*). As market infrastructure provides no native access to historical offer logs, a custom "Optical State Archival" architecture was deployed.

The acquisition interface utilized an iOS device configured with an **Assistive Touch Macro**. This enabled a single-gesture capture protocol (The "Manual Cookie") that simultaneously acknowledged the offer cognitively and secured the raw visual data digitally.

Three operational mandates enforced statistical representativeness:

1. **Full Spectrum Capture (Zero Filters):** All system-level destination filters and product category filters (Premium / Mid-tier / X) were disabled — capturing the unfiltered "True Market" liquidity.
2. **Safety-Driven Random Sampling:** Offers occurring during high-cognitive-load maneuvers were intentionally skipped. This data loss is classified as **Missing Completely at Random (MCAR)**, introducing no systemic bias.
3. **The "Driver-First" Learning Curve:** A Warm-Up period (Week 1) resulted in a small cluster of "Ghost Offers" — completed missions without source image artifacts. These were handled programmatically in the Engineering Phase.

The pipeline utilizes the **Google Gemini Pro Vision API** to transform visual assets into structured data. The system prompt enforces strict scope limitations, instructing the model to ignore navigation metadata outside the central offer card.

**Output (`offers`):** Total universe of opportunities including the critical Negative Class (N ≈ 4,700 total offers).
            """)

        st.markdown("""
<div class="story-section">
  <span class="story-pill">Post-Session Reconciliation Protocol</span>
  <p>
    At acquisition time, both engines exist as separate, unlinked entities. A rigorous post-session protocol was enforced immediately upon the completion of each fieldwork shift:
  </p>
  <ol>
    <li><strong>Telemetry Consolidation (GTS):</strong> Raw, long-format event logs were processed into a wide-format session ledger — pruning duplicates and cancelled events, and enabling immediate calculation of session-level KPIs such as <em>Net Spread</em> and <em>Accumulated Deadhead</em>.</li>
    <li><strong>High-Fidelity Cognitive Backtagging:</strong> The Agent manually reviewed and tagged every rejected offer from that session to populate the multiclass target variable (<code>reason_primary</code>). Executing this task same-day was imperative to capture the specific, contextual nuance of the decision before operational memory decay occurred.</li>
  </ol>
  <p>In the subsequent engineering phase, the two disparate records were unified into a SQL-queryable relational schema.</p>
</div>
""", unsafe_allow_html=True)

    with subtab2:
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
        st.markdown("## Operational Resilience & Edge Case Notes")
        st.markdown("""
<div class="story-section">
  <span class="story-pill">Stateful Persistence (v4.0)</span>
  <p>The GTS Webapp implements a <strong>Stateful LocalStorage Manager</strong> and an <strong>Offline-First Queue System</strong>. Every state transition is written to local storage before the network sync attempt — guaranteeing zero data loss during connectivity drops, tunnel blackouts, or app backgrounding mid-ride.</p>
</div>

<div class="story-section">
  <span class="story-pill">Asynchronous Geospatial Enrichment</span>
  <p>A client-side pipeline orchestrates the <code>navigator.geolocation</code> API with reverse-geocoding services. Every T0–T4 event is enriched with high-precision coordinates and a human-readable address string <em>prior</em> to persistence — decoupling location capture from UI interaction to avoid blocking the driver's workflow.</p>
</div>

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
  <p>The system captures natural "Idle Gaps" between T4 (Completion) and the subsequent T0 (New Search). If a chained offer was accepted, the next state after T4 would be T1 rather than T0 — the exact acceptance timestamp is lost in the main log but captured by the OCR Engine.</p>
</div>
        """, unsafe_allow_html=True)

        st.caption("Simulator Version: GTS-4.0")

    with subtab3:
        st.markdown("## Engine 2: Gemini OCR Pipeline")
        st.markdown("""
<div class="story-section">
  <span class="story-pill">Raw Capture</span>
  <p>Each screenshot is an unedited frame from the iOS Assistive Touch macro — one gesture, one offer, one artifact. 4,700+ offers were captured; navigate the examples below; Step 1 and Step 2 update to reflect the selected offer.</p>
</div>
""", unsafe_allow_html=True)

        # ── Offer data ─────────────────────────────────────────────
        OFFERS = [
            {
                "img": "assets/offer_cards/01_IMG_1691.PNG",
                "confidence": 0.97, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "UberX",\n  "pickup_address":   "██████████, Col. ████████, CDMX",\n  "dropoff_address":  "████████████████, Col. ████████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.97,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"██████, CDMX"',  "██████",    "VARCHAR",  "geocode_pending"),
                    ("dropoff_address", '"██████, CDMX"',  "██████",    "VARCHAR",  "—"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/02_IMG_3428.PNG",
                "confidence": 0.94, "warnings": ["surge_detected"],
                "ocr_json": '{\n  "upfront_fare_raw": "$███.██",\n  "product_type":     "Comfort",\n  "pickup_address":   "████████████████, Col. ████, CDMX",\n  "dropoff_address":  "████████████, Col. ████████, CDMX",\n  "pickup_eta_min":   ██,\n  "trip_distance_km": ██.█,\n  "surge_indicator":  true,\n  "ocr_confidence":   0.94,\n  "parse_warnings":   ["surge_detected"]\n}',
                "cleaned": [
                    ("upfront_fare",    '"$███.██"',       "███.██",    "FLOAT",    "surge_flag"),
                    ("product_type",    '"Comfort"',       "comfort",   "VARCHAR",  "—"),
                    ("pickup_address",  '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("dropoff_address", '"████████, CDMX"',"████████",  "VARCHAR",  "geocode_pending"),
                    ("pickup_eta_min",  "██",              "██",        "INT",      "high_eta_warning"),
                    ("surge_indicator", "true",            "1",         "BOOL→INT", "surge_flag"),
                ],
            },
            {
                "img": "assets/offer_cards/03_IMG_4346.PNG",
                "confidence": 0.99, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "UberX",\n  "pickup_address":   "█████████, Col. ████████, CDMX",\n  "dropoff_address":  "███████████████, Col. ████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.99,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"█████████, CDMX"',"█████████","VARCHAR",  "—"),
                    ("dropoff_address", '"███████, CDMX"', "███████",   "VARCHAR",  "—"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/04_IMG_5813.PNG",
                "confidence": 0.91, "warnings": ["low_confidence_address"],
                "ocr_json": '{\n  "upfront_fare_raw": "$████.██",\n  "product_type":     "Premier",\n  "pickup_address":   "████████████████, Col. ████████, CDMX",\n  "dropoff_address":  "██████████████████████, CDMX",\n  "pickup_eta_min":   ██,\n  "trip_distance_km": ██.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.91,\n  "parse_warnings":   ["low_confidence_address"]\n}',
                "cleaned": [
                    ("upfront_fare",    '"$████.██"',      "████.██",   "FLOAT",    "—"),
                    ("product_type",    '"Premier"',       "premier",   "VARCHAR",  "—"),
                    ("pickup_address",  '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("dropoff_address", '"██████, CDMX"',  "██████",    "VARCHAR",  "low_conf_geocode"),
                    ("pickup_eta_min",  "██",              "██",        "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/05_IMG_6624.PNG",
                "confidence": 0.98, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "UberX",\n  "pickup_address":   "███████████, Col. ████, CDMX",\n  "dropoff_address":  "█████████████, Col. ████████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.98,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"███████, CDMX"', "███████",   "VARCHAR",  "—"),
                    ("dropoff_address", '"█████████, CDMX"',"█████████","VARCHAR",  "geocode_pending"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/06_IMG_0038.PNG",
                "confidence": 0.96, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "UberX",\n  "pickup_address":   "████████████, Col. ████, CDMX",\n  "dropoff_address":  "██████████, Col. ████████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.96,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("dropoff_address", '"██████, CDMX"',  "██████",    "VARCHAR",  "—"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/07_IMG_3679.PNG",
                "confidence": 0.95, "warnings": ["low_confidence_address"],
                "ocr_json": '{\n  "upfront_fare_raw": "$███.██",\n  "product_type":     "UberX",\n  "pickup_address":   "██████████████, Col. ████, CDMX",\n  "dropoff_address":  "████████████████, Col. ████, CDMX",\n  "pickup_eta_min":   ██,\n  "trip_distance_km": ██.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.95,\n  "parse_warnings":   ["low_confidence_address"]\n}',
                "cleaned": [
                    ("upfront_fare",    '"$███.██"',       "███.██",    "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("dropoff_address", '"████████, CDMX"',"████████",  "VARCHAR",  "low_conf_geocode"),
                    ("pickup_eta_min",  "██",              "██",        "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/08_IMG_9029.PNG",
                "confidence": 0.98, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "Comfort",\n  "pickup_address":   "█████████████, Col. ████████, CDMX",\n  "dropoff_address":  "███████████, Col. ████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.98,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"Comfort"',       "comfort",   "VARCHAR",  "—"),
                    ("pickup_address",  '"█████████, CDMX"',"█████████","VARCHAR",  "—"),
                    ("dropoff_address", '"███████, CDMX"', "███████",   "VARCHAR",  "geocode_pending"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
            {
                "img": "assets/offer_cards/09_IMG_2793.PNG",
                "confidence": 0.93, "warnings": ["surge_detected"],
                "ocr_json": '{\n  "upfront_fare_raw": "$███.██",\n  "product_type":     "UberX",\n  "pickup_address":   "██████████, Col. ████████, CDMX",\n  "dropoff_address":  "████████████████████, CDMX",\n  "pickup_eta_min":   ██,\n  "trip_distance_km": ██.█,\n  "surge_indicator":  true,\n  "ocr_confidence":   0.93,\n  "parse_warnings":   ["surge_detected"]\n}',
                "cleaned": [
                    ("upfront_fare",    '"$███.██"',       "███.██",    "FLOAT",    "surge_flag"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"██████, CDMX"',  "██████",    "VARCHAR",  "—"),
                    ("dropoff_address", '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("pickup_eta_min",  "██",              "██",        "INT",      "high_eta_warning"),
                    ("surge_indicator", "true",            "1",         "BOOL→INT", "surge_flag"),
                ],
            },
            {
                "img": "assets/offer_cards/10_IMG_9277.PNG",
                "confidence": 0.97, "warnings": [],
                "ocr_json": '{\n  "upfront_fare_raw": "$██.██",\n  "product_type":     "UberX",\n  "pickup_address":   "████████████, Col. ████, CDMX",\n  "dropoff_address":  "██████████████, Col. ████████, CDMX",\n  "pickup_eta_min":   █,\n  "trip_distance_km": █.█,\n  "surge_indicator":  false,\n  "ocr_confidence":   0.97,\n  "parse_warnings":   []\n}',
                "cleaned": [
                    ("upfront_fare",    '"$██.██"',        "██.██",     "FLOAT",    "—"),
                    ("product_type",    '"UberX"',         "uberx",     "VARCHAR",  "—"),
                    ("pickup_address",  '"████████, CDMX"',"████████",  "VARCHAR",  "—"),
                    ("dropoff_address", '"██████████, CDMX"',"██████████","VARCHAR", "—"),
                    ("pickup_eta_min",  "█",               "█",         "INT",      "—"),
                    ("surge_indicator", "false",           "0",         "BOOL→INT", "—"),
                ],
            },
        ]

        if "ocr_slide" not in st.session_state:
            st.session_state.ocr_slide = 0

        n = len(OFFERS)
        idx = st.session_state.ocr_slide
        offer = OFFERS[idx]

        # ── Stacked phone frames + filmstrip ──────────────────────
        def _mk_phone(img_path, rotate, tx, ty, opacity, z):
            b = base64.b64encode(pathlib.Path(img_path).read_bytes()).decode()
            return f"""
<div style="position:absolute;width:235px;border-radius:40px;
     background:#0a0a0a;border:8px solid #1a1a1a;padding:10px 0 14px;
     box-shadow:0 20px 48px rgba(0,0,0,0.5),inset 0 0 0 1px rgba(255,255,255,0.05);
     transform:rotate({rotate}deg) translate({tx}px,{ty}px);
     opacity:{opacity};z-index:{z};top:0;left:50%;margin-left:-117px;">
  <div style="width:72px;height:6px;background:#1a1a1a;
              border-radius:0 0 6px 6px;margin:0 auto 10px;"></div>
  <img src="data:image/png;base64,{b}" style="width:100%;display:block;border-radius:4px;" />
  <div style="width:72px;height:4px;background:#333;border-radius:2px;margin:12px auto 0;"></div>
</div>"""

        prev_path = OFFERS[max(idx - 1, 0)]["img"]
        next_path = OFFERS[min(idx + 1, n - 1)]["img"]
        curr_path = offer["img"]

        st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;gap:10px;margin-bottom:16px;">
  <div style="position:relative;width:340px;height:530px;">
    {_mk_phone(prev_path, -7, -32, 10, 0.3, 1)}
    {_mk_phone(next_path,  7,  32, 10, 0.3, 1)}
    {_mk_phone(curr_path,  0,   0,  0, 1.0, 2)}
  </div>
  <div style="font-size:12px;color:#aaa;margin-top:32px;">{idx+1} / {n}</div>
</div>
""", unsafe_allow_html=True)

        # ── Filmstrip ──────────────────────────────────────────────
        thumb_cols = st.columns(n)
        for i, o in enumerate(OFFERS):
            with thumb_cols[i]:
                tb = base64.b64encode(pathlib.Path(o["img"]).read_bytes()).decode()
                border = "2px solid #21918c" if i == idx else "2px solid rgba(255,255,255,0.1)"
                opacity = "1" if i == idx else "0.4"
                st.markdown(f"""
<div style="border-radius:8px;border:{border};overflow:hidden;
            opacity:{opacity};margin-bottom:2px;">
  <img src="data:image/png;base64,{tb}" style="width:100%;display:block;" />
</div>""", unsafe_allow_html=True)
                if st.button(f"{i+1}", key=f"thumb_{i}", use_container_width=True):
                    st.session_state.ocr_slide = i
                    st.rerun()

        # ── Step 1: Raw OCR ────────────────────────────────────────
        st.markdown("---")
        st.markdown("""
<div class="story-section">
  <span class="story-pill">Step 1 — Raw Gemini Vision Output</span>
  <p>The Gemini Pro Vision API receives the raw screenshot and returns a structured JSON. The prompt constrains scope to the central offer card only — navigation chrome and status bar are explicitly excluded.</p>
</div>
""", unsafe_allow_html=True)
        st.code(offer["ocr_json"], language="json")

        # ── Step 2: Post-RGG ───────────────────────────────────────
        st.markdown("---")
        st.markdown("""
<div class="story-section">
  <span class="story-pill">Step 2 — Post-RGG Cleaning (pre-SQL)</span>
  <p>A regex + heuristic normalization layer (RGG) strips currency symbols, casts types, flags anomalies, and resolves address ambiguities before the record is written to <code>pienza.db</code>.</p>
</div>
""", unsafe_allow_html=True)
        cleaned_df = pd.DataFrame(
            offer["cleaned"],
            columns=["field", "raw_value", "cleaned_value", "dtype", "flag"]
        )
        st.dataframe(cleaned_df, use_container_width=True, hide_index=True)
        st.caption(f"Offer {idx+1}/{n} · Confidence: {offer['confidence']:.0%} · Warnings: {offer['warnings'] or 'none'} · RGG = Regex + Gemini + Geo-resolver")

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
            "date_range": "Apr 1, 2026 – May, 31 2026",
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
