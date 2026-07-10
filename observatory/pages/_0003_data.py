"""Data literals and pure helpers used by 0003_Feature_Store.py (Layer 1 extraction)."""

import base64
import re
from pathlib import Path

import streamlit as st

from utils.bq_client import fetch_data_from_bq


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


# Bronze medallion layer: raw canonical OCR-output schema, F01-F37, by domain.
bronze_schema: dict = {
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

# Silver medallion layer: stateful engineered features, F35-F67, by domain.
silver_schema: dict = {
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

# Gold medallion layer: spatial index + volatility suite, F68-F78, by domain.
gold_schema: dict = {
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


def feature_count(schema: dict) -> int:
    """Counts total features across all domains in a bronze/silver/gold schema dict."""
    return sum(len(v) for v in schema.values())


def content(f: dict) -> str:
    """Builds the HTML body for one feature card: category chips (with tooltips) or a plain description."""
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


# Session Playback tab: curated subset of session IDs shown in the picker
# (the rest stay hidden, not deleted, from what the selectbox offers).
VISIBLE_SIDS: set = {f"SID{n:04d}" for n in (30, 35, 38, 45, 51, 56, 58, 62)}


@st.cache_data(ttl=3600)
def pb_sessions():
    """Fetches per-session offer/acceptance counts and start time for Session Playback."""
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


# Batched once for all curated sessions (VISIBLE_SIDS above), instead of a
# separate live BQ query per session selected — a per-sid WHERE clause
# changes the SQL string (and therefore the @st.cache_data key) on every
# dropdown change, firing a fresh query for every session not yet visited
# this run. Measured 2026-07-09: batching all 8 up front costs the same as
# fetching just 1 (BQ latency here is dominated by fixed per-query overhead,
# not row count), so this is a pure win with no downside for the "pick one
# session, stay there a while" usage pattern.
@st.cache_data(ttl=3600)
def pb_offers_all(sids_tuple: tuple):
    """Fetches full offer detail for a batch of curated session IDs, joined to human-readable dimension labels."""
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


def pb_offers(sid: str):
    """Returns the cached offer rows for one curated session ID, from the batched pb_offers_all fetch."""
    df_all = pb_offers_all(tuple(sorted(VISIBLE_SIDS)))
    return df_all[df_all["session_fk"] == sid].drop(columns=["session_fk"]).reset_index(drop=True)


# obf_fare/obf_address here deliberately use per-digit `#` masking instead of
# 0002_Acquisition_Pipelines.py's block/fixed-width style — a documented,
# scoped exception for this page only (see assets/CLAUDE.md's Anonymization
# Protocol section, "Exception (0003_Feature_Store.py only...)"). Do not
# merge with 0002's obf_fare/obf_address or propagate this style elsewhere
# without asking first.

def obf_fare(v):
    """Masks a fare value's digits with # (per-digit), formatted to 0 decimals."""
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    return re.sub(r'\d', '#', f"{float(v):.0f}")


def obf_address(v):
    """Masks the street-number portion of an address per-digit with #; preserves 5-digit zip codes."""
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    _mask_digits = lambda m: re.sub(r'\d', '#', m.group(0))
    return re.sub(r'\b(?!\d{5}\b)\d+[\w-]*\b', _mask_digits, str(v), count=1)


def obf_eph(v):
    """Masks an EPH value's last 1-2 digits, e.g. 217 -> 2##, 87 -> 8#, 9 -> #."""
    s = f"{int(float(v))}"
    if len(s) > 2:
        return s[:-2] + "##"
    elif len(s) == 2:
        return s[0] + "#"
    return "#"
