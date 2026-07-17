"""Data literals and pure helpers used by 0006_Payout_Physics_Causal_Inference.py (Layer 1 extraction)."""


import pandas as pd
import streamlit as st

from utils.bq_client import _bigquery_client

OPUS_TEAL = '#21918c'
OPUS_GREY = '#F5F6F7'
OPUS_TEXT = '#121212'


def teal_callout(text: str, mb: str = "24px") -> str:
    """Builds the canonical teal-tinted callout box HTML for a given text."""
    return f"""<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;padding:14px 18px;font-size:0.88rem;color:#334155;line-height:1.7;margin-bottom:{mb};'>{text}</div>"""


@st.cache_resource
def get_bq_client():
    """Returns the shared, cached BigQuery client for this page."""
    return _bigquery_client()


def map_category(cat_name) -> str:
    """Collapses a raw product_category name to one of X / Mid-tier / Premium."""
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower:
        return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower:
        return "Mid-tier"
    elif 'black' in cat_lower:
        return "Premium"
    else:
        return "X"


# Phase 1: Payout Stability — 5-mission moving average of the financial spread.
query_phase1 = """
SELECT
    DATE(o.offer_timestamp) AS session_date,
    o.offer_id,
    p.category_name      AS category,
    o.upfront_fare,
    v.realized_fare,
    v.spread_percentage  AS financial_spread
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
WHERE v.realized_fare IS NOT NULL
"""


@st.cache_data
def get_stability_data():
    """Fetches and dates the Phase 1 payout-stability rows."""
    client = get_bq_client()
    df = client.query(query_phase1).to_dataframe()
    df['session_date'] = pd.to_datetime(df['session_date'])
    return df


# Phase 2: Heteroscedasticity Audit — upfront vs realized fare, for the OLS baseline.
query_phase2 = """
SELECT
    o.offer_id,
    DATE(o.offer_timestamp) AS session_date,
    p.category_name AS category,
    o.upfront_fare,
    v.realized_fare
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
WHERE v.realized_fare IS NOT NULL AND o.upfront_fare IS NOT NULL
"""


@st.cache_data
def get_risk_data():
    """Fetches the Phase 2 heteroscedasticity-audit rows."""
    client = get_bq_client()
    df = client.query(query_phase2).to_dataframe()
    df['session_date'] = pd.to_datetime(df['session_date'])
    return df


# Phase 3 (Reality Check Matrix tab): fare + trip-time correlation inputs.
query_reality_check = """
SELECT
    o.upfront_fare,
    v.realized_fare,
    (o.est_trip_time_sec / 60.0) AS est_trip_time_min,
    (v.duration_trip_sec / 60.0) AS actual_trip_time_min
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
WHERE v.realized_fare IS NOT NULL
AND o.est_trip_time_sec > 0
"""


@st.cache_data
def get_reality_check_data():
    """Fetches the Reality Check Matrix correlation-input rows."""
    client = get_bq_client()
    df = client.query(query_reality_check).to_dataframe()
    return df


# Phase 3 (Fraud Prevention / LOWESS "U" curve): financial vs time spread.
query_fraud_prevention = """
SELECT
    o.offer_id,
    DATE(o.offer_timestamp) AS session_date,
    p.category_name AS category,
    v.spread_percentage AS financial_spread,
    (v.duration_trip_sec / NULLIF(o.est_trip_time_sec, 0)) AS time_spread
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
WHERE o.est_trip_time_sec > 0
AND v.realized_fare IS NOT NULL
"""


@st.cache_data
def get_fraud_prevention_data():
    """Fetches the fraud-prevention (financial vs time spread) rows."""
    client = get_bq_client()
    df = client.query(query_fraud_prevention).to_dataframe()
    df['session_date'] = pd.to_datetime(df['session_date'])
    return df
