import base64
import datetime
import json
import pathlib
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from components.styles import GLOBAL_CSS
from utils.bq_client import fetch_data_from_bq
from config import FAVICON
from utils.gcp_client import fetch_bytes_from_gcs

st.set_page_config(layout="wide", page_title="Acquisition Pipelines | Pienza", page_icon=FAVICON)

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
            st.download_button(
                "📄 Download 91-Page Report (PDF)",
                data=pdf_data,
                file_name="Project_Pienza_Full_Report.pdf",
                mime="application/pdf"
            )
        except Exception:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<style>
h2 { font-size: 22px !important; font-weight: 600 !important; letter-spacing: -0.5px; }
h3 { font-size: 16px !important; font-weight: 600 !important; }
p, li { color: #555; font-size: 0.9rem; line-height: 1.7; }
/* The generic p rule above overrides the teal color the active st.tabs()
   label normally inherits from its parent button (labels are <p> tags),
   leaving the underline teal but the text gray - restore it here. */
[data-baseweb="tab"][aria-selected="true"] p { color: #21918c !important; }

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
/* Prev/Next carousel arrows: st.button(key="nav_prev_*"/"nav_next_*") gets a
   stable st-key-nav_prev_*/st-key-nav_next_* class on its wrapper div - the
   old `.nav-carousel` class above was never actually attached to the button
   DOM node by Streamlit, so that rule silently never applied. */
div[class*="st-key-nav_prev_"] button, div[class*="st-key-nav_next_"] button {
    border: 1.5px solid #21918c !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    color: #21918c !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 10px !important;
}
div[class*="st-key-nav_prev_"] button:hover, div[class*="st-key-nav_next_"] button:hover {
    background: rgba(33,145,140,0.08) !important;
}
div[class*="st-key-nav_prev_"] button:disabled, div[class*="st-key-nav_next_"] button:disabled {
    border-color: #d0d5dd !important;
    color: #98a2b3 !important;
    background: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Acquisition Pipelines")

st.markdown("""
<style>
.fn-wrap.fn-below .fn-tooltip { bottom: auto; top: 130%; }
.fn-wrap.fn-below .fn-tooltip::after { top: auto; bottom: 100%; border-top-color: transparent; border-bottom-color: #21918c; }
.info-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 1px solid #21918c;
    background: #ffffff;
    color: #21918c;
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-weight: 700;
    font-size: 9px;
    cursor: default;
    transition: background 0.2s ease;
    vertical-align: middle;
    margin-left: 5px;
}
.info-mark:hover { background: #f0fafa; }
</style>
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
To overcome the data sparsity inherent in third-party platform exports, the agent had to
<em style='margin-left:4px;margin-right:4px;'>go get it</em> — and architected a proprietary,
<strong>dual-engine acquisition ecosystem.</strong> This was executed over a strict 6-week
observation window (August 22 – October 1, 2025), digitizing the agent's operational reality
in real-time.<span class="fn-wrap fn-below"><span class="info-mark">i</span><span class="fn-tooltip">The resulting dataset does not model the total ride-hailing universe of Mexico City — it is a strictly constrained mirror of the Agent's Operational Reality. The Agent never altered his heuristics to capture more data, so it reflects only his specific times and zones of operation.</span></span>
</p>
""", unsafe_allow_html=True)


subtab2, subtab3 = st.tabs(["Engine 1: GTS Telemetry Emulator", "Engine 2: Gemini OCR"])

with subtab2:
    st.markdown("<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>This module simulates the <strong>Engine 1</strong> mobile experience. It demonstrates the \"One-Touch\" state transitions and the logic used to calculate operational KPIs in the field. Press <strong>Start Session</strong> and walk through each event — the log and KPIs update in real time.</p>", unsafe_allow_html=True)

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
    with st.expander("Operational Resilience & Edge Cases"):
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

with subtab3:
    st.markdown("<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>Each screenshot is an unedited frame from the iOS Assistive Touch macro — one gesture, one offer, one artifact. 4,700+ offers were captured; navigate the examples below; Step 1 and Step 2 update to reflect the selected offer.</p>", unsafe_allow_html=True)

    # ── Offer data ─────────────────────────────────────────────
    OFFERS = [
        {
            "img": "01_IMG_1691.PNG",
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
            "img": "02_IMG_3428.PNG",
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
            "img": "03_IMG_4346.PNG",
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
            "img": "04_IMG_5813.PNG",
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
            "img": "05_IMG_6624.PNG",
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
            "img": "06_IMG_0038.PNG",
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
            "img": "07_IMG_3679.PNG",
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
            "img": "08_IMG_9029.PNG",
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
            "img": "09_IMG_2793.PNG",
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
            "img": "10_IMG_9277.PNG",
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

    def _nav_buttons(key_suffix):
        _gap1, _c1, _c2, _gap2 = st.columns([3, 1, 1, 3])
        with _c1:
            if st.button("←", key=f"nav_prev_{key_suffix}", disabled=(idx == 0), use_container_width=True):
                st.session_state.ocr_slide = idx - 1
                st.rerun()
        with _c2:
            if st.button("→", key=f"nav_next_{key_suffix}", disabled=(idx == n - 1), use_container_width=True):
                st.session_state.ocr_slide = idx + 1
                st.rerun()

    # ── Stacked phone frames + filmstrip ──────────────────────
    def _mk_phone(img_path, rotate, tx, ty, opacity, z):
        b = base64.b64encode(fetch_bytes_from_gcs("pienza-streamlit", img_path)).decode()
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
            tb = base64.b64encode(fetch_bytes_from_gcs("pienza-streamlit", o["img"])).decode()
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

    # ── BQ: fetch raw_offers_ocr for carousel images ───────────
    img_filenames = [pathlib.Path(o["img"]).name for o in OFFERS]
    # Strip leading "XX_" prefix to match BQ image_filename values
    bq_filenames  = [f.split("_", 1)[1] for f in img_filenames]
    bq_list       = ", ".join(f"'{v}'" for v in bq_filenames)

    df_ocr = fetch_data_from_bq(f"""
        SELECT *
        FROM `645009831643.pienza_mini.raw_offers_ocr`
        WHERE image_filename IN ({bq_list})
    """)

    # Map each carousel position back to its BQ row
    curr_filename = bq_filenames[idx]
    if not df_ocr.empty and curr_filename in df_ocr["image_filename"].values:
        ocr_row = df_ocr[df_ocr["image_filename"] == curr_filename].iloc[0]
        ocr_dict = ocr_row.to_dict()
    else:
        ocr_row  = None
        ocr_dict = {}

    # ── Stepper CSS ────────────────────────────────────────────
    st.markdown("""
<style>
.stepper-wrap { margin-top: 28px; }
.step-row { display: flex; gap: 0; align-items: stretch; margin-bottom: 0; }
.step-spine {
display: flex; flex-direction: column; align-items: center;
width: 40px; flex-shrink: 0;
}
.step-circle {
width: 28px; height: 28px; border-radius: 50%;
background: #21918c; color: #fff;
font-size: 12px; font-weight: 700;
display: flex; align-items: center; justify-content: center;
flex-shrink: 0; z-index: 1;
}
.step-line {
width: 2px; background: rgba(33,145,140,0.25);
flex: 1; min-height: 12px;
}
.step-line-cap { width: 2px; height: 14px; background: transparent; }
.step-body { flex: 1; padding: 0 0 0 12px; padding-bottom: 8px; }
.step-title {
font-size: 13px; font-weight: 700; color: #21918c;
letter-spacing: 0.4px; margin-bottom: 4px; padding-top: 4px;
}
.step-desc {
font-size: 12px; color: #475569; line-height: 1.6; margin-bottom: 10px;
}
.step-final .step-line { background: transparent; }
</style>
<div class="stepper-wrap">
""", unsafe_allow_html=True)

    # ── Step 1: Raw OCR ────────────────────────────────────────
    st.markdown("""
<div class="step-row">
  <div class="step-spine">
<div class="step-circle">1</div>
<div class="step-line"></div>
  </div>
  <div class="step-body">
<div class="step-title">Raw Gemini Pro Vision Output</div>
<div class="step-desc">Screenshots were batch-processed via the <strong>Google Gemini Pro Vision API</strong>. Despite rigorous prompt engineering, each batch produced slightly different formatting — making the normalization layer in Step 2 non-trivial.</div>
  </div>
</div>
""", unsafe_allow_html=True)
    import re as _re

    def _obf_fare(v):
        """Replace upfront fare digits with #### blocks."""
        if v is None:
            return v
        return _re.sub(r'\d', '#', str(v))

    def _obf_address(v):
        """Mask street number (non-5-digit numbers) in address; preserve zip codes."""
        if v is None:
            return v
        return _re.sub(r'\b(?!\d{5}\b)\d+[\w-]*\b', '####', str(v), count=1)

    def _obf_hash(v):
        """Truncate hash to 12 chars + ellipsis."""
        if v is None:
            return v
        s = str(v)
        return s[:12] + "..." if len(s) > 12 else s

    def _obf_latlon(v):
        """Keep ##.## and mask remaining decimals."""
        if v is None:
            return v
        s = str(v)
        dot = s.find(".")
        if dot == -1:
            return s
        return s[:dot + 3] + "####"

    _gap, _content = st.columns([1, 11])
    with _content:
        if ocr_dict:
            col_order = [
                "ocr_id", "image_filename", "time_taken", "ride_type",
                "upfront_fare", "pickup_details", "pickup_address",
                "trip_details", "dropoff_address", "rider_rating", "special_note",
            ]
            ordered = {k: ocr_dict[k] for k in col_order if k in ocr_dict}
            ordered.update({k: v for k, v in ocr_dict.items() if k not in ordered})

            ordered["upfront_fare"]    = _obf_fare(ordered.get("upfront_fare"))
            ordered["pickup_address"]  = _obf_address(ordered.get("pickup_address"))
            ordered["dropoff_address"] = _obf_address(ordered.get("dropoff_address"))

            st.code(json.dumps(ordered, indent=2, default=str, ensure_ascii=False), language="json")
        else:
            st.warning(f"No BQ record found for `{curr_filename}`")
        _nav_buttons("s1")

    # ── Step 2: Canonical offers row (denormalized) ────────────
    st.markdown("""
<div class="step-row">
  <div class="step-spine">
<div class="step-circle">2</div>
<div class="step-line"></div>
  </div>
  <div class="step-body">
<div class="step-title">Canonical Offer Record</div>
<div class="step-desc">The cleaned record as it lives in <code>pienza.db</code> — raw strings cast to typed fields, currency symbols stripped, incentive flags parsed. Denormalized here for explainability; in the actual database it is normalized across lookup tables. Coordinates resolved via the <strong>Google Maps Geocoding API</strong>.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    df_offers = fetch_data_from_bq(f"""
        SELECT
            o.offer_id, o.session_fk, o.image_content_hash, o.offer_timestamp,
            o.upfront_fare,
            p.category_name AS product_category,
            o.time_to_pickup_sec, o.dist_to_pickup_km,
            o.est_trip_time_sec, o.est_trip_dist_km,
            o.pickup_address, o.dropoff_address,
            o.pickup_lat, o.pickup_lon, o.dropoff_lat, o.dropoff_lon,
            o.is_surge, o.surge_amount,
            o.is_turbo_plus, o.turbo_plus_amount,
            o.is_reservation, o.reservation_amount,
            o.is_priority, o.priority_amount,
            o.is_exclusive, o.is_vip, o.is_identity_verified,
            o.is_long_trip, o.is_multiple_destinations, o.is_teens,
            o.rider_star_rating, o.rider_trip_count
        FROM `645009831643.pienza_mini.offers` o
        LEFT JOIN `645009831643.pienza_mini.product_category` p
            ON o.product_category_fk = p.product_category_id
        LEFT JOIN `645009831643.pienza_mini.raw_offers_ocr` r
            ON o.ocr_fk = r.ocr_id
        WHERE r.image_filename = '{curr_filename}'
        LIMIT 1
    """)

    df_dtypes = fetch_data_from_bq("""
        SELECT column_name, data_type
        FROM `645009831643.pienza_mini.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'offers'
    """)

    _gap, _content = st.columns([1, 11])
    with _content:
        if not df_offers.empty:
            dtype_map = dict(zip(df_dtypes["column_name"], df_dtypes["data_type"]))
            dtype_map["product_category"]   = "STRING"
            dtype_map["image_content_hash"] = "STRING"

            dtypes_row = {col: dtype_map.get(col, "—") for col in df_offers.columns}
            values_row = df_offers.iloc[0].to_dict()

            values_row["upfront_fare"]       = _obf_fare(values_row.get("upfront_fare"))
            values_row["pickup_address"]     = _obf_address(values_row.get("pickup_address"))
            values_row["dropoff_address"]    = _obf_address(values_row.get("dropoff_address"))
            values_row["image_content_hash"] = _obf_hash(values_row.get("image_content_hash"))
            for _col in ("pickup_lat", "pickup_lon", "dropoff_lat", "dropoff_lon"):
                values_row[_col] = _obf_latlon(values_row.get(_col))

            display_df = pd.DataFrame([dtypes_row, values_row], index=["dtype", "value"])
            st.dataframe(display_df, use_container_width=True)

            with st.expander("💡 Did You Know?"):
                st.markdown(
                    "<div style='font-size:13px;color:#334155;line-height:1.7;'>"
                    "The OCR pipeline initially extracted only an <strong>HH:MM string</strong>, making offer deduplication impossible. "
                    "Second-level granularity was achieved via a Python script that extracted standard <strong>EXIF metadata</strong> "
                    "from the screenshots, enabling unique <strong>SHA-256 fingerprinting</strong> and downstream velocity-based features."
                    "</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.warning(f"No canonical offer record found for `{curr_filename}`")
        _nav_buttons("s2")

    # ── Step 3: Geo-Semantic Enrichment (Silver Palette) ────────────
    st.markdown("""
<div class="step-row">
  <div class="step-spine">
<div class="step-circle">3</div>
<div class="step-line"></div>
  </div>
  <div class="step-body">
<div class="step-title">Geo-Semantic Enrichment</div>
<div class="step-desc">Raw lat/lon at full precision act as a surrogate index and cause overfitting. Coordinates were bucketed into three zone representations — heuristic polygons, H3 hexagons, and HDBSCAN clusters — ready for Supervised Learning.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    df_silver = fetch_data_from_bq(f"""
        SELECT
            sp.dropoff_polygon_name,
            sp.dropoff_h3_hex_id,
            sp.dropoff_hdbscan_name
        FROM `645009831643.pienza_mini.silver_palette` sp
        JOIN `645009831643.pienza_mini.offers` o
            ON sp.offer_id = o.offer_id
        JOIN `645009831643.pienza_mini.raw_offers_ocr` r
            ON o.ocr_fk = r.ocr_id
        WHERE r.image_filename = '{curr_filename}'
        LIMIT 1
    """)

    _gap, _content = st.columns([1, 11])
    with _content:
        if not df_silver.empty:
            sv = df_silver.iloc[0].to_dict()
            silver_display = pd.DataFrame([{
                "polygon_zone": sv.get("dropoff_polygon_name", "—"),
                "h3_hex_id (Res 9)":    sv.get("dropoff_h3_hex_id",    "—"),
                "hdbscan_cluster": sv.get("dropoff_hdbscan_name", "—"),
            }])
            st.dataframe(silver_display, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No Silver Palette record found for `{curr_filename}`")
        _nav_buttons("s3")

    # ── Dropoff transformation pipeline ────────────────────────────
    st.markdown("""
<div class="step-row step-final">
  <div class="step-spine">
<div class="step-circle" style="background:#21918c;">↓</div>
<div class="step-line" style="background:transparent;"></div>
  </div>
  <div class="step-body">
<div class="step-title" style="color:#21918c;">Dropoff Field — End-to-End Transformation</div>
<div class="step-desc">How a single dropoff field evolves from raw OCR string to geo-semantic zone.</div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

    raw_dropoff  = ocr_dict.get("dropoff_address", "—") if ocr_dict else "—"
    lat_val      = values_row.get("dropoff_lat",  "—") if not df_offers.empty else "—"
    lon_val      = values_row.get("dropoff_lon",  "—") if not df_offers.empty else "—"
    poly_zone    = sv.get("dropoff_polygon_name", "—") if not df_silver.empty else "—"
    h3_hex       = sv.get("dropoff_h3_hex_id",   "—") if not df_silver.empty else "—"
    hdbscan_name = sv.get("dropoff_hdbscan_name","—") if not df_silver.empty else "—"

    _gap, _content = st.columns([1, 11])
    with _content:
        st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
<tr>
  <th style="width:22%;text-align:left;padding:8px 12px;
             border-bottom:2px solid rgba(33,145,140,0.4);
             color:#21918c;font-size:10px;letter-spacing:1px;text-transform:uppercase;">Stage</th>
  <th style="text-align:left;padding:8px 12px;
             border-bottom:2px solid rgba(33,145,140,0.4);
             color:#21918c;font-size:10px;letter-spacing:1px;text-transform:uppercase;">Value</th>
</tr>
  </thead>
  <tbody>
<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
  <td style="padding:9px 12px;color:#94a3b8;white-space:nowrap;">① Raw OCR</td>
  <td style="padding:9px 12px;font-family:monospace;color:#94a3b8;">{_obf_address(raw_dropoff)}</td>
</tr>
<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
  <td style="padding:9px 12px;color:#94a3b8;white-space:nowrap;">② Lat / Lon</td>
  <td style="padding:9px 12px;font-family:monospace;color:#94a3b8;">{_obf_latlon(lat_val)}, {_obf_latlon(lon_val)}</td>
</tr>
<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
  <td style="padding:9px 12px;color:#94a3b8;white-space:nowrap;">③ Polygon zone</td>
  <td style="padding:9px 12px;color:#94a3b8;">{poly_zone}</td>
</tr>
<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
  <td style="padding:9px 12px;color:#94a3b8;white-space:nowrap;">③ H3 hex ID <span style="font-size:11px;color:#64748b;">(Res 9)</span></td>
  <td style="padding:9px 12px;font-family:monospace;color:#94a3b8;">{h3_hex}</td>
</tr>
<tr>
  <td style="padding:9px 12px;color:#94a3b8;white-space:nowrap;">③ HDBSCAN cluster</td>
  <td style="padding:9px 12px;color:#94a3b8;">{hdbscan_name}</td>
</tr>
  </tbody>
</table>
""", unsafe_allow_html=True)
        _nav_buttons("s4")

