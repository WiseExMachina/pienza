import streamlit as st
from pathlib import Path
from google.cloud import bigquery
from components.styles import GLOBAL_CSS

st.set_page_config(page_title="Exploratory SQL Sandbox | Pienza", page_icon="🔍", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

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
        st.page_link("pages/0004_Exploratory_SQL_Sandbox.py", label="Exploratory SQL Sandbox")
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
        st.page_link("pages/9000_Foundations_and_Architecture.py", label="Foundations & Architecture")
        st.page_link("pages/9000_Target_and_Feature_Engineering.py", label="Target and Feature Engineering")
        st.page_link("pages/9000_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox (legacy)")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                st.download_button("📄 Download 91-Page Report (PDF)", data=f.read(),
                                   file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

# ─────────────────────────────────────────────
# PAGE-LOCAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* stepper (house signature, page-local — mirrors Feature Store) */
.step-row    { display: flex; gap: 0; align-items: stretch; }
.step-spine  { display: flex; flex-direction: column; align-items: center; width: 44px; flex-shrink: 0; }
.step-circle { width: 30px; height: 30px; border-radius: 50%; color: #fff; font-size: 12px;
               font-weight: 700; display: flex; align-items: center; justify-content: center; z-index: 1; }
.step-line   { width: 2px; background: rgba(150,150,150,0.2); flex: 1; min-height: 16px; }
.step-body   { flex: 1; padding: 0 0 30px 14px; }
.step-label  { font-size: 15px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 3px; padding-top: 5px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.65; }
.step-why code { background: #f4f4f5; padding: 1px 5px; border-radius: 3px; font-size: 0.8rem; color: #21918c; }

/* linear financial chain */
.chain-flow  { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin: 6px 0 4px 0; }
.chain-node  { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 15px;
               font-family: 'Courier New', monospace; font-size: 0.8rem; font-weight: 700; color: #1a1a1a;
               box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.chain-arrow { display: flex; flex-direction: column; align-items: center; color: #21918c; line-height: 1; }
.chain-rel   { font-size: 0.58rem; font-weight: 700; color: #94a3b8; font-family: monospace; margin-bottom: 1px; }
.chain-glyph { font-size: 0.95rem; font-weight: 700; }

/* view-layer mini cards */
.view-grid   { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 10px; margin-top: 6px; }
.view-card   { background: #fff; border: 1px solid #eaeaea; border-radius: 9px; padding: 13px 15px; transition: all 0.2s ease; }
.view-card:hover { border-color: #21918c; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.view-name   { font-family: 'Courier New', monospace; font-size: 0.8rem; font-weight: 700; color: #21918c; margin-bottom: 3px; }
.view-desc   { font-size: 0.76rem; color: #666; line-height: 1.45; }

.sec-head    { font-size: 1.15rem; font-weight: 800; color: #1a1a1a; letter-spacing: -0.2px; margin: 6px 0 2px 0; }
.sec-sub     { font-size: 0.86rem; color: #888; margin: 0 0 16px 0; }

.stTextArea textarea {
    font-family: 'Courier New', Courier, monospace !important;
    background-color: #f8f8f8 !important; color: #121212 !important;
    border-left: 4px solid #21918c !important; font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BIGQUERY
# ─────────────────────────────────────────────
PROJECT = "645009831643"
DATASET = "pienza_mini"

@st.cache_resource
def get_bq_client():
    json_path = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

@st.cache_data(ttl=300)
def run_query(sql: str):
    try:
        return get_bq_client().query(sql).to_dataframe(), None
    except Exception as e:
        return None, str(e)

try:
    get_bq_client()
    _bq_ok = True
except Exception as _e:
    _bq_ok = False
    _bq_err = str(_e)

# ─────────────────────────────────────────────
# HEADER + BRIDGE
# ─────────────────────────────────────────────
st.markdown("# Exploratory SQL Sandbox")
st.markdown("""
<p style='color:#555;font-size:0.9rem;line-height:1.7;max-width:860px;'>
With the Feature Store fully defined, the project reconciled every offer against the platform's official
ledgers — earnings settlements and trip event logs — and certified the result as a relational Golden Master
through an idempotent ETL pipeline. That pipeline produced <code>pienza.db</code>, migrated to BigQuery
as <code>pienza_mini</code>.
</p>
<p style='color:#555;font-size:0.9rem;line-height:1.7;max-width:860px;margin-top:10px;'>
The financial chain is strictly linear — no circular references, truth flows only forward:
</p>
<div class='chain-flow' style='margin:10px 0 6px 0;'>
  <div class='chain-node'>offers</div>
  <div class='chain-arrow'><span class='chain-rel'>1:1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>trip_events</div>
  <div class='chain-arrow'><span class='chain-rel'>1:0..1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>lifetime_trips</div>
  <div class='chain-arrow'><span class='chain-rel'>1:1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>activity_earnings</div>
</div>
<p style='color:#555;font-size:0.9rem;line-height:1.7;max-width:860px;margin-top:14px;'>
Use the sandbox below to run your own queries against <code>pienza_mini</code> and explore the dataset
directly. The preset queries cover data lineage checkpoints — the full EDA suite will be added once
this module is complete.
</p>
""", unsafe_allow_html=True)

st.write("")

tab_sandbox, tab_context = st.tabs(["🔍 SQL Sandbox", "🗂️ Data & Architecture"])

# ─────────────────────────────────────────────
# TAB 1 — SQL SANDBOX
# ─────────────────────────────────────────────
with tab_sandbox:
    st.markdown("<div class='sec-sub'>Pick a starting query or write your own. Read-only — SELECT statements only.</div>", unsafe_allow_html=True)

    QUERIES = {
        "Decision & Product Mix": f"""-- Decision and product-category distribution
SELECT
    oa.offer_action_description AS action,
    pc.category_name            AS product,
    COUNT(*)                    AS n,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa     ON oa.offer_action_id = ml.offer_action_fk
LEFT JOIN `{PROJECT}.{DATASET}.product_category` pc ON pc.product_category_id = ml.product_category_fk
GROUP BY 1, 2
ORDER BY n DESC;""",

        "Mission Dossier (EPH)": f"""-- Per-trip KPIs: spread, EPH tiers (the Golden Link)
SELECT *
FROM `{PROJECT}.{DATASET}.v_mission_dossier`
LIMIT 25;""",

        "ML Feature Vector": f"""-- Canonical ML view: full feature vector
SELECT
    ml.offer_id,
    oa.offer_action_description AS str_action,
    pc.category_name            AS str_product,
    ml.eph_direct,
    ml.eph_operational,
    ml.eph_realized_ML,
    ml.eph_complete_ML,
    ml.consecutive_rejects,
    ml.time_since_last_offer,
    ml.cycle_cum_net_earnings
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa     ON oa.offer_action_id = ml.offer_action_fk
LEFT JOIN `{PROJECT}.{DATASET}.product_category` pc ON pc.product_category_id = ml.product_category_fk
LIMIT 25;""",

        "Lifecycle Audit": f"""-- GTS timestamps vs. platform server logs (delta validation)
SELECT *
FROM `{PROJECT}.{DATASET}.v_lifecycle_audit_accepted`
LIMIT 25;""",
    }

    selected = st.pills("", list(QUERIES.keys()), default=list(QUERIES.keys())[0],
                        key="sandbox_pill", label_visibility="collapsed")

    if "sandbox_sql" not in st.session_state or st.session_state.get("_last_pill") != selected:
        st.session_state.sandbox_sql = QUERIES[selected or list(QUERIES.keys())[0]]
        st.session_state._last_pill = selected

    query_input = st.text_area("SQL Editor", key="sandbox_sql", height=210, label_visibility="collapsed")

    if st.button("▶ Execute", type="primary"):
        if any(k in query_input.upper() for k in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE", "MERGE"]):
            st.error("Read-only mode — SELECT queries only.")
        elif not _bq_ok:
            st.error("BigQuery not connected.")
        else:
            with st.spinner("Querying pienza_mini…"):
                df, err = run_query(query_input)
                if err:
                    st.error(f"SQL Error: {err}")
                elif df is not None:
                    st.success(f"{len(df):,} rows returned.")
                    st.dataframe(df, use_container_width=True)

# ─────────────────────────────────────────────
# TAB 2 — DATA & ARCHITECTURE
# ─────────────────────────────────────────────
with tab_context:

    # Data Census
    st.markdown("<div class='sec-head'>Data Census</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-sub'>Operational baseline, live from <code>pienza_mini</code>.</div>", unsafe_allow_html=True)

    total_offers, accept_rate, n_sessions = "4,765", "7.26%", "—"

    if _bq_ok:
        census_sql = f"""
        SELECT
            COUNT(*)                                                       AS total_offers,
            ROUND(COUNTIF(oa.offer_action_description = 'accepted') * 100.0 / COUNT(*), 2) AS accept_rate,
            COUNT(DISTINCT ml.session_fk)                                  AS sessions
        FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
        LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa ON oa.offer_action_id = ml.offer_action_fk
        """
        df_c, err_c = run_query(census_sql)
        if df_c is not None and not df_c.empty:
            r = df_c.iloc[0]
            total_offers = f"{int(r['total_offers']):,}"
            accept_rate  = f"{r['accept_rate']}%"
            n_sessions   = f"{int(r['sessions']):,}"

    st.markdown(f"""
<div class="bento-grid">
  <div class="bento-card">
    <div class="bento-title">Telemetry Ledger</div>
    <div class="bento-value">{total_offers}</div>
    <div class="bento-desc">Total ride offers captured — accepted and rejected alike.</div>
  </div>
  <div class="bento-card">
    <div class="bento-title">Accept Rate</div>
    <div class="bento-value">{accept_rate}</div>
    <div class="bento-desc">Share of offers the agent accepted. The rest is the survivorship-bias-free negative class.</div>
  </div>
  <div class="bento-card">
    <div class="bento-title">Field Sessions</div>
    <div class="bento-value">{n_sessions}</div>
    <div class="bento-desc">Distinct driving sessions reconstructed from the telemetry stream.</div>
  </div>
  <div class="bento-card">
    <div class="bento-title">Reconciliation</div>
    <div class="bento-value">+/-1 MXN</div>
    <div class="bento-desc">Validated tolerance between internal telemetry and the official bank settlement ledger.</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if not _bq_ok:
        st.caption(f"BigQuery unreachable — showing paper baseline. ({_bq_err})")

    st.write("")
    st.divider()

    # ETL Lineage Stepper
    st.markdown("<div class='sec-head'>Data Lineage &amp; ETL Architecture</div>", unsafe_allow_html=True)
    st.markdown("<div class='sec-sub'>How raw OCR events became a fully reconciled, ML-ready relational database.</div>", unsafe_allow_html=True)

    def _step(letter, color, label, why, last=False):
        line = "" if last else "<div class='step-line'></div>"
        st.markdown(f"""
    <div class='step-row'>
      <div class='step-spine'>
        <div class='step-circle' style='background:{color}'>{letter}</div>
        {line}
      </div>
      <div class='step-body'>
        <div class='step-label' style='color:{color}'>{label}</div>
        <div class='step-why'>{why}</div>
      </div>
    </div>
        """, unsafe_allow_html=True)

    _step("L", "#21918c", "Official Ledger Integration",
          "Two platform exports were ingested as the source of truth: <code>lifetime_trips</code> "
          "(every trip state change — Request to Pickup to Dropoff) and <code>activity_earnings</code> "
          "(the definitive net-payout settlement log).")

    _step("R", "#21918c", "Reconciliation Audit · Outer Join",
          "The platform logs only successful transactions; the OCR stream logs the agent's <em>intent</em>. "
          "An Outer Join preserved System_Failure records absent from the official ledger — keeping them as valid "
          "ML data points and neutralizing survivorship bias in the positive class. Validated to ±1 MXN with "
          "GTS timestamps aligned to platform server logs.")

    _step("G", "#b45309", "The Golden Link · 2-Engine Match",
          "A matching cascade forged the join between <code>offers</code> and <code>trip_events</code>: "
          "Tier 1 exact (date + fare), Tier 2 fuzzy (rounded fare), Tier 3 orphan (unique fare within 24h). "
          "Edge-case Stolen Identity collisions were resolved by a manual remediation layer.")

    _step("T", "#7c3aed", "Idempotent ETL · Tabula Rasa",
          "Every run hard-deletes the binary, reinstantiates the schema from <code>schema.sql</code>, and fully "
          "reloads — no incremental drift, no ghost data. A WAL checkpoint + <code>os.fsync</code> certify "
          "<code>pienza.db</code> as Golden Master before migration to <code>pienza_mini</code> on BigQuery.",
          last=True)

    st.write("")

    # Linear financial chain
    st.markdown("<div style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;margin-bottom:6px;'>Linear Financial Chain · no circular references</div>", unsafe_allow_html=True)
    st.markdown("""
<div class='chain-flow'>
  <div class='chain-node'>offers</div>
  <div class='chain-arrow'><span class='chain-rel'>1:1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>trip_events</div>
  <div class='chain-arrow'><span class='chain-rel'>1:0..1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>lifetime_trips</div>
  <div class='chain-arrow'><span class='chain-rel'>1:1</span><span class='chain-glyph'>-></span></div>
  <div class='chain-node'>activity_earnings</div>
</div>
<p style='font-size:0.8rem;color:#888;margin-top:4px;'>Truth flows strictly forward — from the behavioral trigger to the bank settlement — so financial outcomes never feed back into the decision context.</p>
""", unsafe_allow_html=True)

    st.write("")

    # SQL View Architecture
    st.markdown("<div style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;margin-bottom:6px;'>SQL View Architecture · the intelligence layer</div>", unsafe_allow_html=True)
    st.markdown("""
<div class='view-grid'>
  <div class='view-card'><div class='view-name'>v_trip_funnel_wide</div><div class='view-desc'>Pivots the vertical event stream into one horizontal lifecycle row via MAX(CASE WHEN...).</div></div>
  <div class='view-card'><div class='view-name'>v_trip_final_kpis</div><div class='view-desc'>The Physics of Profitability — durations, Spread %, and all EPH tiers.</div></div>
  <div class='view-card'><div class='view-name'>v_mission_dossier</div><div class='view-desc'>The Golden Link: anchors every financial outcome to its originating offer_id.</div></div>
  <div class='view-card'><div class='view-name'>v_broche_fks</div><div class='view-desc'>FK lineage audit across all six layers, OCR to Earnings.</div></div>
  <div class='view-card'><div class='view-name'>v_offers_human</div><div class='view-desc'>Denormalized EDA surface — dimension tables resolved to readable labels.</div></div>
  <div class='view-card'><div class='view-name'>v_lifecycle_audit_accepted</div><div class='view-desc'>GTS vs. platform timestamp deltas for accepted offers.</div></div>
  <div class='view-card' style='border-color:#21918c;'><div class='view-name'>v_ML_Supervised</div><div class='view-desc'><strong>Canonical.</strong> The full ML feature vector — preferred over raw joins.</div></div>
</div>
""", unsafe_allow_html=True)

    st.write("")

    with st.expander("Relational Schema — full ERD (Vertabelo / RedGate)", expanded=False):
        erd_path = Path(__file__).resolve().parent.parent / "assets" / "Pienza_ERD.png"
        if erd_path.exists():
            st.image(str(erd_path), use_container_width=True, caption="Pienza — Definitive Star Schema")
        else:
            st.caption(f"ERD image not found at: {erd_path}")
