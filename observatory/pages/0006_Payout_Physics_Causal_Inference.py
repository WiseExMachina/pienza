import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from components.styles import GLOBAL_CSS
from config import FAVICON
from pages._0006_data import (
    OPUS_GREY,
    OPUS_TEAL,
    OPUS_TEXT,
    get_bq_client,
    get_fraud_prevention_data,
    get_reality_check_data,
    get_risk_data,
    get_stability_data,
    load_favicon_b64 as _load_favicon_b64,
    map_category,
    teal_callout,
)
from utils.mem_debug import log_mem

log_mem("0006 top")

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(page_title="Payout Physics | Pienza", page_icon=FAVICON, layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ols-kpi {
  position: relative; border-radius: 6px; padding: 6px 16px; cursor: default;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.ols-kpi:hover { transform: translateY(-4px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
.ols-tip {
  visibility: hidden; opacity: 0; width: 240px;
  background: #ffffff; color: #475569;
  font-size: 0.78rem; line-height: 1.55; font-weight: 400;
  border: 1px solid #21918c; border-radius: 8px; padding: 10px 14px;
  position: absolute; bottom: calc(100% + 10px); left: 50%;
  transform: translateX(-50%);
  box-shadow: 0 4px 14px rgba(0,0,0,0.10);
  transition: opacity 0.18s ease;
  z-index: 9999; text-transform: none; letter-spacing: 0;
}
.ols-tip::after {
  content: ''; position: absolute; top: 100%; left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent; border-top-color: #21918c;
}
.ols-kpi:hover .ols-tip { visibility: visible; opacity: 1; }
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def build_sidebar():
    with st.sidebar:
        st.markdown(
            "<div class='sb-brand'>"
            "<div class='sb-brand-mark'>"
            f"<img src='data:image/png;base64,{_load_favicon_b64()}' width='40' height='40' /></div>"
            "<div><div class='sb-brand-text-title'>Project Pienza</div>"
            "<div class='sb-brand-text-sub'>Digital Twin · CDMX</div></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.page_link("main.py", label="Home", icon=":material/home:")
        st.markdown("<div class='sb-section-label'>Modules</div>", unsafe_allow_html=True)
        st.page_link("pages/0001_Foundations.py", label="Foundations", icon=":material/layers:")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines", icon=":material/sync:")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store", icon=":material/database:")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics", icon=":material/search:")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping", icon=":material/report:")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference", icon=":material/account_tree:")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning", icon=":material/shield:")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer", icon=":material/bolt:")
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big", icon=":material/send:")

        with st.container(key="sb-footer"):
            st.markdown("---")
            pdf_link = (
                "<a href='app/static/Pienza_Papers.pdf' target='_blank' "
                "class='sb-pdf-link'>Download PDF</a>"
            )

            st.markdown(
                "<div class='sb-meta-line'><b>Author:</b> Bernardo Lozano Wise<br>"
                "<b>LinkedIn:</b> <a href='https://www.linkedin.com/in/bernardolw/' target='_blank' class='sb-pdf-link'>/bernardolw</a><br>"
                "<b>GitHub:</b> <a href='https://github.com/WiseExMachina/pienza' target='_blank' class='sb-pdf-link'>/pienza</a><br>"
                "<b>Domain:</b> Data Science — Mobility & Logistics<br>"
                "<b>Stack:</b> Python, XGBoost, TensorFlow, BigQuery, PySpark, NetworkX<br>"
                f"<b>AI Knowledge Base:</b> {pdf_link}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")

build_sidebar()
# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("# Payout Physics")
st.markdown("<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>Testing the Payout Spread — From Correlation to Causal Structure</h4>", unsafe_allow_html=True)

st.markdown("""
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
Rational search boundaries are only meaningful if the underlying payout structure is stable.
This section validates that foundation — formally testing the Payout Spread hypothesis across
the full mission cohort, retroactively confirming the assumptions the model was built on.
</p>
""", unsafe_allow_html=True)

top_tab1, top_tab2 = st.tabs(["Analysis", "Interactive Inference Tool"])

with top_tab1:
    st.markdown("""
<style>
.ci-stepper { display:flex; align-items:flex-start; gap:0; margin:18px 0 28px 0; }
.ci-step {
  display:flex; flex-direction:column; align-items:center; flex:1;
  position:relative; cursor:pointer;
}
.ci-step:not(:last-child)::after {
  content:''; position:absolute; top:14px; left:calc(50% + 14px);
  width:calc(100% - 28px); height:2px; background:rgba(33,145,140,0.2); z-index:0;
}
.ci-dot {
  width:28px; height:28px; border-radius:50%;
  background:rgba(33,145,140,0.12); border:1.5px solid rgba(33,145,140,0.4);
  display:flex; align-items:center; justify-content:center;
  font-size:0.60rem; font-weight:700; color:#21918c;
  z-index:1; position:relative; flex-shrink:0;
  transition: background 0.15s, border-color 0.15s;
}
.ci-step:hover .ci-dot { background:rgba(33,145,140,0.22); border-color:#21918c; }
.ci-step-label {
  font-size:0.68rem; font-weight:600; color:#334155;
  text-align:center; margin-top:6px; line-height:1.3;
}
.ci-step-sub {
  font-size:0.60rem; color:#94a3b8;
  text-align:center; margin-top:2px; line-height:1.3;
}
.ci-step:hover .ci-step-label { color:#21918c; }
/* hide inner subtab bar and its border — stepper handles navigation */
[data-baseweb="tab-panel"] [data-baseweb="tab-list"] { display:none !important; }
[data-baseweb="tab-panel"] [data-baseweb="tab-border"] { display:none !important; }
/* active stepper dot */
.ci-step.ci-active .ci-dot {
  background:#21918c !important; border-color:#21918c !important; color:#fff !important;
}
.ci-step.ci-active .ci-step-label { color:#21918c !important; font-weight:700; }
</style>
<div class="ci-stepper">
  <div class="ci-step">
    <div class="ci-dot">P1</div>
    <div class="ci-step-label">Payout Stability</div>
    <div class="ci-step-sub">Structural haircut confirmed</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P2</div>
    <div class="ci-step-label">Heteroscedasticity</div>
    <div class="ci-step-sub">Baseline OLS + Cone of uncertainty</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P3</div>
    <div class="ci-step-label">Reality Check Matrix</div>
    <div class="ci-step-sub">Hierarchy of predictability</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">P4</div>
    <div class="ci-step-label">LOWESS Curve</div>
    <div class="ci-step-sub">Integrity buffer identified</div>
  </div>
  <div class="ci-step">
    <div class="ci-dot">★</div>
    <div class="ci-step-label">Polynomial Model</div>
    <div class="ci-step-sub">Inelasticity threshold: 0.94x</div>
  </div>
</div>
""", unsafe_allow_html=True)

    components.html("""
<script>
setTimeout(function() {
  var steps = window.parent.document.querySelectorAll('.ci-step');
  var allTabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');

  function setActive(idx) {
    steps.forEach(function(s) { s.classList.remove('ci-active'); });
    if (steps[idx]) steps[idx].classList.add('ci-active');
  }

  // initialise: find which inner tab is currently selected
  var initIdx = 0;
  for (var j = 2; j < allTabs.length; j++) {
    if (allTabs[j].getAttribute('aria-selected') === 'true') { initIdx = j - 2; break; }
  }
  setActive(initIdx);

  steps.forEach(function(step, i) {
    step.addEventListener('click', function() {
      var target = allTabs[i + 2];
      if (target) {
        var sy = window.parent.scrollY;
        target.click();
        setActive(i);
        setTimeout(function() { window.parent.scrollTo(0, sy); }, 50);
        setTimeout(function() { window.parent.scrollTo(0, sy); }, 300);
      }
    });
  });
}, 300);
</script>
""", height=0)

    tab1, tab3, tab4, tab5, tab6 = st.tabs([
        "Payout Stability",
        "Heteroscedasticity Audit",
        "Time-vs-Money Matrix",
        "LOWESS Response Curve",
        "Polynomial Risk Model"
    ])

# ==============================================================================
# PHASE 1: FINANCIAL STABILITY & POLICY INTERVENTION AUDIT
# ==============================================================================
with tab1:
    st.markdown("""
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
Longitudinal analysis shows the platform enforces a structural haircut. Across 249 completed missions, the payout never drifts far from <strong style='color:#0f172a;'>0.84</strong> — individual yields scatter, but the 5-mission moving average stays anchored. The system isn't noisy; it's calibrated.
</p>
""", unsafe_allow_html=True)

    df_dated = get_stability_data()

    # --- 2. DATA PREPARATION ---
    df_dated = df_dated.sort_values(['session_date', 'offer_id'], ascending=True)
    df_dated['mission_rank'] = range(1, len(df_dated) + 1)
    df_dated['spread_ma'] = df_dated['financial_spread'].rolling(window=5).mean()

    # Mapping the Tier Label for the hover
    df_dated['tier_label'] = df_dated['category'].apply(map_category)

    event_date = pd.to_datetime('2025-09-24')
    event_rank = df_dated[df_dated['session_date'] >= event_date]['mission_rank'].min()
    global_mean = df_dated['financial_spread'].mean()

    # --- 3. INTERACTIVE PLOTTING (Plotly) ---
    fig1 = go.Figure()

    # Individual Missions
    fig1.add_trace(go.Scatter(
        x=df_dated['mission_rank'],
        y=df_dated['financial_spread'],
        mode='markers',
        name='Individual Mission Yield',
        marker=dict(color=OPUS_TEAL, size=8, opacity=0.4, line=dict(width=0.5, color='white')),
        
        # Custom Data: ID, Date, Tier
        customdata=df_dated[['offer_id', 'session_date', 'tier_label']],
        hovertemplate=(
            "<b>Offer ID:</b> %{customdata[0]}<br>" +
            "<b>Date:</b> %{customdata[1]|%Y-%m-%d}<br>" +
            "<b>Tier:</b> %{customdata[2]}<br>" +
            "<b>Financial Spread (Yield):</b> %{y:.4f}<br>" +
            "<extra></extra>"
        )
    ))

    # Trend Line (MA)
    fig1.add_trace(go.Scatter(
        x=df_dated['mission_rank'], y=df_dated['spread_ma'],
        mode='lines', name='5-Mission Moving Average',
        line=dict(color='red', width=2), hoverinfo='skip'
    ))

    # Global Baseline
    fig1.add_hline(y=global_mean, line_dash="dash", line_color="#666666",
                annotation_text=f"Global Average: {global_mean:.4f}", annotation_position="bottom right")

    # Pre / Post computed for stat row and callout below
    mask = df_dated['session_date'] < event_date
    pre_event = df_dated.loc[mask, 'financial_spread'].mean()
    post_event = df_dated.loc[~mask, 'financial_spread'].mean()
    lift = ((post_event / pre_event) - 1) * 100

    # Policy Intervention Line
    if pd.notna(event_rank):
        fig1.add_vline(x=event_rank, line_width=2, line_color=OPUS_TEAL)
        fig1.add_annotation(
            x=event_rank, y=1.25, text='POLICY INTERVENTION',
            showarrow=True, arrowhead=2, arrowcolor=OPUS_TEAL,
            ax=-60, ay=-30, bgcolor="white", bordercolor=OPUS_TEAL, borderwidth=1
        )

    fig1.update_layout(
        autosize=True,
        plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
        xaxis_title=dict(text="Operational Timeline", font=dict(size=14, color=OPUS_TEXT)),
        yaxis_title=dict(text="Financial Spread (Realized / Upfront)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis=dict(range=[0.6, 1.3], gridcolor='lightgrey', zeroline=False),
        xaxis=dict(gridcolor='lightgrey'),
        margin=dict(l=60, r=20, t=40, b=50),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="#F5F6F7", bordercolor="#cccccc", borderwidth=1)
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown(f"""
<div style='display:flex;align-items:center;justify-content:center;gap:32px;padding:14px 0;margin-bottom:20px;'>
  <div><span style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;'>Global Mean</span><br><span style='font-size:1.1rem;font-weight:800;color:#334155;'>{global_mean:.4f}</span></div>
  <div style='color:#cbd5e1;font-size:1.2rem;'>·</div>
  <div><span style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;'>Pre</span><br><span style='font-size:1.1rem;font-weight:800;color:#334155;'>{pre_event:.4f}</span></div>
  <div style='color:#cbd5e1;font-size:1.2rem;'>·</div>
  <div><span style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#21918c;'>Post</span><br><span style='font-size:1.1rem;font-weight:800;color:#21918c;'>{post_event:.4f}</span></div>
  <div style='color:#cbd5e1;font-size:1.2rem;'>·</div>
  <div style='background:rgba(33,145,140,0.1);border-radius:6px;padding:4px 12px;'><span style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#21918c;'>Yield Lift</span><br><span style='font-size:1.1rem;font-weight:800;color:#21918c;'>+{lift:.2f}%</span></div>
</div>""", unsafe_allow_html=True)

    st.markdown(teal_callout(f"The equilibrium is anchored, but not static. A September 24 policy intervention — a formal earnings increase notice — triggered a definitive <strong>+{lift:.2f}% yield lift</strong>, proving that formal communications measurably shift the underlying payout physics.", mb="0"), unsafe_allow_html=True)








# ==============================================================================
# PHASE 2: THE HETEROSCEDASTICITY AUDIT (THE CONE OF UNCERTAINTY)
# ==============================================================================
import statsmodels.api as sm
import statsmodels.stats.api as sms
import numpy as np

with tab3:

    # ── POLISHED TOP ────────────────────────────────────────────────────────────
    st.markdown("""
<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
A baseline Ordinary Least Squares (OLS) model was architected to quantify the structural relationship between the quoted fare and operational reality. The estimated regression equation is defined as:
</p>
""", unsafe_allow_html=True)

    st.latex(r"\widehat{\text{realized\_fare}} = 6.31 + 0.79 \cdot \text{upfront\_fare}")

    st.markdown("""
<div style='display:flex;align-items:center;gap:20px;padding:12px 0;margin-bottom:8px;justify-content:center;'>
  <div class='ols-kpi' style='border-left:3px solid #21918c;border-radius:0 4px 4px 0;padding:4px 10px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div class='ols-tip'>How much of the outcome the model explains. 93% of variation in realized fare is predicted by the quoted fare alone.</div>
    <span style='font-size:0.68rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>R-squared <span style='color:#22c55e;'>✓</span></span>
    <span style='font-size:0.88rem;font-weight:700;color:#334155;margin-left:8px;'>0.930</span>
  </div>
  <div class='ols-kpi' style='border-left:3px solid #21918c;border-radius:0 4px 4px 0;padding:4px 10px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div class='ols-tip'>Asymmetry in the error distribution. At 2.64, errors lean positive — the model undershoots more than it overshoots, especially at higher fares.</div>
    <span style='font-size:0.68rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>Skewness <span style='color:#f59e0b;'>⚠</span></span>
    <span style='font-size:0.88rem;font-weight:700;color:#334155;margin-left:8px;'>2.638</span>
  </div>
  <div class='ols-kpi' style='border-left:3px solid #21918c;border-radius:0 4px 4px 0;padding:4px 10px;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div class='ols-tip'>How extreme the outliers are. Normal sits around 3. At 13.05, the tails are dangerously fat — catastrophic prediction errors are far more frequent than the model assumes.</div>
    <span style='font-size:0.68rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>Kurtosis <span style='color:#ef4444;'>⚠</span></span>
    <span style='font-size:0.88rem;font-weight:700;color:#334155;margin-left:8px;'>13.054</span>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(teal_callout("The 93% predictive synchrony is a baseline illusion. Extreme Kurtosis (13.05) flags a heavily skewed error distribution, showing that predictability decays as the fare increases."), unsafe_allow_html=True)

    st.markdown("""<div style='font-size:1.4rem;color:#21918c;font-weight:700;margin:20px 0 4px 0;text-align:center;'>↓</div>""", unsafe_allow_html=True)

    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
The visual evidence reveals that the model is precise for low-value trips, but error variance fans out significantly as the quoted fare rises, thus confirming heteroscedasticity in the OLS residuals.
</p>""", unsafe_allow_html=True)

    df_risk = get_risk_data()

    # --- 2. DATA PREPARATION & OLS MODEL ---
    df_risk['upfront_fare'] = pd.to_numeric(df_risk['upfront_fare'], errors='coerce')
    df_risk['realized_fare'] = pd.to_numeric(df_risk['realized_fare'], errors='coerce')
    df_clean = df_risk.dropna(subset=['upfront_fare', 'realized_fare'])

    # Fit OLS Model
    X = sm.add_constant(df_clean['upfront_fare'])
    y = df_clean['realized_fare']
    model_fare = sm.OLS(y, X).fit()

    # Calculate Residuals
    df_clean['residuals'] = model_fare.resid

    # Apply Mappings
    df_clean['tier_label'] = df_clean['category'].apply(map_category)

    # --- 3. STATISTICAL VALIDATION (Breusch-Pagan) ---
    bp_test = sms.het_breuschpagan(model_fare.resid, model_fare.model.exog)
    bp_pvalue = bp_test[1]

    # --- 4. INTERACTIVE PLOTTING (Plotly) ---
    fig2 = go.Figure()

    # Individual Prediction Errors
    fig2.add_trace(go.Scatter(
        x=df_clean['upfront_fare'],
        y=df_clean['residuals'],
        mode='markers',
        name='Prediction Error',
        marker=dict(color=OPUS_TEAL, size=8, opacity=0.5, line=dict(width=0.5, color='white')),
        
        # Payload: ID, Date, Tier, Error
        customdata=df_clean[['offer_id', 'session_date', 'tier_label']],
        hovertemplate=(
            "<b>Offer ID:</b> %{customdata[0]}<br>" +
            "<b>Date:</b> %{customdata[1]|%Y-%m-%d}<br>" +
            "<b>Tier:</b> %{customdata[2]}<br>" +
            "<b>Error (Residual):</b> %{y:.2f}<br>" +
            "<extra></extra>"
        )
    ))

    # Zero-Error Baseline
    fig2.add_hline(y=0, line_dash="dash", line_color="#121212", line_width=2)

    # Risk Expansion Lines (The Cone)
    fare_min, fare_max = df_clean['upfront_fare'].min(), df_clean['upfront_fare'].max()
    x_cone = np.linspace(fare_min, fare_max, 100)
    fig2.add_trace(go.Scatter(x=x_cone, y=0.15 * x_cone, mode='lines', name='+15% Risk Expansion', line=dict(color=OPUS_TEAL, dash='dot', width=2), hoverinfo='skip'))
    fig2.add_trace(go.Scatter(x=x_cone, y=-0.15 * x_cone, mode='lines', name='-15% Risk Expansion', line=dict(color=OPUS_TEAL, dash='dot', width=2), hoverinfo='skip'))

    # Verdict Annotation
    verdict_text = f"<b>Statistical Audit:</b><br>• BP p-value: {bp_pvalue:.2e}<br>• Verdict: HETEROSCEDASTICITY CONFIRMED"

    fig2.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text=verdict_text,
        showarrow=False, align="left",
        bgcolor="white", bordercolor=OPUS_TEAL, borderwidth=1,
        font=dict(family="monospace", size=12)
    )

    # Layout Refinements
    fig2.update_layout(
        autosize=True,
        plot_bgcolor=OPUS_GREY,
        paper_bgcolor=OPUS_GREY,
        xaxis_title=dict(text="Platform's Promised Fare ($ MXN)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis_title=dict(text="Prediction Error (Residuals)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis=dict(gridcolor='lightgrey', zeroline=False),
        xaxis=dict(gridcolor='lightgrey'),
        margin=dict(l=60, r=20, t=40, b=50),
        legend=dict(
            yanchor="top", y=0.98, 
            xanchor="left", x=0.01,
            bgcolor="#F5F6F7", bordercolor="#cccccc", borderwidth=1,
            font=dict(size=11)
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(teal_callout("A simple OLS is not sufficient. To diagnose the root cause of this expanding variance, the next phase introduces the temporal variable."), unsafe_allow_html=True)




# ==============================================================================
# THE REALITY CHECK MATRIX (CORE MISSIONS)
# ==============================================================================
import plotly.express as px

with tab4:
    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
Pure financial prediction is insufficient. By cross-referencing estimated and realized fares against actual trip durations, this matrix exposes a Hierarchy of Predictability, revealing exactly how the algorithm weighs time against money.
</p>""", unsafe_allow_html=True)

    df_core_reality = get_reality_check_data()

    # --- 2. DATA PREPARATION ---
    for col in df_core_reality.columns:
        df_core_reality[col] = pd.to_numeric(df_core_reality[col], errors='coerce')
    df_core_reality = df_core_reality.dropna()

    df_core_reality.columns = [
        'Upfront Fare ($)', 
        'Realized Fare ($)', 
        'Est. Trip Time (min)', 
        'Actual Trip Time (min)'
    ]

    corr_matrix_core = df_core_reality.corr(method='pearson')

    # --- 3. INTERACTIVE HEATMAP (Plotly) ---
    teal_scale = [[0.0, "white"], [1.0, OPUS_TEAL]]

    fig3 = px.imshow(
        corr_matrix_core,
        text_auto=".3f",
        color_continuous_scale=teal_scale,
        aspect="auto",
        labels=dict(color="Correlation")
    )

    # Layout Refinements (Fully Responsive)
    fig3.update_layout(
        autosize=True,
        plot_bgcolor=OPUS_GREY,
        paper_bgcolor=OPUS_GREY,
        title=dict(text=""),
        xaxis=dict(tickfont=dict(size=12, color=OPUS_TEXT)),
        yaxis=dict(tickfont=dict(size=12, color=OPUS_TEXT)),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=40)
    )

    st.plotly_chart(fig3, use_container_width=True)

    # --- 4. INSIGHTS ---
    st.markdown("""
<div style='display:flex;flex-direction:column;gap:12px;max-width:480px;margin:28px auto 28px auto;'>
  <div style='background:#fff;border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px;'>
      <span style='font-family:monospace;font-size:0.6rem;font-weight:700;color:#94a3b8;'>r = 0.961</span>
      <span style='font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;padding:1px 5px;border-radius:4px;background:#f1f5f9;color:#64748b;'>Financial Synchrony</span>
    </div>
    <div style='font-size:0.8rem;font-weight:700;color:#1a1a1a;margin-bottom:2px;'>Upfront Fare → Realized Fare</div>
    <div style='font-size:0.72rem;color:#777;line-height:1.45;'>Near-perfect predictability. The platform locks in the financial outcome at offer time.</div>
  </div>
  <div style='background:#fff;border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px;'>
      <span style='font-family:monospace;font-size:0.6rem;font-weight:700;color:#94a3b8;'>r = 0.813</span>
      <span style='font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;padding:1px 5px;border-radius:4px;background:#f1f5f9;color:#64748b;'>Operational Synchrony</span>
    </div>
    <div style='font-size:0.8rem;font-weight:700;color:#1a1a1a;margin-bottom:2px;'>Est. Trip Time → Actual Trip Time</div>
    <div style='font-size:0.72rem;color:#777;line-height:1.45;'>Strong but lower. Time on the road is noisier than the money — and the algorithm knows it.</div>
  </div>
  <div style='background:#fff;border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px;'>
      <span style='font-family:monospace;font-size:0.6rem;font-weight:700;color:#94a3b8;'>r = 0.621</span>
      <span style='font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;padding:1px 5px;border-radius:4px;background:#fef3c7;color:#92400e;'>Smoking Gun ⚠</span>
    </div>
    <div style='font-size:0.8rem;font-weight:700;color:#1a1a1a;margin-bottom:2px;'>Realized Fare → Actual Trip Time</div>
    <div style='font-size:0.72rem;color:#777;line-height:1.45;'>In an unbuffered market this would exceed 0.90. The gap proves the platform deliberately decouples financial outcome from time spent — neutralizing the incentive to pad trips.</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(teal_callout("The platform doesn't predict the fare — it enforces it by creating a structural buffer. To map the elasticity of this buffer, the next phase introduces the Response Curve."), unsafe_allow_html=True)


# ==============================================================================
# PHASE 3: THE FRAUD PREVENTION MECHANISM AUDIT (THE "U" CURVE)
# ==============================================================================
with tab5:

    # --- CAUSAL INFERENCE CONTEXT (INTRO) ---
    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
To visualize the buffer in action, the relationship between temporal variance and financial outcome was modeled using a LOWESS regression.
</p>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    df_fraud = get_fraud_prevention_data()

    # --- 2. DATA PREPARATION ---
    df_fraud['time_spread'] = pd.to_numeric(df_fraud['time_spread'], errors='coerce')
    df_fraud['financial_spread'] = pd.to_numeric(df_fraud['financial_spread'], errors='coerce')
    df_final = df_fraud.dropna(subset=['financial_spread', 'time_spread'])
    df_final['tier_label'] = df_final['category'].apply(map_category)

    # Calculate Correlation
    r_val = df_final['time_spread'].corr(df_final['financial_spread'])

    # --- 3. INTERACTIVE PLOTTING (Plotly) ---
    # We use px.scatter for the LOWESS engine, then customize for the Canonical Hover
    fig4 = px.scatter(
        df_final, 
        x='time_spread', 
        y='financial_spread',
        opacity=0.4,
        color_discrete_sequence=[OPUS_TEAL],
        trendline="lowess",             
        trendline_color_override="red", 
        # We pass the metadata columns here so they are available for the hovertemplate
        hover_data={'offer_id': True, 'session_date': True, 'tier_label': True, 'financial_spread': ':.4f', 'time_spread': ':.4f'}
    )

    # Customizing the marker trace for the Canonical Hover
    fig4.update_traces(
        marker=dict(size=8, line=dict(width=0.5, color='white')),
        selector=dict(mode='markers'),
        hovertemplate=(
            "<b>Offer ID:</b> %{customdata[0]}<br>" +
            "<b>Date:</b> %{customdata[1]|%Y-%m-%d}<br>" +
            "<b>Tier:</b> %{customdata[2]}<br>" +
            "<b>Financial Spread:</b> %{y:.4f}<br>" +
            "<b>Time Spread:</b> %{x:.4f}<br>" +
            "<extra></extra>"
        ),
        # Map customdata to the columns in df_final
        customdata=df_final[['offer_id', 'session_date', 'tier_label']]
    )

    fig4.update_traces(line=dict(width=3), selector=dict(mode='lines')) 

    # --- STRATEGIC ANNOTATIONS ---
    fig4.add_vline(x=1.0, line_dash="dash", line_color="#666666",
                annotation_text="Perfect Prediction", annotation_position="bottom left")

    fig4.add_hline(y=0.84, line_dash="dot", line_color="#666666", 
                annotation_text="Global Yield Baseline", annotation_position="bottom right")

    fig4.add_vrect(
        x0=1.0, x1=1.35,
        fillcolor="grey", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="Integrity Buffer<br>(Anti-Gaming Window)", annotation_position="top right"
    )

    # Layout Refinements
    fig4.update_layout(
        autosize=True,
        plot_bgcolor=OPUS_GREY,
        paper_bgcolor=OPUS_GREY,
        xaxis_title=dict(text="Temporal Variance (Actual / Estimated)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis_title=dict(text="Financial Outcome (Realized / Upfront)", font=dict(size=14, color=OPUS_TEXT)),
        xaxis=dict(range=[0.5, 2.5], gridcolor='lightgrey'),
        yaxis=dict(range=[0.6, 1.3], gridcolor='lightgrey', zeroline=False),
        margin=dict(l=60, r=20, t=40, b=50),
        showlegend=False
    )

    st.plotly_chart(fig4, use_container_width=True)


    st.markdown("""
<div style='display:flex;flex-direction:column;gap:12px;max-width:480px;margin:28px auto 28px auto;'>
  <div style='background:#fff;border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px;'>
      <span style='font-family:monospace;font-size:0.6rem;font-weight:700;color:#94a3b8;'>1.0x – 1.35x</span>
      <span style='font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;padding:1px 5px;border-radius:4px;background:#f1f5f9;color:#64748b;'>Integrity Buffer</span>
    </div>
    <div style='font-size:0.8rem;font-weight:700;color:#1a1a1a;margin-bottom:2px;'>Inelastic Payout Zone</div>
    <div style='font-size:0.72rem;color:#777;line-height:1.45;'>A purely inelastic payout zone. The system flatlines compensation for moderate delays, neutralizing any incentive to intentionally pad trips.</div>
  </div>
  <div style='background:#fff;border-left:3px solid #21918c;border-radius:0 6px 6px 0;padding:10px 16px;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>
    <div style='display:flex;align-items:center;gap:8px;margin-bottom:2px;'>
      <span style='font-family:monospace;font-size:0.6rem;font-weight:700;color:#94a3b8;'>&gt; 1.35x</span>
      <span style='font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.4px;padding:1px 5px;border-radius:4px;background:#f1f5f9;color:#64748b;'>Exogenous Shocks</span>
    </div>
    <div style='font-size:0.8rem;font-weight:700;color:#1a1a1a;margin-bottom:2px;'>Elasticity Breaks</div>
    <div style='font-size:0.72rem;color:#777;line-height:1.45;'>Once delays exceed the driver's control envelope, the system compensates for the extreme volatility.</div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(teal_callout("This non-linear architecture confirms that the system is expertly calibrated to prioritize price integrity and fraud prevention while maintaining a safety net for legitimate market disruptions."), unsafe_allow_html=True)


# ==============================================================================
# THE MATHEMATICAL VERDICT (QUADRATIC RISK MODEL)
# ==============================================================================
import statsmodels.formula.api as smf
import numpy as np
with tab6:

    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
To provide a precise mathematical anchor for the observed response curve, a quadratic polynomial regression was fitted to the dataset. The estimated equation is defined as:
</p>""", unsafe_allow_html=True)

    st.latex(r"\widehat{Yield} = 0.9915 - 0.3645(\Delta T) + 0.1945(\Delta T^2)")

    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
Where ΔT represents the Temporal Variance (Actual/Estimated Time). The model is statistically robust (F-statistic: 46.80, p = 8.22 × 10⁻¹⁸), confirming the non-linear architecture is a structural property of the system.
</p>""", unsafe_allow_html=True)

    # --- THE "0 BS" MATH REVEAL ---
    math_logic = """
    # 1. Fit the Quadratic Model using the Phase 3 Dataset
    model_poly = smf.ols('financial_spread ~ time_spread + np.power(time_spread, 2)', data=df_final).fit()

    # 2. Calculate the Vertex (Tipping Point) using -b / 2a
    b1 = model_poly.params['time_spread']
    b2 = model_poly.params['np.power(time_spread, 2)']
    tipping_point = -b1 / (2 * b2)
    """

    # --- 1. FIT THE QUADRATIC MODEL ---
    # Using df_final from Phase 3
    model_poly = smf.ols('financial_spread ~ time_spread + np.power(time_spread, 2)', data=df_final).fit()

    # --- 2. CALCULATE THE "TIPPING POINT" (Vertex) ---
    b1 = model_poly.params['time_spread']
    b2 = model_poly.params['np.power(time_spread, 2)']
    tipping_point = -b1 / (2 * b2)

    # Calculate the predicted y-value at the tipping point for our star marker
    y_tip = model_poly.predict(pd.DataFrame({'time_spread': [tipping_point]})).iloc[0]

    # --- 3. INTERACTIVE PLOTTING (Plotly) ---
    fig5 = go.Figure()

    # Plot the raw data (The operational cloud) with CANONICAL HOVER
    fig5.add_trace(go.Scatter(
        x=df_final['time_spread'],
        y=df_final['financial_spread'],
        mode='markers',
        name='Operational Cloud',
        marker=dict(color=OPUS_TEAL, size=8, opacity=0.25, line=dict(width=0.5, color='white')),
        
        # Canonical Payload: ID, Date, Tier, Financial Spread, Time Spread
        customdata=df_final[['offer_id', 'session_date', 'tier_label']],
        hovertemplate=(
            "<b>Offer ID:</b> %{customdata[0]}<br>" +
            "<b>Date:</b> %{customdata[1]|%Y-%m-%d}<br>" +
            "<b>Tier:</b> %{customdata[2]}<br>" +
            "<b>Financial Spread:</b> %{y:.4f}<br>" +
            "<b>Time Spread:</b> %{x:.4f}<br>" +
            "<extra></extra>"
        )
    ))

    # Generate the Quadratic Fit Line
    x_range = np.linspace(0.5, 2.5, 100)
    y_pred = model_poly.predict(pd.DataFrame({'time_spread': x_range}))

    fig5.add_trace(go.Scatter(
        x=x_range,
        y=y_pred,
        mode='lines',
        name='Quadratic Risk Model',
        line=dict(color='red', width=2),
        hoverinfo='skip'
    ))

    # Mark the Tipping Point with the Star
    fig5.add_trace(go.Scatter(
        x=[tipping_point],
        y=[y_tip],
        mode='markers',
        name=f'Threshold: {tipping_point:.2f}x',
        marker=dict(symbol='star', size=18, color=OPUS_TEAL, line=dict(width=1, color='white')),
        hovertemplate="<b>Inelasticity Threshold:</b> %{x:.2f}x<br><b>Predicted Spread:</b> %{y:.2f}<extra></extra>"
    ))

    # Tipping Point Vertical Line
    fig5.add_vline(x=tipping_point, line_dash="dash", line_color=OPUS_TEAL, opacity=0.8)

    # Layout Aesthetics
    fig5.update_layout(
        autosize=True,
        plot_bgcolor=OPUS_GREY,
        paper_bgcolor=OPUS_GREY,
        xaxis_title=dict(text="Temporal Variance (Actual / Estimated)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis_title=dict(text="Financial Outcome (Realized / Upfront)", font=dict(size=14, color=OPUS_TEXT)),
        xaxis=dict(range=[0.5, 2.5], gridcolor='lightgrey'),
        yaxis=dict(range=[0.6, 1.3], gridcolor='lightgrey', zeroline=False),
        margin=dict(l=60, r=20, t=40, b=50),
        legend=dict(
            yanchor="top", y=0.98,
            xanchor="left", x=0.01,
            bgcolor="#F5F6F7", bordercolor="#cccccc", borderwidth=1,
            font=dict(size=11)
        )
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.markdown(teal_callout("By anchoring the payout at a 0.94x floor, the algorithm effectively decouples marginal labor time from marginal compensation, ensuring that price integrity is maintained for the passenger while guaranteeing that the Agent is fully paid even if the mission is completed faster than expected."), unsafe_allow_html=True)






# ==============================================================================
# TAB 2: EXECUTIVE SANDBOX
# ==============================================================================
with top_tab2:
    st.markdown("""<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>
See the fitted polynomial model in action. Adjust the upfront fare and time spread to observe how the estimated payout yield deviates from the structural baseline.
</p>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
    st.markdown(r"""
<div style='text-align:center;'>

$$\small \widehat{Fare}(\Delta T) = \begin{cases} 6.31 + 0.79 \cdot \text{Upfront Fare} & \text{if } \Delta T \leq 1.0 \\ \text{Upfront Fare} \times (0.9915 - 0.3645\,\Delta T + 0.1945\,\Delta T^2) & \text{if } \Delta T > 1.0 \end{cases}$$

</div>
""", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:32px;'></div>", unsafe_allow_html=True)

    # --- 1. REFINED INTERACTIVE INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        test_fare = st.selectbox(
            "Promised Upfront Fare ($)",
            options=[50, 100, 150, 200, 300, 500],
            index=3
        )
    with col2:
        time_spread = st.slider(
            "Time Spread (Actual / Est. Time)",
            min_value=0.5,
            max_value=3.0,
            value=2.05,
            step=0.05
        )

    # --- 2. LIVE MATH ENGINE ---
    base_pred = 6.3081 + (0.7906 * test_fare)

    if time_spread <= 1.0:
        quad_pred = base_pred
    else:
        quad_yield = 0.9915 - (0.3645 * time_spread) + (0.1945 * (time_spread ** 2))
        quad_pred = test_fare * quad_yield

    true_delta_usd = quad_pred - base_pred
    true_delta_pct = (quad_pred / base_pred) - 1

    ols_pred = 6.3081 + (0.7906 * test_fare)

    # --- 3. FOCUSED OUTPUT METRICS ---
    delta_color = "#21918c" if true_delta_usd >= 0 else "#ef4444"
    st.markdown(f"""
<div style='display:flex;gap:16px;margin:20px 0;'>
  <div style='flex:1;background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:18px 20px;box-shadow:0 4px 6px rgba(0,0,0,0.02);'>
    <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;margin-bottom:6px;'>Base Payout (T = 1.0x)</div>
    <div style='font-size:1.5rem;font-weight:800;color:#334155;'>${base_pred:.2f}</div>
    <div style='font-size:0.72rem;color:#94a3b8;margin-top:4px;'>Structural Target</div>
  </div>
  <div style='flex:1;background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:18px 20px;box-shadow:0 4px 6px rgba(0,0,0,0.02);'>
    <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;margin-bottom:6px;'>Realized Fare (Quadratic)</div>
    <div style='font-size:1.5rem;font-weight:800;color:#334155;'>${quad_pred:.2f}</div>
    <div style='font-size:0.72rem;color:{delta_color};margin-top:4px;'>{true_delta_pct * 100:+.1f}% vs Base Payout</div>
  </div>
  <div style='flex:1;background:#fff;border:1px solid #eaeaea;border-radius:12px;padding:18px 20px;box-shadow:0 4px 6px rgba(0,0,0,0.02);'>
    <div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#94a3b8;margin-bottom:6px;'>Exogenous Compensation</div>
    <div style='font-size:1.5rem;font-weight:800;color:{delta_color};'>{true_delta_usd:+.2f} MXN</div>
    <div style='font-size:0.72rem;color:#94a3b8;margin-top:4px;'>Added for delay</div>
  </div>
</div>""", unsafe_allow_html=True)

    # --- 4. THE DIVERGENCE CHART ---
    t_range = np.linspace(0.5, 3.0, 100)
    ols_curve = np.full_like(t_range, ols_pred)
    ols_base = 6.3081 + (0.7906 * test_fare)
    quad_curve = np.where(
        t_range <= 1.0,
        ols_base,
        test_fare * (0.9915 - (0.3645 * t_range) + (0.1945 * (t_range ** 2)))
    )

    fig_sandbox = go.Figure()
    fig_sandbox.add_trace(go.Scatter(x=t_range, y=ols_curve, mode='lines', name='Naive OLS (Blind to Time)', line=dict(color="#cccccc", width=3, dash='dash'), hovertemplate="OLS Baseline: $%{y:.2f}<extra></extra>"))
    fig_sandbox.add_trace(go.Scatter(x=t_range, y=quad_curve, mode='lines', name='Quadratic Architecture', line=dict(color=OPUS_TEAL, width=4), hovertemplate="Risk Adjusted Payout: $%{y:.2f}<extra></extra>"))
    fig_sandbox.add_trace(go.Scatter(x=[time_spread], y=[quad_pred], mode='markers', name='Current State', marker=dict(color=OPUS_TEAL, size=18, symbol='star', line=dict(color='white', width=1)), hovertemplate="<b>Your State</b><br>Time Spread: %{x:.2f}x<br>Final Payout: $%{y:.2f}<extra></extra>"))
    fig_sandbox.add_vrect(x0=1.0, x1=1.35, fillcolor="grey", opacity=0.1, layer="below", line_width=0, annotation_text="Integrity Buffer", annotation_position="bottom right")

    fig_sandbox.update_layout(
        autosize=True, height=400,
        plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
        xaxis_title=dict(text="Time Spread (Actual / Estimated)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis_title=dict(text="Predicted Payout ($ MXN)", font=dict(size=14, color=OPUS_TEXT)),
        xaxis=dict(range=[0.5, 3.0], gridcolor='lightgrey'),
        yaxis=dict(gridcolor='lightgrey', zeroline=False),
        margin=dict(l=60, r=20, t=20, b=50),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(255,255,255,0.8)", bordercolor="#cccccc", borderwidth=1)
    )

    st.plotly_chart(fig_sandbox, use_container_width=True)

    st.markdown(teal_callout(
        f"An upfront fare of <strong>${test_fare} MXN</strong> yields a base payout of <strong>${base_pred:.2f}</strong>. "
        f"Adjusting for a <strong>{time_spread:.2f}x</strong> time expansion, the model yields a realized fare of <strong>${quad_pred:.2f}</strong>."
    ), unsafe_allow_html=True)