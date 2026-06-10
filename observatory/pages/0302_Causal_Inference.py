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

# --- 3. DATA INGESTION (BIGQUERY VERSION) ---
@st.cache_data
def get_stability_data():
    client = get_bq_client()
    query = """
    SELECT
        DATE(o.offer_timestamp) AS session_date,
        o.offer_id,
        p.category_name      AS category,
        v.spread_percentage  AS financial_spread
    FROM `645009831643.pienza_mini.v_mission_dossier` v
    JOIN `645009831643.pienza_mini.offers` o ON v.offer_id = o.offer_id
    JOIN `645009831643.pienza_mini.product_category` p ON o.product_category_fk = p.product_category_id
    WHERE v.realized_fare IS NOT NULL
    """
    df = client.query(query).to_dataframe()
    df['session_date'] = pd.to_datetime(df['session_date'])
    return df
    
df_dated = get_stability_data()

# 4. DATA PREPARATION
df_dated = df_dated.sort_values(['session_date', 'offer_id'], ascending=True)
df_dated['mission_rank'] = range(1, len(df_dated) + 1)
df_dated['spread_ma'] = df_dated['financial_spread'].rolling(window=5).mean()

event_date = pd.to_datetime('2025-09-24')
event_rank = df_dated[df_dated['session_date'] >= event_date]['mission_rank'].min()

global_mean = df_dated['financial_spread'].mean()


# 5. INTERACTIVE PLOTTING (Plotly Version)
fig = go.Figure()

# Individual Missions (The Dots with Hover)
fig.add_trace(go.Scatter(
    x=df_dated['mission_rank'],
    y=df_dated['financial_spread'],
    mode='markers',
    name='Individual Mission Yield',
    marker=dict(
        color=OPUS_TEAL,
        size=8,
        opacity=0.4,
        line=dict(width=0.5, color='white')
    ),
    # Tooltip configuration
    customdata=df_dated[['offer_id', 'category', 'session_date']],
    hovertemplate=(
        "<b>Offer ID:</b> %{customdata[0]}<br>" +
        "<b>Category:</b> %{customdata[1]}<br>" +
        "<b>Date:</b> %{customdata[2]|%Y-%m-%d}<br>" +
        "<b>Spread:</b> %{y:.4f}<br>" +
        "<extra></extra>"
    )
))

# Operational Trend (Moving Average)
fig.add_trace(go.Scatter(
    x=df_dated['mission_rank'],
    y=df_dated['spread_ma'],
    mode='lines',
    name='5-Mission Moving Average',
    line=dict(color='red', width=2),
    hoverinfo='skip'
))

# Global Equilibrium Baseline
fig.add_hline(
    y=global_mean, 
    line_dash="dash", 
    line_color="#666666",
    annotation_text=f"Global Average: {global_mean:.4f}",
    annotation_position="bottom right"
)

# Policy Intervention Line & Label
if pd.notna(event_rank):
    fig.add_vline(x=event_rank, line_width=2, line_color=OPUS_PURPLE)
    fig.add_annotation(
        x=event_rank, y=1.25,
        text='POLICY INTERVENTION<br>"Earnings Increase"',
        showarrow=True, arrowhead=2, arrowcolor=OPUS_PURPLE,
        ax=-60, ay=-30,
        bgcolor="white", bordercolor=OPUS_PURPLE, borderwidth=1
    )

# Layout Refinement
fig.update_layout(
    plot_bgcolor=OPUS_GREY,
    paper_bgcolor=OPUS_GREY,
    
    xaxis_title=dict(text="Operational Timeline", font=dict(size=14, color=OPUS_TEXT)),
    yaxis_title=dict(text="Financial Spread (Realized / Upfront)", font=dict(size=14, color=OPUS_TEXT)),
    
    yaxis=dict(
        range=[0.6, 1.3], 
        gridcolor='lightgrey',
        zeroline=False
    ),
    xaxis=dict(
        gridcolor='lightgrey',
        tickformat="%b-%d"
    ),
    
    height=600,
    margin=dict(l=60, r=20, t=40, b=50),
    
    legend=dict(
        yanchor="top", y=0.98, 
        xanchor="left", x=0.01,
        bgcolor="white",
        bordercolor="#cccccc",
        borderwidth=1,
        font=dict(size=11)
    )
)

# Render the interactive chart
st.plotly_chart(fig, use_container_width=True)

# 6. ENHANCED STATISTICS (Using Metric Cards)
pre_event = df_dated[df_dated['session_date'] < event_date]['financial_spread'].mean()
post_event = df_dated[df_dated['session_date'] >= event_date]['financial_spread'].mean()

st.divider()
col1, col2, col3 = st.columns(3)
lift = ((post_event/pre_event)-1)*100

col1.metric("Global Mean Spread", f"{global_mean:.4f}")
col2.metric("Post-Intervention Mean", f"{post_event:.4f}", f"{post_event-pre_event:.4f}")
col3.metric("Realized Yield Lift", f"{lift:.2f}%", f"{lift:.2f}%")