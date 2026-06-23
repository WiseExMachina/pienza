import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt
from google.cloud import bigquery
from pathlib import Path
from scipy.interpolate import interp1d
from components.styles import GLOBAL_CSS

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(page_title="The Cost of Patience | Pienza",
                   layout="wide")
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
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census (The Basics)")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience")
        st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
        st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data,
                               file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

# ==============================================================================
# CONSTANTS
# ==============================================================================
OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
OPUS_TEXT   = '#121212'

COLORS = {
    'Rich / Fast': '#21918c',   # primary teal
    'Rich / Slow': '#99d5d1',   # pale teal
    'Poor / Fast': '#cbd5e1',   # light slate
    'Poor / Slow': '#64748b',   # dark slate
}

# ==============================================================================
# BIGQUERY
# ==============================================================================
@st.cache_resource
def get_bq_client():
    json_path = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

def map_category(cat_name):
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower: return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower: return "Mid-tier"
    elif 'black' in cat_lower: return "Premium"
    else: return "X"

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("# The Cost of Patience")
st.markdown(
    "<p style='color:#555;font-size:0.88rem;line-height:1.75;max-width:820px;'>"
    "Optimal Stopping Theory addresses a single problem: given a sequential stream of transient options, when is the exact moment to commit? "
    "In ride-hailing, every accepted offer locks the agent into a trajectory, while every rejection burns finite operational time. "
    "The clock is a continuous financial penalty."
    "</p>"
    "<p style='color:#555;font-size:0.88rem;line-height:1.75;max-width:820px;margin-top:10px;'>"
    "The classical <em>Secretary Problem</em> provides a theoretical baseline: reject the first "
    "1/e ≈ 37% of candidates, then accept the next observation exceeding all prior maximums. "
    "This model, however, assumes a known population size, costless waiting, and a stationary distribution. "
    "In field operations, idle time directly erodes EPH, and market quality shifts dynamically between sessions."
    "</p>"
    "<p style='color:#555;font-size:0.88rem;line-height:1.75;max-width:820px;margin-top:10px;'>"
    "Therefore, the operative metric is the <strong>Continuation Value (CV)</strong>. An offer is rejected only when "
    "the expected return of continuing the search within a rational time window exceeds the immediate baseline:"
    "</p>",
    unsafe_allow_html=True,
)

_col_latex, _col_fn = st.columns([11, 1])
with _col_latex:
    st.latex(r"CV(\tau) = p(\tau)\cdot EPH_{\text{target}} + (1-p(\tau))\cdot EPH_{\text{fallback}} - EPH_{\text{immediate}}")
with _col_fn:
    st.markdown(
        "<div style='padding-top:22px;'>"
        "<span class='fn-wrap'>"
        "<span class='fn-mark'>†</span>"
        "<span class='fn-tooltip' style='width:320px;font-size:0.75rem;line-height:1.6;'>"
        "<b>Plain-English breakdown:</b><br><br>"
        "<b>p(τ)</b> — probability of finding a premium offer if you wait window τ.<br><br>"
        "<b>EPH_target</b> — your yield <em>if</em> the premium offer is found and completed.<br><br>"
        "<b>EPH_fallback</b> — your yield <em>if</em> nothing is found and you fall back to baseline — "
        "but penalized by the idle time already burned. Same fare, lower EPH because the denominator grew.<br><br>"
        "<b>EPH_immediate</b> — your yield if you accept the current baseline offer right now, zero wait cost.<br><br>"
        "CV &gt; 0 → wait. CV &lt; 0 → accept now."
        "</span></span></div>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<p style='color:#888;font-size:0.78rem;line-height:1.6;max-width:820px;margin-top:4px;'>"
    "where p(τ) is the empirical probability of encountering a premium offer within search window τ, "
    "conditional on the active market regime. The equilibrium point where CV(τ) = 0 defines the mathematical boundary of rational patience."
    "</p>"
    "<div style='margin-top:24px;'></div>"
    "<p style='color:#555;font-size:0.88rem;line-height:1.75;max-width:820px;'>"
    "Deriving that boundary requires four sequential phases — each building on the last."
    "</p>"
    "<div style='display:flex;gap:12px;margin-top:20px;max-width:820px;flex-wrap:wrap;'>"
    "<div style='flex:1;min-width:160px;border-left:3px solid #21918c;padding:8px 12px;'>"
    "<div style='font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>Phase 1</div>"
    "<div style='font-size:0.82rem;font-weight:600;color:#1e293b;margin-top:3px;'>Market Quality Index</div>"
    "<div style='font-size:0.75rem;color:#64748b;margin-top:2px;'>Normalize offers across tiers into a single dimensionless quality score.</div>"
    "</div>"
    "<div style='flex:1;min-width:160px;border-left:3px solid #21918c;padding:8px 12px;'>"
    "<div style='font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>Phase 2</div>"
    "<div style='font-size:0.82rem;font-weight:600;color:#1e293b;margin-top:3px;'>Market Quadrants</div>"
    "<div style='font-size:0.75rem;color:#64748b;margin-top:2px;'>Classify sessions by offer quality and arrival velocity into four regimes.</div>"
    "</div>"
    "<div style='flex:1;min-width:160px;border-left:3px solid #21918c;padding:8px 12px;'>"
    "<div style='font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>Phase 3</div>"
    "<div style='font-size:0.82rem;font-weight:600;color:#1e293b;margin-top:3px;'>The CV(τ) Playbook</div>"
    "<div style='font-size:0.75rem;color:#64748b;margin-top:2px;'>Compute CV(τ) per quadrant to derive rational search time boundaries.</div>"
    "</div>"
    "<div style='flex:1;min-width:160px;border-left:3px solid #21918c;padding:8px 12px;'>"
    "<div style='font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>Phase 4</div>"
    "<div style='font-size:0.82rem;font-weight:600;color:#1e293b;margin-top:3px;'>The Efficient Frontier</div>"
    "<div style='font-size:0.75rem;color:#64748b;margin-top:2px;'>Map the Pareto boundary between selectivity and realized yield.</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ==============================================================================
# DATA PIPELINE — runs once, feeds all tabs
# ==============================================================================
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
def get_mqi_data(query):
    return get_bq_client().query(query).to_dataframe()

@st.cache_data
def get_moneymap_data(query):
    return get_bq_client().query(query).to_dataframe()

@st.cache_data
def get_ven_data(query):
    return get_bq_client().query(query).to_dataframe()

with st.spinner("Loading data…"):
    df_mqi          = get_mqi_data(query_mqi)
    df_money        = get_moneymap_data(query_moneymap)
    df_playbook_raw = get_ven_data(query_ven)

# ── Phase 2 aggregation ──
# Behavioral clock reset (mirrors Jupyter Cell 1.8):
# prev_offer_action is already LAG'd in SQL — if the previous offer was accepted
# the driver was on a trip, so the inter-offer gap is not search time → reset to 0.
def _sanitize_wait(row):
    if pd.isna(row['prev_offer_action']):
        return np.nan
    if 'accept' in str(row['prev_offer_action']).lower():
        return 0.0
    return row['raw_delta']

df_money['clean_wait'] = df_money.apply(_sanitize_wait, axis=1)
df_money['upfront_fare'] = pd.to_numeric(df_money['upfront_fare'], errors='coerce')
df_money['est_trip_time_sec'] = pd.to_numeric(df_money['est_trip_time_sec'], errors='coerce')
df_money['eph_realized'] = (df_money['upfront_fare'] / df_money['est_trip_time_sec']) * 3600
df_money['simplified_category'] = df_money['category'].apply(map_category)

df_core_money = df_money[df_money['simplified_category'].isin(['X', 'Mid-tier', 'Premium'])].copy()
global_anchors = df_core_money.groupby('simplified_category')['eph_realized'].median().to_dict()
df_core_money['category_anchor'] = df_core_money['simplified_category'].map(global_anchors)
df_core_money['mqi'] = df_core_money['eph_realized'] / df_core_money['category_anchor']

session_stats = df_core_money.groupby('session_fk').agg(
    velocity_median=('clean_wait', 'median'),
    quality_median=('mqi', 'median'),
    quality_mean=('mqi', 'mean'),
    offer_count=('offer_id', 'count'),
    total_potential=('upfront_fare', 'sum'),
).reset_index()
session_stats = session_stats[
    session_stats['velocity_median'] < session_stats['velocity_median'].quantile(0.98)
]

GLOBAL_VELOCITY = session_stats['velocity_median'].median()
GLOBAL_QUALITY  = 1.0

def get_quadrant(row):
    is_rich = row['quality_median'] >= GLOBAL_QUALITY
    is_fast = row['velocity_median'] <= GLOBAL_VELOCITY
    if is_rich and is_fast:      return 'Rich / Fast'
    if is_rich and not is_fast:  return 'Rich / Slow'
    if not is_rich and is_fast:  return 'Poor / Fast'
    return 'Poor / Slow'

session_stats['Quadrant'] = session_stats.apply(get_quadrant, axis=1)

def format_currency_label(val):
    return f"${val/1000:.1f}k" if val >= 1000 else f"${val:.0f}"

session_stats['label'] = session_stats['total_potential'].apply(format_currency_label)
session_stats['color'] = session_stats['Quadrant'].map(COLORS)

# ── Tab 3 pipeline — single dataset, mirrors notebook Cell 1 → 1.8 → 3 v2.1 → 3.5 ──
_df_pb = df_playbook_raw.copy()
_df_pb['offer_timestamp'] = pd.to_datetime(_df_pb['offer_timestamp'], utc=True).dt.tz_convert(None)
_df_pb.sort_values(['session_fk', 'offer_timestamp'], inplace=True)

# Category filter (notebook Cell 1: drop 'Other')
def _simplify_cat(cat):
    c = str(cat).lower()
    if 'uberx' in c:                              return 'X'
    if 'comfort' in c or 'business' in c:         return 'Mid-tier'
    if 'black' in c:                              return 'Premium'
    return None

_df_pb['simplified_category'] = _df_pb['category_name'].apply(_simplify_cat)
_df_pb = _df_pb[_df_pb['simplified_category'].notna()].copy()

# MQI (notebook Cell 1)
_anchors_pb = _df_pb.groupby('simplified_category')['eph_real'].median().to_dict()
_df_pb['offer_quality_index'] = _df_pb['eph_real'] / _df_pb['simplified_category'].map(_anchors_pb)

# Sanitized search delta (notebook Cell 1.8)
def _sanitize_delta(row):
    if pd.isna(row['prev_offer_action']):
        return np.nan
    if 'accept' in str(row['prev_offer_action']).lower():
        return 0.0
    return row['raw_delta']

_df_pb['sanitized_search_delta'] = _df_pb.apply(_sanitize_delta, axis=1)

# Quadrant assignment (notebook Cell 3 v2.1)
# Quality axis: mean MQI per session
_sess_quality = _df_pb.groupby('session_fk')['offer_quality_index'].median().to_dict()
# Velocity axis: offer-level median as global threshold, per-session median for classification
_global_rhythm = _df_pb['sanitized_search_delta'].median()
_sess_rhythm   = _df_pb.groupby('session_fk')['sanitized_search_delta'].median().to_dict()

_df_pb['session_mqi']    = _df_pb['session_fk'].map(_sess_quality)
_df_pb['session_rhythm'] = _df_pb['session_fk'].map(_sess_rhythm)
_df_pb['quality_state']  = _df_pb['session_mqi'].apply(lambda x: 'Rich' if x >= 1.0 else 'Poor')
_df_pb['velocity_state'] = _df_pb['session_rhythm'].apply(
    lambda x: 'Fast' if x <= _global_rhythm else 'Slow'
)
_df_pb['Quadrant'] = _df_pb['quality_state'] + ' / ' + _df_pb['velocity_state']

# No dropoff_non_operational filter — notebook skips it (column not available there)
df_playbook = _df_pb.copy()

st.markdown(
    "<div style='margin-top:28px;'></div>"
    "<style>"
    "[data-testid='stTabs'] { scroll-margin-top: 9999px; }"
    "[data-testid='stTabsContent'] { min-height: 1800px; }"
    "</style>",
    unsafe_allow_html=True,
)

# ==============================================================================
# TABS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Market Quality Index",
    "Market Quadrants",
    "The CV(τ) Playbook",
    "The Efficient Frontier",
])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — placeholder (MQI lives in Data Census)
# ──────────────────────────────────────────────────────────────────────────────
with tab1:
    def _lerp_hex(lo, hi, t):
        lr, lg, lb = int(lo[1:3],16), int(lo[3:5],16), int(lo[5:7],16)
        hr, hg, hb = int(hi[1:3],16), int(hi[3:5],16), int(hi[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(
            int(lr+(hr-lr)*t), int(lg+(hg-lg)*t), int(lb+(hb-lb)*t)
        )

    def _mqi_color(val, vmin, vmid, vmax):
        if val <= vmid:
            t = max(0.0, (val - vmin) / max(vmid - vmin, 1e-9))
            return _lerp_hex("#c8dede", "#7bbfbb", t)
        else:
            t = min(1.0, (val - vmid) / max(vmax - vmid, 1e-9))
            return _lerp_hex("#21918c", "#0a4a47", t)

    def _map_cat_mqi(cat):
        c = str(cat).lower()
        if "uberx" in c: return "X"
        if "comfort" in c or "business_comfort" in c: return "Mid-tier"
        if "black" in c: return "Black"
        return None

    _df = df_mqi.copy()
    _df["simplified_category"] = _df["category"].apply(_map_cat_mqi)
    _df["eph_operational"] = pd.to_numeric(_df["eph_operational"], errors="coerce")

    _df_core = _df[_df["simplified_category"].isin(["X", "Mid-tier", "Black"])].dropna(subset=["eph_operational"]).copy()
    _cap99 = float(np.percentile(_df_core["eph_operational"].values, 99))
    _df_core = _df_core[_df_core["eph_operational"] <= _cap99]

    _anchors = _df_core.groupby("simplified_category")["eph_operational"].median().to_dict()
    _df_core["iq"] = _df_core["eph_operational"] / _df_core["simplified_category"].map(_anchors)

    CAT_ORDER  = ["X", "Mid-tier", "Black"]
    CAT_COLORS = {"X": "#99d5d1", "Mid-tier": "#21918c", "Black": "#0a4a47"}

    st.markdown("""
<p style='color:#555;font-size:0.88rem;line-height:1.7;max-width:860px;'>
The Market Quality Index measures how rich or lean the offer pool was within a given session —
but without normalization, a single strong premium offer would dominate the session score and drown out a cluster of suboptimal X offers.
Each offer is scored against its tier's historical median EPH, then aggregated into a single session-level MQI.
</p>
""", unsafe_allow_html=True)

    _p97 = float(np.percentile(_df_core["eph_operational"].values, 97))
    _p02 = float(np.percentile(_df_core["eph_operational"].values, 2))

    _AXIS_COMMON = dict(
        paper_bgcolor="white", plot_bgcolor="white",
        font_family="Inter", showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
        violingap=0.35, height=380,
    )

    fig_before = go.Figure()
    for cat in CAT_ORDER:
        color   = CAT_COLORS[cat]
        v_eph   = _df_core[_df_core["simplified_category"] == cat]["eph_operational"].values
        med_eph = float(np.median(v_eph))
        fig_before.add_trace(go.Violin(
            y=v_eph, x=[cat] * len(v_eph),
            name=cat, fillcolor=color, opacity=0.55,
            line_color=color, line_width=1.5,
            points=False, spanmode="soft",
            box_visible=True, box_fillcolor="white", meanline_visible=False,
            hovertemplate=f"<b>{cat}</b><br>EPH Operational: $%{{y:.2f}} MXN/hr<extra></extra>",
        ))
        fig_before.add_annotation(
            x=cat, y=med_eph, showarrow=False, xshift=44,
            text=f"<b>${med_eph:.0f}</b>",
            font=dict(size=10, color=color, family="Inter"),
            bgcolor="white", bordercolor=color, borderwidth=1, borderpad=3,
        )
    fig_before.update_layout(
        **_AXIS_COMMON,
        title=dict(text="Before: Raw EPH Operational by Category (MXN/hr)",
                   font_size=13, x=0.5, xanchor="center"),
        yaxis=dict(title="MXN/hr", range=[_p02, 475],
                   gridcolor="#f0f0f0", zeroline=False,
                   tickfont=dict(size=11), title_font=dict(size=12)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )

    fig_after = go.Figure()
    for cat in CAT_ORDER:
        color  = CAT_COLORS[cat]
        v_iq   = _df_core[_df_core["simplified_category"] == cat]["iq"].values
        anchor = _anchors.get(cat, 1.0)
        fig_after.add_trace(go.Violin(
            y=v_iq, x=[cat] * len(v_iq),
            name=cat, fillcolor=color, opacity=0.22,
            line_color=color, line_width=1.5,
            points="all", jitter=0.35, pointpos=0,
            marker=dict(color=color, size=2, opacity=0.12),
            hoveron="points+violins", spanmode="soft",
            box_visible=False, meanline_visible=False,
            hovertemplate=f"<b>{cat}</b><br>IQ: %{{y:.2f}}<extra></extra>",
        ))
        fig_after.add_annotation(
            x=cat, y=1.0, showarrow=False, yshift=16,
            text=f"<b>${anchor:.0f}/hr</b>",
            font=dict(size=10, color=color, family="Inter"),
            bgcolor="white", bordercolor=color, borderwidth=1, borderpad=4,
        )
    fig_after.add_hline(y=1.0, line_dash="dash", line_color="#475569", line_width=1.2, opacity=0.5)
    fig_after.add_annotation(
        x=1.0, y=1.0, xref="paper", yref="y",
        text="1.0 — market average", showarrow=False,
        xanchor="right", yshift=-12,
        font=dict(size=9, color="#475569", family="Inter"),
    )
    fig_after.update_layout(
        **_AXIS_COMMON,
        title=dict(text="After: Quality Index (IQ) Normalized",
                   font_size=13, x=0.5, xanchor="center"),
        yaxis=dict(title="Quality Index", gridcolor="#f0f0f0", zeroline=False,
                   tickfont=dict(size=11), title_font=dict(size=12)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
    )

    _col_a, _col_b = st.columns(2)
    with _col_a:
        st.plotly_chart(fig_before, use_container_width=True)
    with _col_b:
        st.plotly_chart(fig_after, use_container_width=True)

    st.markdown(
        "<div style='font-size:0.9rem;font-weight:700;color:#334155;margin:20px 0 2px;'>"
        "Session Quality Timeline</div>"
        "<div style='color:#888;font-size:0.82rem;margin:0 0 8px 0;'>"
        "Each box is one session. Darker teal = above the 1.0 baseline; lighter teal = below.</div>",
        unsafe_allow_html=True,
    )

    _mqi_sess = _df_core.groupby("session_fk").agg(
        MQI=("iq", "mean"), N=("eph_operational", "count"),
    ).reset_index()
    _mqi_sess = _mqi_sess[_mqi_sess["N"] >= 10].sort_values("session_fk")

    if _mqi_sess.empty:
        st.warning("Not enough sessions with 10+ offers to render timeline.")
    else:
        vmin_s = float(_mqi_sess["MQI"].min())
        vmax_s = float(_mqi_sess["MQI"].max())
        _df_sm = _df_core[_df_core["session_fk"].isin(_mqi_sess["session_fk"])].merge(
            _mqi_sess[["session_fk", "MQI"]], on="session_fk"
        )
        fig_sess = go.Figure()
        for sess_id in _mqi_sess["session_fk"]:
            sd      = _df_sm[_df_sm["session_fk"] == sess_id]
            mqi_val = float(sd["MQI"].iloc[0])
            hex_col = _mqi_color(mqi_val, vmin_s, 1.0, vmax_s)
            fig_sess.add_trace(go.Box(
                y=sd["iq"], name=str(sess_id),
                marker=dict(color=hex_col, size=3, opacity=0.6),
                line=dict(color=hex_col, width=1.2),
                fillcolor=hex_col, boxpoints="outliers",
                hovertemplate=(
                    f"<b>{sess_id}</b><br>MQI: {mqi_val:.2f}<br>IQ: %{{y:.2f}}<extra></extra>"
                ),
            ))
        fig_sess.add_hline(y=1.0, line_dash="dot", line_color="#475569", line_width=1.2, opacity=0.5)
        fig_sess.add_annotation(
            x=1.0, y=1.0, xref="paper", yref="y",
            text="<b>1.0</b>  global baseline", showarrow=False,
            xanchor="right", yshift=10,
            font=dict(size=9, color="#475569", family="Inter"),
        )
        fig_sess.update_layout(
            height=360, paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10), font_family="Inter",
            showlegend=False,
            yaxis=dict(title="IQ", range=[0.4, 2.6], zeroline=False,
                       gridcolor="#f0f0f0", tickfont=dict(size=11, family="Inter"),
                       title_font=dict(size=12, family="Inter")),
            xaxis=dict(type="category", showticklabels=False, showgrid=False, zeroline=False),
        )
        st.plotly_chart(fig_sess, use_container_width=True)

        st.markdown("""
<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:4px;font-size:0.82rem;color:#334155;line-height:1.7;'>
The market is deeply heterogeneous — both across sessions and within them. Selectivity exploits market variance, but waiting burns EPH. To optimize this trade-off, sessions must first be classified by the quality and velocity of their offer flow.
</div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — The Money Map
# ──────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown(
        "<p style='color:#555;font-size:0.88rem;line-height:1.7;max-width:860px;'>"
        "Each session was classified into one of four quadrants defined by two axes: "
        "Market Quality (MQI) on the vertical, and Market Velocity — the median wait time between offers — on the horizontal. "
        "Circle size represents the total gross potential value of the session."
        "</p>",
        unsafe_allow_html=True,
    )

    with st.expander("View SQL"):
        st.code(query_moneymap, language="sql")

    fig_money = go.Figure()
    _sizeref = 2.0 * session_stats['total_potential'].max() / (70.**2)
    for quad in ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']:
        qd = session_stats[session_stats['Quadrant'] == quad]
        fig_money.add_trace(go.Scatter(
            x=qd['velocity_median'], y=qd['quality_median'],
            mode='markers', name=quad,
            marker=dict(
                color=COLORS[quad],
                size=qd['total_potential'],
                sizemode='area',
                sizeref=_sizeref,
                sizemin=10,
                line=dict(width=0.8, color='white'),
                opacity=0.72,
            ),
            customdata=qd[['session_fk', 'offer_count', 'total_potential']],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Total Potential: $%{customdata[2]:,.0f}<br>"
                "Offers: %{customdata[1]}<br>"
                "Median Wait: %{x:.0f}s<br>"
                "MQI: %{y:.2f}<extra></extra>"
            ),
        ))

    y_max = session_stats['quality_median'].max() * 1.05
    y_min = session_stats['quality_median'].min() * 0.95
    x_max = session_stats['velocity_median'].max() * 1.05
    x_min = max(0, session_stats['velocity_median'].min() - 10)

    fig_money.add_vline(x=GLOBAL_VELOCITY, line_width=1.5, line_dash="dash", line_color="#d1d5db")
    fig_money.add_hline(y=GLOBAL_QUALITY,  line_width=1.5, line_dash="dash", line_color="#d1d5db")
    fig_money.update_layout(
        autosize=True, height=620,
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Inter",
        title=dict(text="", font=dict(size=14, color="#334155")),
        xaxis_title=dict(text=f"Market Friction — Median Wait: {GLOBAL_VELOCITY:.0f}s",
                         font=dict(size=12, color="#334155")),
        yaxis_title=dict(text="Market Quality (Median MQI)", font=dict(size=12, color="#334155")),
        xaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        yaxis=dict(gridcolor="#f0f0f0", zeroline=False),
        annotations=[
            dict(x=x_min, y=y_max, text="PARADISE", showarrow=False,
                 xanchor='left', yanchor='top',
                 font=dict(color=COLORS['Rich / Fast'], size=11, family="Inter")),
            dict(x=x_max, y=y_max, text="SNIPER", showarrow=False,
                 xanchor='right', yanchor='top',
                 font=dict(color=COLORS['Rich / Slow'], size=11, family="Inter")),
            dict(x=x_min, y=y_min, text="GRIND", showarrow=False,
                 xanchor='left', yanchor='bottom',
                 font=dict(color=COLORS['Poor / Fast'], size=11, family="Inter")),
            dict(x=x_max, y=y_min, text="DESERT", showarrow=False,
                 xanchor='right', yanchor='bottom',
                 font=dict(color=COLORS['Poor / Slow'], size=11, family="Inter")),
        ],
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.01,
                    font=dict(size=11, family="Inter")),
        margin=dict(l=50, r=110, t=50, b=50),
    )
    st.plotly_chart(fig_money, use_container_width=True)

    # ── Quadrant bento cards ──
    _quad_summary = (
        session_stats.groupby("Quadrant")
        .agg(
            sessions=("session_fk", "count"),
            med_mqi=("quality_median", "median"),
            med_wait=("velocity_median", "median"),
            avg_offers=("offer_count", "mean"),
        )
        .reset_index()
        .sort_values("med_mqi", ascending=False)
        .to_dict("records")
    )
    _QUAD_ORDER = ["Rich / Fast", "Rich / Slow", "Poor / Fast", "Poor / Slow"]
    _quad_summary = sorted(_quad_summary, key=lambda r: _QUAD_ORDER.index(r["Quadrant"]) if r["Quadrant"] in _QUAD_ORDER else 99)

    _bento_cols = st.columns(4)
    for _col, _row in zip(_bento_cols, _quad_summary):
        _q = _row["Quadrant"]
        _accent = COLORS.get(_q, "#21918c")
        with _col:
            st.markdown(f"""
<div style='border-top:3px solid {_accent};background:#ffffff;border-radius:8px;
     padding:14px 16px 12px;font-family:Inter,sans-serif;'>
  <div style='font-size:0.65rem;font-weight:800;text-transform:uppercase;letter-spacing:0.9px;
       color:{_accent};margin-bottom:10px;'>{_q.replace(" / ", " · ")}</div>
  <div style='display:flex;flex-direction:column;gap:6px;'>
    <div>
      <div style='font-size:1.35rem;font-weight:700;color:#1e293b;line-height:1;'>{_row["sessions"]}</div>
      <div style='font-size:0.65rem;color:#94a3b8;margin-top:1px;letter-spacing:0.3px;'>Sessions</div>
    </div>
    <div style='border-top:1px solid #f1f5f9;padding-top:6px;'>
      <div style='font-size:1.05rem;font-weight:600;color:#1e293b;line-height:1;'>{_row["med_mqi"]:.2f}</div>
      <div style='font-size:0.65rem;color:#94a3b8;margin-top:1px;letter-spacing:0.3px;'>Median MQI</div>
    </div>
    <div style='border-top:1px solid #f1f5f9;padding-top:6px;'>
      <div style='font-size:1.05rem;font-weight:600;color:#1e293b;line-height:1;'>{_row["med_wait"]:.0f}s</div>
      <div style='font-size:0.65rem;color:#94a3b8;margin-top:1px;letter-spacing:0.3px;'>Median Wait</div>
    </div>
    <div style='border-top:1px solid #f1f5f9;padding-top:6px;'>
      <div style='font-size:1.05rem;font-weight:600;color:#1e293b;line-height:1;'>{_row["avg_offers"]:.0f}</div>
      <div style='font-size:0.65rem;color:#94a3b8;margin-top:1px;letter-spacing:0.3px;'>Avg Offers</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Key insight callout ──
    _paradise_pct = int(round(
        len(session_stats[session_stats["Quadrant"] == "Rich / Fast"]) / len(session_stats) * 100
    ))
    st.markdown(f"""
<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;
 padding:12px 16px;margin-top:16px;font-size:0.82rem;color:#334155;line-height:1.7;'>
Only <strong>{_paradise_pct}%</strong> of sessions fell into the Paradise quadrant — high quality <em>and</em> high velocity.
With the market quadrants established, rational search time boundaries can now be derived for each regime in the next phase.
</div>
""", unsafe_allow_html=True)

    st.write("")

    # ── Pending fix yellow callout ──
    st.markdown("""
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — Backpropagate session MQI change</span><br><br>
  Session MQI was updated from <strong>mean → median</strong> in this chart. This change must be
  backpropagated to: the LaTeX paper (PNG figures) and the source Jupyter notebooks (.ipynb).
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — The CV(τ) Playbook
# ──────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        "<p style='color:#555;font-size:0.88rem;line-height:1.7;max-width:860px;'>"
        "The playbook operationalizes the Continuation Value formula. For a given target yield and market regime, "
        "it computes the empirical probability of encountering a premium offer within each search window "
        "and resolves whether waiting is mathematically justified over accepting the immediate baseline."
        "<span class='fn-wrap'><span class='fn-mark'>†</span><span class='fn-tooltip' style='width:300px;font-size:0.75rem;line-height:1.6;'>"
        "<b>Scope &amp; constraint:</b> This playbook answers one specific question — <em>is waiting for +$30/hr over your current offer worth it?</em> "
        "The $30 gap is held constant across all slider positions so that any change in the optimal search window reflects "
        "target difficulty and market regime only, not a change in the size of the bet. "
        "It does not prescribe an absolute yield to aim for — only whether the gamble is rational given the market you are currently in."
        "</span></span>"
        "</p>",
        unsafe_allow_html=True,
    )

    with st.expander("View SQL"):
        st.code(query_ven, language="sql")

    TARGET_EPH = st.select_slider(
        "Target Premium Yield ($/hr)",
        options=[170, 180, 200, 220, 250, 280],
        value=200,
        help="The premium rate you are holding out for. Baseline is locked at $30 below this.",
    )
    BASELINE_EPH = TARGET_EPH - 30

    props_target = df_playbook[df_playbook['eph_real'].between(TARGET_EPH - 15, TARGET_EPH + 15)][
        ['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()
    props_base   = df_playbook[df_playbook['eph_real'].between(BASELINE_EPH - 15, BASELINE_EPH + 15)][
        ['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()

    if props_target.isnull().any() or props_base.isnull().any():
        st.warning(f"⚠️ Insufficient historical data near ${TARGET_EPH}/hr or ${BASELINE_EPH}/hr. Adjust the slider.")
    else:
        # 1:1 port of Jupyter Cell 3.5 — global sort, forward-looking roll, quadrant-grouped probability
        df_sim = df_playbook.sort_values('offer_timestamp').copy()
        df_sim['is_success'] = (df_sim['eph_real'] >= TARGET_EPH).astype(int)
        df_sim = df_sim.set_index('offer_timestamp')
        df_reversed = df_sim.iloc[::-1]

        time_windows = {'1m': '60s', '3m': '180s', '5m': '300s', '10m': '600s', '15m': '900s'}
        results = []
        eph_base_immediate = (props_base['upfront_fare'] /
                              (props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec'])) * 3600

        for label, delta_str in time_windows.items():
            delta_sec = int(delta_str[:-1])

            found_success = df_reversed['is_success'].rolling(window=delta_str).max().iloc[::-1]
            probs = found_success.groupby(df_sim['Quadrant']).mean()

            for quad, p in probs.items():
                cycle_success = delta_sec + props_target['time_to_pickup_sec'] + props_target['est_trip_time_sec']
                eph_success   = (props_target['upfront_fare'] / cycle_success) * 3600
                cycle_failure = delta_sec + props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec']
                eph_failure   = (props_base['upfront_fare'] / cycle_failure) * 3600
                ev_wait = (p * eph_success) + ((1 - p) * eph_failure)
                ven     = ev_wait - eph_base_immediate
                results.append({'Quadrant': quad, 'Window': label, 'VEN': ven, 'Prob': p})

        df_res = pd.DataFrame(results)
        df_res['Label'] = df_res.apply(lambda x: f"<b>${x['VEN']:+.0f}</b><br>({x['Prob']:.0%})", axis=1)

        ven_matrix   = df_res.pivot(index='Quadrant', columns='Window', values='VEN')
        label_matrix = df_res.pivot(index='Quadrant', columns='Window', values='Label')
        q_order   = ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']
        cols_order = ['1m', '3m', '5m', '10m', '15m']
        ven_matrix   = ven_matrix.reindex([q for q in q_order if q in ven_matrix.index])[cols_order]
        label_matrix = label_matrix.reindex([q for q in q_order if q in label_matrix.index])[cols_order]

        fig_heat = go.Figure(data=go.Heatmap(
            z=ven_matrix.values, x=ven_matrix.columns, y=ven_matrix.index,
            text=label_matrix.values, texttemplate="%{text}",
            colorscale="RdYlGn", zmid=0, showscale=False,
            hovertemplate="<b>%{y}</b><br>Wait: %{x}<br>CV(τ): $%{z:.2f}<extra></extra>",
        ))
        fig_heat.update_layout(
            autosize=True, height=500,
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            title=dict(
                text=f"CV(τ) — Continuation Value by Regime & Search Window  "
                     f"(Target: ${TARGET_EPH}/hr | Baseline: ${BASELINE_EPH}/hr)",
                font=dict(size=13, color="#334155"),
            ),
            xaxis_title=dict(text="Search Window", font=dict(size=12, color="#334155")),
            yaxis_title=dict(text="Market Regime", font=dict(size=12, color="#334155")),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=60, r=20, t=60, b=80),
            annotations=[dict(
                x=1, y=-0.22, xref="paper", yref="paper",
                xanchor="right", yanchor="bottom",
                text="<b>$</b> = expected return of waiting (CV(τ)) · <b>%</b> = probability of finding a premium offer within the window"
                     " · <span style='color:#5a8a3c;'>●</span> Green = wait · <span style='color:#b8860b;'>●</span> Yellow = marginal · <span style='color:#b91c1c;'>●</span> Red = accept now",
                showarrow=False,
                font=dict(size=11, color="#64748b"),
                align="right",
            )],
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        # ── Dynamic callout derived from df_res ──
        _window_order  = ['1m', '3m', '5m', '10m', '15m']
        _window_min    = {'1m': 1, '3m': 3, '5m': 5, '10m': 10, '15m': 15}

        _at_15m = df_res[df_res['Window'] == '15m']
        _prob_min_15 = f"{_at_15m['Prob'].min():.0%}"
        _prob_max_15 = f"{_at_15m['Prob'].max():.0%}"
        _ven_min_15  = f"${_at_15m['VEN'].min():+.0f}"
        _ven_max_15  = f"${_at_15m['VEN'].max():+.0f}"

        # Interpolate breakeven minute per quadrant, then report median across quadrants
        _breakevens = []
        for _q in df_res['Quadrant'].unique():
            _qrows = df_res[df_res['Quadrant'] == _q].set_index('Window')
            for _i in range(len(_window_order) - 1):
                _wa, _wb = _window_order[_i], _window_order[_i + 1]
                if _wa not in _qrows.index or _wb not in _qrows.index:
                    continue
                _va, _vb = _qrows.loc[_wa, 'VEN'], _qrows.loc[_wb, 'VEN']
                if _va > 0 and _vb <= 0:
                    _ma, _mb = _window_min[_wa], _window_min[_wb]
                    _cross = _ma + (_va / (_va - _vb)) * (_mb - _ma)
                    _breakevens.append(_cross)
                    break
            else:
                if all(_qrows.loc[w, 'VEN'] > 0 for w in _window_order if w in _qrows.index):
                    _breakevens.append(15.0)

        _rational_boundary = f"~{np.median(_breakevens):.0f} min" if _breakevens else "unknown"

        st.markdown(
            f"<div style='border-left:4px solid #21918c;background:rgba(33,145,140,0.07);border-radius:0 8px 8px 0;"
            f"padding:14px 18px;margin-top:16px;font-size:0.82rem;color:#334155;line-height:1.8;'>"
            f"While the probability of finding a <b>${TARGET_EPH}/hr</b> offer ranges from "
            f"<b>{_prob_min_15}</b> to <b>{_prob_max_15}</b> across regimes after 15 minutes, "
            f"waiting that long yields a net return against the <b>${BASELINE_EPH}/hr</b> baseline "
            f"of <b>{_ven_min_15}</b> to <b>{_ven_max_15}</b> — "
            f"all negative. The rational boundary sits around <b>{_rational_boundary}</b>, "
            f"where CV(τ) crosses zero and patience stops paying."
            f"</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — The Efficient Frontier
# ──────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown(
        "<p style='color:#555;font-size:0.88rem;line-height:1.7;max-width:860px;'>"
        "For any given target ambition, this model calculates the <strong>Maximum Rational Search Time</strong> — "
        "the exact minute where the Net Expected Value drops below zero."
        "</p>",
        unsafe_allow_html=True,
    )

    target_range  = range(160, 240, 10)
    windows_min   = [1, 3, 5, 10, 15]
    windows_sec   = [60, 180, 300, 600, 900]
    windows_map   = dict(zip(windows_min, windows_sec))
    frontier_data = []

    with st.spinner("Simulating the Efficient Frontier…"):
        for target_eph in target_range:
            baseline_eph = target_eph - 30
            props_base   = df_playbook[df_playbook['eph_real'].between(baseline_eph - 15, baseline_eph + 15)][
                ['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()
            props_target = df_playbook[df_playbook['eph_real'].between(target_eph - 15, target_eph + 15)][
                ['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()

            if props_base.isnull().any() or props_target.isnull().any():
                continue

            eph_base_immediate = (props_base['upfront_fare'] /
                                  (props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec'])) * 3600

            df_sim = df_playbook.sort_values(['session_fk', 'offer_timestamp']).copy()
            df_sim['is_success'] = (df_sim['eph_real'] >= target_eph).astype(int)
            df_sim['offer_timestamp'] = pd.to_datetime(df_sim['offer_timestamp'])
            df_sim = df_sim.set_index('offer_timestamp')

            quadrant_vens = {q: [] for q in ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']}

            for w_min, w_sec in windows_map.items():
                window_str    = f"{w_sec}s"
                found_success = df_sim.groupby('session_fk')['is_success'].apply(
                    lambda x: x.iloc[::-1].rolling(window=window_str).max().iloc[::-1]
                ).reset_index(level=0, drop=True)
                df_sim['found_success'] = found_success
                probs = df_sim.groupby('Quadrant')['found_success'].mean()

                for quad in quadrant_vens:
                    if quad in probs:
                        prob          = probs[quad]
                        cycle_success = w_sec + props_target['time_to_pickup_sec'] + props_target['est_trip_time_sec']
                        eph_success   = (props_target['upfront_fare'] / cycle_success) * 3600
                        cycle_failure = w_sec + props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec']
                        eph_failure   = (props_base['upfront_fare'] / cycle_failure) * 3600
                        ev_wait       = (prob * eph_success) + ((1 - prob) * eph_failure)
                        ven           = ev_wait - eph_base_immediate
                        quadrant_vens[quad].append(ven)
                    else:
                        quadrant_vens[quad].append(np.nan)

            for quad, vens in quadrant_vens.items():
                valid_indices = [i for i, v in enumerate(vens) if not pd.isna(v)]
                if len(valid_indices) < 2:
                    continue
                x_vals = [windows_min[i] for i in valid_indices]
                y_vals = [vens[i]        for i in valid_indices]
                if y_vals[0] < 0:
                    break_even_time = 0
                elif all(y > 0 for y in y_vals):
                    break_even_time = 15.2
                else:
                    f = interp1d(y_vals, x_vals, kind='linear', fill_value="extrapolate")
                    break_even_time = float(np.clip(f(0), 0, 15.5))
                frontier_data.append({
                    'Target EPH': target_eph,
                    'Quadrant':   quad,
                    'Max Wait Time (Minutes)': break_even_time,
                })

    df_frontier = pd.DataFrame(frontier_data)
    if df_frontier.empty:
        st.warning("⚠️ Insufficient data to plot the Efficient Frontier.")
    else:
        teal_purple_palette = {
            'Rich / Fast': '#00897B',
            'Rich / Slow': '#4DB6AC',
            'Poor / Fast': '#BA68C8',
            'Poor / Slow': '#6A1B9A',
        }
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OPUS_GREY)
        ax.set_facecolor(OPUS_GREY)
        sns.lineplot(data=df_frontier, x='Target EPH', y='Max Wait Time (Minutes)',
                     hue='Quadrant', palette=teal_purple_palette, style='Quadrant',
                     markers=True, dashes=False, linewidth=3, markersize=9, ax=ax)
        ax.axhline(0, color='black', linewidth=1.5, linestyle='-')
        ax.set_ylim(0, 9)

        rich_fast = df_frontier[df_frontier['Quadrant'] == 'Rich / Fast']
        for _, row in rich_fast.iterrows():
            ax.text(row['Target EPH'], row['Max Wait Time (Minutes)'] + 0.2,
                    f"{row['Max Wait Time (Minutes)']:.1f}m",
                    color=teal_purple_palette['Rich / Fast'], fontsize=10,
                    fontweight='bold', ha='center')

        ax.set_title('The Efficient Frontier: Rational Search Time by Ambition',
                     fontsize=18, fontweight='bold', color=OPUS_PURPLE, pad=25)
        fig.text(0.5, 0.02,
                 "Baseline Assumption: For any Target $X, the alternative is holding a Base Offer of ($X - 30)",
                 ha="center", fontsize=11, style='italic', color='#555555',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=5))
        ax.set_xlabel('Target Ambition ($/hr)', fontsize=12, fontweight='bold', color=OPUS_TEXT)
        ax.set_ylabel('Max Rational Search Time (Minutes)', fontsize=12, fontweight='bold', color=OPUS_TEXT)
        ax.set_xticks(list(target_range))
        ax.grid(True, alpha=0.15)
        ax.legend(title='Market Context', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
        plt.subplots_adjust(bottom=0.15)
        st.pyplot(fig)
