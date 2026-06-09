import streamlit as st
import pandas as pd
from utils.sidebar import build_sidebar

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Acquistion and Ground Truth",
    layout="wide"
)


build_sidebar()




# ==========================================
# CUSTOM FONT & SIZE INJECTION (SAFE VERSION)
# ==========================================
st.markdown("""
    <style>
        /* Import Crimson Pro (Serif) and Inter (Sans-Serif) from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');
        
        /* 1. Body Text (Crimson Pro) - Target semantic content tags only! */
        p, li, td, th {
            font-family: 'Crimson Pro', serif !important;
            font-size: 18px !important;  
            line-height: 1.6 !important; 
        }

        /* 2. Headers Base Setup (Inter) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }

        /* 2a. Individual Header Sizes */
        h1 { font-size: 38px !important; } 
        h2 { font-size: 28px !important; } 
        h3 { font-size: 22px !important; } 

        /* 3. Expander Headers (Force them to match H3 Inter styling) */
        [data-testid="stExpander"] details summary p {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }

        /* 4. Code Blocks & Terminal (Monospace) */
        code, pre {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 15px !important; 
        }
    </style>
""", unsafe_allow_html=True)


import streamlit as st


import streamlit as st

# ==========================================
# PHASE 1: ACQUISITION & GROUND TRUTH (Non-Collapsible Intro)
# ==========================================
st.header("Acquisition and Ground Truth")

st.markdown("""
Project Pienza models the decision policy of an expert agent rather than a system in a learning phase. Prior to data collection, the subject had completed 24 months of field operations, concluding the *Exploration* stage of the Reinforcement Learning cycle. 

Utilizing the framework of Hopfield Networks as explored by Anil Ananthaswamy in *Why Machines Learn*, the agent’s decision policy is modeled as a "cooled" system settled into a stable local minimum (*an attractor state*). This equilibrium represents an optimization contingent on the agent’s specific constraints: geographic preferences, risk tolerance, and physical endurance. While a theoretical global optimum for city-wide revenue may exist in the state space, the captured dataset represents a phase of pure *exploitation*. By prioritizing established, low-variance heuristics over high-energy experimental maneuvers, the resulting dataset provides a high-fidelity record of a converged policy.

Project Pienza utilizes a proprietary, dual-engine acquisition ecosystem to overcome the data sparsity inherent in third-party platform exports. The primary acquisition campaign was executed over a strict 6-week observation window (August 22 -- October 1, 2025), digitizing the agent's operational reality in real-time.
""")

# ==========================================
# PHASE 1: ENGINE 1 (Collapsible Section)
# ==========================================
with st.expander("Engine 1: The Operational Telemetry (GTS Webapp)", expanded=False):

    st.markdown("""
    To establish the ground truth of completed missions, a bespoke Progressive Web Application (PWA) designated as the **Geotimestamps (GTS) Webapp** was deployed. The interface was optimized for low-cognitive-load fieldwork, functioning as a "One-Touch Timestamping" instrument while maintaining resilience through a production-grade stack (Netlify Frontend, Google Sheets Backend).

    **Lifecycle Mapping Protocol (T0--T4).** The system logs the five critical state transitions of a gig economy mission with geospatial precision:
    * **T0 (Search):** Idle state; actively seeking offers.
    * **T1 (Acceptance):** Offer accepted; en route to pickup. *(Captures quoted upfront fare)*.
    * **T2 (Arrival):** At pickup location; waiting for passenger.
    * **T3 (In-Progress):** Mission started.
    * **T4 (Completion):** Mission finalized. *(Captures realized net fare)*.

    **Technical Stack & Evolution.** The system was engineered to maintain 100% capture fidelity through two critical iterations:
    * **Stateful Persistence (v4.0):** To prevent data loss during network intermittency, the app implements a *Stateful LocalStorage Manager* and an *Offline-First Queue System*. 
    * **Asynchronous Geospatial Enrichment:** To overcome the geographic blindness of simple timestamps, a client-side pipeline orchestrates the `navigator.geolocation` API with reverse-geocoding services, enriching every state transition with high-precision coordinates prior to persistence.

    **Output (`trip_events`):** A verified timeline of physical state transitions and realized financial outcomes ($N \\approx 350$ completed trips).
    """)



# ==========================================
# PHASE 1: ENGINE 2 (Collapsible Section)
# ==========================================
with st.expander("Engine 2: The 'Total Offer' Stream (OCR Pipeline)", expanded=False):

    st.markdown("""
    To neutralize **Survivorship Bias**, the system must capture the decision boundary—specifically the Rejected Offers (*The Negative Class*). As market infrastructure provides no native access to historical offer logs, a custom "Optical State Archival" architecture was deployed.

    The acquisition interface utilized an iOS device configured with an **Assistive Touch Macro**. This enabled a single-gesture capture protocol (The "Manual Cookie") that simultaneously acknowledged the offer cognitively and secured the raw visual data digitally. 

    To ensure statistical representativeness, three operational mandates were enforced:

    1. **Full Spectrum Capture (Zero Filters):** All system-level destination filters and product category filters (Premium/Mid-tier/X) were disabled. This ensured the captured stream represented the unfiltered "True Market" liquidity, not a curated subset.
    2. **Safety-Driven Random Sampling:** Offers occurring during high-cognitive-load maneuvers or complex passenger interactions were intentionally skipped. This data loss is classified as **Missing Completely at Random (MCAR)**, introducing no systemic bias into the profitability models.
    3. **The "Driver-First" Learning Curve:** The dataset acknowledges a specific "Warm-Up" period (Week 1) where operational cadence took precedence over data capture, resulting in a small cluster of "Ghost Offers" (Completed missions without source image artifacts). These were programmatically handled in the Engineering Phase.

    The pipeline utilizes the **Google Gemini Pro Vision API** to transform visual assets into structured data. The primary challenge involved isolating the *Foreground Signal* (the offer card) from *Background Noise* (active navigation and status bar metadata). To ensure data integrity, the system prompt enforces strict scope limitations, instructing the model to ignore metadata outside the central offer card.

    **Engine 2 Output (`offers`):** This high-fidelity dataset captures the total universe of opportunities, including the critical Negative Class ($N \\approx 4,700$ total offers).
    """)


# ==========================================
# PHASE 1: POST-SESSION PROTOCOL (Non-Collapsible)
# ==========================================
st.markdown("""
At this stage, both engines exist as separate, unlinked entities. In the subsequent engineering phase, these disparate records were unified into a SQL-queryable relational schema. 
""")

st.subheader("The Post-Session Reconciliation Protocol")

st.markdown("""
To maintain data integrity and preserve the agent's decision context, a rigorous post-session protocol was enforced immediately upon the completion of each fieldwork shift:

1. **Telemetry Consolidation (GTS):** The raw, long-format event logs from the webapp were processed into a wide-format session ledger. This involved pruning duplicate entries and cancelled events, enabling the immediate calculation of session-level KPIs such as *Net Spread* and *Accumulated Deadhead*, metrics which would become engineered features in later stages.

2. **High-Fidelity Cognitive Backtagging:** The Agent manually reviewed and tagged every rejected offer from that session to populate the multiclass target variable (`reason_primary`). Executing this task same-day was imperative to capture the specific, contextual nuance of the decision before operational memory decay occurred.
""")

st.divider()



st.info("PLACEHOLDER: RECREATE WEBAPP WITH OBFUSCATED DATA")

# ... (Keep all your existing code above the simulator)

st.divider()

# ... (Keep all your existing code above the simulator)

st.divider()

# ... (Keep all your existing code above the st.divider())

st.divider()

# ==========================================
# INTERACTIVE ARTIFACT: GTS WEBAPP SIMULATOR
# ==========================================
st.subheader("Interactive Artifact: GTS Telemetry Simulator")
st.markdown("""
This module simulates the **Engine 1** mobile experience. It demonstrates the "One-Touch" state transitions and the logic used to calculate operational KPIs in the field.
""")

import datetime
import pandas as pd
import time

# --- SESSION STATE INITIALIZATION ---
if 'sim_active' not in st.session_state:
    st.session_state.sim_active = False
if 'sim_log' not in st.session_state:
    st.session_state.sim_log = []
if 'start_time_dt' not in st.session_state:
    st.session_state.start_time_dt = None

# --- CSS: IPHONE UI + SPECIFIC COLOR MAPPING ---
st.markdown("""
<style>
    .iphone-wrapper { display: flex; justify-content: center; padding: 20px; }
    .iphone-device {
        width: 380px; background-color: #ffffff; border-radius: 40px;
        border: 12px solid #222; padding: 30px 20px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        font-family: 'Inter', sans-serif !important;
    }
    .iphone-header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    .iphone-header h4 { margin: 0; color: #888; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }

    /* High Speed Timer Styling */
    #timer-display {
        font-family: 'Courier New', monospace;
        font-size: 26px; font-weight: bold; color: #dc3545;
        text-align: center; margin: 10px 0; background: #fff5f5;
        padding: 8px; border-radius: 12px; border: 1px solid #ffc1c1;
    }

    /* Standard Button Styling */
    div.stButton > button, div[data-testid="stPopover"] > button {
        width: 100%; border-radius: 10px !important; padding: 15px !important;
        font-weight: 700 !important; font-size: 14px !important;
        text-transform: none !important; border: none !important;
        transition: all 0.2s ease;
    }

    /* EXACT COLOR MAPPING FROM HTML VERSION */
    /* T0: Looking (Blue) */
    div[data-testid="stVerticalBlock"] > div:nth-child(5) button { background-color: #007BFF !important; color: white !important; }
    /* T1: Accepted (Yellow) */
    div[data-testid="stVerticalBlock"] > div:nth-child(6) button { background-color: #FFC107 !important; color: black !important; }
    /* T2: Waiting (Orange) */
    div[data-testid="stVerticalBlock"] > div:nth-child(7) button { background-color: #FD7E14 !important; color: white !important; }
    /* T3: Started (Cyan) */
    div[data-testid="stVerticalBlock"] > div:nth-child(8) button { background-color: #17A2B8 !important; color: white !important; }
    /* T4: Completed (Green) */
    div[data-testid="stVerticalBlock"] > div:nth-child(9) button { background-color: #28A745 !important; color: white !important; }

    /* End Session Button Styling */
    button[kind="secondary"] { background-color: #dc3545 !important; color: white !important; }

    .summary-card {
        background-color: #f8f9fa; border: 1px solid #ddd;
        border-radius: 12px; padding: 15px; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def log_sim_event(status, ride_id, upfront=0.0, realized=0.0):
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_cdmx = now_utc - datetime.timedelta(hours=6) # Mexico City Mock
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
    if not st.session_state.sim_log: return None
    df = pd.DataFrame(st.session_state.sim_log).sort_values("raw_ts")
    total_up = df["upfrontFare"].sum()
    total_re = df["realizedFare"].sum()
    spread = ((total_re / total_up) - 1) * 100 if total_up > 0 else 0
    
    durs = {"Looking": 0, "Driving": 0, "Waiting": 0, "On Ride": 0}
    for i in range(len(df)-1):
        delta = df.iloc[i+1]["raw_ts"] - df.iloc[i]["raw_ts"]
        etype = df.iloc[i]["eventType"]
        if "T0" in etype: durs["Looking"] += delta
        elif "T1" in etype: durs["Driving"] += delta
        elif "T2" in etype: durs["Waiting"] += delta
        elif "T3" in etype: durs["On Ride"] += delta
    return {"up": total_up, "re": total_re, "spread": spread, "times": durs}

# --- SIMULATOR UI ---
col_l, col_m, col_r = st.columns([0.5, 2, 0.5])

with col_m:
    st.markdown('<div class="iphone-wrapper"><div class="iphone-device">', unsafe_allow_html=True)
    st.markdown('<div class="iphone-header"><h4>Geotimestamps GTS-4</h4></div>', unsafe_allow_html=True)

    # 1. SESSION CONTROL
    if not st.session_state.sim_active:
        if st.button("Start Session", type="primary", use_container_width=True):
            st.session_state.sim_active = True
            st.session_state.start_time_dt = time.time()
            st.session_state.sim_log = []
            st.rerun()
    else:
        if st.button("End Session", type="secondary", use_container_width=True):
            st.session_state.sim_active = False
            st.rerun()

    # 2. ACTIVE SESSION
    if st.session_state.sim_active:
        # High Speed JS Timer
        st.components.v1.html(f"""
            <div id="timer-display">00:00:00:000</div>
            <script>
                (function() {{
                    const start = {st.session_state.start_time_dt} * 1000;
                    const el = document.getElementById('timer-display');
                    function update() {{
                        const d = Date.now() - start;
                        const h = Math.floor(d / 3600000).toString().padStart(2, '0');
                        const m = Math.floor((d % 3600000) / 60000).toString().padStart(2, '0');
                        const s = Math.floor((d % 60000) / 1000).toString().padStart(2, '0');
                        const ms = Math.floor(d % 1000).toString().padStart(3, '0');
                        el.innerHTML = h + ":" + m + ":" + s + ":" + ms;
                        requestAnimationFrame(update);
                    }}
                    update();
                }})();
            </script>
        """, height=70)

        ride_id = st.text_input("Daily Ride ID:", value="Pienza-Aug-2025")
        
        # T0: Button
        if st.button("T0: Looking for rides"):
            log_sim_event("T0: Looking for rides", ride_id)

        # T1: Popover
        with st.popover("T1: Ride Accepted, Driving to Pickup", use_container_width=True):
            u_fare = st.number_input("Upfront Fare ($)", min_value=0.0, step=1.0)
            if st.button("Confirm T1"):
                log_sim_event("T1: Ride Accepted, Driving to Pickup", ride_id, upfront=u_fare)
                st.rerun()

        # T2: Button
        if st.button("T2: Waiting for passenger"):
            log_sim_event("T2: Waiting for passenger", ride_id)

        # T3: Button
        if st.button("T3: Ride Started"):
            log_sim_event("T3: Ride Started", ride_id)

        # T4: Popover
        with st.popover("T4: Ride completed", use_container_width=True):
            r_fare = st.number_input("Realized Fare ($)", min_value=0.0, step=1.0)
            if st.button("Confirm T4"):
                log_sim_event("T4: Ride completed", ride_id, realized=r_fare)
                st.rerun()

    # 3. POST-SESSION KPI SUMMARY
    if not st.session_state.sim_active and st.session_state.sim_log:
        stats = calculate_summary()
        if stats:
            st.markdown('<div class="summary-card">', unsafe_allow_html=True)
            st.markdown("#### Session Summary")
            st.write(f"**Total Upfront:** ${stats['up']:.2f}")
            st.write(f"**Total Realized:** ${stats['re']:.2f}")
            st.write(f"**Net Spread:** {stats['spread']:.2f}%")
            st.divider()
            for k, v in stats['times'].items():
                st.write(f"⏱ **{k}:** {time.strftime('%H:%M:%S', time.gmtime(v))}")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Clear Log"):
                st.session_state.sim_log = []
                st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

# --- LIVE TELEMETRY TABLE ---
if st.session_state.sim_log:
    st.markdown("#### Real-time Telemetry Buffer")
    df_table = pd.DataFrame(st.session_state.sim_log).drop(columns=['raw_ts'])
    st.dataframe(df_table, use_container_width=True, hide_index=True)




    # ... (Continuing from the Telemetry Buffer Table)

st.divider()

# ... (Continuing from the Telemetry Buffer Table)

st.divider()

# ==========================================
# OPERATIONAL RESILIENCE & EDGE CASE NOTES
# ==========================================
st.subheader("Operational Resilience & Edge Case Notes")

with st.expander("The Reality of Field Data Collection", expanded=True):
    st.markdown("""
    *   **Atomic Persistence (Offline-First):** Data is not "dumped" in a single batch at the end of a session. Every state transition (T0–T4) is captured as an atomic event and queued immediately for backend synchronization. This ensures that even if a session is never formally "Ended," every captured data point is preserved.

    *    Operational shifts typically conclude at **T0 (Searching)** after the final drop-off, for consistency in the final dataset, this trailing deadhead period was pruned. The final engineered record always terminates with a **T4 (Completed Ride)**.

    *   **Redundancy & Deduplication:** To minimize cognitive load during high-stress driving, the agent would "Double-Tap" a state if they were unsure if a transition had logged (especially if the app became idle). The architecture prioritizes **Capture over Cleanliness**; duplicate entries and accidental out-of-order clicks are programmatically pruned during the Post-Session Reconciliation Protocol.

    *   **Financial Ground Truth:** All fares entered in the field are treated as **"High-Confidence Drafts."** To ensure 100% financial accuracy, every entry is audited back-home against:
        1.  **Engine 2 Visual Artifacts** (Screenshots) for Upfront Quoted Fares.
        2.  **Platform Activity History** for Realized Net Fares.
                
                The edgest of cases ocurred only once that alttered the temporal sequence of events, An accepted reservation whithin 1 hour of acceptance, then accepted and completd trip, then the occurrence of the reservation. this broke the logic and had to swap some variables because they were inverted. 

    *   **Temporal Fidelity:** The system captures the natural "Idle Gaps" between T4 (Completion) and the subsequent T0 (New Search). While these seconds of "micro-deadhead" were generally ignored in final modeling, they serve as a critical anchor: if a logging mistake was made, the timestamp for **T4 (Ride n)** serves as the anchor for **T0 (Ride n)**.
    If a chained offer was accepted, after the T4 timestamp, the next state transition would be T1 (Accepted) instead of T0, The real time at which this ride was accepted was lost in this dataset, but unimportant to the analysis. However, it was captured by the OCR Engine through the screenshot.
                """)

st.caption("Simulator Version: GTS-4.0 | Phase: Converged Policy Exploitation")