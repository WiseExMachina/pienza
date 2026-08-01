---
name: view-sql-locations
description: Archive of every "View SQL" expander's query text, for restoring after deprecation/removal
---

# "View SQL" archive

Full backup of the SQL behind every `st.expander("View SQL")` in the Observatory, captured 2026-07-09 **before** they were deprecated/removed. If you ever want one back, copy the query text below into a `st.code(..., language="sql")` inside a `with st.expander("View SQL"):` block, at the same page/location it came from.

**Why this file exists:** user is removing all "View SQL" expanders but wants the queries archived in case of regret — this is the restore point, not a location index (line numbers rot as pages get edited; the actual query text does not).

---

## 0004_Data_Census_(The_Basics).py

One expander, shared across 5 pills — whichever pill is active determines which query shows. `{PROJECT}`/`{DATASET}` are f-string placeholders resolved at runtime.

### Pill: "Decision & Product Mix"
```sql
-- Categorical census: action, product, rejection reason, outcome
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
ORDER BY dimension, n DESC;
```

### Pill: "Incentives"
```sql
-- Incentive structure: prevalence flags + amounts (surge, turbo+, reservation)
SELECT
is_surge,        surge_amount,
is_turbo_plus,   turbo_plus_amount,
is_reservation,  reservation_amount
FROM `{PROJECT}.{DATASET}.offers`;
```

### Pill: "Traffic Index"
```sql
-- Traffic Index by hour of day
-- 1.0 = baseline (2 min/km). Values >3.0 are CDMX gridlock territory.
SELECT traffic_index_base_120, hour_of_day
FROM `{PROJECT}.{DATASET}.v_ML_Supervised`
WHERE traffic_index_base_120 IS NOT NULL;
```

### Pill: "Home Vector"
```sql
-- Strategic alignment: direction of each offer relative to home base
-- Score range: -1.0 (directly away) to +1.0 (directly toward home)
SELECT
home_vector_alignment_score,
session_progress_ratio,
oa.offer_action_description AS action
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa ON oa.offer_action_id = ml.offer_action_fk
WHERE home_vector_alignment_score IS NOT NULL
  AND session_progress_ratio IS NOT NULL;
```

### Pill: "Profitability Funnel"
```sql
-- EPH funnel: from platform promise to holistic reality
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
  AND ml.eph_direct < 1000;
```

---

## 0005_The_Cost_of_Patience.py

### Tab: "Market Quadrants" (variable `query_moneymap`)
```sql
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
```

### Tab: "The CV(τ) Playbook" (variable `query_ven`)
```sql
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
```

No expander existed in "Market Quality Index" or "The Efficient Frontier" tabs — nothing to archive there.

---

## 0006_Payout_Physics_Causal_Inference.py

All 4 live inside `top_tab1` ("Analysis") → inner tabs.

### Tab: "Payout Stability" (variable `query_phase1`)
```sql
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
```

### Tab: "Heteroscedasticity Audit" (variable `query_phase2`)
```sql
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
```

### Tab: "Time-vs-Money Matrix" (variable `query_reality_check`)
```sql
SELECT
    o.upfront_fare,
    v.realized_fare,
    (o.est_trip_time_sec / 60.0) AS est_trip_time_min,
    (v.duration_trip_sec / 60.0) AS actual_trip_time_min
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
WHERE v.realized_fare IS NOT NULL 
AND o.est_trip_time_sec > 0
```

### Tab: "LOWESS Response Curve" (variable `query_fraud_prevention`)
```sql
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
```

No expander existed in "Polynomial Risk Model" — nothing to archive there.

**How to use:** when removing a "View SQL" block, leave the underlying query variable (`query_phase1`, `query_moneymap`, etc.) untouched — it's still used to fetch the chart data, only the `st.expander(...)`/`st.code(...)` display wrapper goes away. This file is only needed if you also delete the query variable itself and later want it back verbatim.
