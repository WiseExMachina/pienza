import streamlit as st
from components.styles import GLOBAL_CSS
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
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
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

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Feature Store")
st.markdown("<p style='color:#555;font-size:0.9rem;line-height:1.7'>Raw OCR output flows through three successive enrichment layers — each adding structure, context, and predictive signal — until it becomes the feature vector consumed by the classification models.</p>", unsafe_allow_html=True)

st.markdown("""
<style>
.stepper-wrap { margin-top: 32px; }
.step-row    { display: flex; gap: 0; align-items: stretch; margin-bottom: 0; }
.step-spine  { display: flex; flex-direction: column; align-items: center; width: 44px; flex-shrink: 0; }
.step-circle { width: 30px; height: 30px; border-radius: 50%;
               color: #fff; font-size: 12px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 1; }
.step-line   { width: 2px; background: rgba(150,150,150,0.2); flex: 1; min-height: 16px; }
.step-body   { flex: 1; padding: 0 0 48px 12px; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 2px; padding-top: 6px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.6; margin-bottom: 4px; }

/* shared chips */
.cat-chip { display: inline-block; font-size: 0.65rem; font-weight: 600;
            padding: 2px 7px; border-radius: 3px; margin: 2px 3px 2px 0;
            background: #f4f4f5; color: #52525b; border: 1px solid #d4d4d8; }
.chip-wrap { display: inline-block; position: relative; }
.chip-wrap .cat-chip { cursor: help; border-bottom: 1px dotted #21918c; }
.chip-tip  { visibility: hidden; opacity: 0; width: 260px;
             background: #fff; color: #555; font-size: 0.76rem; line-height: 1.5;
             border: 1px solid #21918c; border-radius: 8px; padding: 9px 13px;
             position: absolute; bottom: 140%; left: 50%; transform: translateX(-50%);
             box-shadow: 0 4px 14px rgba(0,0,0,0.10); transition: opacity 0.2s ease;
             z-index: 9999; pointer-events: none; }
.chip-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
                   transform: translateX(-50%); border: 6px solid transparent;
                   border-top-color: #21918c; }
.chip-wrap:hover .chip-tip { visibility: visible; opacity: 1; }
.feat-count { font-size: 0.72rem; color: #aaa; font-weight: 600; margin-left: 10px; }

/* ── Profitability Funnel cascade ── */
.funnel-wrap  { width: 100%; margin-top: 8px; display: flex; flex-direction: column; gap: 0; }
.funnel-intro { font-size: 0.77rem; color: #444; line-height: 1.55; padding: 10px 14px;
                background: #f5f5f5; border: 1px solid #e5e5e5; border-radius: 7px;
                margin-bottom: 10px; }
.funnel-tier  { background: #fff; border: 1px solid #eaeaea; border-radius: 8px; padding: 12px 16px; }
.funnel-tier-final { }
.funnel-tier-label  { font-size: 0.73rem; font-weight: 700; text-transform: uppercase;
                      letter-spacing: 0.8px; color: #21918c; margin-bottom: 2px; }
.funnel-tier-formula { font-size: 0.75rem; color: #1a1a1a; font-family: 'Courier New', monospace; margin-bottom: 8px; }
.funnel-row   { display: flex; align-items: flex-start; gap: 8px; padding: 5px 0;
                border-bottom: 1px solid #f5f5f5; }
.funnel-row:last-child { border-bottom: none; }
.funnel-id    { color: #21918c; font-weight: 700; font-family: 'Courier New', monospace;
                font-size: 0.67rem; width: 34px; flex-shrink: 0; padding-top: 2px; }
.funnel-main  { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.funnel-name-line { display: flex; align-items: center; gap: 8px; }
.funnel-name  { color: #1a1a1a; font-weight: 600; font-size: 0.83rem; }
.funnel-type  { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                color: #94a3b8; background: #f1f5f9; padding: 1px 5px; border-radius: 3px; }
.funnel-desc  { font-size: 0.73rem; color: #666; line-height: 1.4; }
.funnel-trans { display: flex; align-items: center; gap: 10px; padding: 5px 0 5px 14px; }
.funnel-trans-label { font-size: 0.71rem; font-weight: 600; color: #555;
                      background: #f8f8f8; border: 1px solid #e5e5e5;
                      border-radius: 4px; padding: 2px 8px; }
.funnel-arrow { font-size: 0.80rem; color: #21918c; }

/* layer transition arrows */
.step-connector { display: flex; align-items: center; gap: 0; margin: 16px 0; }
.step-conn-spine { width: 44px; flex-shrink: 0; display: flex; flex-direction: column; align-items: center; gap: 0; }
.step-conn-line  { width: 2px; height: 20px; background: rgba(150,150,150,0.2); }
.step-conn-arrow { font-size: 0.7rem; color: #21918c; line-height: 1; }

/* ── Style A (Bronze): 2-line rows, mono ID badge ── */
.ta-wrap { width: 100%; margin-top: 4px; }
.ta-row  { display: flex; gap: 16px; align-items: flex-start;
           padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.ta-row:last-child { border-bottom: none; }
.ta-id   { font-family: 'Courier New', monospace; font-size: 0.65rem; font-weight: 700;
           color: #21918c; background: #f0fdf9; border: 1px solid #99f6e4;
           border-radius: 4px; padding: 2px 6px; white-space: nowrap; flex-shrink: 0; }
.ta-main { flex: 1; }
.ta-top  { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.ta-name { font-size: 0.82rem; font-weight: 600; color: #1a1a1a; }
.ta-badge { font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.4px; padding: 1px 6px; border-radius: 4px;
            background: #f1f5f9; color: #64748b; }
.ta-desc { font-size: 0.75rem; color: #888; line-height: 1.5; }

/* ── Style B (Silver): left-accent card rows ── */
.tb-wrap { width: 100%; margin-top: 4px; display: flex; flex-direction: column; gap: 4px; }
.tb-card { background: #fff; border-left: 3px solid #21918c; border-radius: 0 6px 6px 0;
           padding: 6px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
           transition: box-shadow 0.2s, transform 0.2s; }
.tb-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.07); transform: translateX(2px); }
.tb-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.tb-id   { font-family: 'Courier New', monospace; font-size: 0.6rem; font-weight: 700;
           color: #94a3b8; }
.tb-badge { font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.4px; padding: 1px 5px; border-radius: 4px;
            background: #f1f5f9; color: #64748b; }
.tb-name { font-size: 0.8rem; font-weight: 700; color: #1a1a1a; margin-bottom: 2px; }
.tb-desc { font-size: 0.72rem; color: #777; line-height: 1.45; }
.tb-warn-wrap { display: inline-block; position: relative; margin-left: 7px; vertical-align: middle; }
.tb-star { display: inline-block; font-size: 0.58rem; font-weight: 700;
           background: #21918c; color: #fff; border-radius: 3px;
           padding: 1px 7px; margin-left: 8px; vertical-align: middle; }
.tb-warn-badge { display: inline-flex; align-items: center; justify-content: center;
                 width: 16px; height: 16px; border-radius: 50%;
                 background: #fef3c7; border: 1px solid #f59e0b;
                 color: #b45309; font-size: 0.6rem; font-weight: 800;
                 cursor: help; line-height: 1; }
.tb-warn-tip { visibility: hidden; opacity: 0; width: 280px;
               background: #fffbeb; color: #78350f; font-size: 0.74rem; line-height: 1.5;
               border: 1px solid #f59e0b; border-radius: 8px; padding: 9px 13px;
               position: absolute; bottom: 140%; left: 50%; transform: translateX(-50%);
               box-shadow: 0 4px 14px rgba(0,0,0,0.10); transition: opacity 0.2s ease;
               z-index: 9999; pointer-events: none; }
.tb-warn-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
                      transform: translateX(-50%); border: 6px solid transparent;
                      border-top-color: #f59e0b; }
.tb-warn-wrap:hover .tb-warn-tip { visibility: visible; opacity: 1; }

/* ── Style C (Gold): zebra + teal ID column ── */
.tc-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-top: 4px; }
.tc-table th { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: 0.6px; color: #aaa; padding: 0 12px 6px 0;
               border-bottom: 2px solid #eee; }
.tc-table th:first-child { padding-left: 10px; }
.tc-table tr:nth-child(even) td { background: #fafafa; }
.tc-table tr:nth-child(odd)  td { background: #ffffff; }
.tc-table td { padding: 8px 12px 8px 0; vertical-align: top; color: #444;
               border-bottom: 1px solid #f0f0f0; }
.tc-id   { color: #21918c !important; font-family: 'Courier New', monospace;
           font-weight: 700; font-size: 0.7rem; background: #f0fdf9 !important;
           padding-left: 10px !important; width: 50px; }
.tc-name { font-weight: 600; color: #1a1a1a !important; width: 200px; }
.tc-type { color: #21918c; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }

/* domain pills — st.pills styling */
[data-testid="stPills"] { margin-bottom: 6px; }
[data-testid="stElementContainer"]:has([data-testid="stPills"]) { margin-top: -1.8rem !important; }
[data-testid="stPills"] > label { display: none; }
[data-testid="stPills"] [role="option"] {
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 3px 12px !important;
    border-radius: 20px !important;
    border: 1px solid #21918c !important;
    background: #f0fafa !important;
    color: #21918c !important;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stPills"] [role="option"]:hover {
    background: #e0f5f5 !important;
}
[data-testid="stPills"] [role="option"][aria-selected="true"] {
    background: #21918c !important;
    color: #ffffff !important;
}
</style>
<div class="stepper-wrap">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEATURE DATA
# ─────────────────────────────────────────────

bronze_schema = {
    "⏱️ Temporal": [
        {"id": "F01", "type": "Datetime",  "name": "offer_timestamp",       "desc": "Chronological timestamp of the offer dispatch."},
        {"id": "F02", "type": "Integer",   "name": "time_in_session_sec",   "desc": "Elapsed seconds since the agent's current session began."},
        {"id": "F03", "type": "Float",     "name": "session_progress_ratio","desc": "Normalized metric tracking progression through the active session."},
    ],
    "🚗 Physics": [
        {"id": "F04", "type": "Float",      "name": "upfront_fare",         "desc": "Financial baseline offered for the mission prior to adjustments."},
        {"id": "F05", "type": "Categorical","name": "product_category",     "categories": ["x", "comfort", "business_comfort", "black", "planet", "pet", "envíos"]},
        {"id": "F06", "type": "Integer",   "name": "time_to_pickup_sec",    "desc": "Estimated logistical time to reach the pickup coordinate."},
        {"id": "F07", "type": "Float",     "name": "dist_to_pickup_km",     "desc": "Logistical distance to reach the pickup coordinate."},
        {"id": "F08", "type": "Integer",   "name": "est_trip_time_sec",     "desc": "Estimated duration of the actual rider trip."},
        {"id": "F09", "type": "Float",     "name": "est_trip_dist_km",      "desc": "Estimated distance of the actual rider trip."},
    ],
    "📍 Geospatial": [
        {"id": "F10", "type": "String",   "name": "pickup_address",  "desc": "Raw localized string of the pickup location."},
        {"id": "F11", "type": "String",   "name": "dropoff_address", "desc": "Raw localized string of the dropoff location."},
        {"id": "F12", "type": "GeoPoint", "name": "pickup_lat/lon",  "desc": "Absolute spatial coordinates for the mission start."},
        {"id": "F13", "type": "GeoPoint", "name": "dropoff_lat/lon", "desc": "Absolute spatial coordinates for the mission end."},
    ],
    "💰 Incentives": [
        {"id": "F14", "type": "Boolean", "name": "is_surge",            "desc": "Flag for active dynamic pricing."},
        {"id": "F15", "type": "Float",   "name": "surge_amount",        "desc": "Absolute monetary value of the surge."},
        {"id": "F16", "type": "Boolean", "name": "is_turbo_plus",       "desc": "Flag for strategic platform bonuses."},
        {"id": "F17", "type": "Float",   "name": "turbo_plus_amount",   "desc": "Absolute monetary value of the bonus."},
        {"id": "F18", "type": "Boolean", "name": "is_reservation",      "desc": "Flag: pre-scheduled mission."},
        {"id": "F19", "type": "Float",   "name": "reservation_amount",  "desc": "Premium monetary value of the reservation."},
        {"id": "F20", "type": "Boolean", "name": "is_priority",         "desc": "Flag for high-demand priority routing."},
        {"id": "F21", "type": "Float",   "name": "priority_amount",     "desc": "Monetary value of the priority fee."},
    ],
    "🚩 Service Flags": [
        {"id": "F22", "type": "Boolean", "name": "is_exclusive",             "desc": "Client tiering flag for exclusive routing."},
        {"id": "F23", "type": "Boolean", "name": "is_vip",                   "desc": "Client tiering flag for VIP status accounts."},
        {"id": "F24", "type": "Boolean", "name": "is_identity_verified",     "desc": "Security flag confirming rider documentation."},
        {"id": "F25", "type": "Boolean", "name": "is_long_trip",             "desc": "Complexity flag for extended duration missions."},
        {"id": "F26", "type": "Boolean", "name": "is_multiple_destinations", "desc": "Complexity flag for multi-stop routing."},
        {"id": "F27", "type": "Boolean", "name": "is_teens",                 "desc": "Flag: registered minor account."},
    ],
    "👤 Rider Profile": [
        {"id": "F28", "type": "Float",   "name": "rider_star_rating", "desc": "Aggregated historical rating of the account."},
        {"id": "F29", "type": "Integer", "name": "rider_trip_count",  "desc": "Total historical missions completed by the account."},
    ],
    "⚖️ Decision": [
        {"id": "F30", "type": "Categorical", "name": "offer_action",              "categories": ["Accepted", "Reject"],
         "tips": {"Accepted": "The <strong>ACCEPTED</strong> class captures intent, not just completion. It includes rides where the offer was accepted but the mission later timed out or was cancelled before completion."}},
        {"id": "F31", "type": "Categorical", "name": "reason_primary", "star": True,
         "categories": ["dropoff_non_operational", "dropoff_proxy", "low_profitability", "long_pickup_time", "strategic_mismatch", "expected_value_gamble", "NULL"],
         "tips": {
             "dropoff_non_operational": "Destination lies within a pre-defined zone outside the operational area.",
             "dropoff_proxy":           "Destination is outside the primary zone but acceptable if aligned with a homecoming vector toward <em>Anzures</em>.",
             "low_profitability":       "Offer fails baseline EPH requirements relative to estimated duration.",
             "long_pickup_time":        "Uncompensated pickup time exceeds tolerance; threshold relaxes during extreme gridlock.",
             "strategic_mismatch":      "High-value offer rejected due to unfavorable routing context (e.g., <em>Santa Fe → Polanco</em> during Friday peak gridlock).",
             "expected_value_gamble":   "Viable offer rejected based on the probabilistic expectation of a superior imminent event.",
             "NULL":                    "Absence of objection — signals an accepted offer. No rejection reason is assigned.",
         }},
        {"id": "F32", "type": "Categorical", "name": "heuristic_flag",
         "warning": "During an ablation study, these flags were determined to be a proxy for the target labels — and therefore a form of <strong>data leakage</strong>. They were dropped from the final model.",
         "categories": ["deadhead_risk", "long_ride_risk", "dropoff_uncertain", "obj_end_session", "friday_gridlock", "system_error", "market_anomaly", "protest_anomaly"],
         "tips": {
             "deadhead_risk":    "Short-duration offers with a high probability of immediate return to an idle search state.",
             "long_ride_risk":   "Trips &gt;45 min where high traffic volatility creates risk of uncompensated time.",
             "dropoff_uncertain":"Destinations with high geospatial entropy/ambiguity.",
             "obj_end_session":  "Intent to terminate the work shift; prioritizes homecoming vector alignment over intrinsic EPH.",
             "friday_gridlock":  "Friday-specific regime; prioritizes egress from high-friction density sectors (<em>Polanco</em>).",
             "system_error":     "Physically impossible platform time-estimates (e.g., 20 min predicted time from Vistahermosa to Polanco during morning traffic).",
             "market_anomaly":   "Non-standard offer physics (e.g., operational outliers near National Holidays).",
             "protest_anomaly":  "External socio-political shocks (marches, road closures) disrupting standard market flow.",
         }},
        {"id": "F33", "type": "Categorical", "name": "driver_state_at_request",
         "categories": ["idle", "on_trip"],
         "tips": {
             "idle":    "<strong>Open offer.</strong> Agent received the request while in an idle search state. Acceptance threshold is governed purely by offer economics.",
             "on_trip": "<strong>Chained offer.</strong> Agent received the request while already on an active mission. A primary driver of the acceptance threshold — the agent evaluates the incoming offer against the residual value of the current trip.",
         }},
        {"id": "F34", "type": "Categorical", "name": "outcome",
         "categories": ["completed", "rider_canceled", "driver_canceled", "system_failure", "NULL"],
         "tips": {
             "completed":      "Transaction successfully finalized.",
             "rider_canceled": "External termination by passenger post-acceptance.",
             "driver_canceled":"Agent-initiated termination due to post-acceptance friction.",
             "system_failure": "Offers intended for acceptance but lost due to operational capture latency. Strategically mapped as <strong>ACCEPTED</strong> for model training to reflect the agent's true policy.",
             "NULL":           "Implicit state for rejected offers — no operational outcome generated.",
         }},
    ],
}

silver_schema = {
    "📡 Market Pressure": [
        {"id": "S01", "type": "Float",   "name": "time_since_last_offer",    "desc": "Seconds elapsed since previous request. Proxy for market silence."},
        {"id": "S02–S05", "type": "Integer", "name": "offer_density_[10-180]sec","desc": "Rolling counts of offers across 10, 30, 60, and 180s windows."},
        {"id": "S06", "type": "Integer", "name": "consecutive_rejects",      "desc": "Stateful counter resetting on acceptance. Proxy for patience threshold."},
    ],
    "🚦 Supply & Traffic": [
        {"id": "S07", "type": "Float", "name": "traffic_index_base_120",  "desc": "(Est Trip Time ÷ Est Trip Dist) ÷ 120. Baseline 120 s/km = 5 km in 10 min under ideal conditions. Index = 1.0 means no friction; &gt;1.0 means slower than baseline (congestion)."},
        {"id": "S08", "type": "Float", "name": "cycle_avg_dtp_km",        "desc": "Mean Distance-to-Pickup in current cycle. High = low local supply."},
        {"id": "S09", "type": "Float", "name": "cycle_std_dtp_km",        "desc": "Standard deviation of Distance-to-Piickup. Measures supply volatility across the session."},
        {"id": "S10", "type": "Float", "name": "cycle_ttp_dtp_ratio",     "desc": "Ratio of Pickup Time to Pickup Distance. Localized traffic proxy."},
        {"id": "S11", "type": "Float", "name": "dispatch_lead_time_sec",  "desc": "Time remaining on active trip when next offer is received (chained logic)."},
    ],
    "🧠 Internal State": [
        {"id": "S12", "type": "Float", "name": "total_acc_deadhead_sec",     "desc": "Cumulative unpaid seconds (Search + Pickup + Waiting) in current cycle."},
        {"id": "S13", "type": "Float", "name": "cycle_rolling_avg_spread",   "desc": "Temporally-safe rolling average of the Upfront/Realized fare delta."},
        {"id": "S14", "type": "Float", "name": "cycle_cum_net_earnings",     "desc": "Cumulative realized income for the session."},
    ],
    "💹 Profitability Funnel": [
        {"id": "S15", "type": "Float",        "name": "eph_direct",                    "desc": "Raw EPH (Upfront Fare / Est Trip Time). The platform's raw signal."},
        {"id": "S16", "type": "Float / Cat",  "name": "eph_direct_index / label",      "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S17", "type": "Float",        "name": "eph_operational",               "desc": "True EPH adding Pickup Time. First reality check on the platform signal."},
        {"id": "S18", "type": "Float / Cat",  "name": "eph_operational_index / label", "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S19", "type": "Boolean",      "name": "is_operational_downgrade",      "desc": "True if offer flips from Premium (Direct EPH) to Discount (Operational EPH)."},
        {"id": "S20", "type": "Float",       "name": "eph_realized_ML",               "desc": "Predicted EPH adjusting for historical spread. No future leakage."},
        {"id": "S21", "type": "Float / Cat", "name": "eph_realized_index / label_ML", "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S22", "type": "Boolean",     "name": "is_spread_downgrade_ML",        "desc": "True if spread adjustment kills North Star EPH target ($200 MXN/hr)."},
        {"id": "S23", "type": "Float",       "name": "eph_complete_ML",               "desc": "Holistic EPH: Predicted Fare / Total Cycle Time. True yield signal."},
        {"id": "S24", "type": "Float / Cat", "name": "eph_complete_index / label_ML", "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S25", "type": "Boolean",     "name": "is_total_cycle_downgrade_ML",   "desc": "True if final outcome was a downgrade vs EPH realized."},
        {"id": "S26", "type": "Float",       "name": "eph_realized_EDA",               "desc": "Actual EPH using finalized Realized Fare. Post-facto — firewalled from ML."},
        {"id": "S27", "type": "Float / Cat", "name": "eph_realized_index / label_EDA", "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S28", "type": "Boolean",     "name": "is_spread_downgrade_EDA",        "desc": "True if actual payment lowered yield below the North Star."},
        {"id": "S29", "type": "Float",       "name": "eph_complete_EDA",               "desc": "Absolute Truth EPH: Actual Fare / Actual Total Time. Ground truth yield."},
        {"id": "S30", "type": "Float / Cat", "name": "eph_complete_index / label_EDA", "desc": "Normalized score.", "categories": ["Premium", "Discount"]},
        {"id": "S31", "type": "Boolean",     "name": "is_total_cycle_downgrade_EDA",   "desc": "True if final outcome was a downgrade vs EPH realized."},
    ],
    "🧭 Context": [
        {"id": "S32", "type": "Float",       "name": "home_vector_alignment",    "desc": "Cosine Similarity (-1 to 1) of dropoff vector relative to Home Base."},
        {"id": "S33–S34", "type": "Boolean",     "name": "pickup/dropoff_ambiguity", "desc": "Binary flags for low-confidence geospatial coordinates. One per endpoint."},
        {"id": "S35", "type": "Int64",       "name": "hour_of_day",       "desc": "Hour of the offer timestamp (5–22). Consecutive integer representing active operating hours."},
        {"id": "S36", "type": "Categorical", "name": "day_type",         "categories": ["morning", "afternoon", "evening", "night"]},
        {"id": "S37", "type": "Categorical", "name": "time_of_day_block", "categories": ["weekday", "friday", "weekend"]},
    ],
}

gold_schema = {
    "📍 Spatial Index": [
        {"id": "G01", "type": "Integer", "name": "pickup_polygon_id",    "desc": "Hand-crafted operational zone polygon containing the pickup coordinate."},
        {"id": "G02", "type": "Text",    "name": "pickup_h3_hex_id",     "desc": "Uber H3 hexagonal grid cell ID (Res 9) for the pickup location."},
        {"id": "G03", "type": "Integer", "name": "dropoff_polygon_id",   "desc": "Hand-crafted operational zone polygon containing the dropoff coordinate."},
        {"id": "G04", "type": "Text",    "name": "dropoff_h3_hex_id",    "desc": "Uber H3 hexagonal grid cell ID (Res 9) for the dropoff location."},
        {"id": "G05", "type": "Integer", "name": "dropoff_hdbscan_id",   "desc": "HDBSCAN cluster ID — one of 44 machine-discovered demand hubs."},
    ],
    "🌊 Volatility Suite": [
        {"id": "G06", "type": "Float", "name": "realized_traffic_index",       "desc": "(Realized Trip Time ÷ Est Trip Dist) ÷ 120. Computed post-facto and only for completed missions — reflects what actually happened on the road, not the platform's estimate. Serves as the anchor for all subsequent rolling features in this suite."},
        {"id": "G07", "type": "Float", "name": "historical_rolling_avg_traffic_index", "desc": "Session-level rolling average of realized_traffic_index across all completed missions prior to the current offer."},
        {"id": "G08", "type": "Float", "name": "traffic_volatility_index",     "desc": "The difference between the platform's expected traffic (the \"promise\") and the agent's recent historical traffic performance (historical_rolling_avg_traffic_index). Quantifies the predictive error of the algorithm at the moment an offer is presented."},
    ],
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _feature_count(schema):
    return sum(len(v) for v in schema.values())

def _content(f):
    cats = f.get("categories")
    if cats:
        tips = f.get("tips", {})
        out = ""
        for c in cats:
            if c in tips:
                out += f"<span class='chip-wrap'><span class='cat-chip'>{c}</span><span class='chip-tip'>{tips[c]}</span></span>"
            else:
                out += f"<span class='cat-chip'>{c}</span>"
        return out
    return f.get("desc", "")

def _render_table_b(features):
    rows = ""
    for f in features:
        warn = f.get("warning", "")
        warn_html = f"""<span class='tb-warn-wrap'>
            <span class='tb-warn-badge'>!</span>
            <span class='tb-warn-tip'>{warn}</span>
        </span>""" if warn else ""
        star_html = "<span class='tb-star'>★ Target Feature</span>" if f.get("star") else ""
        rows += f"""<div class='tb-card'>
            <div class='tb-meta'><span class='tb-id'>{f['id']}</span><span class='tb-badge'>{f['type']}</span></div>
            <div class='tb-name'>{f['name']}{warn_html}{star_html}</div>
            <div class='tb-desc'>{_content(f)}</div>
        </div>"""
    return f"<div class='tb-wrap'>{rows}</div>"

def _render_funnel(features):
    def _row(fid, name, type_label, desc):
        return f"""<div class='funnel-row'>
            <span class='funnel-id'>{fid}</span>
            <div class='funnel-main'>
                <div class='funnel-name-line'><span class='funnel-name'>{name}</span><span class='funnel-type'>{type_label}</span></div>
                <div class='funnel-desc'>{desc}</div>
            </div>
        </div>"""

    def _trans(label):
        return f"<div class='funnel-trans'><span class='funnel-trans-label'>{label}</span><span class='funnel-arrow'>↓</span></div>"

    intro = """<div class='funnel-intro'>
        Each offer is audited across four successive EPH checkpoints — Earnings Per Hour —
        each adding a layer of operational cost to the denominator. The reference target is
        <strong>$200 MXN/hr</strong>: the agent's North Star. This funnel quantifies the
        <em>Information Asymmetry gap</em> where high-nominal offers may resolve as low-yield operations.
    </div>"""

    t1 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 1 · Direct EPH</div>
      <div class='funnel-tier-formula'>Upfront Fare ÷ Est Trip Time</div>
      {_row('S15','eph_direct','Float','Platform raw signal — the quoted fare divided by estimated trip time.')}
      {_row('S16','eph_direct_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('S16','eph_direct_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t2 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 2 · Operational EPH</div>
      <div class='funnel-tier-formula'>Upfront Fare ÷ (Est Time + Pickup Time)</div>
      {_row('S17','eph_operational','Float','First reality check — adds uncompensated pickup time to the cost denominator.')}
      {_row('S18','eph_operational_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('S18','eph_operational_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t3 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 3 · Realized EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Est Trip Time</div>
      {_row('S20','eph_realized','Float',"Rolling feature — corrects the quoted fare using the historical spread observed across all rides completed prior to this offer. Updates only after a ride is fully completed, never mid-trip, ensuring zero leakage. Captures the agent's recent financial performance as a behavioral signal.")}
      {_row('S21','eph_realized_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('S21','eph_realized_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t4 = f"""<div class='funnel-tier funnel-tier-final'>
      <div class='funnel-tier-label'>Tier 4 · Complete EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Total Cycle Time  (Est Trip + Pickup + Deadhead Looking for Rides + Deadhead Waiting for Passenger)</div>
      {_row('S23','eph_complete','Float','Same rolling logic as Tier 3 — updates only after ride completion, no leakage — but the denominator now carries the full accumulated deadhead cost of the cycle, making this the most conservative and complete yield signal available at decision time.')}
      {_row('S24','eph_complete_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('S24','eph_complete_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    return f"""<div class='funnel-wrap'>
      {intro}
      {t1}
      {_trans('+ Pickup Time')}
      {t2}
      {_trans('+ Spread Correction  (Quoted → Realized Fare)')}
      {t3}
      {_trans('+ Full Cycle Cost  (Pickup + Deadhead Looking for Rides + Deadhead Waiting for Passenger)')}
      {t4}
    </div>"""

def _render_connector():
    st.markdown("""
    <div class='step-connector'>
      <div class='step-conn-spine'>
        <div class='step-conn-line'></div>
        <div class='step-conn-arrow'>▼</div>
        <div class='step-conn-line'></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def _render_step(circle_color, label, count, why, schema, radio_key, table_fn, domain_renderers=None):
    st.markdown(f"""
    <div class='step-row'>
      <div class='step-spine'>
        <div class='step-circle' style='background:{circle_color}'>{label[0]}</div>
        <div class='step-line'></div>
      </div>
      <div class='step-body'>
        <div class='step-label' style='color:{circle_color}'>{label} <span class='feat-count'>· {count} features</span></div>
        <div class='step-why'>{why}</div>
    """, unsafe_allow_html=True)

    import re
    domains = list(schema.keys())
    labels = [re.sub(r'^[^\w]+\s*', '', d).strip() for d in domains]
    label_to_domain = dict(zip(labels, domains))
    selected_label = st.pills("", labels, default=labels[0], key=radio_key, label_visibility="collapsed")
    selected = label_to_domain[selected_label or labels[0]]
    renderer = (domain_renderers or {}).get(selected, table_fn)
    st.markdown(renderer(schema[selected]), unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
pipeline_tab, sim_tab = st.tabs(["🗂️ Feature Pipeline", "🎮 Simulator"])

with pipeline_tab:
    _render_step(
        circle_color="#cd7f32",
        label="Bronze · Raw Canonical Schema",
        count=_feature_count(bronze_schema),
        why="Direct output of the OCR pipeline: offer physics, geospatial coordinates, incentive flags, rider profile, and the decision label. No derivations — the contract between raw data and the engineering layer.",
        schema=bronze_schema,
        radio_key="bronze_domain",
        table_fn=_render_table_b,
    )

    _render_connector()

    _render_step(
        circle_color="#94a3b8",
        label="Silver · Stateful Engineered Features",
        count=37,
        why="Session-dependent features computed by a sequential state machine. Captures market pressure, agent fatigue, yield trajectory, and operational EPH variants. Strict no-look-ahead rule: _ML features use only data available at decision time; _EDA features are firewalled.",
        schema=silver_schema,
        radio_key="silver_domain",
        table_fn=_render_table_b,
        domain_renderers={"💹 Profitability Funnel": _render_funnel},
    )

    _render_connector()

    _render_step(
        circle_color="#b8860b",
        label="Gold · Spatial + Volatility",
        count=_feature_count(gold_schema),
        why="Causal analysis in Phase 3 revealed the ex-ante traffic index is a poor proxy for operational risk. This layer adds H3 spatial indexing and a volatility suite derived from the 2 min/km market baseline — the final predictive signal layer.",
        schema=gold_schema,
        radio_key="gold_domain",
        table_fn=_render_table_b,
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='background:#FFFF00;border:3px solid #FFD700;padding:12px 18px;margin-top:32px;font-size:0.85rem;font-weight:700;color:#000;'>⚠️ PENDING: reduce gap between step description and domain pills — Streamlit internal element container spacing not overridable via CSS in v1.58. FIX ME BEFORE SHIPPING.</div>", unsafe_allow_html=True)

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

    if run_sim:
        import numpy as np
        import time
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

