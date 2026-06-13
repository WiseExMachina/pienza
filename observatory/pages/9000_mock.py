import streamlit as st

# --- CANONICAL CONFIGURATION ---
st.set_page_config(
    layout="wide",
    page_title="Causal Inference | Project Pienza",
    page_icon="🔍"
)

# --- SIDEBAR ---
def build_sidebar():
    with st.sidebar:
        st.markdown("Proyect Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0000_mock.py", label="mock")
        st.page_link("pages/0002_found2.py", label="Found2")
        st.page_link("pages/0001_Foundations_and_Architecture.py", label="Foundations & Architecture")
        st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox")
        st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping & The Efficient Frontier")
        st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
        st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
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

# --- GLOBAL STYLES (matching main.py exactly) ---
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
        color: #21918c;
        font-size: 30px !important;
        font-weight: 300 !important;
        margin-top: -10px;
    }
    h3 {
        color: #21918c;
        font-size: 26px !important;
        font-weight: 400 !important;
        margin-top: -10px;
    }
    h4 {
        color: #21918c;
        font-weight: 100 !important;
        margin-top: -10px;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        font-size: 12px !important;
    }

    .block-container { padding-top: 2rem; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* --- BENTO CARD SYSTEM --- */
    .bento-card {
        background: #ffffff;
        border: 1px solid #eaeaea;
        border-radius: 12px;
        padding: 24px 28px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        height: 100%;
    }
    .bento-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
        border-color: #21918c;
    }
    .bento-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #21918c;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 16px;
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
    }

    /* --- DATA TABLE INSIDE BENTO --- */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.83rem;
        color: #333;
    }
    .data-table th {
        font-weight: 700;
        color: #121212;
        text-align: left;
        padding: 7px 10px 7px 0;
        border-bottom: 2px solid #eaeaea;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .data-table th.right { text-align: right; }
    .data-table td {
        padding: 7px 10px 7px 0;
        border-bottom: 1px solid #f5f5f5;
        color: #444;
        vertical-align: middle;
    }
    .data-table td.right { text-align: right; font-variant-numeric: tabular-nums; }
    .data-table tr:last-child td { border-bottom: none; }

    /* highlight total row */
    .data-table tr.total-row td {
        font-weight: 700;
        color: #121212;
        border-top: 2px solid #eaeaea;
        padding-top: 10px;
    }
    /* highlight accepted row */
    .data-table tr.accent-row td {
        font-weight: 700;
        color: #21918c;
    }

    /* Divider inside a double table card */
    .table-divider {
        border: none;
        border-top: 1px dashed #eaeaea;
        margin: 18px 0;
    }

    /* Key insight box */
    .insight-box {
        background: #f4fafa;
        border-left: 4px solid #21918c;
        border-radius: 0 8px 8px 0;
        padding: 16px 20px;
        margin-top: 28px;
        font-size: 0.85rem;
        color: #444;
        line-height: 1.6;
    }
    .insight-box strong { color: #121212; }

    /* Phase badge */
    .phase-badge {
        display: inline-block;
        background: #21918c;
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 12px;
    }

    /* Placeholder tab content */
    .placeholder-box {
        background: #f8f9fa;
        border: 2px dashed #ddd;
        border-radius: 12px;
        padding: 60px 40px;
        text-align: center;
        color: #aaa;
    }
    .placeholder-box .ph-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .placeholder-box .ph-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #ccc;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# --- PAGE HEADER ---
st.title("Phase 3: Exploratory Analysis & Causal Inference")
st.markdown("""
    <h4 style='color: #21918c; font-weight: 400; margin-top: -10px;'>
        Diagnostic Audit · Structural Imbalance · Causal Modeling
    </h4>
""", unsafe_allow_html=True)

st.write("")

st.markdown("""
Following the relational stabilization of the dataset in Phase 2, the analytical focus pivots toward inference 
and causal modeling. This phase is structured as a **Diagnostic Audit** to ensure the dataset is a precise 
digital twin of the agent's operational reality.
""")

st.write("")

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "📊  Data Census",
    "📈  Feature Store",
    "🔬  Placeholder"
])

# ═══════════════════════════════════════════════
# TAB 1: OPERATIONAL BASELINE — DATA CENSUS
# ═══════════════════════════════════════════════
with tab1:

    st.write("")
    st.markdown("<span class='phase-badge'>Operational Baseline</span>", unsafe_allow_html=True)
    st.markdown("### Data Census")
    st.markdown("""
    The primary objective of the univariate audit was to establish the numerical context of the 
    **N ≈ 4,765 offers**, defining the inherent market frequency and structural biases before feature analysis.
    """)

    st.write("")

    # --- PURE PYTHON SLIDER STATE ---
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 0

    total_slides = 4

    # Navigation Callback Functions
    def next_slide():
        st.session_state.current_slide = (st.session_state.current_slide + 1) % total_slides

    def prev_slide():
        st.session_state.current_slide = (st.session_state.current_slide - 1) % total_slides

    # Carousel Controls
    col_prev, col_content, col_next = st.columns([1, 10, 1])

    with col_prev:
        st.write("<br><br><br>", unsafe_allow_html=True)  # Center vertical alignment roughly
        st.button("←", on_click=prev_slide, key="btn_prev", use_container_width=True)

    with col_next:
        st.write("<br><br><br>", unsafe_allow_html=True)
        st.button("→", on_click=next_slide, key="btn_next", use_container_width=True)

    with col_content:
        # Slide 1: Decision Action Census
        if st.session_state.current_slide == 0:
            st.markdown("""
            <div class="bento-card">
              <div class="bento-label">01 &nbsp;·&nbsp; Decision Action Census</div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Decision Action</th>
                    <th class="right">Count</th>
                    <th class="right">Rate (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Reject</td>
                    <td class="right">4,419</td>
                    <td class="right">92.74</td>
                  </tr>
                  <tr class="accent-row">
                    <td>Accepted</td>
                    <td class="right">346</td>
                    <td class="right">7.26</td>
                  </tr>
                </tbody>
              </table>
              <div class="c-card-caption" style="font-size: 0.72rem; color: #aaa; margin-top: 18px; font-style: italic;">Total offers N ≈ 4,765 · Table 10</div>
            </div>
            """, unsafe_allow_html=True)

        # Slide 2: Product Tier Distribution
        elif st.session_state.current_slide == 1:
            st.markdown("""
            <div class="bento-card">
              <div class="bento-label">02 &nbsp;·&nbsp; Product Tier Distribution</div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Product Tier</th>
                    <th class="right">Rate (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="accent-row"><td>UberX</td><td class="right">75.93</td></tr>
                  <tr><td>Comfort</td><td class="right">17.17</td></tr>
                  <tr><td>Business_Comfort</td><td class="right">3.69</td></tr>
                  <tr><td>Envíos_Uber</td><td class="right">1.49</td></tr>
                  <tr><td>Black</td><td class="right">0.82</td></tr>
                  <tr><td>Uber_Planet</td><td class="right">0.80</td></tr>
                  <tr><td>Uber_Pet</td><td class="right">0.10</td></tr>
                </tbody>
              </table>
              <div class="c-card-caption" style="font-size: 0.72rem; color: #aaa; margin-top: 18px; font-style: italic;">Market share by platform product · Table 10</div>
            </div>
            """, unsafe_allow_html=True)

        # Slide 3: Primary Target Variable
        elif st.session_state.current_slide == 2:
            st.markdown("""
            <div class="bento-card">
              <div class="bento-label">03 &nbsp;·&nbsp; Primary Target Variable — Distribution</div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Primary Target Label</th>
                    <th class="right">Count</th>
                    <th class="right">Rate (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>dropoff_non_operational</td><td class="right">2,366</td><td class="right">49.65</td></tr>
                  <tr><td>low_profitability</td><td class="right">838</td><td class="right">17.59</td></tr>
                  <tr><td>long_pickup_time</td><td class="right">366</td><td class="right">7.68</td></tr>
                  <tr class="accent-row"><td><strong>ACCEPTED (Implicit/NaN)</strong></td><td class="right">346</td><td class="right">7.26</td></tr>
                  <tr><td>expected_value_gamble</td><td class="right">330</td><td class="right">6.93</td></tr>
                  <tr><td>dropoff_strategic_mismatch</td><td class="right">275</td><td class="right">5.77</td></tr>
                  <tr><td>dropoff_proxy</td><td class="right">239</td><td class="right">5.02</td></tr>
                  <tr><td>system_logic_failure</td><td class="right">5</td><td class="right">0.10</td></tr>
                  <tr class="total-row">
                    <td><strong>Total Observations</strong></td>
                    <td class="right"><strong>4,765</strong></td>
                    <td class="right"><strong>100.00</strong></td>
                  </tr>
                </tbody>
              </table>
              <div class="c-card-caption" style="font-size: 0.72rem; color: #aaa; margin-top: 18px; font-style: italic;">Figure 3a: Structural imbalance of the decision target</div>
            </div>
            """, unsafe_allow_html=True)

        # Slide 4: Mission Outcomes
        elif st.session_state.current_slide == 3:
            st.markdown("""
            <div class="bento-card">
              <div class="bento-label">04 &nbsp;·&nbsp; Mission Outcomes — Accepted Rides</div>
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Mission Outcome</th>
                    <th class="right">Count</th>
                    <th class="right">Rate (%)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="accent-row"><td>Completed</td><td class="right">250</td><td class="right">72.0</td></tr>
                  <tr><td>System Failure</td><td class="right">43</td><td class="right">12.4</td></tr>
                  <tr><td>Rider Canceled</td><td class="right">24</td><td class="right">8.1</td></tr>
                  <tr><td>Driver Canceled</td><td class="right">26</td><td class="right">7.5</td></tr>
                  <tr class="total-row">
                    <td><strong>Total Accepted Missions</strong></td>
                    <td class="right"><strong>347</strong></td>
                    <td class="right"><strong>100.0%</strong></td>
                  </tr>
                </tbody>
              </table>
              <div class="c-card-caption" style="font-size: 0.72rem; color: #aaa; margin-top: 18px; font-style: italic;">Figure 3b: Realized outcome of accepted missions</div>
            </div>
            """, unsafe_allow_html=True)

    # Progress Indicator Layout
    st.write("")
    col_space1, col_indicators, col_space2 = st.columns([4, 4, 4])
    with col_indicators:
        # Display crisp progress metrics instead of fragile CSS dots
        st.metric(label="", value=f"Slide {st.session_state.current_slide + 1} of {total_slides}")

    # --- KEY INSIGHT ---
    st.markdown("""
    <div class="insight-box">
        <strong>Key Insight:</strong> The census confirms a severe structural imbalance in the target variable, 
        where nearly 50% of all events are dedicated to filtering non-operational offers. This necessity justifies 
        the subsequent development of a <strong>Hierarchical Classification</strong> model, explicitly designed to 
        manage this class imbalance. Model validation will strictly utilize 
        <strong>Stratified K-Fold Cross-Validation</strong> to ensure all classes are proportionally represented 
        in each training fold.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# TAB 2: FEATURE STORE (12 Bento Cards)
# ═══════════════════════════════════════════════
with tab2:
    st.write("")
    st.markdown("<span class='phase-badge'>Data Dictionary</span>", unsafe_allow_html=True)
    st.markdown("### Feature Store Directory")
    st.markdown("""
    A curated registry of operational, temporal, and spatial features feeding the hierarchical classification models. 
    Below is a live snapshot of the primary engineered variables mapped to current pipeline distributions.
    """)
    st.write("")

    # Mock Data for the 12 features
    features = [
        {"id": "F01", "name": "driver_acc_rate_7d", "val": "84.2%", "desc": "Rolling 7-day acceptance"},
        {"id": "F02", "name": "surge_mult_live", "val": "1.4x", "desc": "Real-time pricing multiplier"},
        {"id": "F03", "name": "route_complexity", "val": "0.76", "desc": "Graph-based routing difficulty"},
        {"id": "F04", "name": "hist_profit_margin", "val": "12.4%", "desc": "Historical operational margin"},
        {"id": "F05", "name": "rider_cancel_prob", "val": "0.08", "desc": "XGB predicted cancel risk"},
        {"id": "F06", "name": "traffic_delay_delta", "val": "+4.2m", "desc": "Deviation from expected ETA"},
        {"id": "F07", "name": "pickup_eta_var", "val": "1.2m", "desc": "Variance in dispatch distance"},
        {"id": "F08", "name": "weather_severity", "val": "Low", "desc": "Aggregated climate index"},
        {"id": "F09", "name": "event_demand_spike", "val": "False", "desc": "Proximity to active venues"},
        {"id": "F10", "name": "comp_price_ratio", "val": "0.98", "desc": "Market rate competitiveness"},
        {"id": "F11", "name": "user_ltv_decile", "val": "8", "desc": "Rider lifetime value rank"},
        {"id": "F12", "name": "supply_demand_idx", "val": "1.15", "desc": "Local hex-cluster ratio"}
    ]

    # Generate a 3x4 grid using Streamlit columns
    for i in range(0, len(features), 4):
        cols = st.columns(4)
        for j in range(4):
            with cols[j]:
                f = features[i+j]
                # We inline margin-bottom here to ensure spacing between rows
                st.markdown(f"""
                <div class="bento-card" style="margin-bottom: 24px;">
                    <div class="bento-label">{f['id']} &nbsp;·&nbsp; {f['name']}</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #121212; letter-spacing: -0.5px;">{f['val']}</div>
                    <div style="font-size: 0.75rem; color: #888; margin-top: 10px; line-height: 1.4;">{f['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 3: SCHEMA DICTIONARY (Logical Domains)
# ═══════════════════════════════════════════════
with tab3:
    st.write("")
    st.markdown("<span class='phase-badge'>Data Dictionary</span>", unsafe_allow_html=True)
    st.markdown("### Canonical Offers Schema")
    st.markdown("""
    Explore the stabilization of the dataset across its logical domains. Select a domain below to review 
    the engineered features, their data types, and base operational data.
    """)
    st.write("")

    # --- DOMAIN TABS ---
    domain_tabs = st.tabs([
        "⏱️ Temporal", 
        "🚗 Physics", 
        "📍 Geospatial", 
        "💰 Incentives", 
        "🚩 Service Flags", 
        "👤 Rider Profile", 
        "⚖️ Decision"
    ])

    # --- SCHEMA DATA DICTIONARY ---
    # Organized with continuous F## IDs and explicitly defined data types
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

    # --- DYNAMIC RENDERING LOOP ---
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

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "Lozano Wise, B. (2026). Project Pienza. Independent Research Initiative."
    "</div>",
    unsafe_allow_html=True
)