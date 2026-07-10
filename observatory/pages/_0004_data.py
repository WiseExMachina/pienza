"""Data literals and pure helpers used by 0004_Data_Census_(The_Basics).py (Layer 1 extraction)."""

import base64
import re
from pathlib import Path

import streamlit as st

from utils.bq_client import _bigquery_client

PROJECT = "645009831643"
DATASET = "pienza_mini"


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


@st.cache_resource
def get_bq_client():
    """Returns the shared, cached BigQuery client for this page."""
    return _bigquery_client()


@st.cache_data
def run_query(sql: str):
    """Runs a SQL string against BigQuery, returning (dataframe, error_message)."""
    try:
        return get_bq_client().query(sql).to_dataframe(), None
    except Exception as e:
        return None, str(e)


def clean_label(s):
    """Strips the 'uber'/'uber_' prefix from a product/category label per the brand convention."""
    if s is None:
        return s
    s = re.sub(r'(?i)uber_?', '', str(s)).strip('_').strip()
    return s if s else str(s)


# Data Census sandbox: one SQL string per pill, prefetched in parallel on
# first load (see project_perf_tricks memory for the ThreadPoolExecutor
# rationale — each query is still a genuinely live BigQuery round trip).
QUERIES: dict = {
    "Decision & Product Mix": f"""-- Categorical census: action, product, rejection reason, outcome
SELECT 'action'  AS dimension, oa.offer_action_description  AS label, COUNT(*) AS n
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa ON oa.offer_action_id = ml.offer_action_fk
GROUP BY label

UNION ALL

SELECT 'product' AS dimension, pc.category_name AS label, COUNT(*) AS n
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.product_category` pc ON pc.product_category_id = ml.product_category_fk
GROUP BY label

UNION ALL

SELECT 'reason'  AS dimension, rp.reason_primary_description AS label, COUNT(*) AS n
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.reason_primary` rp ON rp.reason_primary_id = ml.reason_primary_fk
GROUP BY label

UNION ALL

SELECT 'outcome' AS dimension, oc.outcome_description AS label, COUNT(*) AS n
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.outcome` oc ON oc.outcome_id = CAST(ml.outcome_fk AS INT64)
GROUP BY label
ORDER BY dimension, n DESC;""",

    "Incentives": f"""-- Incentive structure: prevalence flags + amounts (surge, turbo+, reservation)
SELECT
is_surge,        surge_amount,
is_turbo_plus,   turbo_plus_amount,
is_reservation,  reservation_amount
FROM `{PROJECT}.{DATASET}.offers`;""",

    "Traffic Index": f"""-- Traffic Index by hour of day
-- 1.0 = baseline (2 min/km). Values >3.0 are CDMX gridlock territory.
SELECT traffic_index_base_120, hour_of_day
FROM `{PROJECT}.{DATASET}.v_ML_Supervised`
WHERE traffic_index_base_120 IS NOT NULL;""",

    "Home Vector": f"""-- Strategic alignment: direction of each offer relative to home base
-- Score range: -1.0 (directly away) to +1.0 (directly toward home)
SELECT
home_vector_alignment_score,
session_progress_ratio,
oa.offer_action_description AS action
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa ON oa.offer_action_id = ml.offer_action_fk
WHERE home_vector_alignment_score IS NOT NULL
  AND session_progress_ratio IS NOT NULL;""",

    "Profitability Funnel": f"""-- EPH funnel: from platform promise to holistic reality
-- eph_direct = upfront fare / estimated ride time
-- eph_operational = adds pickup time to denominator
-- eph_realized_EDA = corrects for spread (what was actually paid)
-- eph_complete_EDA = full cost: pickup + spread + dead miles
SELECT
ml.eph_direct,
ml.eph_operational,
ml.eph_realized_EDA,
ml.eph_complete_EDA,
pc.category_name AS product
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.product_category` pc ON pc.product_category_id = ml.product_category_fk
WHERE ml.eph_direct IS NOT NULL
  AND ml.eph_direct < 1000;""",
}
