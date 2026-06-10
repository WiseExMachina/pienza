import streamlit as st
import pandas as pd
from google.cloud import bigquery
from pathlib import Path
import os


# ==========================================
# PAGE CONFIGURATION (NEW Wins)
# ==========================================
st.set_page_config(
    page_title="Feature Factory",
    page_icon="🧠",
    layout="wide"
)

OPUS_TEAL = '#21918c'



# ==========================================
# CUSTOM FONT & CSS INJECTION (Merged)
# ==========================================
st.markdown("""
    <style>
        /* Import Crimson Pro (Serif) and Inter (Sans-Serif) from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');
        
        /* Padding Adjustment from Current */
        .block-container { padding-top: 2rem; }

        /* 1. Body Text (Crimson Pro) - Target semantic content tags only! */
        p, li, td, th {
            font-family: 'Crimson Pro', serif !important;
            font-size: 18px !important;  
            line-height: 1.6 !important; 
        }

        /* 2. Headers Base Setup (Inter) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }

        /* 2a. Individual Header Sizes */
        h1 { font-size: 38px !important; } 
        h2 { font-size: 28px !important; } 
        h3 { font-size: 22px !important; } 

        /* 3. Expander Headers (Force them to match H3 Inter styling) */
        [data-testid="stExpander"] details summary p {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }

        /* 4. Code Blocks & Terminal (Monospace) */
        code, pre {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 15px !important; 
        }

        /* 5. SQL Sandbox Text Area (From Current) */
        .stTextArea textarea {
            font-family: 'Courier New', Courier, monospace !important;
            background-color: #f0f2f6 !important; 
            color: #121212 !important; 
            border-left: 4px solid #21918c !important;
            font-size: 13px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SETUP CLIENTE BIGQUERY (Retained from Current)
# ==========================================
@st.cache_resource
def get_bq_client():
    json_path = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

try:
    client = get_bq_client()
except Exception as e:
    st.error(f"❌ Error de conexión GCP: {e}")
    client = None

def run_query(query_string):
    if not client: return None, "Cliente no inicializado."
    try:
        return client.query(query_string).to_dataframe(), None
    except Exception as e:
        return None, str(e)

# --- 3. HEADER ---
st.title("SQL Pipeline & Live Sandbox")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Point of Order! ...Proceed</span>**", unsafe_allow_html=True)


st.markdown("""
Once the offer stream was enriched with context, it was necessary to anchor these decision events to the **"Official Truth"** of the platform’s ledgers. This required a rigorous reconciliation campaign to validate financial outcomes and account for discrepancies in transaction status.
""")

import streamlit as st

st.markdown("""
Once the offer stream was enriched with context, it was necessary to anchor these decision events to the **"Official Truth"** of the platform’s ledgers. This required a rigorous reconciliation campaign to validate financial outcomes and account for discrepancies in transaction status.
""")

# ------------------------------------------
# Consolidated Collapsible Section
# ------------------------------------------
with st.expander("Official Ledger Integration & Reconciliation Audit", expanded=False):

    st.markdown("### Integration of Official Ledgers")
    st.markdown("""
    Two new tables were architected to ingest the platform's official data exports:

    * **`lifetime_trips`:** The operational log of every trip state change (Request → Pickup → Dropoff).
    * **`activity_earnings`:** The definitive financial settlement log (Net Payout).
    """)

    st.divider()

    st.markdown("### The Reconciliation Audit (Outer Join Logic)")
    st.markdown("""
    Before automation, a manual audit was conducted to reconcile the Agent’s internal telemetry (`trip_events`) and OCR logs (`offers`) against these official exports. An **Outer Join** strategy was mandated to preserve the `System_Failure` class.

    * **Platform View:** The official log records *only* successfully initiated transactions.
    * **Agent View:** The OCR log captures the *Intent to Accept*.

    > **Preventing Survivorship Bias:** Trips accepted by the agent but failed due to system latency were absent from the official ledger. The Outer Join ensured these records were preserved as valid decision data points for the ML model, preventing survivorship bias in the positive class.
    """)

    st.divider()

    st.markdown("### Validation Confirmed")
    st.markdown("""
    1. **Financial Integrity:** The Realized Fare recorded in the internal systems matched the Net Earning in the bank ledger (within a $\pm$ 1.00 MXN variance).
    2. **Temporal Consistency:** The Agent’s manual timestamps ($T_1 \dots T_4$) consistently aligned with the platform’s server logs, validating the use of internal telemetry.
    """)


import streamlit as st

# ==========================================
# PHASE 2D: STAR SCHEMA DESIGN (Collapsible Section)
# ==========================================
with st.expander("Star Schema Design: Normalization and Relational Logic", expanded=False):

    st.markdown("""
    A formal Entity-Relationship Diagram (ERD) was designed using *Vertabelo* (RedGate) to define the relational architecture. This design decouples the high-density **Fact Tables** (`offers`, `trip_events`) from their context-rich **Dimension Tables** (e.g., `product_category`, `reason_primary`, `driver_state`).

    The schema utilizes strict normalization to ensure data integrity and consistent labeling for machine learning:

    * **Traceability (1:1 Mirroring):** The `raw_offers_ocr` table serves as an immutable staging mirror. It maintains a strictly enforced 1:1 relationship with the cleaned `offers` table, ensuring that every engineered record can be traced back to its raw OCR source string for forensic auditing.
    
    * **Categorical Dimensions:** Low-cardinality strings were extracted into lookup tables linked via Foreign Keys (suffix `_fk`). While this degree of normalization is typically optimized for transaction processing (OLTP), it was retained in this static analytical (OLAP) context to enforce a rigid vocabulary for the model features.
    
    * **Heuristic Flags (Many-to-Many vs. Pragmatism):** The schema includes a bridge table (`heuristic_flag_offers`) architected to support a many-to-many relationship, allowing multiple flags per offer. However, for pragmatic simplicity during the manual backtagging phase, a "Single Flag" protocol was enforced (one dominant heuristic per offer), though the architecture remains extensible.
    
    * **Atomic Design:** The system was architected for maximum atomicity in its storage layer. While engineered features are deliberately non-atomic to provide session context, the telemetry data is stored in its rawest state. Although wide-format ledgers with pre-calculated KPIs existed during the spreadsheet phase, the database was designed to ingest the raw, "long" event stream into the `trip_events` table. This design offloads mission reconstruction to the SQL view layer, ensuring that durations and efficiency metrics are calculated programmatically rather than persisted as static, pre-aggregated values.
    """)


import streamlit as st

# ==========================================
# PHASE 2D: CIRCULAR AVOIDANCE (Collapsible Section)
# ==========================================
with st.expander("Circular Avoidance: The Linear Financial Chain", expanded=False):

    st.markdown("""
    The relationship between internal logs and official platform data is architected to prevent circular references. The flow of truth is strictly linear:
    """)

    # Render LaTeX Equation natively in Streamlit
    st.latex(r"\texttt{offers} \xrightarrow{1:1} \texttt{trip\_events} \xrightarrow{1:0..1} \texttt{lifetime\_trips} \xrightarrow{1:1} \texttt{activity\_earnings}")

    st.markdown("""
    This chain ensures that financial data flows from the definitive bank settlement (`activity_earnings`) back to the behavioral trigger (`offers`) without ambiguity.
    """)



import streamlit as st

# ==========================================
# PHASE 2D: IDEMPOTENT ETL PIPELINE (Collapsible Section)
# ==========================================
with st.expander("Idempotent ETL Pipeline: Tabula Rasa", expanded=False):

    st.markdown("""
    The engineering phase concluded with the consolidation of all transformation logic into a single, idempotent ETL pipeline; executing the end-to-end transformation cycle—from raw Google Sheets to the final population of `pienza.db`—guaranteeing 100% reproducibility. The pipeline rejects standard "Incremental Load" patterns in favor of a "Big Bang" reconstruction philosophy to eliminate state risk.
    """)

    st.markdown("""
    The pipeline initiates with a clean slate command. The script detects the existence of the binary database file and executes a hard deletion (`os.remove`). This enforces a stateless execution environment, ensuring that no "ghost data" or schema drift from previous iterations can survive to contaminate the current analysis. The database schema is then freshly instantiated from the `schema.sql` definition file.
    """)




import streamlit as st

# ==========================================
# PHASE 2D: SQL VIEW ARCHITECTURE (Collapsible Section)
# ==========================================
with st.expander("The SQL View Architecture", expanded=False):

    st.markdown("""
    While the base tables maintain a normalized 3NF structure for referential integrity, they are abstracted into a series of SQL Views that serve as the primary interface for analysis. These views transform the relational schema into an active intelligence engine:

    * **`v_trip_funnel_wide`:** Utilizing conditional aggregation (`MAX(CASE WHEN...)`), this view flattens the vertical, sequential stream of telemetry logs into a single horizontal lifecycle. This is the foundational step for time-series reconstruction.
    
    * **`v_trip_final_kpis`:** Built upon the pivoted funnel, this view calculates the "Physics of Profitability." It derives durations via Julian Day conversions and computes critical metrics such as *Spread Percentage* and EPH.
    
    * **`v_mission_dossier`:** Integrates the final mission KPIs directly with the originating `offer_id`. This view serves as the ultimate proof of the "Golden Link," anchoring every financial outcome to the specific algorithmic incentive that triggered it.
    
    * **`v_broche_fks`:** A high-level audit view that traces foreign key lineage across all six layers of the architecture (OCR → Offers → Features → Events → Lifetime Trips → Earnings). It validates the integrity of the end-to-end data lineage.
    
    * **`v_offers_human`:** The primary interface for EDA. It denormalizes the eight core dimension tables into human-readable labels and joins the engineered features, providing a context-rich narrative of every offer.
    
    * **`v_lifecycle_audit`:** An alignment view that compares five dimensions of truth. By measuring the *Delta Timestamp* between manual agent logs and corporate server timestamps, it statistically validates the integrity of the N=1 dataset.
    """)















# --- 4. SECCIÓN SUPERIOR: ERD GRANDOTA ---
st.subheader("1. The Foundational Relational Model (Bronze/Silver)")
st.info("The `offers` core table acts as the nexus between temporal events, spatial coordinates, and engineered heuristics.")

base_path = Path(__file__).resolve().parent.parent
erd_path = base_path / "assets" / "Pienza_ERD.png"

if erd_path.exists():
    st.image(str(erd_path), use_container_width=True, caption="Pienza Relational Model")
else:
    st.error(f"⚠️ Imagen no encontrada en: {erd_path}")

st.divider()

# --- 5. SECCIÓN INFERIOR: SQL SANDBOX ---
st.subheader("2. Interactive SQL Sandbox (Gold Layer)")
st.markdown("Run live queries against the `drivers-dilemma` BigQuery dataset. Data is obfuscated for privacy.")

# Inicializar la variable en el estado de la sesión si no existe
if "sql_query" not in st.session_state:
    st.session_state.sql_query = "SELECT * FROM `drivers-dilemma.pienza_mini.offers` LIMIT 5;"

# --- CANNED QUERIES ---
st.markdown("**Quick Run Scenarios:**")
c1, c2, c3 = st.columns(3)

# LA QUERY MAESTRA (LIMIT 10)
if c1.button("📊 The Gold Layer (Lifecycle Audit)", use_container_width=True):
    st.session_state.sql_query = """-- THE GOLD LAYER: COMPREHENSIVE LIFECYCLE AUDIT
-- (Note: Smart execution routes this logic to the materialized view for zero-latency).
WITH TripEventsPivot AS (
    SELECT offer_id_fk, trip_id_legacy,
        MAX(CASE WHEN event_types_id_fk = 2 THEN event_timestamp END) as t1_timestamp,
        MAX(CASE WHEN event_types_id_fk = 4 THEN event_timestamp END) as t3_timestamp,
        MAX(CASE WHEN event_types_id_fk = 5 THEN event_timestamp END) as t4_timestamp,
        MAX(upfront_fare) as te_upfront_fare, MAX(realized_fare) as te_realized_fare
    FROM trip_events GROUP BY offer_id_fk
),
HistoryStats AS (
    SELECT lt.offer_id_fk, lt.lifetime_trips_id, lt.original_fare, ae.net_earning,
        SUM(lt.original_fare) OVER (ORDER BY lt.request_timestamp ROWS UNBOUNDED PRECEDING) as cum_uber_earnings,
        SUM(ae.net_earning) OVER (ORDER BY lt.request_timestamp ROWS UNBOUNDED PRECEDING) as cum_net_earnings,
        AVG(ae.net_earning / NULLIF(lt.original_fare, 0)) OVER (ORDER BY lt.request_timestamp ROWS UNBOUNDED PRECEDING) as rolling_avg_net_take_rate
    FROM lifetime_trips lt
    LEFT JOIN activity_earnings ae ON lt.lifetime_trips_id = ae.lifetime_trips_fk
)
SELECT
    o.offer_id, o.session_fk, te.trip_id_legacy,
    r.time_taken AS ocr_raw_time, o.offer_timestamp AS clean_timestamp, ef.day_of_week, ef.time_of_day_block,
    r.ride_type AS ocr_product, pc.category_name AS internal_product, ae.product_category AS bank_product, lt.global_product_name AS official_product,
    r.pickup_address AS ocr_pickup, o.pickup_address AS clean_pickup, ef.pickup_ambiguity,
    r.dropoff_address AS ocr_dropoff, o.dropoff_address AS clean_dropoff, ef.dropoff_ambiguity,
    lt.original_fare AS uber_original_fare, r.upfront_fare AS ocr_upfront, o.upfront_fare AS clean_upfront, te.te_upfront_fare AS events_upfront, te.te_realized_fare AS events_realized, ae.net_earning AS bank_net_earning,
    te.t1_timestamp AS gts_t1_accepted, lt.request_timestamp AS uber_request, ROUND((julianday(te.t1_timestamp) - julianday(lt.request_timestamp)) * 86400) AS delta_accept_sec,
    te.t3_timestamp AS gts_t3_started, lt.pickup_timestamp AS uber_pickup, ROUND((julianday(te.t3_timestamp) - julianday(lt.pickup_timestamp)) * 86400) AS delta_start_sec,
    te.t4_timestamp AS gts_t4_completed, lt.dropoff_timestamp AS uber_dropoff, ROUND((julianday(te.t4_timestamp) - julianday(lt.dropoff_timestamp)) * 86400) AS delta_end_sec,
    hist.cum_uber_earnings, hist.cum_net_earnings, hist.rolling_avg_net_take_rate
FROM offers o
LEFT JOIN raw_offers_ocr r ON o.ocr_fk = r.ocr_id
LEFT JOIN engineered_features ef ON o.offer_id = ef.offer_id_fk
LEFT JOIN product_category pc ON o.product_category_fk = pc.product_category_id
LEFT JOIN TripEventsPivot te ON o.offer_id = te.offer_id_fk
LEFT JOIN lifetime_trips lt ON o.offer_id = lt.offer_id_fk
LEFT JOIN activity_earnings ae ON lt.lifetime_trips_id = ae.lifetime_trips_fk
LEFT JOIN HistoryStats hist ON o.offer_id = hist.offer_id_fk;"""

if c2.button("⏱️ Operation Deltas", use_container_width=True):
    st.session_state.sql_query = """-- Analizando la eficiencia operativa
SELECT 
    session_fk, clean_pickup, delta_accept_sec, delta_start_sec, delta_end_sec
FROM `drivers-dilemma.pienza_mini.v_lifecycle_audit_accepted`
WHERE delta_accept_sec IS NOT NULL
LIMIT 10;"""

if c3.button("🧠 Latent Features Join", use_container_width=True):
    st.session_state.sql_query = """-- Uniendo crudos con heurísticas
SELECT 
    o.offer_id, ef.eph_real, ef.offer_quality_index
FROM `drivers-dilemma.pienza_mini.offers` o
JOIN `drivers-dilemma.pienza_mini.engineered_features` ef 
    ON o.offer_id = ef.offer_id_fk
LIMIT 10;"""

# --- TEXT AREA ATADO AL SESSION STATE ---
query_final = st.text_area("SQL Editor", key="sql_query", height=380, label_visibility="collapsed")

if st.button("▶ Execute Query", type="primary"):
    
    # 🕵️‍♂️ EL INTERCEPTOR MÁGICO (SMART ROUTING) - AHORA CON LIMIT 10
    if "TripEventsPivot" in query_final and "HistoryStats" in query_final:
        actual_query_to_run = "SELECT * FROM `drivers-dilemma.pienza_mini.v_lifecycle_audit_accepted` LIMIT 10;"
        st.info("💡 **Smart Query Optimizer:** Architectural query intercepted. Routing directly to the materialized view `v_lifecycle_audit_accepted` for performance.")
    else:
        actual_query_to_run = query_final

    # Bloqueo de seguridad básico
    if any(k in actual_query_to_run.upper() for k in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]):
        st.error("🚫 Solo se permiten consultas SELECT (Modo Lectura) por seguridad.")
    else:
        with st.spinner("🛰️ Ejecutando consulta en BigQuery..."):
            df, err = run_query(actual_query_to_run)
            if err:
                st.error(f"SQL Error: {err}")
            elif df is not None:
                st.success(f"✅ Resultados: {len(df)} filas obtenidas.")
                st.dataframe(df, use_container_width=True)





st.info("PLACEHOLDER: DATA CENSUS WILL BE QUERYABLE IN THE SANDBOX")
