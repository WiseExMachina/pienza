---
name: project-bigquery
description: "BigQuery project ID, dataset, tables, canonical views, join patterns, and auth"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4c7fa891-5c41-4c2c-a190-97de71bc34d3
---

- **Project ID:** `645009831643`
- **Dataset:** `pienza_mini`
- **Auth:** observatory/.streamlit/service-account.json (set via GOOGLE_APPLICATION_CREDENTIALS)
- **Schema reference:** assets/drivers-dilemma_pienza-mini_schema_2026-06-18.json — always consult before writing any BQ query

## Key tables

- `raw_offers_ocr` — OCR output, keyed by `ocr_id`, has `image_filename`
- `offers` — canonical offer record, `offer_id` PK
- `engineered_features` — Silver stateful features, FK `offer_id_fk`
- `silver_palette` — Gold geo + volatility features, FK `offer_id`
- `trip_events` — has `realized_fare`, `upfront_fare` per event; FK `offer_id_fk`

## Key views (prefer over raw joins)

- `v_ML_Supervised` — canonical: offers + engineered_features + silver_palette. Has `consecutive_rejects`. Does NOT have `str_*` fields.
- `v_offers_human` — human-readable with `str_action`/`str_product`/`str_reason`/`str_driver_state`. Lacks `consecutive_rejects`.
- `v_lifecycle_audit_accepted` — accepted offers with GTS event timestamps and earnings
- `v_mission_dossier` — per-trip KPIs: `spread_percentage`, `eph_on_ride`, `eph_total_time`

## Canonical join pattern (v_ML_Supervised + str_* fields)

```sql
FROM `645009831643.pienza_mini.v_ML_Supervised` ml
LEFT JOIN `645009831643.pienza_mini.offer_action` oa       ON oa.offer_action_id = ml.offer_action_fk
LEFT JOIN `645009831643.pienza_mini.product_category` pc   ON pc.product_category_id = ml.product_category_fk
LEFT JOIN `645009831643.pienza_mini.reason_primary` rp     ON rp.reason_primary_id = ml.reason_primary_fk
LEFT JOIN `645009831643.pienza_mini.driver_state_at_request` ds ON ds.driver_state_at_request_id = ml.driver_state_at_request_fk
```

**How to apply:** Always verify exact column names against the schema JSON before writing queries.
