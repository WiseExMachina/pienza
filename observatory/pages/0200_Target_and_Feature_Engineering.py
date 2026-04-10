import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Feature Factory",
    page_icon="🧠",
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

# ==========================================
# PHASE 2: FEATURE FACTORY (Non-Collapsible Intro Placeholder)
# ==========================================
st.header("Target and Feature Engineering")

st.info("""
**[CONTENT PLACEHOLDER: Introduction]** *The theoretical foundation and strategic overview for the Feature Factory phase will be inserted here. This non-collapsible section will define the transition from raw telemetry to the engineered state space before diving into the specific technical modules below.*
""")

import pandas as pd

# ==========================================
# PHASE 2: CORE ENTITY SCHEMA (Collapsible Section)
# ==========================================
with st.expander("Core Entity: The `raw_offers` Schema", expanded=False):

    st.markdown("""
    The ingestion pipeline consolidated OCR outputs into a primary staging table. The raw schema captured the unstructured state of the visual data prior to normalization.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    raw_schema_data = {
        "Column": [
            "`ocr_id`", "`image_filename`", "`time_taken`", "`ride_type`", 
            "`upfront_fare`", "`pickup_details`", "`pickup_address`", 
            "`trip_details`", "`dropoff_address`", "`rider_rating`", "`special_note`"
        ],
        "Data Type": [
            "Integer (PK)", "String", "String", "Categorical", 
            "Numeric", "String (Raw)", "String (Raw)", 
            "String (Raw)", "String (Raw)", "String (Raw)", "Text (Blob)"
        ],
        "Description": [
            "Incremental sequential identifier assigned during ingestion",
            "Source asset filename stored in the archival vault.",
            "Raw time string (HH:MM) extracted from the device status bar.",
            "Product class (e.g., *X, mid-Tier, Premium*).",
            "The nominal fare amount presented in the offer card.",
            "Combined text field containing ETA and distance to pickup.",
            "Unstructured pickup location text (street, POI).",
            "Combined text field containing estimated trip duration and distance.",
            "Unstructured destination location text.",
            "Combined text string with Passenger Rating and Trip Count.",
            "Unstructured text field capturing all incentive tags (*Surge, Turbo+*) and status flags (*Reservation, Priority*)."
        ]
    }
    
    df_raw_schema = pd.DataFrame(raw_schema_data)
    
    # Render using Pandas to Markdown for clean UI integration
    st.markdown(df_raw_schema.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Definition of the `raw_offers` schema post-ingestion.")



import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: TARGET ENGINEERING (Collapsible Section)
# ==========================================
with st.expander("Target Engineering: `reason_primary`", expanded=False):

    st.markdown("""
    The multiclass target variable, `reason_primary`, is a hierarchical filtration system formalized as the **Cognitive Cascade**. To ensure a clean signal for supervised learning, each offer is assigned a single, mutually exclusive label representing the entry-point failure across a three-tiered triage: geospatial feasibility (Tier 1), economic viability (Tier 2), and strategic alignment (Tier 3). This prevents label contamination by focusing the model on the primary decision driver.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    target_schema_data = {
        "Class Label": [
            "`dropoff_non_operational`", 
            "`dropoff_proxy`", 
            "`low_profitability`", 
            "`long_pickup_time`", 
            "`strategic_mismatch`", 
            "`expected_value_gamble`", 
            "`NULL` (Implicit)"
        ],
        "Operational Logic": [
            "Destination lies within a pre-defined zone outside the operational area.",
            "Destination is outside the primary zone but acceptable if aligned with a homecoming vector toward *Anzures*.",
            "Offer fails baseline EPH requirements relative to estimated duration.",
            "Uncompensated pickup time exceeds tolerance; threshold relaxes during extreme gridlock.",
            "High-value offer rejected due to unfavorable routing context (e.g., *Santa Fe → Polanco* during Friday's peak gridlock).",
            "Viable offer rejected based on the probabilistic expectation of a superior imminent event.",
            "Absence of objection signals an accepted offer."
        ]
    }
    
    df_target_schema = pd.DataFrame(target_schema_data)
    
    # Render using Pandas to Markdown for clean UI integration
    st.markdown(df_target_schema.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Lexicon of the Decision Target Variable (`reason_primary`).")


import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: CONTEXTUAL FEATURE EXTRACTION (Collapsible Section)
# ==========================================
with st.expander("Contextual Feature Extraction: `heuristic_flag`", expanded=False):

    st.markdown("""
    The following table defines the categorical flags engineered to capture qualitative operational risks and strategic shifts that are not detectable through raw numerical features alone. These labels provide the model with the **"Agent's perspective"** on market conditions.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    heuristic_data = {
        "Category": [
            "**Risk Mitigation**", "", "", 
            "**Strategic Intent**", "", 
            "**System/Market**", "", ""
        ],
        "Flag Label": [
            "`deadhead_risk`", "`long_ride_risk`", "`dropoff_uncertain`",
            "`obj_end_session`", "`friday_gridlock`",
            "`system_error`", "`market_anomaly`", "`protest_anomaly`"
        ],
        "Operational Logic": [
            "Short-duration offers with a high probability of immediate return to an idle search state.",
            "Trips >45 min where high traffic volatility creates risk of uncompensated time.",
            "Destinations with high geospatial entropy/ambiguity.",
            "Intent to terminate the work shift; prioritizes homecoming vector alignment over intrinsic EPH.",
            "Friday-specific regime; prioritizes egress from high-friction density sectors (*Polanco*).",
            "Physically impossible platform time-estimates (e.g., 20 min predicted time from Vistahermosa to Polanco during morning traffic).",
            "Non-standard offer physics (e.g., operational outliers near National Holidays).",
            "External socio-political shocks (marches, road closures) disrupting standard market flow."
        ]
    }
    
    df_heuristic = pd.DataFrame(heuristic_data)
    
    # Render using Pandas to Markdown
    st.markdown(df_heuristic.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Categorical Lexicon of Heuristic Flags for Model Enrichment.")


import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: BEHAVIORAL TARGETS (Collapsible Section)
# ==========================================
with st.expander("Behavioral Targets and Operational Outcomes", expanded=False):

    st.markdown("""
    To differentiate between **agent intent** and **realized performance**, the schema implements two distinct categorical dimensions: `offer_action` (Binary Intent) and `outcome` (Realized State).
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    outcome_data = {
        "Target": [
            "**Intent**", 
            "**Outcome**", "", "", "", ""
        ],
        "Class Label": [
            "`Accept / Reject`", 
            "`completed`", "`rider_canceled`", "`driver_canceled`", "`system_failure`", "`NULL`"
        ],
        "Strategic Context": [
            "Alternative binary target representing the primary decision vector.",
            "Transaction successfully finalized.",
            "External termination by passenger post-acceptance.",
            "Agent-initiated termination due to post-acceptance friction (e.g., realization of hidden traffic).",
            "Offers intended for acceptance but lost due to operational capture latency. Mapped as **ACCEPTED** for training.",
            "Implicit state for rejected offers; no operational outcome generated."
        ]
    }
    
    df_outcome = pd.DataFrame(outcome_data)
    
    # Render using Pandas to Markdown
    st.markdown(df_outcome.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Mapping of Behavioral Intent and Operational Outcome categories.")



import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: ACQUISITION ARTIFACT (Collapsible Section)
# ==========================================
with st.expander("Acquisition Artifact: The Enriched `offers` Dataset", expanded=False):

    st.markdown("""
    By the conclusion of the acquisition campaign, the raw OCR stream had been enriched with manual behavioral labels, initial geospatial coordinates, and parsed operational metrics. The following schema represents the state of the dataset prior to the deep Data Engineering phase.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    enriched_schema_data = {
        "Feature Name": [
            # OCR Section
            "**Source: OCR Extraction**", "`time_taken`", "`product_tier`", "`upfront_fare`", 
            "`special_note`", "`star_rating`", "`trip_count`", "`time_to_pickup`", 
            "`dist_to_pickup`", "`est_trip_time`", "`est_trip_dist`",
            # Cognitive Section
            "**Source: Cognitive Backtagging**", "`offer_action`", "`reason_primary`", 
            "`heuristic_flag`", "`driver_state`", "`outcome`",
            # Geospatial Section
            "**Source: Google Geocoding API**", "`pickup_lat/lon`", "`dropoff_lat/lon`"
        ],
        "Data Type": [
            "", "String", "Categorical", "Numeric", 
            "String", "Numeric", "Integer", "Numeric", 
            "Numeric", "Numeric", "Numeric",
            "", "Binary", "Categorical", 
            "Categorical", "Categorical", "Categorical",
            "", "Float", "Float"
        ],
        "Categories / Definition": [
            "", "Raw HH:MM timestamp from device.", "X, mid-Tier, Premium.", "Nominal fare value (MXN).", 
            "Unstructured text (Surge, Turbo, Priority).", "Passenger rating (1.0–5.0 scale).", "Lifetime trips completed by passenger.", "Parsed duration to pickup (seconds).", 
            "Parsed distance to pickup (km).", "Parsed estimated trip duration (seconds).", "Parsed estimated trip distance (km).",
            "", "Accept, Reject.", "dropoff_non_operational, low_profitability, long_pickup, strategic_mismatch, expected_value_gamble.", 
            "deadhead_risk, long_ride_risk, dropoff_uncertain, obj_end_session, friday_gridlock, system_error, market_anomaly, protest_anomaly.", "Idle (Open), On-Trip (Chained).", "Completed, Rider_Cancel, Driver_Cancel, System_Failure.",
            "", "Initial coordinate estimation.", "Initial coordinate estimation."
        ]
    }
    
    df_enriched = pd.DataFrame(enriched_schema_data)
    
    # Render using Pandas to Markdown
    st.markdown(df_enriched.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Final Schema State of the Acquisition Phase (N ≈ 4,700).")






import streamlit as st

# ==========================================
# PHASE 2: TEMPORAL RECOVERY (Collapsible Section)
# ==========================================
with st.expander("High-Precision Temporal Recovery & Identity", expanded=False):

    st.markdown("""
    Standard minute-level timestamps (HH:MM) proved insufficient for analyzing high-frequency market dynamics. To recover seconds-level precision, a custom Python pipeline was developed to extract internal metadata from the non-standard PNG chunks of the source assets. 
    
    This timing capability was identified during localization trials. While initially seeking GPS metadata, the discovery of second-level markers enabled a higher analytical resolution. 
    
    **Architectural Risks Addressed:**
    Two primary risks necessitated this precision:
    * **iOS Filename Recycling:** Ambiguity in native file naming conventions.
    * **System-Level Offer Repetition:** The platform often resends identical offers, creating visually congruent artifacts. As these repetitions can occur within a single minute but at distinct second intervals, standard HH:MM granularity would result in data loss through erroneous duplicate detection.
    """)

    st.divider()

    st.markdown("### Cryptographic Primary Key Generation")
    st.markdown("To ensure absolute uniqueness, a primary key (`event_id`) was generated via a SHA-256 hash of a combined event signature:")

    # Render LaTeX Equation natively in Streamlit
    st.latex(r"event\_id = \text{SHA-256}(\text{image\_content\_hash} + \text{high\_precision\_timestamp})")

    st.markdown("""
    This transformation converted the unstructured file repository into an audited relational ledger. The resulting high-fidelity temporal baseline directly unlocked the engineering of velocity-based features (e.g., *Offer Density*) required for stateful intelligence.
    """)








import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: CANONICAL OFFERS TABLE (Collapsible Section)
# ==========================================
with st.expander("The Canonical Version of the `offers` Table", expanded=False):

    st.markdown("""
    The following table represents the canonical version of `offers` prior to the ETL process into `pienza.db`. This schema serves as the unified source of truth, consolidating physical, temporal, and behavioral dimensions.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    canonical_schema_data = {
        "Logical Domain": [
            "**Identity**", 
            "**Temporal**", 
            "**Physics**", "", "",
            "**Geospatial**", "", "", "",
            "**Incentives**", "", "", "",
            "**Service Flags**", "",
            "**Rider Profile**",
            "**Decision**", "", "",
            "**Audit Layer**"
        ],
        "Engineered Columns": [
            "`offer_id`, `session_id`, `image_content_hash`",
            "`offer_timestamp`, `time_in_session_sec`, `session_progress_ratio`",
            "`upfront_fare`, `product_category`",
            "`time_to_pickup_sec`, `dist_to_pickup_km`",
            "`est_trip_time_sec`, `est_trip_dist_km`",
            "`pickup_address`, `dropoff_address`",
            "`pickup_lat/lon`, `dropoff_lat/lon`",
            "`inferred_agent_lat/lon/bearing/speed_mps`",
            "`interpolation_quality`, `is_imputed`",
            "`is_surge`, `surge_amount`",
            "`is_turbo_plus`, `turbo_plus_amount`",
            "`is_reservation`, `reservation_amount`",
            "`is_priority`, `priority_amount`",
            "`is_exclusive`, `is_vip`, `is_identity_verified`",
            "`is_long_trip`, `is_multiple_destinations`, `is_teens`",
            "`rider_star_rating`, `rider_trip_count`",
            "`offer_action`, `reason_primary` (Target Variable)",
            "`heuristic_flag`",
            "`driver_state_at_request`, `outcome`",
            "`special_note_raw`, `comment_1`, `comment_2`, `record_status`"
        ],
        "Role": [
            "Traceability",
            "Chronology",
            "Financials",
            "Logistics (Pickup)",
            "Logistics (Trip)",
            "Raw Geodata",
            "Absolute Location",
            "Agent Vector",
            "Data Integrity",
            "Dynamic Pricing",
            "Strategic Bonus",
            "Scheduling Fee",
            "Demand Fee",
            "Client Tiering",
            "Operation Complexity",
            "Risk Metrics",
            "Behavioral Data",
            "Strategic Context",
            "Operational State",
            "Forensics"
        ]
    }
    
    df_canonical = pd.DataFrame(canonical_schema_data)
    
    # Render using Pandas to Markdown
    st.markdown(df_canonical.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Canonical `offers` schema state at the conclusion of the initial engineering phase.")





import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: STATEFUL INTELLIGENCE (Collapsible Section)
# ==========================================
with st.expander("Stateful Intelligence: Session-Dependent Feature Engineering", expanded=False):

    st.markdown("""
    While physical parameters define a potential transaction, they fail to capture the broader **operational context** governing an agent’s decision boundary. Risk tolerance and profitability thresholds are dynamic functions of session history—fatigue, recent yield, and market volatility. 

    This logic is implemented via a **sequential state machine** (Google Apps Script) that maintains a persistent "memory" across five critical dimensions:
    """)

    # ------------------------------------------
    # 5-Dimension Summary (Using Columns for Scannability)
    # ------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 1. Temporal Integrity
        Strict adherence to a **No Look-Ahead Rule**. Features like `cycle_rolling_avg_spread` only incorporate missions completed *prior* to the current timestamp to prevent data leakage.

        ### 2. Uncompensated Load
        Aggregation of `total_accumulated_deadhead_sec`. This sums T0 (Idle), T1 (Pickup), and T2 (Waiting) to quantify the "sunk cost" pressure on the decision boundary.
        
        ### 3. Market Physics
        High-velocity signals including `offer_density` and a continuous **Traffic Index** (normalized against a 120s/km baseline) to measure real-time congestion friction.
        """)

    with col2:
        st.markdown("""
        ### 4. North Star Convergence
        A baseline of **$200 MXN realized EPH**. Normalized indices (`eph_*_index`) quantify how offers deviate from this target, modeling how the agent forces long-term mean convergence.

        ### 5. The Profitability Funnel
        Quantifying the **Information Asymmetry** gap across four levels of granularity:
        * **Direct:** Upfront Fare / Est. Trip Time.
        * **Operational:** Adjusted for Time to Pickup.
        * **Realized:** Realized Fare / Est. Trip Time.
        * **Complete:** Realized Fare / (Deadhead + Est. Trip Time).
        """)

    st.divider()

    # ------------------------------------------
    # Technical Note / Guardrails
    # ------------------------------------------
    st.warning("""
    **Technical Note: Feature Fireballing**
    * **`_ML` Suffix:** Features engineered using only historical averages available at the moment of decision.
    * **`_EDA` Suffix:** Features incorporating actual outcomes (realized performance), firewalled for exploratory analysis only to ensure zero data leakage.
    """)

import streamlit as st
import pandas as pd

# ==========================================
# PHASE 2: CANONICAL STATEFUL FEATURES (Collapsible Section)
# ==========================================
with st.expander("The Canonical Stateful Features", expanded=False):

    st.markdown("""
    These features were engineered within the `engineered_features` table to provide the model with a stateful representation of the market dynamics and the agent's internal progress throughout a session.
    """)

    # ------------------------------------------
    # Dictionary-to-Pandas Table Rendering
    # ------------------------------------------
    stateful_features_data = {
        "Dimension": [
            "**Market Pressure**", "", "",
            "**Supply & Traffic**", "", "", "", "",
            "**Internal State**", "", "",
            "**Base Profitability**", "", "", "", "",
            "**Predictive (ML)**", "", "", "", "", "",
            "**Exploratory (EDA)**", "", "", "", "", "",
            "**Strategic Context**", "", ""
        ],
        "Feature Name": [
            "`time_since_last_offer`", "`offer_density_[10-180]sec`", "`consecutive_rejects`",
            "`traffic_index_base_120`", "`cycle_avg_dtp_km`", "`cycle_std_dtp_km`", "`cycle_ttp_dtp_ratio`", "`dispatch_lead_time_sec`",
            "`total_acc_deadhead_sec`", "`cycle_rolling_avg_spread`", "`cycle_cum_net_earnings`",
            "`eph_direct`", "`eph_direct_index/label`", "`eph_operational`", "`eph_operational_index/label`", "`is_operational_downgrade`",
            "`eph_realized_ML`", "`eph_realized_index/label_ML`", "`is_spread_downgrade_ML`", "`eph_complete_ML`", "`eph_complete_index/label_ML`", "`is_total_cycle_downgrade_ML`",
            "`eph_realized_EDA`", "`eph_realized_index/label_EDA`", "`is_spread_downgrade_EDA`", "`eph_complete_EDA`", "`eph_complete_index/label_EDA`", "`is_total_cycle_downgrade_EDA`",
            "`home_vector_alignment`", "`pickup/dropoff_ambiguity`", "`day_type/time_block`"
        ],
        "Engineering Logic & Strategic Proxy": [
            "Seconds elapsed since previous request. Proxy for market 'silence.'",
            "Rolling counts of offers across 10, 30, 60, 180s windows.",
            "Stateful counter resetting on acceptance. Proxy for frustration/patience.",
            "Normalized congestion metric (Base: 120s/km). Values >1.0 indicate friction.",
            "Mean Distance-to-Pickup in current cycle. High values = Low local supply.",
            "Standard deviation of DTP. Measures supply volatility.",
            "Ratio of Pickup Time to Pickup Distance. Localized traffic proxy.",
            "Time remaining on active trip when next offer is received (Chained Logic).",
            "Cumulative unpaid seconds (Search + Pickup + Waiting) in current cycle.",
            "Temporally-safe rolling average of the Upfront/Realized fare delta.",
            "Cumulative realized income for the session.",
            "Raw EPH (Upfront Fare / Est Trip Time).",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "True EPH adding Pickup Time. The first reality check.",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "**Bool:** True if offer flips from Premium (Direct) to Discount (Op).",
            "Predicted EPH adjusting for historical Spread (No future leakage).",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "**Bool:** True if Spread adjustment kills North Star EPH.",
            "**Holistic EPH:** (Predicted Fare / Total Cycle Time). The Agent's true yield.",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "**Bool:** True if final outcome was a downgrade vs EPH realized.",
            "Actual EPH using finalized Realized Fare (Post-facto).",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "**Bool:** True if the actual platform payment lowered yield.",
            "**Absolute Truth EPH:** Actual Fare / Actual Total Time.",
            "Normalized Score and Categorical Label (>1.0 = Premium; else, Discount).",
            "**Bool:** True if final outcome was a downgrade vs EPH realized.",
            "Cosine Similarity score (-1 to 1) relative to Home Base.",
            "Binary flags for low-confidence geospatial coordinates.",
            "Semantic temporal segments (Weekday, Morning, Friday)."
        ]
    }
    
    df_stateful = pd.DataFrame(stateful_features_data)
    
    # Render using Pandas to Markdown
    st.markdown(df_stateful.to_markdown(index=False))
    
    # Elegant Table Caption
    st.caption("Comprehensive stateful feature inventory engineered for the model.")



st.info("PLACEHOLDER: RECREATE SESSION WITH OBFUSCATED DATA")



import streamlit as st
import time
import pandas as pd
import numpy as np

# ==========================================
# PHASE 3: THE EXPERT COCKPIT (Session Playback)
# ==========================================
st.divider()
st.header("🎮 Session Playback: Inference in Motion")
st.markdown("""
To understand how **Contextual** and **Stateful** features drive behavior, we must view them in sequence. 
Average sessions contain **60–90 offers** with only **4–6 acceptances**. 

**Select a session and hit 'Start Timelapse' to see the Agent's decision logic evolve as fatigue, traffic, and sunk costs accumulate.**
""")

# --- Sidebar Controls for the Simulation ---
with st.sidebar:
    st.markdown("---")
    st.subheader("🕹️ Simulation Controls")
    sim_session = st.selectbox("Select Field Session", ["Shift_042 (Friday PM)", "Shift_089 (Rainy Monday)"])
    play_speed = st.select_slider("Playback Speed", options=[0.1, 0.5, 1.0, 2.0], value=0.5, help="Seconds per offer")
    run_sim = st.button("🚀 START TIMELAPSE", use_container_width=True)

# --- The HUD (Heads-Up Display) ---
# We use st.empty() so we can update these values in a loop
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    m_fatigue = st.empty()
with col_m2:
    m_deadhead = st.empty()
with col_m3:
    m_earnings = st.empty()
with col_m4:
    m_traffic = st.empty()

st.markdown("---")

# --- The Cockpit View ---
col_offer, col_brain = st.columns([1, 1])

with col_offer:
    st.subheader("📲 The 'Naked Physics'")
    st.caption("What the Platform Presents")
    naked_card = st.empty()

with col_brain:
    st.subheader("🧠 The 'Expert Brain'")
    st.caption("Contextual & Stateful Reality")
    brain_card = st.empty()

# --- The Big Verdict Banner ---
verdict_banner = st.empty()

# ==========================================
# SIMULATION ENGINE (Logic)
# ==========================================
if run_sim:
    # Creating a mock session based on your parameters (60 offers, 4-6 acceptances)
    total_offers = 60
    accept_indices = [12, 28, 45, 58]
    
    for i in range(total_offers):
        # 1. Update State Variables
        progress = (i / total_offers)
        deadhead_accum = i * 42 # seconds
        pocket_money = len([idx for idx in accept_indices if idx < i]) * 165
        current_traffic = 1.1 + (np.sin(i/10) * 0.4) # Varying traffic
        
        # 2. Update HUD Metrics
        m_fatigue.metric("Shift Progress (Fatigue)", f"{int(progress*100)}%", delta=f"{i}/60")
        m_deadhead.metric("Sunk Cost (Deadhead)", f"{deadhead_accum}s", delta="Accumulating")
        m_earnings.metric("Net Earnings", f"${pocket_money} MXN")
        m_traffic.metric("Market Friction", f"{current_traffic:.2}x", delta="Gridlock" if current_traffic > 1.3 else "Fluid")

        # 3. Generate Random Offer Physics
        is_premium = i % 7 == 0
        fare = np.random.randint(85, 380)
        dest_zone = np.random.randint(1, 42)
        
        # 4. Determine Decision Logic
        if i in accept_indices:
            decision = "ACCEPT"
            reason = "Optimal Yield / Home Vector Fit"
            bg_color = "#1db954" # Success Green
        else:
            decision = "REJECT"
            # Switch reasons based on session progress
            if progress < 0.3: reason = "Low Profitability"
            elif current_traffic > 1.3: reason = "Gridlock: Traffic Index Violation"
            elif progress > 0.8: reason = "Strategic Mismatch (Non-Homecoming)"
            else: reason = "Expected Value Gamble"
            bg_color = "#e91e63" # Reject Pink/Red

        # 5. Render "Naked Physics" Card
        with naked_card.container(border=True):
            st.markdown(f"### {'💎' if is_premium else '🚗'} { 'Uber Black' if is_premium else 'UberX'}")
            st.write(f"**Upfront Fare:** ${fare} MXN")
            st.write(f"**Trip Duration:** {np.random.randint(12, 45)} mins")
            st.write(f"**Distance:** {np.random.randint(4, 18)} km")

        # 6. Render "Expert Brain" Card
        with brain_card.container(border=True):
            st.write(f"🚦 **Traffic Index:** {current_traffic:.2} (120s/km baseline)")
            st.write(f"🏠 **Home Alignment:** {0.1 + progress:.2} (Anzures Vector)")
            st.write("---")
            st.write("**Active Heuristic Flags:**")
            if progress > 0.8: st.warning("⚠️ `obj_end_session` ACTIVE")
            if current_traffic > 1.4: st.error("🛑 `friday_gridlock` TRIGGERED")
            if i % 4 == 0: st.info("📉 `deadhead_risk` DETECTED")

        # 7. Render Verdict Banner
        verdict_banner.markdown(f"""
            <div style="background-color: {bg_color}; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid white;">
                <h1 style="color: white; font-family: 'Inter'; font-weight: 700; margin: 0; letter-spacing: 2px;">{decision}</h1>
                <p style="color: white; font-family: 'Crimson Pro'; font-size: 20px; margin: 10px 0 0 0;">{reason}</p>
            </div>
        """, unsafe_allow_html=True)

        # Control Playback Timing
        time.sleep(play_speed)

    st.balloons()
    st.success("🏁 Session Complete. Summary: 60 Offers Filtered | 4 Missions Authorized.")

else:
    # State before simulation starts
    m_fatigue.metric("Shift Progress", "--")
    m_deadhead.metric("Sunk Cost", "--")
    m_earnings.metric("Net Earnings", "--")
    m_traffic.metric("Market Friction", "--")
    
    with naked_card.container(border=True):
        st.write("Waiting for telemetry stream...")
    with brain_card.container(border=True):
        st.write("Initializing state machine...")