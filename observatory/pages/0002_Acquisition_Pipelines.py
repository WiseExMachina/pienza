import base64
import datetime
import json
import pathlib
import time
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from components.styles import GLOBAL_CSS
from config import FAVICON
from pathlib import Path
from utils.gcp_client import fetch_bytes_from_gcs

st.set_page_config(layout="wide", page_title="Acquisition Pipelines | Pienza", page_icon=FAVICON)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
@st.cache_data
def _load_favicon_b64():
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


def build_sidebar():
    with st.sidebar:
        st.markdown(
            "<div class='sb-brand'>"
            "<div class='sb-brand-mark'>"
            f"<img src='data:image/png;base64,{_load_favicon_b64()}' width='28' height='28' /></div>"
            "<div><div class='sb-brand-text-title'>Project Pienza</div>"
            "<div class='sb-brand-text-sub'>Digital Twin · CDMX</div></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.page_link("main.py", label="Home", icon=":material/home:")
        st.markdown("<div class='sb-section-label'>Modules</div>", unsafe_allow_html=True)
        st.page_link("pages/0001_Foundations.py", label="Foundations", icon=":material/layers:")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines", icon=":material/sync:")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store", icon=":material/database:")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics", icon=":material/search:")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping", icon=":material/report:")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference", icon=":material/account_tree:")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning", icon=":material/shield:")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer", icon=":material/bolt:")
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big", icon=":material/send:")

        with st.container(key="sb-footer"):
            st.markdown("---")
            pdf_link = (
                "<a href='app/static/Pienza_Papers.pdf' target='_blank' "
                "class='sb-pdf-link'>Download PDF</a>"
            )

            st.markdown(
                "<div class='sb-meta-line'><b>Author:</b> Bernardo Lozano Wise<br>"
                "<b>LinkedIn:</b> <a href='https://www.linkedin.com/in/bernardolw/' target='_blank' class='sb-pdf-link'>/bernardolw</a><br>"
                "<b>GitHub:</b> <a href='https://github.com/WiseExMachina/pienza' target='_blank' class='sb-pdf-link'>/pienza</a><br>"
                "<b>Domain:</b> Data Science · Applied ML — Mobility & Logistics<br>"
                "<b>Stack:</b> Python, XGBoost, TensorFlow, BigQuery, PySpark, NetworkX<br>"
                f"<b>AI Knowledge Base:</b> {pdf_link}</div>",
                unsafe_allow_html=True,
            )
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
st.markdown("<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>Two Engines, One Ground Truth — GTS Telemetry + Gemini OCR</h4>", unsafe_allow_html=True)

# Shared cache for OCR screenshot base64 encoding. Two real costs were found
# here during a 2026-07-09 perf pass (see project_live_calls_audit memory):
# 1) fetch_bytes_from_gcs is cached, but base64.b64encode() itself was redone
#    every rerun for the same ~10 image draws (3x phone-stack + up to 10x
#    filmstrip) — pure CPU work with no reason to repeat.
# 2) The bigger one: these are full-resolution offer screenshots (750x1624,
#    ~400-620KB PNG each) served at ~200px display width. Every arrow click
#    re-rendered the whole filmstrip + phone-stack markup, re-transmitting
#    ~5.4MB of base64 text over the websocket for images displayed at a
#    fraction of their native size. Resizing to actual display width + JPEG
#    recompression cuts each image to ~25-50KB (~10-15x smaller) with no
#    visible quality loss at the sizes these are shown.
@st.cache_data(show_spinner=False)
def _img_b64(img_path: str, max_width: int = 320) -> str:
    from PIL import Image
    import io
    raw = fetch_bytes_from_gcs("pienza-streamlit", img_path)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if img.width > max_width:
        h = int(img.height * max_width / img.width)
        img = img.resize((max_width, h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

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

# Each engine is isolated in its own @st.fragment: without this, clicking a
# nav/state-transition button anywhere on this page (either engine) triggers
# st.rerun(), which by default re-executes this entire ~965-line script —
# including the other engine's simulator/components.html blocks and all its
# BQ/image loads (cache-hit, but still real per-rerun overhead). Scoping each
# engine to its own fragment means a click in Engine 2 no longer re-renders
# Engine 1's GTS device-frame simulator, and vice versa.
@st.fragment
def _render_engine1():
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
                st.rerun(scope="fragment")
        else:
            if st.button("■  End Session", use_container_width=True):
                st.session_state.sim_active = False
                st.session_state.show_summary = True
                st.rerun(scope="fragment")

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
                    st.rerun(scope="fragment")

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
                    st.rerun(scope="fragment")

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
                st.rerun(scope="fragment")

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
  <p>A client-side pipeline orchestrates the <code style="color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;">navigator.geolocation</code> API with reverse-geocoding services. Every T0–T4 event is enriched with high-precision coordinates and a human-readable address string <em>prior</em> to persistence — decoupling location capture from UI interaction to avoid blocking the driver's workflow.</p>
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

with subtab2:
    _render_engine1()

# Hardcoded 2026-07-09 — see project_live_calls_audit / project_tech_debt memory.
# Frozen ground truth for the 10 Engine 2 carousel offers (never changes; this
# IS the dataset, not a query result that could drift). Sensitive fields
# (upfront_fare, pickup/dropoff_address, image_content_hash, lat/lon) are
# pre-masked with the same _obf_* functions used elsewhere on this page —
# the obfuscation functions are idempotent, so any downstream re-application
# is a safe no-op. Regenerate by re-running the 3 batched BQ queries this
# replaced if the underlying offers/raw_offers_ocr/silver_palette rows ever change.

_DF_OCR_RECORDS = [{'ocr_id': 'OCR01714',
  'image_filename': 'IMG_9277.PNG',
  'time_taken': '2:47 PM',
  'ride_type': 'Black Exclusivo',
  'upfront_fare': '$###.##',
  'pickup_details': '7 min (1.7 km)',
  'pickup_address': 'Calle Montes Urales, Lomas de Chapultepec',
  'trip_details': '27 min (8.9 km)',
  'dropoff_address': 'Privada Tamarindos ####, Granjas Palo Alto, 05120 Cuajimalpa de Morelos - Bosques de las lomas',
  'rider_rating': '4.70 (622 ratings)',
  'special_note': '+$8.00 incluido'},
 {'ocr_id': 'OCR03289',
  'image_filename': 'IMG_2793.PNG',
  'time_taken': '6:33',
  'ride_type': 'Comfort',
  'upfront_fare': '##.#',
  'pickup_details': '5 min (2.9 km)',
  'pickup_address': 'Av Tamaulipas, Santa Fe',
  'trip_details': '4 min (2.3 km)',
  'dropoff_address': 'Prol Paseo de Reforma ####, Álvaro Obregón, 01219 Álvaro Obregón - Santa Fe',
  'rider_rating': '4.82 (789)',
  'special_note': 'Exclusivo, +$18.00 incluido, Turbo+ de $9.44 incluido'},
 {'ocr_id': 'OCR03573',
  'image_filename': 'IMG_3428.PNG',
  'time_taken': '7:21',
  'ride_type': 'Turbo+',
  'upfront_fare': '###.##',
  'pickup_details': '10 min (4.1 km)',
  'pickup_address': 'Primer Retorno de Cumbres de Acultzingo, Bosques',
  'trip_details': '16 min (6.0 km)',
  'dropoff_address': 'Bondojito ####, Col Las Américas, 01120 Álvaro Obregón - Observatorio',
  'rider_rating': '4.80 (330)',
  'special_note': 'Identidad verificada, Turbo+ de $15.36 incluido'},
 {'ocr_id': 'OCR03692',
  'image_filename': 'IMG_3679.PNG',
  'time_taken': '15:37',
  'ride_type': 'UberX',
  'upfront_fare': '###.##',
  'pickup_details': '13 min (13.4 km)',
  'pickup_address': 'Calle Vía Magna, Interlomas',
  'trip_details': '13 min (3.5 km)',
  'dropoff_address': 'Av Universidad Anáhuac ####, Col Lomas Anáhuac Huixquilucan, 52786 Huixquilucan, México - '
                     'Bosques',
  'rider_rating': '4.89 (751)',
  'special_note': '+$14.00 incluido,Identidad verificada'},
 {'ocr_id': 'OCR03982',
  'image_filename': 'IMG_4346.PNG',
  'time_taken': '19:13',
  'ride_type': 'UberX',
  'upfront_fare': '###.##',
  'pickup_details': '24 min (2.9 km)',
  'pickup_address': 'Avenida General Pedro Antonio de los Santos, Condesa / Roma',
  'trip_details': '50 min (9.3 km)',
  'dropoff_address': 'Prol. P.º de la Reforma ####, Santa Fe, Zedec Sta Fé, Álvaro Obregón, 01310 Ciudad de México, '
                     'CDMX, México - Santa Fe',
  'rider_rating': '4.69 (629)',
  'special_note': '+$12.00 incluido, Turbo+ de $55.37 incluido, VIP'},
 {'ocr_id': 'OCR01600',
  'image_filename': 'IMG_9029.PNG',
  'time_taken': '5:53',
  'ride_type': 'UberX (Exclusivo)',
  'upfront_fare': '$###.##',
  'pickup_details': '10 min (4.7 km)',
  'pickup_address': 'Calle Naranjo, Claveria - Azcapotzalco',
  'trip_details': '41 min (18.7 km)',
  'dropoff_address': 'Vialidad de la Barranca ####, Col. Ex Hacienda Jesús del Monte, Bosque de las Palmas, 52787 '
                     'Naucalpan de Juárez, Méx., México - Interlomas',
  'rider_rating': '4.79 (6888 ratings)',
  'special_note': 'VIP, +$30.00 incluido'},
 {'ocr_id': 'OCR00159',
  'image_filename': 'IMG_5813.PNG',
  'time_taken': '4:48',
  'ride_type': 'UberX Exclusivo',
  'upfront_fare': '$###.##',
  'pickup_details': '3 min (0.9 km)',
  'pickup_address': 'Calle Bosque de Amates, Bosques de las lomas',
  'trip_details': '44 min (8.5 km)',
  'dropoff_address': 'Av Insurgentes Tacubaya ####, Col Tacubaya Miguel Hidalgo, 11870 Ciudad de México, CMX - '
                     'Condesa / Roma',
  'rider_rating': '4.56 (764 ratings)',
  'special_note': 'A Turbo+ of $42.95 is included. The user is a VIP.'},
 {'ocr_id': 'OCR02768',
  'image_filename': 'IMG_1691.PNG',
  'time_taken': '15:32',
  'ride_type': 'Business Comfort',
  'upfront_fare': '###.##',
  'pickup_details': '8 min (1.7 km)',
  'pickup_address': 'Lomas de Chapultepec',
  'trip_details': '43 min (13.4 km)',
  'dropoff_address': 'Carlos Lazo ####, Col Santa Fe Tlayapaca Álvaro Obregón, 01389 Ciudad de México, Ciudad de '
                     'México - Santa Fe',
  'rider_rating': '4.78 (2118)',
  'special_note': 'Exclusivo, VIP'},
 {'ocr_id': 'OCR00535',
  'image_filename': 'IMG_6624.PNG',
  'time_taken': '8:57',
  'ride_type': 'UberX',
  'upfront_fare': '$###.##',
  'pickup_details': '13 min (4.7 km)',
  'pickup_address': 'Avenida Primero de Mayo, Nápoles',
  'trip_details': '41 min (7.1 km)',
  'dropoff_address': 'Av Paseo de las Palmas #### Torre Optima 1 PB, Miguel Hidalgo, Col Lomas de Chapultepec Miguel '
                     'Hidalgo, 11000 Ciudad de México, Ciudad de México - Lomas de Chapultepec',
  'rider_rating': '4.83 (2834 ratings)',
  'special_note': 'Identity verified.'},
 {'ocr_id': 'OCR02057',
  'image_filename': 'IMG_0038.PNG',
  'time_taken': '6:04 AM',
  'ride_type': 'UberX',
  'upfront_fare': '$###.##',
  'pickup_details': '10 min (3.7 km)',
  'pickup_address': 'Yucatán #### Loc E3 Piso 1er, Cuauhtémoc, Condesa / Roma',
  'trip_details': '19 min (12.7 km)',
  'dropoff_address': 'Av. Capitán Carlos León S/N, Peñón de los Baños, Venustiano Carranza, 15620 Ciudad de México, '
                     'CDMX, México - Aeropuerto Internacional Benito Juárez',
  'rider_rating': '5.00 (0 ratings)',
  'special_note': 'N/A'}]

_DF_OFFERS_RECORDS = [{'image_filename': 'IMG_6624.PNG',
  'offer_id': 'OF00535',
  'session_fk': 'SID0008',
  'image_content_hash': 'bf164a332e03...',
  'offer_timestamp': '2025-08-26 08:57:29',
  'upfront_fare': '###.#',
  'product_category': 'uberx',
  'time_to_pickup_sec': 780.0,
  'dist_to_pickup_km': 4.7,
  'est_trip_time_sec': 2460.0,
  'est_trip_dist_km': 7.1,
  'pickup_address': 'avenida primero de mayo, napoles, ciudad de mexico, cdmx, mexico',
  'dropoff_address': 'Av Paseo de las Palmas #### Torre Optima 1 PB, Miguel Hidalgo, Col Lomas de Chapultepec Miguel '
                     'Hidalgo, 11000 Ciudad de México, Ciudad de México - Lomas de Chapultepec',
  'pickup_lat': '19.39####',
  'pickup_lon': '-99.18####',
  'dropoff_lat': '19.43####',
  'dropoff_lon': '-99.21####',
  'is_surge': 0,
  'surge_amount': None,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 0,
  'is_vip': 0,
  'is_identity_verified': 1,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.83,
  'rider_trip_count': 2834.0},
 {'image_filename': 'IMG_9277.PNG',
  'offer_id': 'OF01714',
  'session_fk': 'SID0025',
  'image_content_hash': 'bcb8ac7cdf89...',
  'offer_timestamp': '2025-09-04 14:47:02',
  'upfront_fare': '###.##',
  'product_category': 'black',
  'time_to_pickup_sec': 420.0,
  'dist_to_pickup_km': 1.7,
  'est_trip_time_sec': 1620.0,
  'est_trip_dist_km': 8.9,
  'pickup_address': 'calle montes urales, lomas de chapultepec',
  'dropoff_address': 'Privada Tamarindos ####, Granjas Palo Alto, 05120 Cuajimalpa de Morelos - Bosques de las lomas',
  'pickup_lat': '19.42####',
  'pickup_lon': '-99.20####',
  'dropoff_lat': '19.38####',
  'dropoff_lon': '-99.25####',
  'is_surge': 1,
  'surge_amount': 8.0,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 1,
  'is_vip': 0,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.7,
  'rider_trip_count': 622.0},
 {'image_filename': 'IMG_0038.PNG',
  'offer_id': 'OF02057',
  'session_fk': 'SID0029',
  'image_content_hash': 'a0bb89ec351d...',
  'offer_timestamp': '2025-09-11 06:04:15',
  'upfront_fare': '###.##',
  'product_category': 'uberx',
  'time_to_pickup_sec': 600.0,
  'dist_to_pickup_km': 3.7,
  'est_trip_time_sec': 1140.0,
  'est_trip_dist_km': 12.7,
  'pickup_address': 'yucatan #### loc e3 piso 1er, cuauhtemoc, condesa / roma',
  'dropoff_address': 'Av. Capitán Carlos León S/N, Peñón de los Baños, Venustiano Carranza, 15620 Ciudad de México, '
                     'CDMX, México - Aeropuerto Internacional Benito Juárez',
  'pickup_lat': '19.41####',
  'pickup_lon': '-99.16####',
  'dropoff_lat': '19.43####',
  'dropoff_lon': '-99.08####',
  'is_surge': 0,
  'surge_amount': None,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 0,
  'is_vip': 0,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 5.0,
  'rider_trip_count': 0.0},
 {'image_filename': 'IMG_2793.PNG',
  'offer_id': 'OF03289',
  'session_fk': 'SID0045',
  'image_content_hash': '8b6b99bc2f6a...',
  'offer_timestamp': '2025-09-22 06:33:23',
  'upfront_fare': '##.#',
  'product_category': 'comfort',
  'time_to_pickup_sec': 300.0,
  'dist_to_pickup_km': 2.9,
  'est_trip_time_sec': 240.0,
  'est_trip_dist_km': 2.3,
  'pickup_address': 'avenida tamaulipas, santa fe, ciudad de mexico, cdmx, mexico',
  'dropoff_address': 'Prol Paseo de Reforma ####, Álvaro Obregón, 01219 Álvaro Obregón - Santa Fe',
  'pickup_lat': '19.35####',
  'pickup_lon': '-99.26####',
  'dropoff_lat': '19.37####',
  'dropoff_lon': '-99.26####',
  'is_surge': 1,
  'surge_amount': 18.0,
  'is_turbo_plus': 1,
  'turbo_plus_amount': 9.44,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 1,
  'is_vip': 0,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.82,
  'rider_trip_count': 789.0},
 {'image_filename': 'IMG_3428.PNG',
  'offer_id': 'OF03573',
  'session_fk': 'SID0047',
  'image_content_hash': '3e4e95f41ec9...',
  'offer_timestamp': '2025-09-23 07:21:04',
  'upfront_fare': '###.##',
  'product_category': 'black',
  'time_to_pickup_sec': 600.0,
  'dist_to_pickup_km': 4.1,
  'est_trip_time_sec': 960.0,
  'est_trip_dist_km': 6.0,
  'pickup_address': 'primer retorno de cumbres de acultzingo, bosques, ciudad de mexico, cdmx, mexico',
  'dropoff_address': 'Bondojito ####, Col Las Américas, 01120 Álvaro Obregón - Observatorio',
  'pickup_lat': '19.40####',
  'pickup_lon': '-99.22####',
  'dropoff_lat': '19.39####',
  'dropoff_lon': '-99.20####',
  'is_surge': 0,
  'surge_amount': None,
  'is_turbo_plus': 1,
  'turbo_plus_amount': 15.36,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 0,
  'is_vip': 0,
  'is_identity_verified': 1,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.8,
  'rider_trip_count': 330.0},
 {'image_filename': 'IMG_3679.PNG',
  'offer_id': 'OF03692',
  'session_fk': 'SID0048',
  'image_content_hash': 'ab4a8bf4a5ca...',
  'offer_timestamp': '2025-09-23 15:37:37',
  'upfront_fare': '###.##',
  'product_category': 'uberx',
  'time_to_pickup_sec': 780.0,
  'dist_to_pickup_km': 13.4,
  'est_trip_time_sec': 780.0,
  'est_trip_dist_km': 3.5,
  'pickup_address': 'calle via magna, interlomas',
  'dropoff_address': 'Av Universidad Anáhuac ####, Col Lomas Anáhuac Huixquilucan, 52786 Huixquilucan, México - '
                     'Bosques',
  'pickup_lat': '19.40####',
  'pickup_lon': '-99.27####',
  'dropoff_lat': '19.40####',
  'dropoff_lon': '-99.26####',
  'is_surge': 1,
  'surge_amount': 14.0,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 0,
  'is_vip': 0,
  'is_identity_verified': 1,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.89,
  'rider_trip_count': 751.0},
 {'image_filename': 'IMG_5813.PNG',
  'offer_id': 'OF00159',
  'session_fk': 'SID0003',
  'image_content_hash': '793dea9502b4...',
  'offer_timestamp': '2025-08-22 16:48:35',
  'upfront_fare': '###.#',
  'product_category': 'uberx',
  'time_to_pickup_sec': 180.0,
  'dist_to_pickup_km': 0.9,
  'est_trip_time_sec': 2640.0,
  'est_trip_dist_km': 8.5,
  'pickup_address': 'bosque de amates, bosques de las lomas',
  'dropoff_address': 'Av Insurgentes Tacubaya ####, Col Tacubaya Miguel Hidalgo, 11870 Ciudad de México, CMX - '
                     'Condesa / Roma',
  'pickup_lat': '19.39####',
  'pickup_lon': '-99.24####',
  'dropoff_lat': '19.40####',
  'dropoff_lon': '-99.18####',
  'is_surge': 1,
  'surge_amount': 4.0,
  'is_turbo_plus': 1,
  'turbo_plus_amount': 42.95,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 1,
  'is_vip': 1,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.56,
  'rider_trip_count': 764.0},
 {'image_filename': 'IMG_9029.PNG',
  'offer_id': 'OF01600',
  'session_fk': 'SID0024',
  'image_content_hash': 'd2cfe46785bb...',
  'offer_timestamp': '2025-09-04 05:53:13',
  'upfront_fare': '###.##',
  'product_category': 'uberx',
  'time_to_pickup_sec': 600.0,
  'dist_to_pickup_km': 4.7,
  'est_trip_time_sec': 2460.0,
  'est_trip_dist_km': 18.7,
  'pickup_address': 'calle naranjo, claveria - azcapotzalco',
  'dropoff_address': 'Vialidad de la Barranca ####, Col. Ex Hacienda Jesús del Monte, Bosque de las Palmas, 52787 '
                     'Naucalpan de Juárez, Méx., México - Interlomas',
  'pickup_lat': '19.45####',
  'pickup_lon': '-99.15####',
  'dropoff_lat': '19.39####',
  'dropoff_lon': '-99.28####',
  'is_surge': 1,
  'surge_amount': 30.0,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 1,
  'is_vip': 1,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.79,
  'rider_trip_count': 6888.0},
 {'image_filename': 'IMG_1691.PNG',
  'offer_id': 'OF02768',
  'session_fk': 'SID0038',
  'image_content_hash': '94511da5ecc5...',
  'offer_timestamp': '2025-09-18 15:32:57',
  'upfront_fare': '###.##',
  'product_category': 'business_comfort',
  'time_to_pickup_sec': 480.0,
  'dist_to_pickup_km': 1.7,
  'est_trip_time_sec': 2580.0,
  'est_trip_dist_km': 13.4,
  'pickup_address': 'lomas de chapultepec',
  'dropoff_address': 'Carlos Lazo ####, Col Santa Fe Tlayapaca Álvaro Obregón, 01389 Ciudad de México, Ciudad de '
                     'México - Santa Fe',
  'pickup_lat': '19.42####',
  'pickup_lon': '-99.21####',
  'dropoff_lat': '19.35####',
  'dropoff_lon': '-99.25####',
  'is_surge': 0,
  'surge_amount': None,
  'is_turbo_plus': 0,
  'turbo_plus_amount': None,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 1,
  'is_vip': 1,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.78,
  'rider_trip_count': 2118.0},
 {'image_filename': 'IMG_4346.PNG',
  'offer_id': 'OF03982',
  'session_fk': 'SID0052',
  'image_content_hash': 'f3bf9140fd64...',
  'offer_timestamp': '2025-09-25 19:13:35',
  'upfront_fare': '###.##',
  'product_category': 'uberx',
  'time_to_pickup_sec': 1440.0,
  'dist_to_pickup_km': 2.9,
  'est_trip_time_sec': 3000.0,
  'est_trip_dist_km': 9.3,
  'pickup_address': 'avenida general pedro antonio de los santos, condesa / roma',
  'dropoff_address': 'Prol. P.º de la Reforma ####, Santa Fe, Zedec Sta Fé, Álvaro Obregón, 01310 Ciudad de México, '
                     'CDMX, México - Santa Fe',
  'pickup_lat': '19.41####',
  'pickup_lon': '-99.18####',
  'dropoff_lat': '19.37####',
  'dropoff_lon': '-99.25####',
  'is_surge': 1,
  'surge_amount': 12.0,
  'is_turbo_plus': 1,
  'turbo_plus_amount': 55.37,
  'is_reservation': 0,
  'reservation_amount': None,
  'is_priority': 0,
  'priority_amount': None,
  'is_exclusive': 0,
  'is_vip': 1,
  'is_identity_verified': 0,
  'is_long_trip': 0,
  'is_multiple_destinations': 0,
  'is_teens': 0,
  'rider_star_rating': 4.69,
  'rider_trip_count': 629.0}]

_DF_SILVER_RECORDS = [{'image_filename': 'IMG_0038.PNG',
  'dropoff_polygon_name': 'unassigned',
  'dropoff_h3_hex_id': '894995b9417ffff',
  'dropoff_hdbscan_name': 'terminal_1_aicm'},
 {'image_filename': 'IMG_6624.PNG',
  'dropoff_polygon_name': 'palmas_jp_morgan',
  'dropoff_h3_hex_id': '894995bac0fffff',
  'dropoff_hdbscan_name': 'el_semaforo_de_palmas'},
 {'image_filename': 'IMG_3679.PNG',
  'dropoff_polygon_name': 'universidad_anahuac',
  'dropoff_h3_hex_id': '894995b1187ffff',
  'dropoff_hdbscan_name': 'lomas_anahuac'},
 {'image_filename': 'IMG_9277.PNG',
  'dropoff_polygon_name': 'tamarindos',
  'dropoff_h3_hex_id': '894995b1557ffff',
  'dropoff_hdbscan_name': 'tamarindos'},
 {'image_filename': 'IMG_1691.PNG',
  'dropoff_polygon_name': 'santa_fe_tec',
  'dropoff_h3_hex_id': '894995b33cfffff',
  'dropoff_hdbscan_name': 'santa_fe_itesm'},
 {'image_filename': 'IMG_3428.PNG',
  'dropoff_polygon_name': 'bondojito_asf',
  'dropoff_h3_hex_id': '894995b12cbffff',
  'dropoff_hdbscan_name': 'observatorio'},
 {'image_filename': 'IMG_9029.PNG',
  'dropoff_polygon_name': 'vialidad_de_la_barranca',
  'dropoff_h3_hex_id': '894995b0217ffff',
  'dropoff_hdbscan_name': 'vialidad_de_la_barranca'},
 {'image_filename': 'IMG_4346.PNG',
  'dropoff_polygon_name': 'sante_fe_patio',
  'dropoff_h3_hex_id': '894995b15cbffff',
  'dropoff_hdbscan_name': 'santa_fe_patio'},
 {'image_filename': 'IMG_2793.PNG',
  'dropoff_polygon_name': 'santa_fe_ibero',
  'dropoff_h3_hex_id': '894995b3367ffff',
  'dropoff_hdbscan_name': 'santa_fe_core'},
 {'image_filename': 'IMG_5813.PNG',
  'dropoff_polygon_name': 'roma_condesa_2',
  'dropoff_h3_hex_id': '894995ba1d3ffff',
  'dropoff_hdbscan_name': 'tacubaya'}]

_DF_DTYPES_RECORDS = [{'column_name': 'offer_id', 'data_type': 'STRING'},
 {'column_name': 'session_fk', 'data_type': 'STRING'},
 {'column_name': 'ocr_fk', 'data_type': 'STRING'},
 {'column_name': 'image_content_hash', 'data_type': 'STRING'},
 {'column_name': 'offer_timestamp', 'data_type': 'STRING'},
 {'column_name': 'upfront_fare', 'data_type': 'FLOAT64'},
 {'column_name': 'time_to_pickup_sec', 'data_type': 'FLOAT64'},
 {'column_name': 'dist_to_pickup_km', 'data_type': 'FLOAT64'},
 {'column_name': 'est_trip_time_sec', 'data_type': 'FLOAT64'},
 {'column_name': 'est_trip_dist_km', 'data_type': 'FLOAT64'},
 {'column_name': 'pickup_address', 'data_type': 'STRING'},
 {'column_name': 'dropoff_address', 'data_type': 'STRING'},
 {'column_name': 'pickup_lat', 'data_type': 'FLOAT64'},
 {'column_name': 'pickup_lon', 'data_type': 'FLOAT64'},
 {'column_name': 'dropoff_lat', 'data_type': 'FLOAT64'},
 {'column_name': 'dropoff_lon', 'data_type': 'FLOAT64'},
 {'column_name': 'is_surge', 'data_type': 'INT64'},
 {'column_name': 'surge_amount', 'data_type': 'FLOAT64'},
 {'column_name': 'is_turbo_plus', 'data_type': 'INT64'},
 {'column_name': 'turbo_plus_amount', 'data_type': 'FLOAT64'},
 {'column_name': 'is_reservation', 'data_type': 'INT64'},
 {'column_name': 'reservation_amount', 'data_type': 'FLOAT64'},
 {'column_name': 'is_priority', 'data_type': 'INT64'},
 {'column_name': 'priority_amount', 'data_type': 'FLOAT64'},
 {'column_name': 'is_exclusive', 'data_type': 'INT64'},
 {'column_name': 'is_vip', 'data_type': 'INT64'},
 {'column_name': 'is_identity_verified', 'data_type': 'INT64'},
 {'column_name': 'is_long_trip', 'data_type': 'INT64'},
 {'column_name': 'is_multiple_destinations', 'data_type': 'INT64'},
 {'column_name': 'is_teens', 'data_type': 'INT64'},
 {'column_name': 'rider_star_rating', 'data_type': 'FLOAT64'},
 {'column_name': 'rider_trip_count', 'data_type': 'FLOAT64'},
 {'column_name': 'time_in_session_sec', 'data_type': 'FLOAT64'},
 {'column_name': 'session_progress_ratio', 'data_type': 'FLOAT64'},
 {'column_name': 'inferred_agent_lat', 'data_type': 'FLOAT64'},
 {'column_name': 'inferred_agent_lon', 'data_type': 'FLOAT64'},
 {'column_name': 'inferred_agent_bearing', 'data_type': 'FLOAT64'},
 {'column_name': 'inferred_agent_speed_mps', 'data_type': 'FLOAT64'},
 {'column_name': 'is_imputed', 'data_type': 'INT64'},
 {'column_name': 'special_note_raw', 'data_type': 'STRING'},
 {'column_name': 'comment_1', 'data_type': 'STRING'},
 {'column_name': 'comment_2', 'data_type': 'STRING'},
 {'column_name': 'product_category_fk', 'data_type': 'INT64'},
 {'column_name': 'offer_action_fk', 'data_type': 'INT64'},
 {'column_name': 'reason_primary_fk', 'data_type': 'FLOAT64'},
 {'column_name': 'post_offer_status_fk', 'data_type': 'INT64'},
 {'column_name': 'driver_state_at_request_fk', 'data_type': 'INT64'},
 {'column_name': 'outcome_fk', 'data_type': 'FLOAT64'},
 {'column_name': 'interpolation_quality_fk', 'data_type': 'FLOAT64'},
 {'column_name': 'record_status_fk', 'data_type': 'INT64'}]

@st.fragment
def _render_engine2():
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
                st.rerun(scope="fragment")
        with _c2:
            if st.button("→", key=f"nav_next_{key_suffix}", disabled=(idx == n - 1), use_container_width=True):
                st.session_state.ocr_slide = idx + 1
                st.rerun(scope="fragment")

    # ── Stacked phone frames + filmstrip ──────────────────────
    def _mk_phone(img_path, rotate, tx, ty, opacity, z):
        b = _img_b64(img_path, max_width=280)
        return f"""
<div style="position:absolute;width:235px;border-radius:40px;
 background:#0a0a0a;border:8px solid #1a1a1a;padding:10px 0 14px;
 box-shadow:0 20px 48px rgba(0,0,0,0.5),inset 0 0 0 1px rgba(255,255,255,0.05);
 transform:rotate({rotate}deg) translate({tx}px,{ty}px);
 opacity:{opacity};z-index:{z};top:0;left:50%;margin-left:-117px;">
  <div style="width:72px;height:6px;background:#1a1a1a;
          border-radius:0 0 6px 6px;margin:0 auto 10px;"></div>
  <img src="data:image/jpeg;base64,{b}" style="width:100%;display:block;border-radius:4px;" />
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
            tb = _img_b64(o["img"], max_width=140)
            border = "2px solid #21918c" if i == idx else "2px solid rgba(255,255,255,0.1)"
            opacity = "1" if i == idx else "0.4"
            st.markdown(f"""
<div style="border-radius:8px;border:{border};overflow:hidden;
        opacity:{opacity};margin-bottom:2px;">
  <img src="data:image/jpeg;base64,{tb}" style="width:100%;display:block;" />
</div>""", unsafe_allow_html=True)
            if st.button(f"{i+1}", key=f"thumb_{i}", use_container_width=True):
                st.session_state.ocr_slide = i
                st.rerun(scope="fragment")

    # ── BQ: fetch raw_offers_ocr for carousel images ───────────
    img_filenames = [pathlib.Path(o["img"]).name for o in OFFERS]
    # Strip leading "XX_" prefix to match BQ image_filename values
    bq_filenames  = [f.split("_", 1)[1] for f in img_filenames]
    bq_list       = ", ".join(f"'{v}'" for v in bq_filenames)

    df_ocr = pd.DataFrame(_DF_OCR_RECORDS)

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
<div class="step-desc">The cleaned record as it lives in <code style="color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;">pienza.db</code> — raw strings cast to typed fields, currency symbols stripped, incentive flags parsed. Denormalized here for explainability; in the actual database it is normalized across lookup tables. Coordinates resolved via the <strong>Google Maps Geocoding API</strong>.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Batched once for all 8 carousel offers (same pattern as df_ocr above),
    # instead of embedding curr_filename in the WHERE clause — that made the
    # SQL string (and therefore the @st.cache_data key) change on every
    # prev/next click, firing a live BQ query on every new slide visited.
    df_offers_all = pd.DataFrame(_DF_OFFERS_RECORDS)
    df_offers = (
        df_offers_all[df_offers_all["image_filename"] == curr_filename].drop(columns=["image_filename"])
        if not df_offers_all.empty else df_offers_all
    )

    df_dtypes = pd.DataFrame(_DF_DTYPES_RECORDS)

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

    # Batched once for all 8 carousel offers — same reasoning as df_offers above.
    df_silver_all = pd.DataFrame(_DF_SILVER_RECORDS)
    df_silver = (
        df_silver_all[df_silver_all["image_filename"] == curr_filename].drop(columns=["image_filename"])
        if not df_silver_all.empty else df_silver_all
    )

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

with subtab3:
    _render_engine2()

