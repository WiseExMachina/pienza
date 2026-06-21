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

with st.expander("Relational Schema — full ERD (Vertabelo / RedGate)", expanded=False):
    erd_path = Path(__file__).resolve().parent.parent / "assets" / "Pienza_ERD.png"
    if erd_path.exists():
        st.image(str(erd_path), use_container_width=True, caption="Pienza — Definitive Star Schema")
    else:
        st.caption(f"ERD image not found at: {erd_path}")

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

        "Data Census": f"""-- Categorical census: action, product, rejection reason, outcome
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

    selected = st.pills("", list(QUERIES.keys()), default=list(QUERIES.keys())[0],
                        key="sandbox_pill", label_visibility="collapsed")

    active_pill = selected or list(QUERIES.keys())[0]
    active_sql  = QUERIES[active_pill]

    with st.expander("View SQL", expanded=False):
        st.code(active_sql, language="sql")

    if not _bq_ok:
        st.error("BigQuery not connected.")
    else:
        with st.spinner("Querying pienza_mini…"):
            df, err = run_query(active_sql)
            if err:
                st.error(f"SQL Error: {err}")
            elif df is not None:
                if selected == "Data Census":
                    import plotly.graph_objects as go
                    import re as _re

                    def _clean_label(s):
                        if s is None:
                            return s
                        s = _re.sub(r'(?i)uber_?', '', str(s)).strip('_').strip()
                        return s if s else str(s)

                    df_action  = df[df["dimension"] == "action"].copy()
                    df_product = df[df["dimension"] == "product"].copy()
                    df_reason  = df[df["dimension"] == "reason"].copy()
                    df_outcome = df[df["dimension"] == "outcome"].copy()

                    df_product["label"] = df_product["label"].apply(_clean_label)
                    df_reason["label"]  = df_reason["label"].apply(
                        lambda v: "NaN (accepted)" if v is None or str(v) in ("None", "nan", "") else _clean_label(v)
                    )
                    df_outcome["label"] = df_outcome["label"].apply(
                        lambda v: "NaN (rejected)" if v is None or str(v) in ("None", "nan", "") else _clean_label(v)
                    )

                    TEAL  = "#21918c"
                    TEAL2 = "#2db3ad"
                    GRAY  = "#94a3b8"

                    CALLOUT = """
<div style='border-left:4px solid #21918c;background:#f0faf9;border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>Class imbalance</strong> — The 93/7 split mirrors operational reality and was handled via
  <strong>Stratified K-Fold</strong> and the <strong>Cognitive Cascade</strong> architecture.
  <code>system_logic_failure</code> (5 records) was dropped downstream — pure noise, not a behavioral signal.
</div>"""

                    if selected == "Data Census":
                        # ── A: Donut + 2 horizontal bars ──
                        ACTION_COLORS = {"accepted": TEAL, "reject": GRAY}
                        fig1 = go.Figure(go.Pie(
                            labels=df_action["label"], values=df_action["n"],
                            hole=0.55,
                            marker_colors=[ACTION_COLORS.get(l, GRAY) for l in df_action["label"]],
                            textinfo="percent", textfont_size=12,
                            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
                        ))
                        fig1.update_layout(
                            title=dict(text="Accept vs. Reject", font_size=14, x=0.5, xanchor="center"),
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font_size=11),
                            height=300,
                            margin=dict(l=10, r=10, t=40, b=10),
                            paper_bgcolor="white", font_family="Inter",
                        )
                        df_p = df_product.sort_values("n")
                        fig2 = go.Figure(go.Bar(
                            x=df_p["n"], y=df_p["label"], orientation="h",
                            marker_color=TEAL,
                            text=df_p["n"].apply(lambda v: f"{v:,}"), textposition="outside",
                            hovertemplate="%{y}: %{x:,}<extra></extra>",
                        ))
                        fig2.update_layout(
                            title=dict(text="Product Mix", font_size=14, x=0.5, xanchor="center"),
                            xaxis=dict(showgrid=False, showticklabels=False, range=[0, df_p["n"].max() * 1.25]),
                            yaxis=dict(tickfont_size=11), height=300,
                            margin=dict(l=10, r=20, t=40, b=10),
                            paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        )
                        df_r = df_reason[df_reason["label"].notna()].sort_values("n")
                        fig3 = go.Figure(go.Bar(
                            x=df_r["n"], y=df_r["label"], orientation="h",
                            marker_color=TEAL2,
                            text=df_r["n"].apply(lambda v: f"{v:,}"), textposition="outside",
                            hovertemplate="%{y}: %{x:,}<extra></extra>",
                        ))
                        fig3.update_layout(
                            title=dict(text="Rejection Reasons", font_size=14, x=0.5, xanchor="center"),
                            xaxis=dict(showgrid=False, showticklabels=False, range=[0, df_r["n"].max() * 1.25]),
                            yaxis=dict(tickfont_size=11), height=320,
                            margin=dict(l=10, r=20, t=40, b=10),
                            paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        )
                        df_o = df_outcome.sort_values("n")
                        fig4 = go.Figure(go.Bar(
                            x=df_o["n"], y=df_o["label"], orientation="h",
                            marker_color=TEAL,
                            text=df_o["n"].apply(lambda v: f"{v:,}"), textposition="outside",
                            hovertemplate="%{y}: %{x:,}<extra></extra>",
                        ))
                        fig4.update_layout(
                            title=dict(text="Accepted Class — Trip Outcomes", font_size=14, x=0.5, xanchor="center"),
                            xaxis=dict(showgrid=False, showticklabels=False, range=[0, df_o["n"].max() * 1.25]),
                            yaxis=dict(tickfont_size=11), height=300,
                            margin=dict(l=10, r=20, t=40, b=10),
                            paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        )
                        c1, c2 = st.columns(2)
                        with c1: st.plotly_chart(fig1, use_container_width=True)
                        with c2: st.plotly_chart(fig2, use_container_width=True)
                        c3, c4 = st.columns(2)
                        with c3: st.plotly_chart(fig3, use_container_width=True)
                        with c4: st.plotly_chart(fig4, use_container_width=True)
                        st.markdown(CALLOUT, unsafe_allow_html=True)

                elif selected == "Incentives":
                    import plotly.graph_objects as go
                    import numpy as np

                    TEAL  = "#21918c"
                    TEAL2 = "#2db3ad"
                    GRAY  = "#94a3b8"

                    INCENTIVES = [
                        ("is_surge",       "surge_amount",       "Surge"),
                        ("is_turbo_plus",  "turbo_plus_amount",  "Turbo+"),
                        ("is_reservation", "reservation_amount", "Reservation"),
                    ]
                    COLORS = [TEAL, TEAL2, "#5a9e9a"]

                    # ── CHART 1: Grouped prevalence bars (present vs absent per incentive) ──
                    st.markdown("<p style='font-weight:600;font-size:1rem;margin:8px 0 4px'>Prevalence — present vs. absent for each incentive type</p>", unsafe_allow_html=True)
                    total = len(df)
                    inc_labels = [l for _, _, l in INCENTIVES]
                    pct_present = []
                    pct_absent  = []
                    hover_present = []
                    hover_absent  = []
                    for (flag, _, label), color in zip(INCENTIVES, COLORS):
                        active = int(df[flag].sum()) if flag in df.columns else 0
                        pct_present.append(round(active / total * 100, 1))
                        pct_absent.append(round((total - active) / total * 100, 1))
                        hover_present.append(f"{label} present: {active:,} ({active/total*100:.1f}%)")
                        hover_absent.append(f"{label} absent: {total-active:,} ({(total-active)/total*100:.1f}%)")
                    fig1 = go.Figure()
                    fig1.add_trace(go.Bar(
                        name="Present", x=inc_labels, y=pct_present,
                        marker_color=TEAL,
                        text=[f"{v:.1f}%" for v in pct_present], textposition="outside",
                        hovertext=hover_present, hoverinfo="text",
                    ))
                    fig1.add_trace(go.Bar(
                        name="Absent", x=inc_labels, y=pct_absent,
                        marker_color=GRAY,
                        text=[f"{v:.1f}%" for v in pct_absent], textposition="outside",
                        hovertext=hover_absent, hoverinfo="text",
                    ))
                    fig1.update_layout(
                        barmode="group", height=300,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font_size=11),
                        yaxis=dict(showgrid=False, showticklabels=False, range=[0, 120]),
                        xaxis=dict(tickfont_size=12),
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                    # ── CHART 2: Box plots of amounts when active ──
                    st.markdown("<p style='font-weight:600;font-size:1rem;margin:16px 0 4px'>Amount — distribution when incentive was active (MXN)</p>", unsafe_allow_html=True)
                    fig2 = go.Figure()
                    for (flag, amt_col, label), color in zip(INCENTIVES, COLORS):
                        vals = df.loc[df[flag] == 1, amt_col].dropna().tolist() if flag in df.columns else []
                        if vals:
                            fig2.add_trace(go.Box(
                                y=vals, name=label,
                                marker_color=color, line_color="#1a6b67",
                                boxmean=True,
                                hovertemplate="%{y:.1f} MXN<extra>" + label + "</extra>",
                            ))
                    fig2.update_layout(
                        height=320, showlegend=False,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        yaxis=dict(title="MXN", gridcolor="#f0f0f0"),
                        xaxis=dict(tickfont_size=12),
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                    # ── CHART 3: Co-occurrence heatmap ──
                    st.markdown("<p style='font-weight:600;font-size:1rem;margin:16px 0 4px'>Co-occurrence — how often incentives appear together</p>", unsafe_allow_html=True)
                    flags = [f for f, _, _ in INCENTIVES]
                    labels = [l for _, _, l in INCENTIVES]
                    matrix = []
                    for f1 in flags:
                        row = []
                        for f2 in flags:
                            count = int(((df[f1] == 1) & (df[f2] == 1)).sum()) if f1 in df.columns and f2 in df.columns else 0
                            row.append(count)
                        matrix.append(row)
                    fig3 = go.Figure(go.Heatmap(
                        z=matrix, x=labels, y=labels,
                        colorscale=[[0, "#f0faf9"], [1, TEAL]],
                        text=[[f"{v:,}" for v in row] for row in matrix],
                        texttemplate="%{text}", textfont=dict(size=14),
                        showscale=False,
                        hovertemplate="%{y} ∩ %{x}: %{z:,} offers<extra></extra>",
                    ))
                    fig3.update_layout(
                        height=280,
                        margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                        xaxis=dict(tickfont_size=12),
                        yaxis=dict(tickfont_size=12, autorange="reversed"),
                    )
                    col_h, _ = st.columns([1, 1])
                    with col_h:
                        st.plotly_chart(fig3, use_container_width=True)

                elif selected == "Traffic Index":
                    import plotly.graph_objects as go
                    import numpy as np

                    TEAL  = "#21918c"
                    TEAL2 = "#2db3ad"
                    TEAL3 = "#5a9e9a"
                    GRAY  = "#94a3b8"

                    CLASSES = [
                        (None, 1.0,  "Super Fluid",  "10km in 15 min — Highway"),
                        (1.0,  1.5,  "Normal",       "10km in 25 min — Flowing city"),
                        (1.5,  2.0,  "Heavy",        "10km in 35 min — Dense traffic"),
                        (2.0,  3.0,  "Gridlock",     "10km in 50 min — Crawling"),
                        (3.0,  None, "Sólo en CDMX", "10km in >1 hour — Parking lot"),
                    ]
                    CLASS_COLORS = [TEAL, TEAL2, TEAL3, GRAY, "#475569"]

                    # ── Hour filter ──
                    all_hours = sorted(df["hour_of_day"].dropna().unique().astype(int).tolist())
                    hour_range = st.slider(
                        "Filter by hour of day", min_value=int(min(all_hours)),
                        max_value=int(max(all_hours)), value=(int(min(all_hours)), int(max(all_hours))),
                        key="traffic_hour_slider",
                    )
                    df_t = df[
                        (df["hour_of_day"] >= hour_range[0]) &
                        (df["hour_of_day"] <= hour_range[1])
                    ]
                    vals = df_t["traffic_index_base_120"].dropna().values
                    total = len(vals)

                    if total == 0:
                        st.warning("No data for selected hour range.")
                    else:
                        # ── CHART 1: Histogram ──
                        counts, bin_edges = np.histogram(vals, bins=50)
                        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                        fig1 = go.Figure()
                        fig1.add_trace(go.Bar(
                            x=bin_centers, y=counts,
                            marker_color=TEAL, opacity=0.8,
                            hovertemplate="index %{x:.2f}: %{y:,} offers<extra></extra>",
                        ))
                        for tv, tl in zip([1.0, 1.5, 2.0, 3.0], ["Normal", "Heavy", "Gridlock", "Sólo en CDMX"]):
                            fig1.add_vline(x=tv, line_dash="dash", line_color=GRAY, line_width=1.2,
                                           annotation_text=tl, annotation_position="top",
                                           annotation_font=dict(size=9, color="#64748b"))
                        fig1.update_layout(
                            title=dict(text="Traffic Index Distribution", font_size=14, x=0.5, xanchor="center"),
                            height=320, showlegend=False,
                            margin=dict(l=10, r=10, t=50, b=10),
                            paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                            xaxis=dict(title="Traffic Index  (1.0 = 2 min/km baseline)", gridcolor="#f0f0f0"),
                            yaxis=dict(title="Offers", gridcolor="#f0f0f0"),
                        )

                        # ── CHART 2: Class breakdown ──
                        sem_labels, sem_counts, sem_anchors = [], [], []
                        for lo, hi, label, anchor in CLASSES:
                            mask = np.ones(len(vals), dtype=bool)
                            if lo is not None: mask &= (vals >= lo)
                            if hi is not None: mask &= (vals < hi)
                            sem_labels.append(label)
                            sem_counts.append(int(mask.sum()))
                            sem_anchors.append(anchor)

                        fig2 = go.Figure(go.Bar(
                            x=sem_labels, y=sem_counts,
                            marker_color=CLASS_COLORS,
                            text=[f"{n:,}  {n/total*100:.1f}%" for n in sem_counts],
                            textposition="outside",
                            hovertemplate="<b>%{x}</b><br>%{y:,} offers<extra></extra>",
                        ))
                        fig2.update_layout(
                            title=dict(text="Operational Conditions", font_size=14, x=0.5, xanchor="center"),
                            height=320, showlegend=False,
                            margin=dict(l=10, r=10, t=50, b=10),
                            paper_bgcolor="white", plot_bgcolor="white", font_family="Inter",
                            yaxis=dict(showgrid=False, showticklabels=False, range=[0, max(sem_counts) * 1.3]),
                            xaxis=dict(tickfont_size=11),
                        )

                        c1, c2 = st.columns(2)
                        with c1: st.plotly_chart(fig1, use_container_width=True)
                        with c2: st.plotly_chart(fig2, use_container_width=True)

                        legend_items = "".join([
                            f"""<div style='display:flex;align-items:center;gap:6px;white-space:nowrap;'>
                              <div style='width:10px;height:10px;border-radius:2px;background:{color};flex-shrink:0;'></div>
                              <span style='font-size:0.78rem;color:#334155;'><strong>{label}</strong> — {anchor}</span>
                            </div>"""
                            for (_, _, label, anchor), color in zip(CLASSES, CLASS_COLORS)
                        ])
                        st.markdown(
                            f"<div style='display:flex;flex-wrap:wrap;justify-content:center;gap:12px 24px;"
                            f"padding:10px 14px;background:#f8f8f8;border-radius:8px;margin-bottom:10px;'>{legend_items}</div>",
                            unsafe_allow_html=True)

                        st.markdown("""
<div style='border-left:4px solid #21918c;background:#f0faf9;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>Note:</strong> These charts reflect the <em>expected</em> traffic conditions shown on the offer card at the moment of decision.
  Realized traffic — what people in Mexico City actually experience — is generally worse.
</div>""", unsafe_allow_html=True)

                        st.markdown("""
<div style='border:3px solid #FFD700;background:#FFFF00;border-radius:8px;
     padding:14px 18px;margin-top:12px;font-size:0.82rem;color:#1a1a1a;line-height:1.65;'>
  <strong>🚧 Coming soon — Traffic Volatility</strong><br>
  Expected conditions are only half the story. The Gold-layer <code>traffic_volatility_index</code> captures
  how unpredictable conditions were relative to the historical baseline — completing the picture of what the
  driver was actually betting on when accepting or rejecting an offer.
</div>""", unsafe_allow_html=True)

                elif selected == "Home Vector":
                    import altair as alt
                    import pandas as pd

                    TEAL = "#21918c"
                    GRAY = "#94a3b8"

                    scores = df["home_vector_alignment_score"].dropna().values
                    total  = len(scores)

                    homeward = int((scores >  0.5).sum())
                    neutral  = int(((scores >= -0.5) & (scores <= 0.5)).sum())
                    away     = int((scores < -0.5).sum())

                    # ── Metric cards ──
                    cards = [
                        ("Away",      "< -0.5",          away,     "#78716c","Offers pulling the driver further from home"),
                        ("Neutral",   "-0.5 to +0.5",    neutral,  "#64748b","Offers with no strong directional bias"),
                        ("Homeward",  "> 0.5",           homeward, TEAL,    "Offers moving the driver toward home base"),
                    ]
                    c1, c2, c3 = st.columns(3)
                    for col, (label, rng, n, color, desc) in zip([c1, c2, c3], cards):
                        pct = n / total * 100
                        with col:
                            st.markdown(f"""
<div style='background:#fff;border:1px solid #e2e8f0;border-top:3px solid {color};
     border-radius:8px;padding:14px 16px;'>
  <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;
       color:#94a3b8;margin-bottom:4px;'>{rng}</div>
  <div style='font-size:0.85rem;font-weight:600;color:#334155;margin-bottom:8px;'>{label}</div>
  <div style='font-size:1.55rem;font-weight:800;color:{color};line-height:1;'>{pct:.1f}%</div>
  <div style='font-size:0.68rem;color:#94a3b8;margin-top:3px;'>{n:,} of {total:,} offers</div>
  <div style='font-size:0.68rem;color:#b0bec5;margin-top:5px;line-height:1.4;'>{desc}</div>
</div>""", unsafe_allow_html=True)

                    st.write("")

                    # ── Altair histogram + KDE + zone bands ──
                    df_vec = df[["home_vector_alignment_score"]].dropna().rename(
                        columns={"home_vector_alignment_score": "score"}
                    )

                    # Zone band rectangles
                    zones = pd.DataFrame([
                        {"x1": -1.0, "x2": -0.5, "zone": "Away",     "color": "#fee2e2"},
                        {"x1": -0.5, "x2":  0.5, "zone": "Neutral",  "color": "#f8fafc"},
                        {"x1":  0.5, "x2":  1.0, "zone": "Homeward", "color": "#ccfbf1"},
                    ])
                    band = alt.Chart(zones).mark_rect(opacity=0.5).encode(
                        x=alt.X("x1:Q", scale=alt.Scale(domain=[-1.1, 1.1])),
                        x2="x2:Q",
                        color=alt.Color("color:N", scale=None, legend=None),
                    )

                    # Histogram
                    hist = alt.Chart(df_vec).mark_bar(
                        color=TEAL, opacity=0.55, binSpacing=1,
                    ).encode(
                        x=alt.X("score:Q", bin=alt.Bin(step=0.05),
                                title="Alignment Score  (−1.0 = away · 0 = neutral · +1.0 = home)",
                                scale=alt.Scale(domain=[-1.1, 1.1]),
                                axis=alt.Axis(tickCount=9, labelFontSize=11, titleFontSize=12,
                                              grid=False)),
                        y=alt.Y("count():Q", title="Offers",
                                axis=alt.Axis(labelFontSize=11, titleFontSize=12, gridColor="#f0f0f0")),
                        tooltip=[
                            alt.Tooltip("score:Q", bin=alt.Bin(step=0.05), title="Score bin"),
                            alt.Tooltip("count():Q", title="Offers"),
                        ],
                    )

                    # KDE overlay (manual, secondary y via normalize)
                    from scipy.stats import gaussian_kde as _kde
                    x_grid = __import__("numpy").linspace(-1.1, 1.1, 400)
                    y_kde  = _kde(scores, bw_method=0.15)(x_grid)
                    # scale KDE to histogram counts
                    bin_width = 0.05
                    y_scaled  = y_kde * len(scores) * bin_width
                    df_kde = pd.DataFrame({"score": x_grid, "density": y_scaled})
                    kde_line = alt.Chart(df_kde).mark_line(
                        color="#134e4a", strokeWidth=2, interpolate="monotone",
                    ).encode(
                        x="score:Q",
                        y=alt.Y("density:Q", axis=None),
                    )

                    # Center rule at 0
                    center = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(
                        color="#334155", strokeWidth=1.5, opacity=0.6,
                    ).encode(x="x:Q")

                    # Zone labels
                    zone_labels = pd.DataFrame([
                        {"x": -0.75, "y": y_scaled.max() * 0.92, "text": "AWAY"},
                        {"x":  0.0,  "y": y_scaled.max() * 0.92, "text": "NEUTRAL"},
                        {"x":  0.75, "y": y_scaled.max() * 0.92, "text": "HOMEWARD"},
                    ])
                    labels = alt.Chart(zone_labels).mark_text(
                        fontSize=10, fontWeight=700, opacity=0.55,
                    ).encode(
                        x="x:Q", y="y:Q", text="text:N",
                        color=alt.Color("text:N", scale=alt.Scale(
                            domain=["AWAY", "NEUTRAL", "HOMEWARD"],
                            range=["#dc2626", "#64748b", "#21918c"],
                        ), legend=None),
                    )

                    chart = (
                        alt.layer(band, hist, kde_line, center, labels)
                        .properties(
                            title=alt.TitleParams(
                                "Strategic Alignment — The Home Vector",
                                fontSize=14, fontWeight=600, anchor="middle",
                            ),
                            height=380,
                        )
                        .configure_view(strokeWidth=0)
                        .configure_title(font="Inter")
                        .configure_axis(labelFont="Inter", titleFont="Inter")
                        .interactive()
                    )
                    st.altair_chart(chart, use_container_width=True)


                    st.markdown("""
<div style='border-left:4px solid #21918c;background:#f0faf9;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>What is the Home Vector?</strong> Each offer is scored by how closely its dropoff direction
  aligns with the driver's home base. <em>+1.0</em> means the ride moves the driver directly
  homeward; <em>−1.0</em> means it pulls them directly away.
</div>""", unsafe_allow_html=True)

                elif selected == "Profitability Funnel":
                    import plotly.graph_objects as go
                    import numpy as np
                    import re as _re

                    TEAL  = "#21918c"
                    TEAL2 = "#2db3ad"
                    TEAL3 = "#5a9e9a"
                    GRAY  = "#94a3b8"

                    STAGES = [
                        ("eph_direct",       "Direct",       TEAL,  "Platform promise",      "Upfront fare ÷ estimated ride time"),
                        ("eph_operational",  "Operational",  TEAL2, "+ Pickup time",          "Adds dead time driving to the passenger"),
                        ("eph_realized_EDA", "Realized",     TEAL3, "+ Spread correction",    "What was actually settled vs. the quoted fare"),
                        ("eph_complete_EDA", "Complete",     GRAY,  "+ Full cost accounting", "Pickup + spread + unpaid kilometers"),
                    ]

                    # ── Product category filter ──
                    CAT_MAP = {}
                    for raw in df["product"].dropna().unique():
                        clean = _re.sub(r'(?i)uber_?', '', str(raw)).strip('_').strip().lower()
                        if clean == "x":
                            CAT_MAP[raw] = "x"
                        elif clean in ("comfort", "business_comfort", "comfort business"):
                            CAT_MAP[raw] = "mid-tier"
                        elif clean == "black":
                            CAT_MAP[raw] = "black"
                    df["_cat"] = df["product"].map(CAT_MAP)
                    df_filtered_all = df[df["_cat"].notna()].copy()

                    cat_counts = df_filtered_all["_cat"].value_counts().to_dict()
                    cat_options = ["All"] + [c for c in ["x", "mid-tier", "black"] if c in df_filtered_all["_cat"].unique()]
                    cat_sel = st.pills("Product category", cat_options, default="All",
                                       key="funnel_cat_pill", label_visibility="collapsed")
                    if cat_sel and cat_sel != "All":
                        df_f = df_filtered_all[df_filtered_all["_cat"] == cat_sel]
                    else:
                        df_f = df_filtered_all

                    # ── Sample size badges ──
                    total_n = len(df_filtered_all)
                    badges = f"<span style='background:#f1f5f9;border:1px solid #e2e8f0;border-radius:20px;padding:3px 10px;font-size:0.72rem;color:#475569;margin-right:6px;'><strong>All</strong> — {total_n:,}</span>"
                    for c in ["x", "mid-tier", "black"]:
                        n = cat_counts.get(c, 0)
                        active = cat_sel == c
                        bg = "#f0faf9" if active else "#f1f5f9"
                        border = "#21918c" if active else "#e2e8f0"
                        badges += f"<span style='background:{bg};border:1px solid {border};border-radius:20px;padding:3px 10px;font-size:0.72rem;color:#475569;margin-right:6px;'><strong>{c}</strong> — {n:,}</span>"
                    st.markdown(f"<div style='margin:4px 0 12px 0;'>{badges}</div>", unsafe_allow_html=True)

                    # ── Compute stats per stage ──
                    stats = []
                    for col, label, color, tag, desc in STAGES:
                        vals = df_f[col].dropna().values
                        if len(vals) == 0:
                            stats.append((label, color, tag, desc, 0, 0, 0, 0))
                            continue
                        stats.append((
                            label, color, tag, desc,
                            float(np.median(vals)),
                            float(np.percentile(vals, 25)),
                            float(np.percentile(vals, 75)),
                            float(np.mean(vals)),
                        ))

                    # ── Metric cards ──
                    first_median = stats[0][4]
                    card_cols = st.columns(4)
                    for i, (label, color, tag, desc, median, q1, q3, mean) in enumerate(stats):
                        delta = median - first_median if i > 0 else None
                        delta_html = (
                            f"<div style='font-size:0.72rem;font-weight:600;"
                            f"color:{'#ef4444' if delta < 0 else TEAL};margin-top:6px;'>"
                            f"{delta:+.0f} MXN/hr</div>"
                        ) if delta is not None else ""
                        with card_cols[i]:
                            st.markdown(f"""
<div style='background:#fff;border:1px solid #e2e8f0;border-top:3px solid {color};
     border-radius:8px;padding:14px 16px;'>
  <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;
       color:#94a3b8;margin-bottom:4px;'>{tag}</div>
  <div style='font-size:0.82rem;font-weight:600;color:#334155;margin-bottom:8px;'>{label}</div>
  <div style='font-size:1.55rem;font-weight:800;color:{color};line-height:1;'>${median:.0f}</div>
  <div style='font-size:0.68rem;color:#94a3b8;margin-top:3px;'>median MXN/hr</div>
  {delta_html}
  <div style='font-size:0.65rem;color:#b0bec5;margin-top:5px;'>IQR {q1:.0f} – {q3:.0f}</div>
</div>""", unsafe_allow_html=True)

                    st.write("")

                    import altair as alt
                    import pandas as pd
                    from scipy.stats import gaussian_kde as _kde

                    STAGE_ORDER = ["Direct", "Operational", "Realized", "Complete"]
                    COLOR_SCALE = alt.Scale(
                        domain=STAGE_ORDER,
                        range=[TEAL, TEAL2, TEAL3, GRAY],
                    )

                    # ── Melt to long format (for box plots) ──
                    col_to_label = {col: label for col, label, *_ in STAGES}
                    df_long = (
                        df_f[[c for c, *_ in STAGES]]
                        .melt(var_name="col", value_name="eph")
                        .dropna()
                    )
                    df_long["Stage"] = df_long["col"].map(col_to_label)

                    # ── Build KDE manually → long dataframe ──
                    x_max  = float(np.percentile(df_long["eph"].dropna().values, 99))
                    x_grid = np.linspace(0, x_max, 600)
                    kde_rows = []
                    median_rows = []
                    for col, label, *_ in STAGES:
                        vals = df_f[col].dropna().values
                        if len(vals) < 2:
                            continue
                        y = _kde(vals, bw_method=0.18)(x_grid)
                        for xi, yi in zip(x_grid, y):
                            kde_rows.append({"Stage": label, "eph": xi, "density": yi})
                        median_rows.append({"Stage": label, "median": float(np.median(vals))})
                    df_kde     = pd.DataFrame(kde_rows)
                    df_medians = pd.DataFrame([
                        {"Stage": s, "eph": m} for s, m in
                        [(r["Stage"], r["median"]) for r in median_rows]
                    ])

                    # ── Chart 1: KDE ──
                    area = alt.Chart(df_kde).mark_area(
                        opacity=0.1, interpolate="monotone",
                    ).encode(
                        x=alt.X("eph:Q", title="MXN / hr",
                                axis=alt.Axis(grid=True, gridColor="#f0f0f0", tickCount=8,
                                              labelFontSize=11, titleFontSize=12)),
                        y=alt.Y("density:Q", title=None, axis=None),
                        color=alt.Color("Stage:N", scale=COLOR_SCALE, sort=STAGE_ORDER,
                                        legend=alt.Legend(orient="top", title=None,
                                                          labelFontSize=11, symbolSize=100,
                                                          padding=10, columnPadding=16)),
                    )
                    line = alt.Chart(df_kde).mark_line(
                        strokeWidth=2, interpolate="monotone",
                    ).encode(
                        x="eph:Q",
                        y="density:Q",
                        color=alt.Color("Stage:N", scale=COLOR_SCALE, sort=STAGE_ORDER, legend=None),
                    )
                    median_rules = alt.Chart(df_medians).mark_rule(
                        strokeDash=[4, 3], strokeWidth=1.2, opacity=0.65,
                    ).encode(
                        x="eph:Q",
                        color=alt.Color("Stage:N", scale=COLOR_SCALE, sort=STAGE_ORDER, legend=None),
                        tooltip=[
                            alt.Tooltip("Stage:N", title="Stage"),
                            alt.Tooltip("median:Q", format=".0f", title="Median MXN/hr"),
                        ],
                    )
                    ref_rule = alt.Chart(pd.DataFrame({"x": [200]})).mark_rule(
                        strokeDash=[6, 4], strokeWidth=1.5, color="#475569", opacity=0.7,
                    ).encode(x="x:Q")

                    kde_chart = (
                        alt.layer(area, line, median_rules, ref_rule)
                        .properties(
                            title=alt.TitleParams("EPH Density — Platform Promise to Full Cost",
                                                  fontSize=14, fontWeight=600, anchor="middle"),
                            height=420,
                        )
                        .configure_view(strokeWidth=0)
                        .configure_title(font="Inter", fontSize=14)
                        .configure_axis(labelFont="Inter", titleFont="Inter")
                        .configure_legend(labelFont="Inter")
                        .interactive()
                    )
                    st.altair_chart(kde_chart, use_container_width=True)

                    # ── Chart 2: Box plots ──
                    box_chart = (
                        alt.Chart(df_long)
                        .mark_boxplot(outliers=False, size=28,
                                      ticks=alt.MarkConfig(size=8))
                        .encode(
                            x=alt.X("eph:Q", title="MXN / hr",
                                    axis=alt.Axis(grid=True, gridColor="#f0f0f0", tickCount=8,
                                                  labelFontSize=11, titleFontSize=12)),
                            y=alt.Y("Stage:N", sort=STAGE_ORDER, title=None,
                                    axis=alt.Axis(labelFontSize=12)),
                            color=alt.Color("Stage:N", scale=COLOR_SCALE,
                                            sort=STAGE_ORDER, legend=None),
                        )
                        .properties(
                            title=alt.TitleParams("EPH Distribution — Stage by Stage",
                                                  fontSize=14, fontWeight=600, anchor="middle"),
                            height=240,
                        )
                        .configure_view(strokeWidth=0)
                        .configure_title(font="Inter", fontSize=14)
                        .configure_axis(labelFont="Inter", titleFont="Inter")
                        .interactive()
                    )
                    st.altair_chart(box_chart, use_container_width=True)

                    # ── Stage descriptors ──
                    desc_items = "".join([
                        f"""<div style='display:flex;align-items:flex-start;gap:8px;'>
                          <div style='width:9px;height:9px;border-radius:2px;background:{color};
                               flex-shrink:0;margin-top:3px;'></div>
                          <span style='font-size:0.78rem;color:#334155;'>
                            <strong>{label}</strong> — {desc}
                          </span>
                        </div>"""
                        for _, label, color, __, desc in STAGES
                    ])
                    st.markdown(
                        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px 32px;"
                        f"padding:12px 16px;background:#f8f8f8;border-radius:8px;margin-bottom:10px;'>{desc_items}</div>",
                        unsafe_allow_html=True)

                    st.markdown("""
<div style='border-left:4px solid #21918c;background:#f0faf9;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>Reading the funnel:</strong> Each stage reveals more of the true hourly rate.
  <em>Direct</em> is what the platform displays; <em>Complete</em> is what the driver actually earns per hour
  of real time invested — including the unpaid kilometers driven to reach the passenger.<br><br>
  <strong>Multiple peaks in the density?</strong> That is a <em>multimodal distribution</em> — the data contains
  distinct clusters of trip types (short city runs, airport transfers, late-night surges) each forming its
  own earnings band. Most visible in the <em>Black</em> category, where premium pricing creates
  well-separated fare tiers.
</div>""", unsafe_allow_html=True)

                else:
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

