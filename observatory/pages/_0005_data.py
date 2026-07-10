"""Data literals and pure helpers used by 0005_The_Cost_of_Patience.py (Layer 1 extraction)."""

import base64
from pathlib import Path

import streamlit as st

from utils.bq_client import _bigquery_client


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
OPUS_TEXT   = '#121212'

# Market Quadrants palette (Phase 2): quality x velocity regime -> color.
COLORS: dict = {
    'Rich / Fast': '#21918c',   # primary teal
    'Rich / Slow': '#99d5d1',   # pale teal
    'Poor / Fast': '#cbd5e1',   # light slate
    'Poor / Slow': '#64748b',   # dark slate
}


@st.cache_resource
def get_bq_client():
    """Returns the shared, cached BigQuery client for this page."""
    return _bigquery_client()


def map_category(cat_name) -> str:
    """Collapses a raw product_category name to one of X / Mid-tier / Premium."""
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower: return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower: return "Mid-tier"
    elif 'black' in cat_lower: return "Premium"
    else: return "X"


# SQL queries backing the three Phase 1-3 cache functions below.
query_mqi = """
SELECT
  ml.offer_id,
  ml.session_fk,
  pc.category_name AS category,
  ml.eph_operational
FROM `645009831643.pienza_mini.v_ML_Supervised` ml
LEFT JOIN `645009831643.pienza_mini.product_category` pc
  ON pc.product_category_id = ml.product_category_fk
WHERE ml.eph_direct IS NOT NULL
  AND ml.eph_direct < 1000
"""

query_moneymap = """
WITH base_offers AS (
    SELECT
        o.offer_id,
        o.session_fk,
        o.offer_timestamp,
        p.category_name AS category,
        o.upfront_fare,
        o.est_trip_time_sec,
        oa.offer_action_description AS offer_action,
        LAG(oa.offer_action_description) OVER(PARTITION BY o.session_fk ORDER BY o.offer_timestamp) AS prev_offer_action,
        TIMESTAMP_DIFF(
            CAST(o.offer_timestamp AS TIMESTAMP),
            LAG(CAST(o.offer_timestamp AS TIMESTAMP)) OVER(PARTITION BY o.session_fk ORDER BY o.offer_timestamp),
            SECOND
        ) as raw_delta
    FROM `645009831643.pienza_mini.offers` o
    JOIN `645009831643.pienza_mini.product_category` p
      ON o.product_category_fk = p.product_category_id
    LEFT JOIN `645009831643.pienza_mini.offer_action` oa
      ON o.offer_action_fk = oa.offer_action_id
    WHERE o.est_trip_time_sec > 0
      AND o.upfront_fare IS NOT NULL
      AND o.session_fk IS NOT NULL
)
SELECT * FROM base_offers
"""

query_ven = """
SELECT
    o.offer_id,
    o.session_fk,
    CAST(o.offer_timestamp AS TIMESTAMP) AS offer_timestamp,
    o.upfront_fare,
    o.est_trip_time_sec,
    o.time_to_pickup_sec,
    pc.category_name,
    ef.eph_operational AS eph_real,
    oa.offer_action_description AS offer_action,
    LAG(oa.offer_action_description)
        OVER(PARTITION BY o.session_fk ORDER BY o.offer_timestamp) AS prev_offer_action,
    TIMESTAMP_DIFF(
        CAST(o.offer_timestamp AS TIMESTAMP),
        LAG(CAST(o.offer_timestamp AS TIMESTAMP))
            OVER(PARTITION BY o.session_fk ORDER BY o.offer_timestamp),
        SECOND
    ) AS raw_delta
FROM `645009831643.pienza_mini.offers` o
JOIN `645009831643.pienza_mini.engineered_features` ef
  ON ef.offer_id_fk = o.offer_id
JOIN `645009831643.pienza_mini.product_category` pc
  ON o.product_category_fk = pc.product_category_id
LEFT JOIN `645009831643.pienza_mini.offer_action` oa
  ON o.offer_action_fk = oa.offer_action_id
WHERE ef.eph_operational IS NOT NULL
  AND o.est_trip_time_sec > 0
  AND o.upfront_fare IS NOT NULL
  AND o.session_fk IS NOT NULL
"""


@st.cache_data
def get_mqi_data(_query):
    """Runs the Market Quality Index SQL query against BigQuery."""
    return get_bq_client().query(_query).to_dataframe()


@st.cache_data
def get_moneymap_data(_query):
    """Runs the Money Map (session wait/fare) SQL query against BigQuery."""
    return get_bq_client().query(_query).to_dataframe()


@st.cache_data
def get_ven_data(_query):
    """Runs the CV(τ) Playbook SQL query against BigQuery."""
    return get_bq_client().query(_query).to_dataframe()
