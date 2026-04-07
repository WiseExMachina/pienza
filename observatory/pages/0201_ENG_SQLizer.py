import streamlit as st
import pandas as pd
from google.cloud import bigquery
from pathlib import Path
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Data Architecture | Pienza")

OPUS_TEAL = '#21918c'

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    /* ARREGLO CSS: Fondo claro con letra negra obligatoria */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace !important;
        background-color: #f0f2f6 !important; 
        color: #121212 !important; 
        border-left: 4px solid #21918c !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SETUP CLIENTE BIGQUERY ---
@st.cache_resource
def get_bq_client():
    json_path = Path(__file__).resolve().parent.parent / "service-account.json"
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
st.title("🏛️ Phase 5: The Data Architecture")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Live SQL Sandbox & Entity-Relationship Model</span>**", unsafe_allow_html=True)
st.markdown("> From raw OCR telemetry to the Gold Medallion Layer. Explore the structural foundation of the Pienza Observatory.")
st.divider()

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