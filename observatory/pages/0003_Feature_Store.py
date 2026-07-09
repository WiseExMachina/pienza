import streamlit as st
from components.styles import GLOBAL_CSS
import streamlit.components.v1 as components
import time
import numpy as np
import pandas as pd
import re
from utils.bq_client import fetch_data_from_bq
from config import FAVICON
from pathlib import Path

st.set_page_config(layout="wide", page_title="Feature Store | Pienza", page_icon=FAVICON)

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
            if st.button("📄 Download 91-Page Report (PDF)", key="pdf_prep_btn", use_container_width=True):
                pdf_data = (Path(__file__).resolve().parent.parent / "assets" / "Pienza_Papers.pdf").read_bytes()
                st.download_button("⬇️ Save PDF", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf", key="pdf_dl_btn")
        except Exception:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")
        if st.button("🧹 Flush Cache", key="flush_cache_btn", use_container_width=True, help="Clears st.cache_data/st.cache_resource and forces all cached data/assets to reload, without restarting the process."):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

build_sidebar()

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Page-specific overrides (kept empty on purpose — matches the vertical
# rhythm of 0001/0002's own style block so the title sits at the same
# height across pages; this extra st.markdown() call is what supplies
# Streamlit's default inter-widget gap before the H1)
st.markdown("<style></style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Feature Store")
st.markdown("<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>Bronze → Silver → Gold — Raw Signal to Predictive Feature</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>Raw OCR output flows through three successive enrichment layers — each adding structure, context, and predictive signal — until it becomes the feature vector consumed by the classification models.</p>", unsafe_allow_html=True)

st.markdown("""
<style>
.stepper-wrap { margin-top: 15px; }
/* Shift the Feature Pipeline stepper block left ~50px and add breathing
   room below the tab bar. Scoped via st.container(key="pipeline-content")
   -> stable st-key-pipeline-content class, not a generic tabpanel selector:
   [role="tabpanel"]:first-of-type never matched (both panels are `div`s
   preceded by other sibling `div`s, e.g. the tablist, so neither panel is
   ever the actual first-of-type `div`), which silently dropped the shift
   entirely. The earlier plain [role="tabpanel"] selector (no :first-of-type)
   matched BOTH panels, dragging Session Playback out of alignment with the
   tab bar - that's why this needs to be scoped to Feature Pipeline only.
   transform (not margin-left) so the box keeps its original width - a
   negative margin-left only moves the left edge, making the box ~50px
   wider than its parent and overflowing 2-column content off-screen. */
div[class*="st-key-pipeline-content"] { transform: translateX(-50px); margin-top: 32px !important; }
/* Steps are wrapped in st.container(key="step-...") so the spine line is a
   single ::before pseudo-element spanning the container's real rendered
   height (title + why + pills + table). Streamlit renders each st.markdown/
   st.pills call as a separate sibling element with a ~16px gap between them
   (not literally nested inside an unclosed <div>), so a flex-stretched
   .step-line inside one markdown call only ever covered the "why" text and
   left the rest of the card's height with no line at all - hence the
   visible break. The ::before line overshoots -16px past the container's
   own bottom edge to bridge that inter-element gap into the connector
   below, which mirrors the trick on both its top and bottom. */
div[class*="st-key-step-"] { position: relative; padding-bottom: 40px; }
div[class*="st-key-step-"]::before {
    content: ""; position: absolute; left: 21px; top: 15px; bottom: -16px;
    width: 2px; background: rgba(150,150,150,0.2); z-index: 0;
}
.step-circle { width: 30px; height: 30px; border-radius: 50%;
               position: absolute; top: 0; left: 7px;
               color: #fff; font-size: 12px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; z-index: 1; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 2px; padding-top: 6px;
               padding-left: 56px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.6; margin-bottom: 4px;
               padding-left: 56px; }

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
.funnel-wrap  { width: calc(100% - 56px); margin-top: 8px; margin-left: 56px; display: flex; flex-direction: column; gap: 0; }
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
.tb-wrap { width: calc(100% - 56px); margin-top: 4px; margin-left: 56px; display: flex; flex-direction: column; gap: 4px; }
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
/* Indent pills to align with the step title/why text (56px = spine width
   44px + step-body's 12px left padding), instead of sitting flush left
   under the spine line. Targets the st-key-*_domain class Streamlit
   attaches via key="..._domain" on all three steppers (bronze/silver/gold)
   - not :has(), which was confirmed unreliable in this Streamlit version
   (see project_tech_debt.md). */
div[class*="st-key-"][class*="_domain"] {
    margin-left: 56px !important;
    margin-top: 14px !important;
}
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

/* Session Playback: teal-accented nav buttons (Back/Next/Restart), matching
   the rest of the site's custom button look instead of Streamlit default
   grey-border buttons. Targeted via key= class, not element type, so it
   only affects these three. */
div[class*="st-key-pb_back_btn"] button,
div[class*="st-key-pb_next_btn"] button,
div[class*="st-key-pb_restart_btn"] button {
    border: 1.5px solid #21918c !important;
    color: #21918c !important;
    background: #ffffff !important;
    font-weight: 600 !important;
}
div[class*="st-key-pb_back_btn"] button:hover,
div[class*="st-key-pb_next_btn"] button:hover,
div[class*="st-key-pb_restart_btn"] button:hover {
    background: rgba(33,145,140,0.08) !important;
    border-color: #1a7576 !important;
    color: #1a7576 !important;
}
div[class*="st-key-pb_back_btn"] button:disabled {
    border-color: #d4d4d8 !important;
    color: #aaa !important;
}

/* Session Playback: style the session selectbox like a card instead of
   Streamlit's default flat grey control. */
div[class*="st-key-pb_sess_select"] [data-baseweb="select"] > div {
    border: 1px solid #eaeaea !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
div[class*="st-key-pb_sess_select"] [data-baseweb="select"] > div:hover {
    border-color: #21918c !important;
}

/* Session Playback: wrap State Machine Context's stat grid + EPH funnel in
   one outer card matching Platform Offer's card exactly (border/radius/
   padding/background), so the two columns read as a matched pair of bento
   cards instead of one boxed card next to a loose stack of smaller ones. */
div[class*="st-key-sm-card"] {
    border: 1px solid #eaeaea !important;
    border-radius: 10px !important;
    padding: 16px !important;
    background: #ffffff !important;
    min-height: 450px !important;
    box-sizing: border-box !important;
}

/* Session Playback: wrap the whole per-offer display (meta line, both
   columns, Decision) in a "control center" panel - same grey as the
   sidebar (#ECECEE) - so the white data cards read as instrument
   readouts against a console background. */
div[class*="st-key-mission-control"] {
    background: #ECECEE !important;
    border: 1px solid #21918c !important;
    border-radius: 14px !important;
    padding: 28px !important;
    margin-top: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
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
        {"id": "F35", "type": "Float",   "name": "time_since_last_offer",    "desc": "Seconds elapsed since previous request. Proxy for market silence."},
        {"id": "F36–F39", "type": "Integer", "name": "offer_density_[10-180]sec","desc": "Rolling counts of offers across 10, 30, 60, and 180s windows."},
        {"id": "F40", "type": "Integer", "name": "consecutive_rejects",      "desc": "Stateful counter resetting on acceptance. Proxy for patience threshold."},
    ],
    "🚦 Supply & Traffic": [
        {"id": "F41", "type": "Float", "name": "traffic_index_base_120",  "desc": "(Est Trip Time ÷ Est Trip Dist) ÷ 120. Baseline 120 s/km = 5 km in 10 min under ideal conditions. Index = 1.0 means no friction; &gt;1.0 means slower than baseline (congestion)."},
        {"id": "F42", "type": "Float", "name": "cycle_avg_dtp_km",        "desc": "Mean Distance-to-Pickup in current cycle. High = low local supply."},
        {"id": "F43", "type": "Float", "name": "cycle_std_dtp_km",        "desc": "Standard deviation of Distance-to-Pickup. Measures supply volatility across the session."},
        {"id": "F44", "type": "Float", "name": "cycle_ttp_dtp_ratio",     "desc": "Ratio of Pickup Time to Pickup Distance. Localized traffic proxy."},
        {"id": "F45", "type": "Float", "name": "dispatch_lead_time_sec",  "desc": "Time remaining on active trip when next offer is received (chained logic)."},
    ],
    "🧠 Internal State": [
        {"id": "F46", "type": "Float", "name": "total_acc_deadhead_sec",     "desc": "Cumulative unpaid seconds (Search + Pickup + Waiting) in current cycle."},
        {"id": "F47", "type": "Float", "name": "cycle_rolling_avg_spread",   "desc": "Temporally-safe rolling average of the Upfront/Realized fare delta."},
        {"id": "F48", "type": "Float", "name": "cycle_cum_net_earnings",     "desc": "Cumulative realized income for the session."},
    ],
    "💹 Profitability Funnel": [
        {"id": "F49", "type": "Float",       "name": "eph_direct",              "desc": "Raw EPH (Upfront Fare / Est Trip Time). The platform's raw signal."},
        {"id": "F50", "type": "Float",       "name": "eph_direct_index",        "desc": "Normalized score: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above = Premium; below = Discount."},
        {"id": "F51", "type": "Categorical", "name": "eph_direct_label",        "desc": "Binary classification derived from the index.", "categories": ["Premium", "Discount"]},
        {"id": "F52", "type": "Float",       "name": "eph_operational",         "desc": "True EPH adding Pickup Time. First reality check on the platform signal."},
        {"id": "F53", "type": "Float",       "name": "eph_operational_index",   "desc": "Normalized score: EPH ÷ $200 MXN/hr."},
        {"id": "F54", "type": "Categorical", "name": "eph_operational_label",   "desc": "Binary classification derived from the index.", "categories": ["Premium", "Discount"]},
        {"id": "F55", "type": "Float",       "name": "eph_realized",            "desc": "Predicted EPH adjusting for historical spread. No future leakage."},
        {"id": "F56", "type": "Float",       "name": "eph_realized_index",      "desc": "Normalized score: EPH ÷ $200 MXN/hr."},
        {"id": "F57", "type": "Categorical", "name": "eph_realized_label",      "desc": "Binary classification derived from the index.", "categories": ["Premium", "Discount"]},
        {"id": "F58", "type": "Float",       "name": "eph_complete",            "desc": "Holistic EPH: Predicted Fare / Total Cycle Time. True yield signal."},
        {"id": "F59", "type": "Float",       "name": "eph_complete_index",      "desc": "Normalized score: EPH ÷ $200 MXN/hr."},
        {"id": "F60", "type": "Categorical", "name": "eph_complete_label",      "desc": "Binary classification derived from the index.", "categories": ["Premium", "Discount"]},
    ],
    "🧭 Context": [
        {"id": "F61", "type": "Float",       "name": "home_vector_alignment_score", "desc": "Cosine Similarity (-1 to 1) of dropoff vector relative to Home Base."},
        {"id": "F62–F63", "type": "Boolean", "name": "pickup/dropoff_ambiguity",    "desc": "Binary flags for low-confidence geospatial coordinates. One per endpoint."},
        {"id": "F64", "type": "Int64",       "name": "hour_of_day",                "desc": "Hour of the offer timestamp (5–22). Consecutive integer representing active operating hours."},
        {"id": "F65", "type": "Categorical", "name": "day_of_week",               "categories": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]},
        {"id": "F66", "type": "Categorical", "name": "day_type",                  "categories": ["weekday", "friday", "weekend"]},
        {"id": "F67", "type": "Categorical", "name": "time_of_day_block",         "categories": ["morning", "afternoon", "evening", "night"]},
    ],
}

gold_schema = {
    "📍 Spatial Index": [
        {"id": "F68", "type": "Integer", "name": "pickup_polygon_id",      "desc": "Hand-crafted operational zone polygon containing the pickup coordinate."},
        {"id": "F69", "type": "String",  "name": "pickup_polygon_name",    "desc": "Human-readable name of the pickup micro-zone."},
        {"id": "F70", "type": "Text",    "name": "pickup_h3_hex_id",       "desc": "Uber H3 hexagonal grid cell ID (Res 9) for the pickup location."},
        {"id": "F71", "type": "Integer", "name": "dropoff_polygon_id",     "desc": "Hand-crafted operational zone polygon containing the dropoff coordinate."},
        {"id": "F72", "type": "String",  "name": "dropoff_polygon_name",   "desc": "Human-readable name of the dropoff micro-zone."},
        {"id": "F73", "type": "Text",    "name": "dropoff_h3_hex_id",      "desc": "Uber H3 hexagonal grid cell ID (Res 9) for the dropoff location."},
        {"id": "F74", "type": "Integer", "name": "dropoff_hdbscan_id",     "desc": "HDBSCAN cluster ID — one of 44 machine-discovered demand hubs."},
        {"id": "F75", "type": "String",  "name": "dropoff_hdbscan_name",   "desc": "Human-readable name of the HDBSCAN cluster."},
    ],
    "🌊 Volatility Suite": [
        {"id": "F76", "type": "Float", "name": "realized_traffic_index",              "desc": "(Realized Trip Time ÷ Est Trip Dist) ÷ 120. Computed post-facto and only for completed missions — reflects what actually happened on the road, not the platform's estimate. Serves as the anchor for all subsequent rolling features in this suite."},
        {"id": "F77", "type": "Float", "name": "historical_rolling_avg_traffic_index","desc": "Session-level rolling average of realized_traffic_index across all completed missions prior to the current offer."},
        {"id": "F78", "type": "Float", "name": "traffic_volatility_index",            "desc": "The difference between the platform's expected traffic (the \"promise\") and the agent's recent historical traffic performance (historical_rolling_avg_traffic_index). Quantifies the predictive error of the algorithm at the moment an offer is presented."},
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
      {_row('F49','eph_direct','Float','Platform raw signal — the quoted fare divided by estimated trip time.')}
      {_row('F50','eph_direct_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F51','eph_direct_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t2 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 2 · Operational EPH</div>
      <div class='funnel-tier-formula'>Upfront Fare ÷ (Est Time + Pickup Time)</div>
      {_row('F52','eph_operational','Float','First reality check — adds uncompensated pickup time to the cost denominator.')}
      {_row('F53','eph_operational_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F54','eph_operational_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t3 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 3 · Realized EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Est Trip Time</div>
      {_row('F55','eph_realized','Float',"Rolling feature — corrects the quoted fare using the historical spread observed across all rides completed prior to this offer. Updates only after a ride is fully completed, never mid-trip, ensuring zero leakage. Captures the agent's recent financial performance as a behavioral signal.")}
      {_row('F56','eph_realized_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F57','eph_realized_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t4 = f"""<div class='funnel-tier funnel-tier-final'>
      <div class='funnel-tier-label'>Tier 4 · Complete EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Total Cycle Time  (Est Trip + Pickup + Deadhead Looking for Rides + Deadhead Waiting for Passenger)</div>
      {_row('F58','eph_complete','Float','Same rolling logic as Tier 3 — updates only after ride completion, no leakage — but the denominator now carries the full accumulated deadhead cost of the cycle, making this the most conservative and complete yield signal available at decision time.')}
      {_row('F59','eph_complete_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F60','eph_complete_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
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

def _render_step(circle_color, label, count, why, schema, radio_key, table_fn, domain_renderers=None):
    with st.container(key=f"step-{radio_key}"):
        st.markdown(f"""
        <div class='step-circle' style='background:{circle_color}'>{label[0]}</div>
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

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
pipeline_tab, pb_tab = st.tabs(["Feature Pipeline", "Session Playback"])

with pipeline_tab:
    with st.container(key="pipeline-content"):
        _render_step(
            circle_color="#cd7f32",
            label="Bronze · Raw Canonical Schema",
            count=_feature_count(bronze_schema),
            why="Direct output of the OCR pipeline: offer physics, geospatial coordinates, incentive flags, rider profile, and the decision label. No derivations — the contract between raw data and the engineering layer.",
            schema=bronze_schema,
            radio_key="bronze_domain",
            table_fn=_render_table_b,
        )

        _render_step(
            circle_color="#94a3b8",
            label="Silver · Stateful Engineered Features",
            count=33,
            why="Session-dependent features computed by a sequential state machine. Captures market pressure, agent fatigue, yield trajectory, and operational EPH variants. Strict no-look-ahead rule: _ML features use only data available at decision time; _EDA features are firewalled.",
            schema=silver_schema,
            radio_key="silver_domain",
            table_fn=_render_table_b,
            domain_renderers={"💹 Profitability Funnel": _render_funnel},
        )

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

# ═══════════════════════════════════════════════
# SESSION PLAYBACK
# ═══════════════════════════════════════════════
with pb_tab:
    with st.container(key="pb-content"):
        _NORTH_STAR = 200.0

        def _obf_fare(v):
            if v is None or str(v) in ("None", "nan", ""):
                return "—"
            return re.sub(r'\d', '#', f"{float(v):.0f}")

        def _obf_address(v):
            if v is None or str(v) in ("None", "nan", ""):
                return "—"
            _mask_digits = lambda m: re.sub(r'\d', '#', m.group(0))
            return re.sub(r'\b(?!\d{5}\b)\d+[\w-]*\b', _mask_digits, str(v), count=1)

        def _obf_eph(v):
            """Keep leading digit(s), mask last 2 — e.g. 217 → 2##, 87 → 8#, 9 → #."""
            s = f"{int(float(v))}"
            if len(s) > 2:
                return s[:-2] + "##"
            elif len(s) == 2:
                return s[0] + "#"
            return "#"

        @st.cache_data(ttl=3600)
        def _pb_sessions():
            return fetch_data_from_bq("""
                SELECT
                    ml.session_fk,
                    COUNT(*)                                                        AS offer_count,
                    SUM(CASE WHEN oa.offer_action_description = 'accepted' THEN 1 ELSE 0 END) AS accepted_count,
                    MIN(ml.offer_timestamp)                                         AS session_start
                FROM `645009831643.pienza_mini.v_ML_Supervised` ml
                LEFT JOIN `645009831643.pienza_mini.offer_action` oa
                       ON oa.offer_action_id = ml.offer_action_fk
                WHERE ml.session_fk IS NOT NULL
                GROUP BY ml.session_fk
                ORDER BY session_start
            """)

        # Batched once for all curated sessions (_VISIBLE_SIDS below), instead
        # of a separate live BQ query per session selected — a per-sid WHERE
        # clause changes the SQL string (and therefore the @st.cache_data
        # key) on every dropdown change, firing a fresh query for every
        # session not yet visited this run. Measured 2026-07-09: batching
        # all 8 up front costs the same as fetching just 1 (BQ latency here
        # is dominated by fixed per-query overhead, not row count), so this
        # is a pure win with no downside for the "pick one session, stay
        # there a while" usage pattern.
        @st.cache_data(ttl=3600)
        def _pb_offers_all(sids_tuple):
            sid_list = ", ".join(f"'{s}'" for s in sids_tuple)
            return fetch_data_from_bq(f"""
                SELECT
                    ml.session_fk,
                    ml.offer_timestamp, ml.upfront_fare,
                    ml.est_trip_time_sec, ml.est_trip_dist_km,
                    ml.time_to_pickup_sec, ml.dist_to_pickup_km,
                    ml.pickup_address, ml.dropoff_address,
                    ml.is_surge, ml.surge_amount, ml.is_turbo_plus, ml.turbo_plus_amount,
                    ml.traffic_index_base_120, ml.time_since_last_offer, ml.offer_density_60sec,
                    ml.consecutive_rejects, ml.total_accumulated_deadhead_sec,
                    ml.cycle_rolling_avg_spread, ml.cycle_cumulative_net_earnings,
                    ml.home_vector_alignment_score, ml.pickup_ambiguity, ml.dropoff_ambiguity,
                    ml.eph_direct, ml.eph_operational, ml.is_operational_downgrade,
                    ml.eph_realized_ML, ml.eph_complete_ML,
                    ml.is_spread_downgrade_ML, ml.is_total_cycle_downgrade_ML,
                    ml.day_of_week, ml.time_of_day_block, ml.day_type,
                    ml.dropoff_polygon_name, ml.dropoff_h3_hex_id,
                    oa.offer_action_description  AS str_action,
                    pc.category_name             AS str_product,
                    rp.reason_primary_description AS str_reason,
                    ds.driver_state_at_request_description AS str_driver_state
                FROM `645009831643.pienza_mini.v_ML_Supervised` ml
                LEFT JOIN `645009831643.pienza_mini.offer_action` oa
                       ON oa.offer_action_id = ml.offer_action_fk
                LEFT JOIN `645009831643.pienza_mini.product_category` pc
                       ON pc.product_category_id = ml.product_category_fk
                LEFT JOIN `645009831643.pienza_mini.reason_primary` rp
                       ON rp.reason_primary_id = ml.reason_primary_fk
                LEFT JOIN `645009831643.pienza_mini.driver_state_at_request` ds
                       ON ds.driver_state_at_request_id = ml.driver_state_at_request_fk
                WHERE ml.session_fk IN ({sid_list})
                ORDER BY ml.session_fk, ml.offer_timestamp
            """)

        def _pb_offers(sid):
            df_all = _pb_offers_all(tuple(sorted(_VISIBLE_SIDS)))
            return df_all[df_all["session_fk"] == sid].drop(columns=["session_fk"]).reset_index(drop=True)

        # ── Session state init ──
        for _k, _v in [("pb_sid", None), ("pb_df", None), ("pb_idx", 0)]:
            if _k not in st.session_state:
                st.session_state[_k] = _v

        # ── Header ──
        st.markdown(
            "<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-top:32px;margin-bottom:24px;'>"
            "Step through a real field session offer by offer. Each card shows exactly what the platform "
            "presented and what the state machine computed at that moment in the session.</p>",
            unsafe_allow_html=True
        )

        # ── Session picker ──
        df_sess = _pb_sessions()
        if df_sess is None or df_sess.empty:
            st.error("Could not load sessions from BigQuery.")
            st.stop()

        # Only show a curated subset of sessions - the rest stay hidden from
        # the selectbox (not deleted, just filtered out of what's offered).
        _VISIBLE_SIDS = {f"SID{n:04d}" for n in (30, 35, 38, 45, 51, 56, 58, 62)}
        df_sess = df_sess[df_sess["session_fk"].isin(_VISIBLE_SIDS)].reset_index(drop=True)
        if df_sess.empty:
            st.error("None of the curated sessions were found in BigQuery.")
            st.stop()

        def _sess_label(r):
            ts  = str(r.get("session_start", ""))[:10]
            n   = int(r.get("offer_count", 0))
            a   = int(r.get("accepted_count", 0))
            pct = f"{a/n*100:.0f}%" if n > 0 else "—"
            return f"{r['session_fk']}  ·  {ts}  ·  {n} offers  ·  {a} accepted ({pct})"

        sess_labels  = df_sess.apply(_sess_label, axis=1).tolist()
        sess_ids     = df_sess["session_fk"].tolist()
        label_to_id  = dict(zip(sess_labels, sess_ids))

        sel_label = st.selectbox("Session", sess_labels, key="pb_sess_select", label_visibility="collapsed")
        sel_id    = label_to_id[sel_label]

        if sel_id != st.session_state.pb_sid:
            st.session_state.pb_sid = sel_id
            st.session_state.pb_df  = _pb_offers(sel_id)
            st.session_state.pb_idx = 0
            st.session_state.pop("pb_jump", None)
            st.rerun()

        if st.session_state.pb_df is None or st.session_state.pb_df.empty:
            st.warning("No offers found for this session.")
            st.stop()

        df    = st.session_state.pb_df
        idx   = st.session_state.pb_idx
        total = len(df)

        # ── Session complete ──
        if idx >= total:
            acc_mask  = df["str_action"].str.lower().str.startswith("accept").fillna(False)
            accepted  = int(acc_mask.sum())
            rejected  = total - accepted

            # Pull final-row state machine values (last offer = end-of-session state)
            last       = df.iloc[-1]
            deadhead   = float(last.get("total_accumulated_deadhead_sec") or 0)
            earnings   = float(last.get("cycle_cumulative_net_earnings")  or 0)
            spread     = float(last.get("cycle_rolling_avg_spread")       or 0)
            max_consec = int(df["consecutive_rejects"].fillna(0).max())

            # Session duration
            try:
                t0  = pd.to_datetime(df["offer_timestamp"].iloc[0])
                t1  = pd.to_datetime(df["offer_timestamp"].iloc[-1])
                dur = int((t1 - t0).total_seconds())
            except Exception:
                dur = None

            # EPH averages (accepted offers only)
            acc_df = df[acc_mask]
            eph_d_avg = acc_df["eph_direct"].dropna().mean()    if "eph_direct"    in df.columns else None
            eph_o_avg = acc_df["eph_operational"].dropna().mean() if "eph_operational" in df.columns else None

            def _hms_s(sec):
                if sec is None: return "—"
                s = int(sec); h, r = divmod(s, 3600); m, s = divmod(r, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"

            st.markdown("<span class='phase-badge'>Session Complete</span>", unsafe_allow_html=True)
            st.markdown("### Session Summary")

            # Row 1 — decision KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Offers",      total)
            c2.metric("Accepted",          f"{accepted}  ({accepted/total*100:.0f}%)")
            c3.metric("Rejected",          rejected)
            c4.metric("Max Consec. Rejects", max_consec)

            st.markdown("---")

            # Row 2 — state machine KPIs
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Acc. Deadhead",       _hms_s(deadhead))
            c6.metric("Session Duration",    _hms_s(dur))
            c7.metric("Cumulative Earnings", f"${_obf_eph(earnings)} MXN")
            c8.metric("Avg Spread Ratio",    f"{spread:.3f}" if spread else "—")

            st.markdown("---")

            # Row 3 — EPH averages (accepted offers only)
            c9, c10, _, _ = st.columns(4)
            c9.metric("Avg Direct EPH",      f"${_obf_eph(eph_d_avg)}/hr" if eph_d_avg else "—")
            c10.metric("Avg Operational EPH", f"${_obf_eph(eph_o_avg)}/hr" if eph_o_avg else "—")

            st.markdown(
                "<div style='border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;"
                "border-radius:0 7px 7px 0;font-size:0.82rem;color:#78350f;line-height:1.7;margin-top:8px;'>"
                "<strong>⚠ Snapshot caveat — by design</strong><br>"
                "These figures reflect the state machine at the timestamp of the <em>last offer presented</em>, "
                "not the true end of the session. Deadhead, earnings, and session duration do <strong>not</strong> "
                "include time or income accrued after completing the final accepted ride. This is intentional: the state machine was engineered as an <strong>ML feature pipeline</strong>. "
                "The model's decision boundary is the accept/reject moment — so the input vector is defined "
                "strictly <em>before</em> the last outcome is known."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown("")
            if st.button("↺ Replay Session", key="pb_restart", use_container_width=False):
                st.session_state.pb_idx = 0
                st.session_state.pop("pb_jump", None)
                st.rerun()
            st.stop()

        row = df.iloc[idx]

        # If a button fired last render, apply its target to the slider key NOW
        # (must happen before st.slider is instantiated)
        _nav = st.session_state.pop("_pb_nav", None)
        if _nav is not None:
            st.session_state["pb_jump"] = _nav

        # ── Slider (jump to any offer) ──
        jump = st.slider("", min_value=1, max_value=total, key="pb_jump",
                         label_visibility="collapsed")
        if jump - 1 != idx:
            st.session_state.pb_idx = jump - 1
            st.rerun()

        # ── Navigation buttons (centered) ──
        _, nb1, nb2, nb3, _ = st.columns([2, 1.2, 1.2, 1.2, 2])
        with nb1:
            if st.button("← Back", key="pb_back_btn", use_container_width=True, disabled=(idx == 0)):
                st.session_state.pb_idx  = idx - 1
                st.session_state["_pb_nav"] = idx     # consumed next render, before slider
                st.rerun()
        with nb2:
            nxt_label = "→ Next" if idx < total - 1 else "→ Summary"
            if st.button(nxt_label, key="pb_next_btn", use_container_width=True):
                st.session_state.pb_idx  = idx + 1
                st.session_state["_pb_nav"] = idx + 2
                st.rerun()
        with nb3:
            if st.button("↺ Restart", key="pb_restart_btn", use_container_width=True):
                st.session_state.pb_idx  = 0
                st.session_state.pop("pb_jump", None)
                st.session_state["_pb_nav"] = 1
                st.rerun()

        with st.container(key="mission-control"):
            st.markdown(
                f"<div style='font-size:0.78rem;color:#888;margin-bottom:14px;margin-top:4px;'>"
                f"Offer <strong style='color:#1a1a1a;'>{idx+1}</strong> of {total} &nbsp;·&nbsp; "
                f"{str(row.get('day_type','') or '')} &nbsp;·&nbsp; "
                f"{str(row.get('time_of_day_block','') or '')} &nbsp;·&nbsp; "
                f"{str(row.get('day_of_week','') or '')}"
                f"</div>",
                unsafe_allow_html=True
            )

            # ── Main columns ──
            offer_col, sm_col = st.columns(2, gap="large")

            def _v(val, fmt="{}", fb="—"):
                try:
                    return fmt.format(val) if val is not None and str(val) not in ("None","nan","") else fb
                except Exception:
                    return fb

            def _hms(sec):
                if sec is None or str(sec) in ("None", "nan", ""):
                    return "—"
                s = int(float(sec))
                h, r = divmod(abs(s), 3600)
                m, s = divmod(r, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"

            with offer_col:
                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-bottom:8px;'>Platform Offer "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(what was presented)</span></div>",
                    unsafe_allow_html=True,
                )

                bonuses = []
                if row.get("is_surge"):      bonuses.append(f"+${_v(row.get('surge_amount'), '{:.0f}')} Surge")
                if row.get("is_turbo_plus"): bonuses.append(f"+${_v(row.get('turbo_plus_amount'), '{:.0f}')} Turbo+")
                bonus_html = " ".join(
                    f"<span style='background:#fef3c7;color:#92400e;border:1px solid #fde68a;"
                    f"border-radius:3px;font-size:0.62rem;font-weight:700;padding:1px 6px;'>{b}</span>"
                    for b in bonuses
                )

                _raw_pickup  = _obf_address(row.get("pickup_address"))
                _raw_dropoff = _obf_address(row.get("dropoff_address"))
                pickup_str   = (_raw_pickup[:38]  + "…") if len(_raw_pickup)  > 38 else _raw_pickup
                dropoff_str  = (_raw_dropoff[:38] + "…") if len(_raw_dropoff) > 38 else _raw_dropoff
                product_name = re.sub(r"(?i)uberx\b", "X", _v(row.get("str_product"), "{}", "Unknown"))

                # decision vars (used below offer card)
                action   = str(row.get("str_action", "—") or "—")
                reason   = str(row.get("str_reason",  "—") or "—")
                acc      = action.lower().startswith("accept")
                d_icon   = "<span style='color:#22c55e;'>✓</span>" if acc else "<span style='color:#ef4444;'>✕</span>"
                d_label  = "Accepted" if acc else action.capitalize()
                reason_line = (
                    f"<span style='font-size:0.88rem;font-weight:700;color:#334155;margin-left:8px;'>"
                    f"{reason}</span>"
                    if reason not in ("—", "NULL", "None", "nan") else ""
                )

                ts = str(row.get('offer_timestamp', '') or '')[:19]

                _no_screenshot = all(
                    row.get(f) is None or str(row.get(f)) in ("None", "nan", "")
                    for f in ("upfront_fare", "time_to_pickup_sec", "est_trip_time_sec")
                )
                if _no_screenshot:
                    st.markdown(
                        "<div style='background:#fefce8;border:2px solid #facc15;border-radius:7px;"
                        "padding:8px 14px;font-size:0.8rem;color:#713f12;font-weight:600;margin-bottom:8px;'>"
                        "📷 No screenshot was captured for this offer — platform fields unavailable."
                        "</div>",
                        unsafe_allow_html=True
                    )

                st.markdown(f"""
                <div style='border:1px solid #eaeaea;border-radius:10px;padding:16px;background:#fff;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>
                    <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>
                      {product_name} {bonus_html}
                    </div>
                    <div style='font-size:0.65rem;font-family:monospace;color:#aaa;font-weight:400;'>{ts}</div>
                  </div>
                  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;'>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Upfront Fare</div>
                      <div style='font-size:1.5rem;font-weight:800;color:#1a1a1a;'>${ _obf_fare(row.get('upfront_fare')) }<span style='font-size:0.75rem;font-weight:400;color:#aaa;'> MXN</span></div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Driver State</div>
                      <div style='font-size:1.0rem;font-weight:600;color:#1a1a1a;'>{_v(row.get('str_driver_state'))}</div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Pickup</div>
                      <div style='font-size:0.95rem;font-weight:600;color:#1a1a1a;'>{_hms(row.get('time_to_pickup_sec'))} &nbsp;<span style='color:#aaa;font-size:0.75rem;'>/ {_v(row.get('dist_to_pickup_km'),'{:.1f}')} km</span></div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Est Trip</div>
                      <div style='font-size:0.95rem;font-weight:600;color:#1a1a1a;'>{_hms(row.get('est_trip_time_sec'))} &nbsp;<span style='color:#aaa;font-size:0.75rem;'>/ {_v(row.get('est_trip_dist_km'),'{:.1f}')} km</span></div>
                    </div>
                  </div>
                  <div style='font-size:0.7rem;color:#666;border-top:1px solid #f5f5f5;padding-top:8px;line-height:1.8;'>
                    <div>📍 {pickup_str}</div>
                    <div>🏁 {dropoff_str}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-top:156px;margin-bottom:8px;'>Decision "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(what the agent decided)</span></div>",
                    unsafe_allow_html=True,
                )
                st.html(
                    f"<div style='border-left:3px solid #21918c;border-radius:0 4px 4px 0;padding:4px 10px;"
                    f"background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);display:inline-block;'>"
                    f"<span style='font-size:0.68rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>"
                    f"{d_label} {d_icon}</span>"
                    f"{reason_line}</div>"
                )


            with sm_col:
                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-bottom:8px;'>State Machine Context "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(at decision time)</span></div>",
                    unsafe_allow_html=True,
                )

                with st.container(key="sm-card"):
                    deadhead    = float(row.get("total_accumulated_deadhead_sec") or 0)
                    consec      = int(row.get("consecutive_rejects") or 0)
                    earnings    = float(row.get("cycle_cumulative_net_earnings") or 0)
                    spread      = float(row.get("cycle_rolling_avg_spread") or 1.0)
                    traffic     = float(row.get("traffic_index_base_120") or 1.0)
                    home_v      = row.get("home_vector_alignment_score")
                    since_last  = row.get("time_since_last_offer")
                    accepted_so_far = int(
                        df.iloc[:idx]["str_action"].str.lower().str.startswith("accept").fillna(False).sum()
                    )

                    cr_color = "#e05252" if consec >= 5 else "#f59e0b" if consec >= 3 else "#1a1a1a"
                    ti_color = "#e05252" if traffic > 1.2 else "#f59e0b" if traffic > 1.05 else "#21918c"

                    def _stat(label, value, color="#1a1a1a"):
                        return (f"<div style='border:1px solid #eaeaea;border-radius:7px;padding:7px 4px;text-align:center;overflow:hidden;'>"
                                f"<div style='font-size:0.58rem;color:#bbb;font-weight:700;text-transform:uppercase;'>{label}</div>"
                                f"<div style='font-size:0.82rem;font-weight:700;color:{color};white-space:nowrap;'>{value}</div>"
                                f"</div>")

                    st.html(
                        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px;'>" +
                        _stat("Acc. Deadhead", _hms(deadhead)) +
                        _stat("Since Last Offer",  _hms(since_last)) +
                        _stat("Consec. Rejects",   consec,          cr_color) +
                        _stat("Accepted",          accepted_so_far) +
                        _stat("Cum Earnings",       f"${_obf_eph(earnings)}") +
                        _stat("Spread Ratio",      f"{spread:.3f}") +
                        _stat("Traffic Index",     f"{traffic:.2f}x", ti_color) +
                        _stat("Home Vector Score", f"{float(home_v):.2f}" if home_v is not None else "—") +
                        "</div>"
                    )

                    # EPH funnel (precomputed from view)
                    def _eph_row(title, formula, eph_val, downgrade=False):
                        if eph_val is None or str(eph_val) in ("None", "nan", ""):
                            return (f"<div style='border:1px solid #f0f0f0;border-radius:7px;padding:7px 12px;"
                                    f"margin-bottom:5px;color:#ccc;font-size:0.7rem;'>{title} — N/A</div>")
                        v    = float(eph_val)
                        ix   = v / _NORTH_STAR
                        lbl  = "Premium" if ix >= 1.0 else "Discount"
                        clr  = "#21918c" if ix >= 1.0 else "#71717a"
                        dg   = ("<span style='font-size:0.6rem;color:#f59e0b;margin-left:5px;'>⚠ downgrade</span>"
                                if downgrade else "")
                        return f"""<div style='border:1px solid #eaeaea;border-radius:7px;padding:7px 12px;margin-bottom:5px;background:#fff;'>
                          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;'>
                            <span style='font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#21918c;'>{title}</span>
                            <span style='font-size:0.6rem;color:#bbb;font-family:monospace;'>{formula}</span>
                          </div>
                          <div style='display:flex;align-items:center;gap:8px;'>
                            <span style='font-size:0.98rem;font-weight:700;color:#1a1a1a;'>${_obf_eph(v)}<span style='font-size:0.64rem;font-weight:400;color:#aaa;'> /hr</span></span>
                            <span style='font-size:0.74rem;font-weight:700;color:{clr};'>{ix:.1f}x</span>
                            <span style='font-size:0.63rem;font-weight:700;color:#fff;background:{clr};padding:1px 6px;border-radius:3px;'>{lbl}</span>
                            {dg}
                          </div>
                        </div>"""

                    st.html(
                        _eph_row("T1 · Direct",      "Fare ÷ Trip",                     row.get("eph_direct")) +
                        _eph_row("T2 · Operational", "Fare ÷ (Trip+Pickup)",            row.get("eph_operational"),  bool(row.get("is_operational_downgrade"))) +
                        _eph_row("T3 · Realized",    f"Fare×{spread:.2f} ÷ Trip",      row.get("eph_realized_ML"), bool(row.get("is_spread_downgrade_ML"))) +
                        _eph_row("T4 · Complete",    f"Fare×{spread:.2f} ÷ Cycle",     row.get("eph_complete_ML"), bool(row.get("is_total_cycle_downgrade_ML")))
                    )





