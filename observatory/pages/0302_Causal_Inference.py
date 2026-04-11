import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from google.cloud import bigquery
from pathlib import Path
import plotly.graph_objects as go


# 1. SETUP CLIENTE (Conectando a tu pienza_mini)
@st.cache_resource
def get_bq_client():
    # .parent nos saca de 'pages' y nos deja en 'observatory'
    # Ahí es donde vive tu service-account.json
    json_path = Path(__file__).resolve().parent.parent / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

client = get_bq_client()

# 2. DEFINICIÓN DEL CANON VISUAL (Opus Lab)
OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
OPUS_TEXT   = '#121212'

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.facecolor': OPUS_GREY, 'axes.facecolor': OPUS_GREY,
    'text.color': OPUS_TEXT, 'axes.titlecolor': OPUS_PURPLE,
    'axes.titleweight': 'bold'
})

# 3. CONFIGURACIÓN DE LA PÁGINA
st.title("Causal Inference & The Policy Intervention")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Motion to Explore! ...Proceed</span>**", unsafe_allow_html=True)
st.set_page_config(layout="wide")




# ==============================================================================
# PHASE 1: FINANCIAL STABILITY & POLICY INTERVENTION AUDIT
# ==============================================================================
st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 1: Financial Stability & Policy Intervention</span>**", unsafe_allow_html=True)
st.markdown("Tracking the financial spread and the impact of the September yield lift.")

# --- THE OBFUSCATION LOGIC (3-Digit Masking) ---
def obfuscate_fare(value):
    try:
        if value is None: return "N/A"
        s = f"{float(value):.2f}"
        dot_idx = s.find('.')
        # Rule: Keep first two digits, mask the 3rd, mask cents
        # e.g., 145.45 -> 14X.XX
        prefix = s[:dot_idx-1]
        return f"{prefix}X.XX"
    except:
        return "N/A"

# --- THE CATEGORY MAPPING LOGIC ---
def map_category(cat_name):
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower:
        return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower:
        return "Mid-tier"
    elif 'black' in cat_lower:
        return "Premium"
    else:
        return "X"

# --- THE "0 BS" SQL REVEAL ---
query_phase1 = """
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
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
    st.code(query_phase1, language="sql")

# --- 1. DATA INGESTION ---
@st.cache_data
def get_stability_data():
    client = get_bq_client()
    df = client.query(query_phase1).to_dataframe()
    
    # Safety Check
    if 'upfront_fare' not in df.columns:
        st.error("🔴 Cache Mismatch: Please 'Clear Cache' in the top-right menu.")
        st.stop()
        
    df['session_date'] = pd.to_datetime(df['session_date'])
    return df
    
df_dated = get_stability_data()

# --- 2. DATA PREPARATION ---
df_dated = df_dated.sort_values(['session_date', 'offer_id'], ascending=True)
df_dated['mission_rank'] = range(1, len(df_dated) + 1)
df_dated['spread_ma'] = df_dated['financial_spread'].rolling(window=5).mean()

# Apply Obfuscation and Custom Category Mapping
df_dated['upfront_masked'] = df_dated['upfront_fare'].apply(obfuscate_fare)
df_dated['realized_masked'] = df_dated['realized_fare'].apply(obfuscate_fare)
df_dated['tier_label'] = df_dated['category'].apply(map_category)

event_date = pd.to_datetime('2025-09-24')
event_rank = df_dated[df_dated['session_date'] >= event_date]['mission_rank'].min()
global_mean = df_dated['financial_spread'].mean()

# --- 3. INTERACTIVE PLOTTING ---
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df_dated['mission_rank'],
    y=df_dated['financial_spread'],
    mode='markers',
    name='Individual Mission Yield',
    marker=dict(color=OPUS_TEAL, size=8, opacity=0.4, line=dict(width=0.5, color='white')),
    
    # Custom Data Payload
    customdata=df_dated[['offer_id', 'session_date', 'upfront_masked', 'realized_masked', 'tier_label']],
    
    hovertemplate=(
        "<b>Offer ID:</b> %{customdata[0]}<br>" +
        "<b>Tier:</b> %{customdata[4]}<br>" +
        "<b>Date:</b> %{customdata[1]|%Y-%m-%d}<br>" +
        "<b>Upfront Fare:</b> $%{customdata[2]}<br>" +
        "<b>Realized Fare:</b> $%{customdata[3]}<br>" +
        "<b>Spread:</b> %{y:.4f}<br>" +
        "<extra></extra>"
    )
))

# Trend Line (Moving Average)
fig1.add_trace(go.Scatter(
    x=df_dated['mission_rank'], y=df_dated['spread_ma'],
    mode='lines', name='5-Mission Moving Average',
    line=dict(color='red', width=2), hoverinfo='skip'
))

# Global Baseline
fig1.add_hline(y=global_mean, line_dash="dash", line_color="#666666",
               annotation_text=f"Global Average: {global_mean:.4f}", annotation_position="bottom right")

if pd.notna(event_rank):
    fig1.add_vline(x=event_rank, line_width=2, line_color=OPUS_PURPLE)
    fig1.add_annotation(
        x=event_rank, y=1.25, text='POLICY INTERVENTION',
        showarrow=True, arrowhead=2, arrowcolor=OPUS_PURPLE,
        ax=-60, ay=-30, bgcolor="white", bordercolor=OPUS_PURPLE, borderwidth=1
    )

fig1.update_layout(
    autosize=True,
    plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
    xaxis_title=dict(text="Operational Timeline", font=dict(size=14, color=OPUS_TEXT)),
    yaxis_title=dict(text="Financial Spread", font=dict(size=14, color=OPUS_TEXT)),
    yaxis=dict(range=[0.6, 1.3], gridcolor='lightgrey', zeroline=False),
    xaxis=dict(gridcolor='lightgrey', tickformat="%b-%d"),
    margin=dict(l=60, r=20, t=40, b=50),
    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="white", bordercolor="#cccccc", borderwidth=1)
)

st.plotly_chart(fig1, use_container_width=True)

# --- 4. METRIC CARDS ---
pre_event = df_dated[df_dated['session_date'] < event_date]['financial_spread'].mean()
post_event = df_dated[df_dated['session_date'] >= event_date]['financial_spread'].mean()

st.divider()
col1, col2, col3 = st.columns(3)
lift = ((post_event/pre_event)-1)*100
col1.metric("Global Mean Spread", f"{global_mean:.4f}")
col2.metric("Post-Intervention Mean", f"{post_event:.4f}", f"{post_event-pre_event:.4f}")
col3.metric("Realized Yield Lift", f"{lift:.2f}%", f"{lift:.2f}%")


# ==============================================================================
# PHASE 2: THE HETEROSCEDASTICITY AUDIT (THE CONE OF UNCERTAINTY)
# ==============================================================================
import statsmodels.api as sm
import statsmodels.stats.api as sms

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 2: The Cone of Uncertainty</span>**", unsafe_allow_html=True)
st.markdown("Auditing prediction error as a function of deal size.")

# --- THE "0 BS" SQL REVEAL ---
query_phase2 = """
SELECT
    o.offer_id,
    p.category_name AS category,
    o.upfront_fare,
    v.realized_fare
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
WHERE v.realized_fare IS NOT NULL AND o.upfront_fare IS NOT NULL
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
    st.code(query_phase2, language="sql")

# --- 1. DATA INGESTION ---
@st.cache_data
def get_risk_data():
    client = get_bq_client()
    df = client.query(query_phase2).to_dataframe()
    return df

df_risk = get_risk_data()

# --- 2. DATA PREPARATION & OLS MODEL ---
df_risk['upfront_fare'] = pd.to_numeric(df_risk['upfront_fare'], errors='coerce')
df_risk['realized_fare'] = pd.to_numeric(df_risk['realized_fare'], errors='coerce')
df_clean = df_risk.dropna(subset=['upfront_fare', 'realized_fare'])

# Fit OLS Model
X = sm.add_constant(df_clean['upfront_fare'])
y = df_clean['realized_fare']
model_fare = sm.OLS(y, X).fit()

# Calculate Predictions and Residuals
df_clean['y_hat'] = model_fare.fittedvalues
df_clean['residuals'] = model_fare.resid

# Apply Hybrid Masking (Obfuscate only y, de-obfuscate others)
df_clean['upfront_masked'] = df_clean['upfront_fare'].apply(obfuscate_fare)
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
    
    # Custom Data: Mix of Obfuscated and Raw
    customdata=df_clean[['offer_id', 'tier_label', 'upfront_masked', 'y_hat', 'realized_fare']],
    hovertemplate=(
        "<b>Offer ID:</b> %{customdata[0]}<br>" +
        "<b>Tier:</b> %{customdata[1]}<br>" +
        "<b>Upfront (y):</b> $%{customdata[2]}<br>" +
        "<b>Predicted OLS (ŷ):</b> $%{customdata[3]:.2f}<br>" +
        "<b>Realized:</b> $%{customdata[4]:.2f}<br>" +
        "<b>Error (Residual):</b> %{y:.2f}<br>" +
        "<extra></extra>"
    )
))

# Zero-Error Baseline
fig2.add_hline(y=0, line_dash="dash", line_color="#121212", line_width=2)

# Risk Expansion Lines (±15% Cone)
fare_min, fare_max = df_clean['upfront_fare'].min(), df_clean['upfront_fare'].max()
x_cone = np.linspace(fare_min, fare_max, 100)
fig2.add_trace(go.Scatter(x=x_cone, y=0.15 * x_cone, mode='lines', name='+15% Risk', line=dict(color=OPUS_PURPLE, dash='dot', width=1.5), hoverinfo='skip'))
fig2.add_trace(go.Scatter(x=x_cone, y=-0.15 * x_cone, mode='lines', name='-15% Risk', line=dict(color=OPUS_PURPLE, dash='dot', width=1.5), hoverinfo='skip'))

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
    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="white", bordercolor="#cccccc", borderwidth=1)
)

st.plotly_chart(fig2, use_container_width=True)

# Math Summary
st.latex(r"e_i = y_i - \hat{y}_i")
st.info(f"**Breusch-Pagan p-value:** {bp_pvalue:.2e} | **Status:** {'Heteroscedasticity Detected' if bp_pvalue < 0.05 else 'Homoscedasticity Assumed'}")





# ==============================================================================
# THE REALITY CHECK MATRIX (CORE MISSIONS)
# ==============================================================================
import plotly.express as px

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>The Reality Check Matrix</span>**", unsafe_allow_html=True)
st.markdown("Auditing the platform's core financial and operational prediction accuracy.")

# --- THE "0 BS" SQL REVEAL ---
query_reality_check = """
SELECT
    o.upfront_fare,
    v.realized_fare,
    (o.est_trip_time_sec / 60.0) AS est_trip_time_min,
    (v.duration_trip_sec / 60.0) AS actual_trip_time_min
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
WHERE v.realized_fare IS NOT NULL 
  AND o.est_trip_time_sec > 0
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
    st.code(query_reality_check, language="sql")

# --- 1. DATA INGESTION (BigQuery) ---
@st.cache_data
def get_reality_check_data():
    client = get_bq_client()
    df = client.query(query_reality_check).to_dataframe()
    return df

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
    title=dict(
        text=f"Core Sample (N={len(df_core_reality)})<br><i>Correlation > 0.8 = High Predictive Synchrony</i>",
        font=dict(size=14, color=OPUS_TEXT),
        y=0.95
    ),
    xaxis=dict(tickfont=dict(size=12, color=OPUS_TEXT)),
    yaxis=dict(tickfont=dict(size=12, color=OPUS_TEXT)),
    margin=dict(l=20, r=20, t=80, b=20)
)

st.plotly_chart(fig3, use_container_width=True)

# --- 4. QUANTITATIVE INSIGHTS ---
st.info(f"**Financial Accuracy (Fare):** {corr_matrix_core.iloc[0,1]:.3f}  |  **Operational Accuracy (Time):** {corr_matrix_core.iloc[2,3]:.3f}")
st.info("Pending UPDATE hover para reflejar los insights del paper")


# ==============================================================================
# PHASE 3: THE FRAUD PREVENTION MECHANISM AUDIT (THE "U" CURVE)
# ==============================================================================
st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 3: The Fraud Prevention Mechanism</span>**", unsafe_allow_html=True)
st.markdown("Visualizing the 'Fraud Prevention Response Curve' and the structural plateau.")

# --- THE "0 BS" SQL REVEAL ---
query_fraud_prevention = """
SELECT
    o.offer_id,
    p.category_name AS category,
    v.spread_percentage AS financial_spread,
    (v.duration_trip_sec / NULLIF(o.est_trip_time_sec, 0)) AS time_spread
FROM `645009831643.pienza_mini.v_mission_dossier` v
JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
WHERE o.est_trip_time_sec > 0
  AND v.realized_fare IS NOT NULL
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
    st.code(query_fraud_prevention, language="sql")

# --- 1. DATA INGESTION (BigQuery) ---
@st.cache_data
def get_fraud_prevention_data():
    client = get_bq_client()
    df = client.query(query_fraud_prevention).to_dataframe()
    return df

df_fraud = get_fraud_prevention_data()

# --- 2. DATA PREPARATION ---
df_fraud['time_spread'] = pd.to_numeric(df_fraud['time_spread'], errors='coerce')
df_fraud['financial_spread'] = pd.to_numeric(df_fraud['financial_spread'], errors='coerce')
df_final = df_fraud.dropna(subset=['financial_spread', 'time_spread'])

# Calculate Correlation
r_val = df_final['time_spread'].corr(df_final['financial_spread'])

# --- 3. INTERACTIVE PLOTTING (Plotly) ---
# We use Plotly Express here to easily generate the LOWESS curve
fig4 = px.scatter(
    df_final, 
    x='time_spread', 
    y='financial_spread',
    opacity=0.4,
    color_discrete_sequence=[OPUS_TEAL],
    trendline="lowess",             # Automatically fits the LOWESS curve
    trendline_color_override="red", # Vibrant Red for the Signal
    hover_data=['offer_id', 'category']
)

# Customizing the traces for the visual canon
fig4.update_traces(marker=dict(size=8, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
fig4.update_traces(line=dict(width=3), selector=dict(mode='lines')) 

# --- STRATEGIC ANNOTATIONS ---
# Perfect Prediction Line
fig4.add_vline(x=1.0, line_dash="dash", line_color="#666666", 
               annotation_text="Perfect Prediction (T_act = T_est)", annotation_position="top left")

# Global Yield Baseline
fig4.add_hline(y=0.84, line_dash="dot", line_color="#666666", 
               annotation_text="Global Yield Baseline", annotation_position="bottom right")

# The "Fraud Prevention" Buffer Zone
fig4.add_vrect(
    x0=1.0, x1=1.35,
    fillcolor="grey", opacity=0.1,
    layer="below", line_width=0,
    annotation_text="Integrity Buffer<br>(Anti-Gaming Window)", annotation_position="top right"
)

# Layout Refinements (Fully Responsive)
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

# --- 4. FINAL VERDICT ---
st.info(f"**Global Correlation (Time Variance vs. Financial Outcome):** {r_val:.4f}")
st.markdown("""
> **Analytical Conclusion:** The response curve remains inelastic within the 1.0x-1.35x window, confirming the Fraud Prevention Mechanism's threshold.
""")






# ==============================================================================
# THE MATHEMATICAL VERDICT (QUADRATIC RISK MODEL)
# ==============================================================================
import statsmodels.formula.api as smf

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>The Mathematical Verdict: Quadratic Risk Model</span>**", unsafe_allow_html=True)
st.markdown("Locating the exact 'Inelasticity Threshold' where the platform's compensation model shifts.")

# --- THE "0 BS" MATH REVEAL ---
math_logic = """
# 1. Fit the Quadratic Model using the Phase 3 Dataset
model_poly = smf.ols('financial_spread ~ time_spread + np.power(time_spread, 2)', data=df_final).fit()

# 2. Calculate the Vertex (Tipping Point) using -b / 2a
b1 = model_poly.params['time_spread']
b2 = model_poly.params['np.power(time_spread, 2)']
tipping_point = -b1 / (2 * b2)
"""

with st.expander("🔍 Click here to view the Live Mathematical Model (No Hardcoding)"):
    st.markdown("This threshold is calculated dynamically from the Phase 3 dataset using Ordinary Least Squares (OLS) regression.")
    st.code(math_logic, language="python")

# --- 1. FIT THE QUADRATIC MODEL ---
model_poly = smf.ols('financial_spread ~ time_spread + np.power(time_spread, 2)', data=df_final).fit()

# --- 2. CALCULATE THE "TIPPING POINT" (Vertex) ---
b1 = model_poly.params['time_spread']
b2 = model_poly.params['np.power(time_spread, 2)']
tipping_point = -b1 / (2 * b2)

# Calculate the predicted y-value at the tipping point for our star marker
y_tip = model_poly.predict(pd.DataFrame({'time_spread': [tipping_point]})).iloc[0]

# --- 3. INTERACTIVE PLOTTING (Plotly) ---
fig5 = go.Figure()

# Plot the raw data (The operational cloud)
fig5.add_trace(go.Scatter(
    x=df_final['time_spread'],
    y=df_final['financial_spread'],
    mode='markers',
    name='Operational Cloud',
    marker=dict(color=OPUS_TEAL, size=8, opacity=0.25, line=dict(width=0.5, color='white')),
    hoverinfo='skip' # Keeping hover clean to focus on the curve
))

# Generate the Quadratic Fit Line (Thinner Red Line)
x_range = np.linspace(0.5, 2.5, 100)
y_pred = model_poly.predict(pd.DataFrame({'time_spread': x_range}))

fig5.add_trace(go.Scatter(
    x=x_range,
    y=y_pred,
    mode='lines',
    name='Quadratic Risk Model',
    line=dict(color='red', width=2)
))

# Mark the Tipping Point with the Star
fig5.add_trace(go.Scatter(
    x=[tipping_point],
    y=[y_tip],
    mode='markers',
    name=f'Threshold: {tipping_point:.2f}x',
    marker=dict(symbol='star', size=18, color=OPUS_PURPLE, line=dict(width=1, color='white')),
    hovertemplate="<b>Inelasticity Threshold:</b> %{x:.2f}x<br><b>Predicted Spread:</b> %{y:.2f}<extra></extra>"
))

# Tipping Point Vertical Line
fig5.add_vline(x=tipping_point, line_dash="dash", line_color=OPUS_PURPLE, opacity=0.8)

# Layout Aesthetics (Fully Responsive)
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
        bgcolor="white", bordercolor="#cccccc", borderwidth=1,
        font=dict(size=11)
    )
)

st.plotly_chart(fig5, use_container_width=True)

# --- 4. FINAL INSIGHT REPORT ---
st.markdown("---")
st.markdown(f"### 🎯 THE INELASTICITY THRESHOLD: **<span style='color:{OPUS_TEAL};'>{tipping_point:.2f}x</span>**", unsafe_allow_html=True)

st.info(f"""
**STRATEGIC INSIGHT:**

The platform's compensation model exhibits total INELASTICITY around the 1.0x mark. 
The 'Fraud Prevention Mechanism' establishes a structural floor at exactly **{tipping_point:.2f}x**.

Whether the trip is slightly faster (0.95x) or moderately delayed (up to 1.3x), the financial spread remains stagnant at the baseline level. This proves the platform is 'deaf' to marginal temporal variance, ensuring that price stability is maintained during the initial delay phase. 

True compensation (*The Disruption Clause*) only triggers when the error is catastrophic.
""")





st.info("### 🕵️‍♂️ OUTLIER DISPLAY")
st.info("DASHBOARD: Run the model against user created data")

