import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Acquistion and Ground Truth",
    layout="wide"
)

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

