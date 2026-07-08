import streamlit as st
from pathlib import Path
from google.cloud import bigquery
from components.styles import GLOBAL_CSS
from config import FAVICON
from utils.gcp_client import fetch_bytes_from_gcs

st.set_page_config(page_title="Data Census (The Basics) | Pienza", page_icon=FAVICON, layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown("Project Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer")
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big")
        st.markdown("---")
        st.markdown("**Archive**")
        st.page_link("pages/9001_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/9002_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/9003_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            pdf_data = fetch_bytes_from_gcs("pienza-streamlit", "Pienza_Papers.pdf")
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data,
                               file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except Exception:
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
st.markdown("# Data Census (The Basics)")
st.markdown("""
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
With the Feature Store fully defined, the project reconciled every offer against the platform's official
ledgers — earnings settlements and trip event logs — and certified the result as a relational Golden Master
through an idempotent ETL pipeline. That pipeline produced <code>pienza.db</code>, migrated to BigQuery
as <code>pienza_mini</code>.
</p>
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-top:10px;margin-bottom:24px;'>
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
""", unsafe_allow_html=True)

st.write("")

with st.expander("Relational Schema — full ERD (Vertabelo / RedGate)", expanded=False):
    erd_path = Path(__file__).resolve().parent.parent / "assets" / "Pienza_ERD.png"
    if erd_path.exists():
        st.image(str(erd_path), use_container_width=True, caption="Pienza — Definitive Star Schema")
    else:
        st.caption(f"ERD image not found at: {erd_path}")

st.markdown("""
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-top:14px;margin-bottom:24px;'>
The pills below surface the first layer of exploratory analysis — categorical counts, incentive structures,
traffic patterns, and financial profiles across the ~4,700 collected offers. This is the baseline census:
what the dataset looks like before any modelling assumptions are applied.
</p>
""", unsafe_allow_html=True)

st.write("")



QUERIES = {
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
            if active_pill == "Decision & Product Mix":
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
<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>Class imbalance</strong> — The 93/7 split mirrors operational reality and was handled via
  <strong>Stratified K-Fold</strong> and the <strong>Cognitive Cascade</strong> architecture.
  <code>system_logic_failure</code> (5 records) was dropped downstream — pure noise, not a behavioral signal.
</div>"""

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
                    paper_bgcolor="#F5F6F7", font_family="Inter",
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
                )
                c1, c2 = st.columns(2)
                with c1: st.plotly_chart(fig1, use_container_width=True)
                with c2: st.plotly_chart(fig2, use_container_width=True)
                c3, c4 = st.columns(2)
                with c3: st.plotly_chart(fig3, use_container_width=True)
                with c4: st.plotly_chart(fig4, use_container_width=True)
                # ── Cell 16: Taxonomy of Decision ──
                st.markdown(
                    "<div style='font-size:0.9rem;font-weight:700;color:#334155;"
                    "margin:16px 0 4px;'>Upfront Fare by reason_primary</div>",
                    unsafe_allow_html=True)

                import altair as alt
                import numpy as _np16
                import pandas as _pd16

                # Fetch fare + reason + action (single extra query, cached)
                _sql16 = f"""
SELECT upfront_fare,
   oa.offer_action_description  AS action,
   rp.reason_primary_description AS reason
FROM `{PROJECT}.{DATASET}.v_ML_Supervised` ml
LEFT JOIN `{PROJECT}.{DATASET}.offer_action` oa   ON oa.offer_action_id = ml.offer_action_fk
LEFT JOIN `{PROJECT}.{DATASET}.reason_primary` rp ON rp.reason_primary_id = ml.reason_primary_fk
WHERE upfront_fare IS NOT NULL AND upfront_fare < 600"""
                _df16, _err16 = run_query(_sql16)

                if _err16:
                    st.warning(f"Taxonomy query failed: {_err16}")
                elif _df16 is not None and not _df16.empty:
                    # Exclude system_logic_failure
                    _df16 = _df16[_df16["reason"] != "system_logic_failure"].copy()

                    # Assign display label
                    def _label16(row):
                        if row["action"] == "accepted":
                            return "NULL (accepted)"
                        return row["reason"] if _pd16.notna(row["reason"]) else "unknown_reject"
                    _df16["group"] = _df16.apply(_label16, axis=1)
                    _df16["label_n"] = _df16["group"]

                    # Sort rejections by median fare; ACCEPTED forced last
                    _rej16 = _df16[_df16["group"] != "NULL (accepted)"]
                    _sort_rej = _rej16.groupby("label_n")["upfront_fare"].median().sort_values().index.tolist()
                    _acc_label = _df16[_df16["group"] == "NULL (accepted)"]["label_n"].unique()[0]
                    _sort_order = _sort_rej + [_acc_label]

                    # Palette: teal gradient, lightest at bottom, darkest (ACCEPTED) at top
                    _TEAL_RAMP = ["#cceae8","#99d5d1","#66c0ba","#2db3ad","#21918c","#0e6b67","#0a4a47"]
                    _n = len(_sort_order)
                    _colors = [
                        _TEAL_RAMP[int(i * (len(_TEAL_RAMP) - 1) / max(_n - 1, 1))]
                        for i in range(_n)
                    ]

                    # Build manual box stats
                    _box16 = []
                    for _lbl in _sort_order:
                        _vals = _df16[_df16["label_n"] == _lbl]["upfront_fare"].dropna().values
                        if len(_vals) < 4:
                            continue
                        _q1, _med, _q3 = float(_np16.percentile(_vals, 25)), float(_np16.median(_vals)), float(_np16.percentile(_vals, 75))
                        _iqr = _q3 - _q1
                        _box16.append({
                            "label": _lbl,
                            "q1": _q1, "median": _med, "q3": _q3,
                            "lower": float(max(_vals.min(), _q1 - 1.5 * _iqr)),
                            "upper": float(min(_vals.max(), _q3 + 1.5 * _iqr)),
                            "n": len(_vals),
                            "color": _colors[_sort_order.index(_lbl)],
                        })
                    _bdf16 = _pd16.DataFrame(_box16)
                    _valid_order = [r["label"] for r in _box16]

                    _c16  = alt.Color("label:N",
                                      scale=alt.Scale(domain=_valid_order, range=[r["color"] for r in _box16]),
                                      legend=None)
                    _y16  = alt.Y("label:N", sort=_valid_order, title=None,
                                  axis=alt.Axis(labelFontSize=11, labelLimit=300))
                    _tt16 = [
                        alt.Tooltip("label:N",  title="Group"),
                        alt.Tooltip("n:Q",      title="N",          format=","),
                        alt.Tooltip("median:Q", title="Median $",   format=".2f"),
                        alt.Tooltip("q1:Q",     title="Q1 $",       format=".2f"),
                        alt.Tooltip("q3:Q",     title="Q3 $",       format=".2f"),
                        alt.Tooltip("lower:Q",  title="Whisker lo", format=".2f"),
                        alt.Tooltip("upper:Q",  title="Whisker hi", format=".2f"),
                    ]
                    _ax16 = alt.Axis(grid=True, gridColor="#f0f0f0", tickCount=8,
                                     labelFontSize=11, titleFontSize=12)
                    _b16  = alt.Chart(_bdf16)
                    _w16  = _b16.mark_rule(strokeWidth=1.4).encode(
                        x=alt.X("lower:Q", title="Upfront Fare (MXN)", axis=_ax16),
                        x2="upper:Q", y=_y16, color=_c16, tooltip=_tt16)
                    _bb16 = _b16.mark_bar(size=22).encode(
                        x=alt.X("q1:Q"), x2="q3:Q", y=_y16, color=_c16, tooltip=_tt16)
                    _m16  = _b16.mark_tick(color="white", thickness=2, size=22).encode(
                        x=alt.X("median:Q"), y=_y16, tooltip=_tt16)
                    _lo16 = _b16.mark_tick(strokeWidth=1.4, size=10).encode(
                        x=alt.X("lower:Q"), y=_y16, color=_c16, tooltip=_tt16)
                    _hi16 = _b16.mark_tick(strokeWidth=1.4, size=10).encode(
                        x=alt.X("upper:Q"), y=_y16, color=_c16, tooltip=_tt16)

                    _chart16 = (
                        alt.layer(_w16, _bb16, _m16, _lo16, _hi16)
                        .properties(height=max(200, len(_valid_order) * 46))
                        .configure_view(strokeWidth=0)
                        .configure_axis(labelFont="Inter", titleFont="Inter")
                        .interactive()
                    )
                    st.altair_chart(_chart16, use_container_width=True)


                st.write("")
                st.markdown(CALLOUT, unsafe_allow_html=True)

            elif active_pill == "Incentives":
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
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
                    paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
                    xaxis=dict(tickfont_size=12),
                    yaxis=dict(tickfont_size=12, autorange="reversed"),
                )
                col_h, _ = st.columns([1, 1])
                with col_h:
                    st.plotly_chart(fig3, use_container_width=True)

            elif active_pill == "Traffic Index":
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
                ].copy()

                if len(df_t) == 0:
                    st.warning("No data for selected hour range.")
                else:
                    vals = df_t["traffic_index_base_120"].dropna().values
                    total = len(vals)

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
                        paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
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
                        paper_bgcolor="#F5F6F7", plot_bgcolor="#F5F6F7", font_family="Inter",
                        yaxis=dict(showgrid=False, showticklabels=False, range=[0, max(sem_counts) * 1.3]),
                        xaxis=dict(tickfont_size=11),
                    )

                    c1, c2 = st.columns(2)
                    with c1: st.plotly_chart(fig1, use_container_width=True)
                    with c2: st.plotly_chart(fig2, use_container_width=True)

                    # ── Metric keys ──
                    key_items = "".join([
                        f"""<div style='display:flex;align-items:center;gap:6px;white-space:nowrap;'>
                          <div style='width:10px;height:10px;border-radius:2px;background:{color};flex-shrink:0;'></div>
                          <span style='font-size:0.78rem;color:#334155;'><strong>{label}</strong> — {anchor}</span>
                        </div>"""
                        for (_, _, label, anchor), color in zip(CLASSES, CLASS_COLORS)
                    ])
                    st.markdown(
                        f"<div style='display:flex;flex-wrap:wrap;gap:10px 28px;"
                        f"padding:10px 14px;background:#f8f8f8;border-radius:8px;margin-bottom:10px;'>{key_items}</div>",
                        unsafe_allow_html=True)

                    st.markdown("""
<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  These figures reflect the <em>expected</em> traffic conditions shown on the offer card at the moment of decision.
  Realized traffic — what drivers in Mexico City actually experience — is generally worse.
</div>""", unsafe_allow_html=True)


            elif active_pill == "Home Vector":
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
                    ("Away",      "< -0.5",          away,     TEAL, "Offers pulling the driver further from home"),
                    ("Neutral",   "-0.5 to +0.5",    neutral,  TEAL, "Offers with no strong directional bias"),
                    ("Homeward",  "> 0.5",           homeward, TEAL, "Offers moving the driver toward home base"),
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
                band = alt.Chart(zones).mark_rect(opacity=0.5, tooltip=None).encode(
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
                    tooltip=[alt.Tooltip("count():Q", title="Offers")],
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
                            "Home Vector Alignment Score",
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
<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:8px;font-size:0.82rem;color:#334155;line-height:1.65;'>
  <strong>What is the Home Vector?</strong> Each offer is scored by how closely its dropoff direction
  aligns with the driver's home base. <em>+1.0</em> means the ride moves the driver directly
  homeward; <em>−1.0</em> means it pulls them directly away.
</div>""", unsafe_allow_html=True)

            elif active_pill == "Profitability Funnel":
                import plotly.graph_objects as go
                import numpy as np
                import re as _re

                TEAL  = "#21918c"

                STAGES = [
                    ("eph_direct",       "Direct",       "#99d5d1", "Platform promise",      "Upfront fare ÷ estimated ride time"),
                    ("eph_operational",  "Operational",  "#2db3ad", "+ Pickup time",          "Adds dead time driving to the passenger"),
                    ("eph_realized_EDA", "Realized",     "#21918c", "+ Spread correction",    "What was actually settled vs. the quoted fare"),
                    ("eph_complete_EDA", "Complete",     "#0a4a47", "+ Full cost accounting", "Pickup + spread + unpaid kilometers"),
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
                    bg = "rgba(33,145,140,0.07)" if active else "#f1f5f9"
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
                    ) if delta is not None else "<div style='font-size:0.72rem;font-weight:600;color:#cbd5e1;margin-top:6px;'>-- MXN/hr</div>"
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

                import pandas as pd

                STAGE_ORDER  = ["Direct", "Operational", "Realized", "Complete"]
                STAGE_COLORS = {
                    "Direct":      "#99d5d1",
                    "Operational": "#2db3ad",
                    "Realized":    "#21918c",
                    "Complete":    "#0a4a47",
                }
                STAGE_CONTEXT = {
                    "Direct":      "Upfront Fare ÷ Est. Trip Time",
                    "Operational": "Upfront Fare ÷ (Pickup + Est. Trip Time)",
                    "Realized":    "Realized Fare ÷ Est. Trip Time",
                    "Complete":    "Realized Fare ÷ (Total Deadhead + Est. Trip Time)",
                }

                # ── Melt to long format ──
                col_to_label = {col: label for col, label, *_ in STAGES}
                df_long = (
                    df_f[[c for c, *_ in STAGES]]
                    .melt(var_name="col", value_name="eph")
                    .dropna()
                )
                df_long["Stage"] = df_long["col"].map(col_to_label)
                # cap at 99th pct for display
                _cap = float(np.percentile(df_long["eph"].values, 99))
                df_long = df_long[df_long["eph"] <= _cap]

                # ── Violin + strip chart (Plotly, vertical) ──
                fig = go.Figure()

                for stage in STAGE_ORDER:
                    vals = df_long[df_long["Stage"] == stage]["eph"].values
                    color = STAGE_COLORS[stage]

                    fig.add_trace(go.Violin(
                        y=vals,
                        x=[stage] * len(vals),
                        name=stage,
                        fillcolor=color,
                        opacity=0.22,
                        line_color=color,
                        line_width=1.5,
                        points="all",
                        jitter=0.35,
                        pointpos=0,
                        marker=dict(color=color, size=2, opacity=0.12),
                        showlegend=False,
                        hoveron="points+violins",
                        hovertemplate="<b>%{x}</b><br>EPH: $%{y:.2f} MXN/hr<extra></extra>",
                        spanmode="soft",
                        box_visible=False,
                        meanline_visible=False,
                    ))

                    # median badge
                    med = float(np.median(vals))
                    fig.add_annotation(
                        x=stage, y=med,
                        text=f"<b>${med:.0f}</b>",
                        showarrow=False,
                        xshift=42,
                        font=dict(size=12, color=color, family="Inter"),
                        bgcolor="white",
                        bordercolor=color,
                        borderwidth=1,
                        borderpad=3,
                    )
                    # context label below stage name
                    fig.add_annotation(
                        x=stage, y=-0.10,
                        yref="paper",
                        text=f"<i>{STAGE_CONTEXT[stage]}</i>",
                        showarrow=False,
                        font=dict(size=8, color="#888", family="Inter"),
                        xanchor="center",
                    )

                # Median legend box — top-right corner
                fig.add_annotation(
                    x=1.0, y=1.0,
                    xref="paper", yref="paper",
                    text="<b>$</b>  median",
                    showarrow=False,
                    xanchor="right", yanchor="top",
                    font=dict(size=10, color="#21918c", family="Inter"),
                    bgcolor="white",
                    bordercolor="#21918c",
                    borderwidth=1,
                    borderpad=5,
                )

                # North Star reference line + label inside plot area
                fig.add_hline(
                    y=200,
                    line_dash="dash", line_color="#475569", line_width=1.5,
                    opacity=0.6,
                )
                fig.add_annotation(
                    x=0.01, y=200,
                    xref="paper", yref="y",
                    text="<b>North Star $200 MXN/hr</b>",
                    showarrow=False,
                    xanchor="left",
                    yshift=10,
                    font=dict(size=9, color="#475569", family="Inter"),
                )

                fig.update_layout(
                    height=520,
                    margin=dict(l=20, r=40, t=50, b=80),
                    paper_bgcolor="#F5F6F7",
                    plot_bgcolor="#F5F6F7",
                    hovermode="closest",
                    xaxis=dict(
                        categoryorder="array",
                        categoryarray=STAGE_ORDER,
                        tickfont=dict(family="Inter", size=12),
                        showgrid=False,
                        title=None,
                    ),
                    yaxis=dict(
                        title="MXN / hr",
                        gridcolor="#f0f0f0",
                        zeroline=False,
                        tickfont=dict(family="Inter", size=11),
                        title_font=dict(family="Inter", size=12),
                    ),
                    violingap=0.4,
                    violingroupgap=0,
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── Stage descriptors ──
                desc_items = "".join([
                    f"""<div style='display:flex;align-items:flex-start;gap:8px;'>
                      <div style='width:9px;height:9px;border-radius:2px;background:{STAGE_COLORS[label]};
                           flex-shrink:0;margin-top:3px;'></div>
                      <span style='font-size:0.78rem;color:#334155;'>
                        <strong>{label}</strong> — {desc}
                      </span>
                    </div>"""
                    for _, label, _, __, desc in STAGES
                ])
                st.markdown(
                    f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px 32px;"
                    f"padding:12px 16px;background:#f8f8f8;border-radius:8px;margin-bottom:10px;'>{desc_items}</div>",
                    unsafe_allow_html=True)

                _north_star = 200
                _pct = {}
                for col, label, *_ in STAGES:
                    vals = df_f[col].dropna().values
                    _pct[label] = 100 * (vals > _north_star).sum() / len(vals) if len(vals) > 0 else 0
                _drop = _pct["Direct"] - _pct["Complete"]

                st.markdown(
                    f"<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);"
                    f"border-radius:0 8px 8px 0;padding:12px 16px;margin-top:8px;font-size:0.82rem;"
                    f"color:#334155;line-height:1.8;'>"
                    f"<strong>{_pct['Direct']:.1f}%</strong> of offers clear the $200 MXN/hr North Star at the "
                    f"quoted rate. Accounting for pickup time, fare spread, and unpaid kilometers, "
                    f"that figure drops to <strong>{_pct['Complete']:.1f}%</strong>."
                    f"</div>",
                    unsafe_allow_html=True)

            else:
                st.success(f"{len(df):,} rows returned.")
                st.dataframe(df, use_container_width=True)
