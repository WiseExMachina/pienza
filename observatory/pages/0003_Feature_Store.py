import streamlit as st
import streamlit.components.v1 as components
import time
import numpy as np

st.set_page_config(layout="wide", page_title="Feature Store | Pienza", page_icon="🗄️")

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
h1 { font-size: 36px !important; font-weight: 400 !important; color: #121212; letter-spacing: -1px; }
h2 { color: #21918c; font-size: 30px !important; font-weight: 300 !important; margin-top: -10px; }
h3 { color: #21918c; font-size: 26px !important; font-weight: 400 !important; margin-top: -10px; }
.block-container { padding-top: 2rem; }
.bento-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.bento-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    border-color: #21918c;
}
.phase-badge {
    display: inline-block;
    background-color: #f0fafa;
    color: #21918c;
    border: 1px solid #21918c;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p { font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("Feature Store")
st.markdown("""
<h4 style='color: #21918c; font-weight: 400; margin-top: -10px;'>
    Canonical Schema · Bronze / Silver / Gold
</h4>
""", unsafe_allow_html=True)
st.write("")

# ─────────────────────────────────────────────
# MEDALLION TABS
# ─────────────────────────────────────────────
bronze_tab, silver_tab, gold_tab, sim_tab = st.tabs(["🥉 Bronze", "🥈 Silver", "🥇 Gold", "🎮 Simulator"])

# ═══════════════════════════════════════════════
# BRONZE: Raw Canonical Schema (Domain Dictionary)
# ═══════════════════════════════════════════════
with bronze_tab:
    st.write("")
    st.markdown("<span class='phase-badge'>Data Dictionary</span>", unsafe_allow_html=True)
    st.markdown("### Canonical Offers Schema")
    st.markdown("""
    Explore the stabilization of the dataset across its logical domains. Select a domain below to review
    the engineered features, their data types, and base operational data.
    """)
    st.write("")

    domain_tabs = st.tabs([
        "⏱️ Temporal",
        "🚗 Physics",
        "📍 Geospatial",
        "💰 Incentives",
        "🚩 Service Flags",
        "👤 Rider Profile",
        "⚖️ Decision"
    ])

    schema_data = {
        "Temporal": [
            {"id": "F01", "type": "Datetime", "name": "offer_timestamp", "desc": "Chronological timestamp of the offer dispatch."},
            {"id": "F02", "type": "Integer", "name": "time_in_session_sec", "desc": "Elapsed seconds since the agent's current session began."},
            {"id": "F03", "type": "Float", "name": "session_progress_ratio", "desc": "Normalized metric tracking progression through the active session."}
        ],
        "Physics": [
            {"id": "F04", "type": "Float", "name": "upfront_fare", "desc": "Financial baseline offered for the mission prior to adjustments."},
            {"id": "F05", "type": "Categorical", "name": "product_category", "desc": "Platform service tier (e.g., UberX, Comfort)."},
            {"id": "F06", "type": "Integer", "name": "time_to_pickup_sec", "desc": "Estimated logistical time to reach the pickup coordinate."},
            {"id": "F07", "type": "Float", "name": "dist_to_pickup_km", "desc": "Logistical distance to reach the pickup coordinate."},
            {"id": "F08", "type": "Integer", "name": "est_trip_time_sec", "desc": "Estimated duration of the actual rider trip."},
            {"id": "F09", "type": "Float", "name": "est_trip_dist_km", "desc": "Estimated distance of the actual rider trip."}
        ],
        "Geospatial": [
            {"id": "F10", "type": "String", "name": "pickup_address", "desc": "Raw localized string of the pickup location."},
            {"id": "F11", "type": "String", "name": "dropoff_address", "desc": "Raw localized string of the dropoff location."},
            {"id": "F12", "type": "GeoPoint", "name": "pickup_lat/lon", "desc": "Absolute spatial coordinates for the mission start."},
            {"id": "F13", "type": "GeoPoint", "name": "dropoff_lat/lon", "desc": "Absolute spatial coordinates for the mission end."},
            {"id": "F14", "type": "Vector (Float)", "name": "inferred_agent_vector", "desc": "Composite vector containing lat/lon, bearing, and speed_mps."},
            {"id": "F15", "type": "Categorical", "name": "interpolation_quality", "desc": "Confidence metric for imputed geospatial data."},
            {"id": "F16", "type": "Boolean", "name": "is_imputed", "desc": "Flag indicating if the coordinates were algorithmically filled."}
        ],
        "Incentives": [
            {"id": "F17", "type": "Boolean", "name": "is_surge", "desc": "Flag for active dynamic pricing."},
            {"id": "F18", "type": "Float", "name": "surge_amount", "desc": "Absolute monetary value of the dynamic pricing surge."},
            {"id": "F19", "type": "Boolean", "name": "is_turbo_plus", "desc": "Flag for strategic platform bonuses."},
            {"id": "F20", "type": "Float", "name": "turbo_plus_amount", "desc": "Absolute monetary value of the strategic bonus."},
            {"id": "F21", "type": "Boolean", "name": "is_reservation", "desc": "Flag indicating a pre-scheduled mission."},
            {"id": "F22", "type": "Float", "name": "reservation_amount", "desc": "Premium monetary value attached to the reservation."},
            {"id": "F23", "type": "Boolean", "name": "is_priority", "desc": "Flag for high-demand priority routing."},
            {"id": "F24", "type": "Float", "name": "priority_amount", "desc": "Monetary value of the priority fee."}
        ],
        "Service Flags": [
            {"id": "F25", "type": "Boolean", "name": "is_exclusive", "desc": "Client tiering flag for exclusive routing."},
            {"id": "F26", "type": "Boolean", "name": "is_vip", "desc": "Client tiering flag for VIP status accounts."},
            {"id": "F27", "type": "Boolean", "name": "is_identity_verified", "desc": "Security flag confirming rider documentation."},
            {"id": "F28", "type": "Boolean", "name": "is_long_trip", "desc": "Operational complexity flag for extended duration missions."},
            {"id": "F29", "type": "Boolean", "name": "is_multiple_destinations", "desc": "Operational complexity flag for multi-stop routing."},
            {"id": "F30", "type": "Boolean", "name": "is_teens", "desc": "Operational flag indicating a registered minor account."}
        ],
        "Rider Profile": [
            {"id": "F31", "type": "Float", "name": "rider_star_rating", "desc": "Aggregated historical rating of the account."},
            {"id": "F32", "type": "Integer", "name": "rider_trip_count", "desc": "Total historical missions completed by the account."}
        ],
        "Decision": [
            {"id": "F33", "type": "Categorical", "name": "offer_action", "desc": "The raw recorded behavioral action (Accept/Reject/Timeout)."},
            {"id": "F34", "type": "Categorical", "name": "reason_primary", "desc": "The target variable for classification models."},
            {"id": "F35", "type": "Categorical", "name": "heuristic_flag", "desc": "Categorical assignment of the strategic decision context."},
            {"id": "F36", "type": "Categorical", "name": "driver_state_at_request", "desc": "Operational state of the agent when the offer was received."},
            {"id": "F37", "type": "Categorical", "name": "outcome", "desc": "The final realized state of an accepted mission."}
        ]
    }

    for tab, (domain, features) in zip(domain_tabs, schema_data.items()):
        with tab:
            st.write("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, f in enumerate(features):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="bento-card" style="margin-bottom: 24px; min-height: 155px; padding: 20px 24px;">
                        <div style="font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                            <span style="color: #21918c;">{f['id']}</span>
                            <span style="color: #eaeaea; margin: 0 6px;">|</span>
                            <span style="color: #888;">{f['type']}</span>
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #121212; margin-bottom: 10px; border-bottom: 1px solid #f5f5f5; padding-bottom: 10px;">
                            {f['name']}
                        </div>
                        <div style="font-size: 0.8rem; color: #555; line-height: 1.5;">
                            {f['desc']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SILVER: Stateful Engineered Features (Phase 2C)
# ═══════════════════════════════════════════════
with silver_tab:
    st.write("")
    st.markdown("<span class='phase-badge'>Stateful Intelligence · Phase 2C</span>", unsafe_allow_html=True)
    st.markdown("### Canonical Stateful Features")
    st.markdown("""
    Session-dependent features engineered via a sequential state machine (`code.gs`). These capture the agent's
    operational context — fatigue, yield trajectory, and market dynamics — across five critical dimensions.
    A strict **No Look-Ahead Rule** is enforced: `_ML` features use only historical data available at decision time;
    `_EDA` features incorporate actual outcomes and are firewalled for exploratory analysis only.
    """)
    st.write("")

    silver_domain_tabs = st.tabs([
        "📡 Market Pressure",
        "🚦 Supply & Traffic",
        "🧠 Internal State",
        "💹 Base Profitability",
        "🤖 Predictive (ML)",
        "🔬 Exploratory (EDA)",
        "🧭 Strategic Context"
    ])

    silver_schema = {
        "Market Pressure": [
            {"id": "S01", "type": "Float", "name": "time_since_last_offer", "desc": "Seconds elapsed since previous request. Proxy for market silence."},
            {"id": "S02", "type": "Integer", "name": "offer_density_[10-180]sec", "desc": "Rolling counts of offers across 10, 30, 60, and 180s windows."},
            {"id": "S03", "type": "Integer", "name": "consecutive_rejects", "desc": "Stateful counter resetting on acceptance. Proxy for frustration and patience threshold."},
        ],
        "Supply & Traffic": [
            {"id": "S04", "type": "Float", "name": "traffic_index_base_120", "desc": "Normalized congestion metric (Baseline: 120s/km). Values >1.0 indicate friction."},
            {"id": "S05", "type": "Float", "name": "cycle_avg_dtp_km", "desc": "Mean Distance-to-Pickup in current cycle. High values indicate low local supply."},
            {"id": "S06", "type": "Float", "name": "cycle_std_dtp_km", "desc": "Standard deviation of DTP. Measures supply volatility across the session."},
            {"id": "S07", "type": "Float", "name": "cycle_ttp_dtp_ratio", "desc": "Ratio of Pickup Time to Pickup Distance. Localized traffic proxy."},
            {"id": "S08", "type": "Float", "name": "dispatch_lead_time_sec", "desc": "Time remaining on active trip when next offer is received (Chained Logic)."},
        ],
        "Internal State": [
            {"id": "S09", "type": "Float", "name": "total_acc_deadhead_sec", "desc": "Cumulative unpaid seconds (Search + Pickup + Waiting) in the current cycle."},
            {"id": "S10", "type": "Float", "name": "cycle_rolling_avg_spread", "desc": "Temporally-safe rolling average of the Upfront/Realized fare delta."},
            {"id": "S11", "type": "Float", "name": "cycle_cum_net_earnings", "desc": "Cumulative realized income for the session."},
        ],
        "Base Profitability": [
            {"id": "S12", "type": "Float", "name": "eph_direct", "desc": "Raw EPH (Upfront Fare / Est Trip Time). The platform's raw signal."},
            {"id": "S13", "type": "Float / Cat", "name": "eph_direct_index / label", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S14", "type": "Float", "name": "eph_operational", "desc": "True EPH adding Pickup Time. The first reality check on the platform signal."},
            {"id": "S15", "type": "Float / Cat", "name": "eph_operational_index / label", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S16", "type": "Boolean", "name": "is_operational_downgrade", "desc": "True if offer flips from Premium (Direct EPH) to Discount (Operational EPH)."},
        ],
        "Predictive (ML)": [
            {"id": "S17", "type": "Float", "name": "eph_realized_ML", "desc": "Predicted EPH adjusting for historical spread. No future leakage."},
            {"id": "S18", "type": "Float / Cat", "name": "eph_realized_index / label_ML", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S19", "type": "Boolean", "name": "is_spread_downgrade_ML", "desc": "True if spread adjustment kills North Star EPH target ($200 MXN/hr)."},
            {"id": "S20", "type": "Float", "name": "eph_complete_ML", "desc": "Holistic EPH: Predicted Fare / Total Cycle Time. The agent's true yield signal."},
            {"id": "S21", "type": "Float / Cat", "name": "eph_complete_index / label_ML", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S22", "type": "Boolean", "name": "is_total_cycle_downgrade_ML", "desc": "True if the final outcome was a downgrade vs EPH realized."},
        ],
        "Exploratory (EDA)": [
            {"id": "S23", "type": "Float", "name": "eph_realized_EDA", "desc": "Actual EPH using finalized Realized Fare. Post-facto — firewalled from ML."},
            {"id": "S24", "type": "Float / Cat", "name": "eph_realized_index / label_EDA", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S25", "type": "Boolean", "name": "is_spread_downgrade_EDA", "desc": "True if the actual platform payment lowered yield below the North Star."},
            {"id": "S26", "type": "Float", "name": "eph_complete_EDA", "desc": "Absolute Truth EPH: Actual Fare / Actual Total Time. Ground truth yield."},
            {"id": "S27", "type": "Float / Cat", "name": "eph_complete_index / label_EDA", "desc": "Normalized score and categorical label (>1.0 = Premium; else, Discount)."},
            {"id": "S28", "type": "Boolean", "name": "is_total_cycle_downgrade_EDA", "desc": "True if the final outcome was a downgrade vs EPH realized."},
        ],
        "Strategic Context": [
            {"id": "S29", "type": "Float", "name": "home_vector_alignment", "desc": "Cosine Similarity score (-1 to 1) of dropoff vector relative to Home Base."},
            {"id": "S30", "type": "Boolean", "name": "pickup / dropoff_ambiguity", "desc": "Binary flags for low-confidence geospatial coordinates."},
            {"id": "S31", "type": "Categorical", "name": "day_type / time_block", "desc": "Semantic temporal segments (e.g., Weekday, Morning, Friday)."},
        ],
    }

    for tab, (domain, features) in zip(silver_domain_tabs, silver_schema.items()):
        with tab:
            st.write("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, f in enumerate(features):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="bento-card" style="margin-bottom: 24px; min-height: 155px; padding: 20px 24px;">
                        <div style="font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                            <span style="color: #21918c;">{f['id']}</span>
                            <span style="color: #eaeaea; margin: 0 6px;">|</span>
                            <span style="color: #888;">{f['type']}</span>
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #121212; margin-bottom: 10px; border-bottom: 1px solid #f5f5f5; padding-bottom: 10px;">
                            {f['name']}
                        </div>
                        <div style="font-size: 0.8rem; color: #555; line-height: 1.5;">
                            {f['desc']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# GOLD: Volatility Suite + Spatial Index (Phase 5)
# ═══════════════════════════════════════════════
with gold_tab:
    st.write("")
    st.markdown("<span class='phase-badge'>Volatility Suite · Phase 5</span>", unsafe_allow_html=True)
    st.markdown("### Silver Palette: Final Feature Layer")
    st.markdown("""
    The causal analysis in Phase 3 identified a critical gap: the ex-ante traffic index is a poor proxy for operational risk.
    The true yield determinant is the **Prediction Error** — the stochastic delta between estimated and realized durations.
    This layer adds spatial indexing and a volatility suite engineered from a 2 min/km market baseline.
    """)
    st.write("")

    gold_domain_tabs = st.tabs([
        "📍 Spatial Index",
        "🌊 Volatility Suite"
    ])

    gold_schema = {
        "Spatial Index": [
            {"id": "G01", "type": "INTEGER", "name": "pickup_polygon_id", "desc": "Hand-crafted operational zone polygon containing the pickup coordinate."},
            {"id": "G02", "type": "TEXT", "name": "pickup_h3_hex_id", "desc": "Uber H3 hexagonal grid cell ID for the pickup location."},
            {"id": "G03", "type": "INTEGER", "name": "dropoff_polygon_id", "desc": "Hand-crafted operational zone polygon containing the dropoff coordinate."},
            {"id": "G04", "type": "TEXT", "name": "dropoff_h3_hex_id", "desc": "Uber H3 hexagonal grid cell ID for the dropoff location."},
            {"id": "G05", "type": "INTEGER", "name": "dropoff_hdbscan_id", "desc": "HDBSCAN cluster ID for the dropoff — one of 44 machine-discovered demand hubs."},
        ],
        "Volatility Suite": [
            {"id": "G06", "type": "REAL", "name": "realized_traffic_index", "desc": "Post-facto ground truth of mission friction: ratio of realized duration to quoted expectation. Reserved for mission-completion audits only."},
            {"id": "G07", "type": "REAL", "name": "hist_avg_traffic_index", "desc": "Session-level rolling average of previously realized traffic indices. Proxy for the agent's contextual memory of recent urban congestion at decision time."},
            {"id": "G08", "type": "REAL", "name": "traffic_volatility_index_ML", "desc": "Primary predictive signal: Historical Traffic Context minus the current offer's expected index. Forward-safe — no leakage."},
            {"id": "G09", "type": "REAL", "name": "traffic_volatility_index_EDA", "desc": "Absolute deviation between realized duration and quoted expectation. Completed missions only — firewalled from ML."},
        ],
    }

    for tab, (domain, features) in zip(gold_domain_tabs, gold_schema.items()):
        with tab:
            st.write("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, f in enumerate(features):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="bento-card" style="margin-bottom: 24px; min-height: 155px; padding: 20px 24px;">
                        <div style="font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                            <span style="color: #21918c;">{f['id']}</span>
                            <span style="color: #eaeaea; margin: 0 6px;">|</span>
                            <span style="color: #888;">{f['type']}</span>
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #121212; margin-bottom: 10px; border-bottom: 1px solid #f5f5f5; padding-bottom: 10px;">
                            {f['name']}
                        </div>
                        <div style="font-size: 0.8rem; color: #555; line-height: 1.5;">
                            {f['desc']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SIMULATOR: Session Playback (Inference in Motion)
# ═══════════════════════════════════════════════
with sim_tab:
    st.write("")
    st.markdown("<span class='phase-badge'>Inference in Motion</span>", unsafe_allow_html=True)
    st.markdown("### Session Playback: The Expert Cockpit")
    st.markdown("""
    To understand how **Contextual** and **Stateful** features drive behavior, we must view them in sequence.
    Average sessions contain **60–90 offers** with only **4–6 acceptances**.

    Select a session and hit **Start Timelapse** to see the agent's decision logic evolve as fatigue, traffic, and sunk costs accumulate.
    """)
    st.write("")

    # --- Controls (inline, not in sidebar) ---
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
    with ctrl_col1:
        sim_session = st.selectbox("Field Session", ["Shift_042 (Friday PM)", "Shift_089 (Rainy Monday)"])
    with ctrl_col2:
        play_speed = st.select_slider(
            "Playback Speed (seconds per offer)",
            options=[0.1, 0.5, 1.0, 2.0],
            value=0.5
        )
    with ctrl_col3:
        st.write("")
        st.write("")
        run_sim = st.button("🚀 Start Timelapse", use_container_width=True)

    st.write("")

    # --- HUD ---
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

    # --- Cockpit ---
    col_offer, col_brain = st.columns(2)
    with col_offer:
        st.subheader("📲 Naked Physics")
        st.caption("What the Platform Presents")
        naked_card = st.empty()
    with col_brain:
        st.subheader("🧠 Expert Brain")
        st.caption("Contextual & Stateful Reality")
        brain_card = st.empty()

    verdict_banner = st.empty()

    # --- Simulation Engine ---
    if run_sim:
        total_offers = 60
        accept_indices = [12, 28, 45, 58]

        for i in range(total_offers):
            progress = i / total_offers
            deadhead_accum = i * 42
            pocket_money = len([idx for idx in accept_indices if idx < i]) * 165
            current_traffic = 1.1 + (np.sin(i / 10) * 0.4)

            m_fatigue.metric("Shift Progress", f"{int(progress * 100)}%", delta=f"{i}/60")
            m_deadhead.metric("Sunk Cost (Deadhead)", f"{deadhead_accum}s", delta="Accumulating")
            m_earnings.metric("Net Earnings", f"${pocket_money} MXN")
            m_traffic.metric("Market Friction", f"{current_traffic:.2f}x",
                             delta="Gridlock" if current_traffic > 1.3 else "Fluid")

            is_premium = i % 7 == 0
            fare = np.random.randint(85, 380)

            if i in accept_indices:
                decision = "ACCEPT"
                reason = "Optimal Yield / Home Vector Fit"
                bg_color = "#1db954"
            else:
                decision = "REJECT"
                if progress < 0.3:
                    reason = "Low Profitability"
                elif current_traffic > 1.3:
                    reason = "Gridlock: Traffic Index Violation"
                elif progress > 0.8:
                    reason = "Strategic Mismatch (Non-Homecoming)"
                else:
                    reason = "Expected Value Gamble"
                bg_color = "#e91e63"

            with naked_card.container(border=True):
                st.markdown(f"### {'💎 Uber Black' if is_premium else '🚗 UberX'}")
                st.write(f"**Upfront Fare:** ${fare} MXN")
                st.write(f"**Trip Duration:** {np.random.randint(12, 45)} mins")
                st.write(f"**Distance:** {np.random.randint(4, 18)} km")

            with brain_card.container(border=True):
                st.write(f"🚦 **Traffic Index:** {current_traffic:.2f} (120s/km baseline)")
                st.write(f"🏠 **Home Alignment:** {0.1 + progress:.2f} (Anzures Vector)")
                st.write("---")
                st.write("**Active Heuristic Flags:**")
                if progress > 0.8:
                    st.warning("⚠️ `obj_end_session` ACTIVE")
                if current_traffic > 1.4:
                    st.error("🛑 `friday_gridlock` TRIGGERED")
                if i % 4 == 0:
                    st.info("📉 `deadhead_risk` DETECTED")

            verdict_banner.markdown(f"""
                <div style="background-color: {bg_color}; padding: 30px; border-radius: 15px; text-align: center; margin-top: 16px;">
                    <h1 style="color: white; font-family: Inter; font-weight: 700; margin: 0; letter-spacing: 2px;">{decision}</h1>
                    <p style="color: white; font-size: 18px; margin: 10px 0 0 0;">{reason}</p>
                </div>
            """, unsafe_allow_html=True)

            time.sleep(play_speed)

        st.balloons()
        st.success("🏁 Session Complete. 60 Offers Filtered | 4 Missions Authorized.")

    else:
        m_fatigue.metric("Shift Progress", "--")
        m_deadhead.metric("Sunk Cost", "--")
        m_earnings.metric("Net Earnings", "--")
        m_traffic.metric("Market Friction", "--")
        with naked_card.container(border=True):
            st.write("Waiting for telemetry stream...")
        with brain_card.container(border=True):
            st.write("Initializing state machine...")
