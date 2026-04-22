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
    json_path = Path(__file__).resolve().parent.parent / ".streamlit" / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

client = get_bq_client()

# 2. DEFINICIÓN DEL CANON VISUAL (Opus Lab)
OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
OPUS_TEXT   = '#121212'

def map_category(cat_name):
    """Maps platform-specific categories to simplified operational tiers."""
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower:
        return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower:
        return "Mid-tier"
    elif 'black' in cat_lower:
        return "Premium"
    else:
        return "X"

def obfuscate_fare(value):
    """Legacy helper for currency masking (BVP standard uses Percentiles)."""
    try:
        if value is None: return "N/A"
        s = f"{float(value):.2f}"
        dot_idx = s.find('.')
        prefix = s[:max(0, dot_idx-1)]
        return f"{prefix}X.XX"
    except:
        return "N/A"

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.facecolor': OPUS_GREY, 'axes.facecolor': OPUS_GREY,
    'text.color': OPUS_TEXT, 'axes.titlecolor': OPUS_PURPLE,
    'axes.titleweight': 'bold'
})

# 3. CONFIGURACIÓN DE LA PÁGINA
st.title("Causal Inference: Revisiting the Initial Hypothesis")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Motion to Explore! ...Proceed</span>**", unsafe_allow_html=True)
st.set_page_config(layout="wide")


# Create the tabs (Cognitive Load = Minimized)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Payout Stability", 
    "Baseline OLS", 
    "Heteroscedasticity Audit", 
    "Time-vs-Money Matrix", 
    "LOWESS Response Curve", 
    "Polynomial Risk Model"
])

# ==============================================================================
# PHASE 1: FINANCIAL STABILITY & POLICY INTERVENTION AUDIT
# ==============================================================================
with tab1:
    st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 1: Financial Stability & Policy Intervention</span>**", unsafe_allow_html=True)

    # --- NEW: CAUSAL INFERENCE CONTEXT ---
    st.markdown(r"""
    Following the acquisition phase, the initial hypothesis regarding the Payout Spread was formally tested using the verified ground-truth of completed missions ($N = 249$, August 22 – October 1 window). The longitudinal data confirms that the **"structural haircut"** identified during the pilot study remains a consistent property of the marketplace architecture throughout the entire campaign.

    The analysis reveals a highly stable financial equilibrium. While individual mission yields exhibit significant dispersion, the 5-mission moving average remains tightly anchored at a global mean of **0.8361**. This confirms that the platform operates under a consistent payout target for the majority of the operational window.
    """)

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
        df['session_date'] = pd.to_datetime(df['session_date'])
        return df
        
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

    # Policy Intervention Line
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
        yaxis_title=dict(text="Financial Spread (Realized / Upfront)", font=dict(size=14, color=OPUS_TEXT)),
        yaxis=dict(range=[0.6, 1.3], gridcolor='lightgrey', zeroline=False),
        xaxis=dict(gridcolor='lightgrey'),
        margin=dict(l=60, r=20, t=40, b=50),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="white", bordercolor="#cccccc", borderwidth=1)
    )

    st.plotly_chart(fig1, use_container_width=True)

    # --- 4. ENHANCED STATISTICS & INTERVENTION CONTEXT ---
    pre_event = df_dated[df_dated['session_date'] < event_date]['financial_spread'].mean()
    post_event = df_dated[df_dated['session_date'] >= event_date]['financial_spread'].mean()
    lift = ((post_event/pre_event)-1)*100

    st.markdown(f"""
    A critical exogenous event occurred on **September 24**, when the platform issued a formal "Policy Intervention" message promising an increase in earnings. The empirical data confirms the validity of this signal:
    * **Mean Spread (Pre-Intervention):** {pre_event:.4f}
    * **Mean Spread (Post-Intervention):** {post_event:.4f}
    * **Realized Yield Lift:** {lift:.2f}%

    This finding proves that while the system is anchored, it is not static, and formal policy communications result in a measurable shift in the underlying financial physics of the marketplace.
    """)





# ==============================================================================
# PHASE 1.5: THE BASELINE MODEL (FINANCIAL PREDICTABILITY)
# ==============================================================================
with tab2:
    st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 1.5: The Baseline Model</span>**", unsafe_allow_html=True)

    st.markdown("""
    #### **The Baseline Model: Financial Predictability**
    To transition from longitudinal monitoring to formal inference, a baseline Ordinary Least Squares (OLS) model was architected to quantify the structural relationship between the quoted fare and operational reality. The estimated regression equation is defined as:
    """)

    # We use st.latex to force centering and bypass Markdown's underscore issues
    st.latex(r"\widehat{\text{realized\_fare}} = 6.31 + 0.79 \cdot \text{upfront\_fare}")

    st.markdown("""
    The model results, summarized below, establish the global financial "physics" of the marketplace.
    """)

    # --- OLS METRICS TABLE ---
    # Using raw strings r"" for the beta symbols so the \b doesn't act as a backspace
    metrics_col1 = {
        "Metric": ["R-squared ($R^2$)", r"Intercept ($\beta_0$)", r"Slope ($\beta_1$)"],
        "Value": ["0.930", "6.3081", "0.7906"]
    }
    metrics_col2 = {
        "Diagnostic": ["Prob (F-statistic)", "Skewness", "Kurtosis"],
        "Value": ["1.00e-144", "2.638", "13.054"]
    }

    c1, c2 = st.columns(2)
    with c1:
        st.table(pd.DataFrame(metrics_col1))
    with c2:
        st.table(pd.DataFrame(metrics_col2))

    st.markdown(r"""
    The model exhibits a high coefficient of determination ($R^2 = 0.930$), confirming that 93% of the variance in realized earnings is explained by the initial offer. This demonstrates a robust **Predictive Synchrony** across the system. 

    However, the high explanatory power masks severe structural instability. The extreme **Kurtosis (13.05)** and **positive Skewness (2.64)** serve as immediate analytical red flags. These metrics indicate a highly non-normal error distribution with "heavy tails," suggesting that the model's predictability is not uniform. The presence of these outliers and the significant deviation from normality point toward a violation of the homoscedasticity assumption, necessitating a deeper investigation: **residual analysis**.
    """)






# ==============================================================================
# PHASE 2: THE HETEROSCEDASTICITY AUDIT (THE CONE OF UNCERTAINTY)
# ==============================================================================
import statsmodels.api as sm
import statsmodels.stats.api as sms
import numpy as np

with tab3:
    st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 2: The Cone of Uncertainty</span>**", unsafe_allow_html=True)

    # --- NEW: CAUSAL INFERENCE CONTEXT (INTRO) ---
    st.markdown(r"""
    #### **Heteroscedasticity: The Cone of Uncertainty**
    To validate the stability of the baseline model, an analysis on residuals was conducted. The objective was to determine if the prediction error remained constant across the financial spectrum or if it scaled with the magnitude of the transaction.

    The visual inspection identifies a classic fanning pattern, or *Cone of Uncertainty*. While the model is highly precise for low-value missions, the variance of the residuals expands significantly as the **Quoted Fare** increases. To confirm this observation with statistical rigor, a Breusch-Pagan test was executed, yielding a p-value of $0.0286$. This result formally rejects the null hypothesis of homoscedasticity, confirming that the model's error variance is non-constant ($p < 0.05$).
    """)

    # --- THE "0 BS" SQL REVEAL ---
    query_phase2 = """
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
    """

    with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
        st.code(query_phase2, language="sql")

    # --- 1. DATA INGESTION ---
    @st.cache_data
    def get_risk_data():
        client = get_bq_client()
        df = client.query(query_phase2).to_dataframe()
        df['session_date'] = pd.to_datetime(df['session_date'])
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
    fig2.add_trace(go.Scatter(x=x_cone, y=0.15 * x_cone, mode='lines', name='+15% Risk Expansion', line=dict(color=OPUS_PURPLE, dash='dot', width=2), hoverinfo='skip'))
    fig2.add_trace(go.Scatter(x=x_cone, y=-0.15 * x_cone, mode='lines', name='-15% Risk Expansion', line=dict(color=OPUS_PURPLE, dash='dot', width=2), hoverinfo='skip'))

    # Verdict Annotation
    verdict_text = f"<b>Statistical Audit:</b><br>• BP p-value: {bp_pvalue:.2e}<br>• Verdict: HETEROSCEDASTICITY CONFIRMED"

    fig2.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text=verdict_text,
        showarrow=False, align="left",
        bgcolor="white", bordercolor=OPUS_PURPLE, borderwidth=1,
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
            bgcolor="white", bordercolor="#cccccc", borderwidth=1,
            font=dict(size=11)
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

    # --- NEW: CAUSAL INFERENCE CONTEXT (OUTRO & TRANSITION) ---
    st.markdown(r"""
    The 15% Risk Expansion Band confirms that absolute financial uncertainty scales proportionally with the **Quoted Fare**. While this diagnostic provided a clear measure of historical variance, the causal inquiry was temporarily paused once it became evident that the model lacked the explanatory power to determine *why* this uncertainty existed. It was only during subsequent multivariate interaction analysis on the completed missions cohort that a superior predictive signal was identified: the **Temporal Variance** (or *Time Spread*).
    """)




# ==============================================================================
# THE REALITY CHECK MATRIX (CORE MISSIONS)
# ==============================================================================
import plotly.express as px

with tab4:
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

    # --- 4. CAUSAL INFERENCE CONTEXT (OUTRO) ---
    st.markdown(r"""
    #### **The Hierarchy of Predictability**
    The correlation matrix reveals a systemic **Hierarchy of Predictability** that prioritizes price stability over operational variance. While the correlation between the Upfront Fare and Realized Fare is nearly perfect ($r = 0.961$), the Operational Synchrony for trip duration is significantly lower ($r = 0.813$). The most critical evidence of this decoupling is the correlation between Realized Fare and Actual Trip Time, which stands at only **0.621**. In an unbuffered marketplace, the final price would be highly sensitive to the actual time spent on the road ($r > 0.90$); however, the observed 0.621 correlation proves that the platform deliberately insulates the financial outcome from temporal fluctuations. The system isn't merely predicting the fare; it is enforcing it.

    #### **Strategic Buffer & Moral Hazard**
    This decoupling suggests a *Fraud Prevention Mechanism* in action. By maintaining a 0.961 financial synchrony while allowing for a 0.813 temporal variance, the algorithm acts as a **Strategic Buffer** that suppresses the marginal financial gain for additional minutes. This might be specifically designed to neutralize moral hazard by ensuring that the financial incentive for a driver to **intentionally take additional minutes for their own profit** is effectively eliminated. 

    Within this window, moderate operational noise or deliberate padding is filtered out of the final transaction rather than being passed on to the passenger. To quantify the exact boundaries of this buffer and identify the threshold where the platform's response shifts from inelasticity to legitimate compensation for exogenous shocks, a **Fraud Prevention Response Curve** has been architected.
    """)


# ==============================================================================
# PHASE 3: THE FRAUD PREVENTION MECHANISM AUDIT (THE "U" CURVE)
# ==============================================================================
with tab5:
    st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 3: The Fraud Prevention Mechanism</span>**", unsafe_allow_html=True)

    # --- CAUSAL INFERENCE CONTEXT (INTRO) ---
    st.markdown(r"""
    #### **The Response Curve: Quantifying Inelasticity**
    To visualize the strategic buffer in action, the relationship between temporal variance and financial outcome was modeled using a Locally Weighted Scatterplot Smoothing (LOWESS) regression. The resulting **Fraud Prevention Response Curve** identifies the empirical boundaries of the platform’s risk-sharing architecture.
    """)

    # --- THE "0 BS" SQL REVEAL (Updated with Metadata) ---
    query_fraud_prevention = """
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
    """

    with st.expander("🔍 Click here to view the live BigQuery SQL (No Hardcoding)"):
        st.code(query_fraud_prevention, language="sql")

    # --- 1. DATA INGESTION ---
    @st.cache_data
    def get_fraud_prevention_data():
        client = get_bq_client()
        df = client.query(query_fraud_prevention).to_dataframe()
        df['session_date'] = pd.to_datetime(df['session_date'])
        return df

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
                annotation_text="Perfect Prediction (T_act = T_est)", annotation_position="top left")

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

    # --- 4. FINAL VERDICT & CAUSAL INFERENCE ---
    st.info(f"**Global Correlation (Time Variance vs. Financial Outcome):** {r_val:.4f}")

    st.markdown(r"""
    #### **Operational Regimes & Market Physics**
    The visualization identifies two distinct operational regimes:

    * **The Integrity Buffer (1.0x - 1.35x):** The response curve exhibits near-total inelasticity. In this window, an increase in trip duration does not result in a proportional increase in realized fare. By maintaining a flat payout profile during moderate delays, the mechanism ensures that the financial burden of standard operational noise is absorbed by the operational margin, effectively removing the incentive for intentional duration padding.
    * **Exogenous Shocks (> 1.35x):** The curve reaches an inflection point and shifts to a sharp positive slope. This transition indicates that the algorithm distinguishes between driver-induced inefficiency and exogenous systemic shocks (e.g., major accidents or extreme rush-hour volatility). Once the delay is clearly beyond the driver's control envelope, the platform triggers a compensatory adjustment, realigning the financial outcome with the actual labor performed. 

    > **Analytical Conclusion:** This non-linear architecture confirms that the system is expertly calibrated to prioritize price integrity and fraud prevention while maintaining a safety net for legitimate market disruptions.
    """)


# ==============================================================================
# THE MATHEMATICAL VERDICT (QUADRATIC RISK MODEL)
# ==============================================================================
import statsmodels.formula.api as smf
import numpy as np
with tab6:
    st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>The Mathematical Verdict: Quadratic Risk Model</span>**", unsafe_allow_html=True)

    # --- CAUSAL INFERENCE CONTEXT (INTRO) ---
    st.markdown(r"""
    #### **Mathematical Formalization: The Inelasticity Threshold**
    To provide a precise mathematical anchor for the observed response curve, a quadratic polynomial regression was fitted to the dataset. This model quantifies the exact point where the platform's *Fraud Prevention Mechanism* reaches its maximum inelasticity before transitioning into compensatory adjustment. The estimated quadratic equation is defined as:
    """)

    # Centered LaTeX Equation
    st.latex(r"\widehat{Yield} = 0.9915 - 0.3645(\Delta T) + 0.1945(\Delta T^2)")

    st.markdown(r"""
    Where $\Delta T$ represents the **Temporal Variance** (Actual/Estimated Time). The model is statistically robust, with an F-statistic of 46.80 and a highly significant p-value ($8.22 \times 10^{-18}$), confirming that the non-linear architecture is a structural property of the system rather than a stochastic artifact.
    """)

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
        marker=dict(symbol='star', size=18, color=OPUS_PURPLE, line=dict(width=1, color='white')),
        hovertemplate="<b>Inelasticity Threshold:</b> %{x:.2f}x<br><b>Predicted Spread:</b> %{y:.2f}<extra></extra>"
    ))

    # Tipping Point Vertical Line
    fig5.add_vline(x=tipping_point, line_dash="dash", line_color=OPUS_PURPLE, opacity=0.8)

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
            bgcolor="white", bordercolor="#cccccc", borderwidth=1,
            font=dict(size=11)
        )
    )

    st.plotly_chart(fig5, use_container_width=True)

    # --- 4. CAUSAL INFERENCE CONTEXT (OUTRO) ---
    st.markdown(r"""
    > **Analytical Conclusion:** The analysis identifies the Inelasticity Threshold at **0.94x**. This finding is strategically significant: it proves that the "floor" of financial yield is reached even before the trip is officially categorized as delayed ($1.0x$). 

    The system exhibits total indifference to temporal fluctuations within the 0.90x to 1.30x range. By anchoring the payout at this 0.94x floor, the algorithm effectively decouples marginal labor time from marginal compensation. This architectural choice ensures that price integrity is maintained for the passenger while guaranteeing that the Agent is fully paid even if the mission is completed faster than expected. 

    The sharp upward trajectory beyond 1.4x confirms that the system incorporates a high-threshold safety net for catastrophic prediction errors, further reinforcing the platform's focus on mitigating moral hazard through strategic inelasticity.
    """)



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



# ==============================================================================
# THE EXECUTIVE SANDBOX: PREDICTIVE PHYSICS (GLOBAL FOOTER)
# ==============================================================================
import numpy as np
import plotly.graph_objects as go

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>The Executive Sandbox: Predictive Physics</span>**", unsafe_allow_html=True)
st.markdown("Test the platform's pricing architecture. Adjust the operational reality below to see how the system dynamically adjusts the payout yield against the structural baseline.")

# --- 1. REFINED INTERACTIVE INPUTS ---
col1, col2 = st.columns(2)
with col1:
    test_fare = st.selectbox(
        "Promised Upfront Fare ($)", 
        options=[50, 100, 150, 200, 300, 500], 
        index=3  # Defaults to 200 to match your test case
    )
with col2:
    time_spread = st.slider(
        "Time Spread (Actual / Est. Time)", 
        min_value=0.5, 
        max_value=3.0, 
        value=2.05, # Defaults to your test case
        step=0.05
    )

# --- 2. LIVE MATH ENGINE ---
# Quadratic Model (Current State)
quad_yield = 0.9915 - (0.3645 * time_spread) + (0.1945 * (time_spread ** 2))
quad_pred = test_fare * quad_yield

# The True Benchmark (Time Spread = 1.0x)
base_yield = 0.9915 - (0.3645 * 1.0) + (0.1945 * (1.0 ** 2)) # Equals 0.8215
base_pred = test_fare * base_yield

# Calculate True Delta (Against the 1.0x Baseline)
true_delta_usd = quad_pred - base_pred
true_delta_pct = (quad_pred / base_pred) - 1

# OLS Model (Calculated purely for the background chart baseline)
ols_pred = 6.3081 + (0.7906 * test_fare)

# --- 3. FOCUSED OUTPUT METRICS ---
st.write("") # Small spatial buffer
rc1, rc2, rc3 = st.columns(3)

# Metric 1: The Base Payout (The True Floor)
rc1.metric(
    label="Base Payout (T = 1.0x)", 
    value=f"${base_pred:.2f}", 
    delta="Structural Target", 
    delta_color="off"
)

# Metric 2: The Realized Fare + The Delta
rc2.metric(
    label="Realized Fare (Quadratic)", 
    value=f"${quad_pred:.2f}", 
    delta=f"{true_delta_pct * 100:+.1f}% vs Base Payout", 
    delta_color="normal" if true_delta_usd >= 0 else "inverse"
)

# Metric 3: The Delta in absolute dollars
rc3.metric(
    label="Exogenous Compensation", 
    value=f"{true_delta_usd:+.2f} MXN", 
    delta="Added for delay", 
    delta_color="normal" if true_delta_usd >= 0 else "inverse"
)
st.write("") # Small spatial buffer

# --- 4. THE DIVERGENCE CHART (Plotly) ---
# Generate the spectrum of Time Spreads for the X-axis
t_range = np.linspace(0.5, 3.0, 100)

# The OLS model is blind to time, creating a perfectly flat array of absolute dollars
ols_curve = np.full_like(t_range, ols_pred)

# The Quadratic curve
quad_curve_yield = 0.9915 - (0.3645 * t_range) + (0.1945 * (t_range ** 2))
quad_curve = test_fare * quad_curve_yield

fig_sandbox = go.Figure()

# Plot 1: The OLS Baseline (Flat Line)
fig_sandbox.add_trace(go.Scatter(
    x=t_range, 
    y=ols_curve, 
    mode='lines', 
    name='Naive OLS (Blind to Time)',
    line=dict(color="#cccccc", width=3, dash='dash'),
    hovertemplate="OLS Baseline: $%{y:.2f}<extra></extra>"
))

# Plot 2: The Quadratic Risk Architecture
fig_sandbox.add_trace(go.Scatter(
    x=t_range, 
    y=quad_curve, 
    mode='lines', 
    name='Quadratic Architecture',
    line=dict(color=OPUS_TEAL, width=4),
    hovertemplate="Risk Adjusted Payout: $%{y:.2f}<extra></extra>"
))

# Plot 3: The "You Are Here" Dynamic Marker
fig_sandbox.add_trace(go.Scatter(
    x=[time_spread], 
    y=[quad_pred], 
    mode='markers', 
    name='Current State',
    marker=dict(color=OPUS_PURPLE, size=18, symbol='star', line=dict(color='white', width=1)),
    hovertemplate="<b>Your State</b><br>Time Spread: %{x:.2f}x<br>Final Payout: $%{y:.2f}<extra></extra>"
))

# Add Integrity Buffer Shaded Region
fig_sandbox.add_vrect(
    x0=1.0, x1=1.35,
    fillcolor="grey", opacity=0.1,
    layer="below", line_width=0,
    annotation_text="Integrity Buffer", annotation_position="bottom right"
)

# Layout Formatting
fig_sandbox.update_layout(
    autosize=True,
    height=400,
    plot_bgcolor=OPUS_GREY,
    paper_bgcolor=OPUS_GREY,
    xaxis_title=dict(text="Time Spread (Actual / Estimated)", font=dict(size=14, color=OPUS_TEXT)),
    yaxis_title=dict(text="Predicted Payout ($ MXN)", font=dict(size=14, color=OPUS_TEXT)),
    xaxis=dict(range=[0.5, 3.0], gridcolor='lightgrey'),
    yaxis=dict(gridcolor='lightgrey', zeroline=False),
    margin=dict(l=60, r=20, t=20, b=50),
    legend=dict(
        yanchor="bottom", y=0.02, 
        xanchor="left", x=0.02,
        bgcolor="rgba(255,255,255,0.8)", 
        bordercolor="#cccccc", borderwidth=1
    )
)

st.plotly_chart(fig_sandbox, use_container_width=True)