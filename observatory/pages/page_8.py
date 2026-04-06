import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIGURACIÓN CANÓNICA ---
st.set_page_config(layout="wide", page_title="Cognitive Cascade | Pienza")

OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
TEAL_PURPLE_PALETTE = ['#00897B', '#4DB6AC', '#BA68C8', '#6A1B9A']

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER: EXECUTIVE SUMMARY ---
st.title("🧠 Phase 8: The Cognitive Cascade")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Explainable AI (XAI) & SHAP Value Decomposition</span>**", unsafe_allow_html=True)

st.markdown("""
> **The Black Box Dilemma:** Machine learning models often obscure their reasoning. The Cognitive Cascade tears down the black box, translating complex non-linear predictions into a human-readable sequence of decisions. 
> 
> Using **SHAP (SHapley Additive exPlanations)**, we can audit exactly *why* the Pienza engine flagged a specific dispatch as a high-yield opportunity.
""")
st.divider()

# --- 3. GLOBAL SHAP (MACRO VIEW) ---
st.subheader("🌍 Macro View: Global Feature Importance")
st.markdown("Which variables drive the algorithm's behavior across the entire market? This shows the mean absolute SHAP value for the top predictive features.")

# MOCK DATA: Global Feature Importance
df_global = pd.DataFrame({
    'Feature': ['Expected EPH (Historical)', 'Sanitized Search Delta', 'Time of Day Block', 'Zone Density Index', 'Pickup Ambiguity', 'Consecutive Rejects'],
    'Importance (Mean SHAP)': [0.85, 0.62, 0.45, 0.38, 0.25, 0.15]
}).sort_values(by='Importance (Mean SHAP)', ascending=True)

fig_global = px.bar(
    df_global, 
    x='Importance (Mean SHAP)', 
    y='Feature', 
    orientation='h',
    color_discrete_sequence=[OPUS_PURPLE]
)
fig_global.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), plot_bgcolor='white')
st.plotly_chart(fig_global, use_container_width=True)

st.divider()

# --- 4. LOCAL SHAP (MICRO VIEW - THE CASCADE) ---
st.subheader("💧 Micro View: The Local Cognitive Cascade (Waterfall)")
st.markdown("Select a specific operational scenario to see exactly how the algorithm derived its final Expected EPH prediction, step-by-step.")

# Escenarios Mockeados
scenario = st.selectbox(
    "Select an Operational Scenario to audit:",
    ["Scenario A: The Golden Ticket (High Yield)", "Scenario B: The Trap (Deceptive Offer)", "Scenario C: The Safe Bet (Average)"]
)

# Lógica del Mock basada en el escenario elegido
if "Golden Ticket" in scenario:
    base_val = 150
    measures = ["relative", "relative", "relative", "relative", "relative", "total"]
    x_labels = ["Base Market EPH", "High Demand Zone", "Rush Hour Boost", "Fast Search Rhythm", "Complex Dropoff", "Predicted Final EPH"]
    y_vals = [base_val, +35, +25, +15, -10, base_val + 35 + 25 + 15 - 10]
elif "The Trap" in scenario:
    base_val = 150
    measures = ["relative", "relative", "relative", "relative", "relative", "total"]
    x_labels = ["Base Market EPH", "High Fare Lure", "Terrible Traffic", "High Pickup Ambiguity", "Dead Zone Dropoff", "Predicted Final EPH"]
    y_vals = [base_val, +40, -30, -20, -25, base_val + 40 - 30 - 20 - 25]
else:
    base_val = 150
    measures = ["relative", "relative", "relative", "relative", "relative", "total"]
    x_labels = ["Base Market EPH", "Standard Zone", "Mid-Day Steady", "Typical Search", "Clear Navigation", "Predicted Final EPH"]
    y_vals = [base_val, +5, +0, -5, +10, base_val + 5 + 0 - 5 + 10]

# Construcción de la Cascada (Waterfall)
fig_waterfall = go.Figure(go.Waterfall(
    name="SHAP Impact",
    orientation="v",
    measure=measures,
    x=x_labels,
    textposition="outside",
    text=[f"${v:+.0f}" if i < len(y_vals)-1 else f"${v:.0f}" for i, v in enumerate(y_vals)],
    y=y_vals,
    connector={"line": {"color": "rgb(63, 63, 63)"}},
    decreasing={"marker": {"color": "#BA68C8"}}, # Soft Purple para negativos
    increasing={"marker": {"color": "#00897B"}}, # Strong Teal para positivos
    totals={"marker": {"color": OPUS_PURPLE}}    # Canonical Purple para el final
))

fig_waterfall.update_layout(
    title=f"SHAP Decision Breakdown for {scenario.split(':')[0]}",
    showlegend=False,
    height=450,
    plot_bgcolor='white',
    margin=dict(l=0, r=0, t=40, b=0),
    yaxis=dict(title="Expected Earnings ($/hr)", range=[80, 240])
)

st.plotly_chart(fig_waterfall, use_container_width=True)

# --- 5. THE MANIFESTO ---
with st.expander("🚀 Architectural Note: Dynamic SHAP Implementation", expanded=False):
    st.markdown("""
    ### *“Trust is engineered, not given.”*
    
    This interface currently utilizes a **Mock Data Sandbox** to demonstrate the UX paradigm of the Cognitive Cascade. In the production deployment, this module connects directly to the trained LightGBM/XGBoost model artifacts.
    
    **Production Pipeline:**
    1. **Model Registry:** The dashboard loads the champion model via `joblib` or MLflow.
    2. **SHAP Explainer:** The `shap.TreeExplainer` calculates exact marginal contributions for the live inference vector.
    3. **Translation:** Raw log-odds are transformed back into business units ($/hr) to ensure the cascade speaks the language of operations, not just data science.
    
    By exposing the algorithm's internal mechanics, we transition from *predictive* modeling to *prescriptive* strategy—allowing operations managers to trust and verify the logic behind every dispatch recommendation.
    """)