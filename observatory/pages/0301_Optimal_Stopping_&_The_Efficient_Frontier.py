import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from google.cloud import bigquery
from pathlib import Path
from scipy.interpolate import interp1d

# ==============================================================================
# 0. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Optimal Stopping", layout="wide")

# ==============================================================================
# 1. OPUS LAB CANON (Visual Identity)
# ==============================================================================
OPUS_PURPLE = '#440154'
OPUS_TEAL   = '#21918c'
OPUS_GREY   = '#FAFAFA'
OPUS_TEXT   = '#121212'

# ==============================================================================
# 2. DATA PIPELINE (BigQuery Connection)
# ==============================================================================
@st.cache_resource
def get_bq_client():
    # Resolves to observatory/service-account.json assuming this is in pages/
    json_path = Path(__file__).resolve().parent.parent / "service-account.json"
    return bigquery.Client.from_service_account_json(json_path)

client = get_bq_client()

# Standard Tier Mapping
def map_category(cat_name):
    """Maps platform-specific categories to simplified operational tiers."""
    cat_lower = str(cat_name).lower()
    if 'uberx' in cat_lower: return "X"
    elif 'business_comfort' in cat_lower or 'comfort' in cat_lower: return "Mid-tier"
    elif 'black' in cat_lower: return "Premium"
    else: return "X"

# ==============================================================================
# 3. HEADER & ARCHITECTURE
# ==============================================================================
st.title("Optimal Stopping: Mission Intake Architecture")
st.markdown(f"**<span style='color:{OPUS_TEAL}; font-size:1.2rem;'>Motion to Explore! ...Proceed</span>**", unsafe_allow_html=True)

st.divider()

# Placeholder for Phase 1 of the Notebook
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 1: Awaiting Logic</span>**", unsafe_allow_html=True)
st.info("Notebook ingestion pending...")




import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ==============================================================================
# PHASE 1: MARKET QUALITY VOLATILITY (MQI)
# ==============================================================================

# --- THE "0 BS" SQL REVEAL ---
query_mqi = """
SELECT
    o.offer_id,
    o.session_fk,
    DATE(o.offer_timestamp) AS session_date,
    p.category_name AS category,
    o.upfront_fare,
    o.est_trip_time_sec
FROM `645009831643.pienza_mini.offers` o
JOIN `645009831643.pienza_mini.product_category` p 
  ON o.product_category_fk = p.product_category_id
WHERE o.est_trip_time_sec > 0 
  AND o.upfront_fare IS NOT NULL
  AND o.session_fk IS NOT NULL
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (Raw Offers Ingestion)"):
    st.code(query_mqi, language="sql")

# --- 1. DATA INGESTION ---
@st.cache_data
def get_mqi_data():
    client = get_bq_client()
    df = client.query(query_mqi).to_dataframe()
    return df

df_alpha_raw = get_mqi_data()

# --- 2. DATA ENGINEERING (CELL 2 & 3 LOGIC) ---
# 2.1 Calculate Expected Payout Per Hour (EPH)
df_alpha_raw['upfront_fare'] = pd.to_numeric(df_alpha_raw['upfront_fare'], errors='coerce')
df_alpha_raw['est_trip_time_sec'] = pd.to_numeric(df_alpha_raw['est_trip_time_sec'], errors='coerce')
df_alpha_raw['eph_real'] = (df_alpha_raw['upfront_fare'] / df_alpha_raw['est_trip_time_sec']) * 3600

# 2.2 Simplify Categories to Strategic Tiers
df_alpha_raw['simplified_category'] = df_alpha_raw['category'].apply(map_category)
df_core = df_alpha_raw[df_alpha_raw['simplified_category'].isin(['X', 'Mid-tier', 'Premium'])].copy()
df_core = df_core.dropna(subset=['eph_real'])

# 2.3 Forge Anchors (Global Medians) & Normalize to Quality Index (IQ)
global_anchors = df_core.groupby('simplified_category')['eph_real'].median().to_dict()
df_core['category_anchor'] = df_core['simplified_category'].map(global_anchors)
df_core['offer_quality_index'] = df_core['eph_real'] / df_core['category_anchor']

# 2.4 Aggregate by Session (MQI)
mqi_timeline = df_core.groupby('session_fk').agg(
    Market_Quality_Index=('offer_quality_index', 'mean'),
    Total_Offers=('offer_id', 'count')
).reset_index()

# Filter out noise (Sessions with < 10 offers)
mqi_timeline = mqi_timeline[mqi_timeline['Total_Offers'] >= 10].sort_values('session_fk')
valid_sessions = mqi_timeline['session_fk'].tolist()
df_plot = df_core[df_core['session_fk'].isin(valid_sessions)].copy()

# Merge Session MQI back into the main df for plotting hover data
df_plot = pd.merge(df_plot, mqi_timeline[['session_fk', 'Market_Quality_Index']], on='session_fk', how='inner')

# --- 3. INTERACTIVE PLOTTING (Plotly boxplots with dynamic RdYlGn mapping) ---
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Market Quality Timeline: Session Volatility</span>**", unsafe_allow_html=True)
st.markdown("This timeline exposes the **structural luck** of individual operational sessions. By normalizing the raw Expected Payout per Hour (EPH) against the global median of each category, we create the **Offer Quality Index (IQ)**. A baseline of 1.0 represents the global average.")

fig_mqi = go.Figure()

# Set up color mapping for Divergent Palettes (Red = Bad, Green = Good)
vmin = mqi_timeline['Market_Quality_Index'].min()
vmax = mqi_timeline['Market_Quality_Index'].max()
norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=1.0, vmax=vmax)
cmap = cm.get_cmap('RdYlGn')

# Plotly requires us to add a Box trace for each session to color them dynamically
for session in mqi_timeline['session_fk']:
    session_data = df_plot[df_plot['session_fk'] == session]
    session_mqi = session_data['Market_Quality_Index'].iloc[0]
    
    # Map the session's MQI to a hex color
    hex_color = mcolors.to_hex(cmap(norm(session_mqi)))
    
    fig_mqi.add_trace(go.Box(
        y=session_data['offer_quality_index'],
        name=str(session),
        marker_color=hex_color,
        boxpoints='outliers', 
        line=dict(width=1.5),
        customdata=session_data[['simplified_category', 'eph_real']],
        hovertemplate=(
            "<b>Session:</b> %{x}<br>" +
            "<b>Offer Quality Index:</b> %{y:.2f}<br>" +
            "<extra></extra>"
        )
    ))

# Add the Canonical 1.0 Baseline
fig_mqi.add_hline(y=1.0, line_dash="dash", line_color="red", line_width=2,
                  annotation_text="1.0 (Global Quality Baseline)", annotation_position="top right")

# Layout Formatting
fig_mqi.update_layout(
    autosize=True,
    height=500,
    plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
    xaxis_title=dict(text="Session ID (Chronological)", font=dict(size=14, color=OPUS_TEXT)),
    yaxis_title=dict(text="Offer Quality Index (IQ)", font=dict(size=14, color=OPUS_TEXT)),
    yaxis=dict(range=[0.5, 2.5], gridcolor='lightgrey', zeroline=False),
    xaxis=dict(gridcolor='lightgrey', type='category', tickangle=90),
    showlegend=False,
    margin=dict(l=60, r=20, t=40, b=80)
)

st.plotly_chart(fig_mqi, use_container_width=True)

# --- 4. INSIGHTS SUMMARY ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label="Total Valid Sessions", value=len(valid_sessions))
with c2:
    st.metric(label="Global MQI Baseline", value="1.00")
with c3:
    max_session = mqi_timeline.loc[mqi_timeline['Market_Quality_Index'].idxmax()]
    st.metric(label=f"Peak Session Luck ({max_session['session_fk']})", value=f"{max_session['Market_Quality_Index']:.2f}x")





    # ==============================================================================
# PHASE 2: THE MONEY MAP (TOTAL ADDRESSABLE MARKET)
# ==============================================================================

# --- EXTENDED PIENZA PALETTE ---
COLORS = {
    'Rich / Fast': '#21918c',  # OPUS_TEAL
    'Rich / Slow': '#440154',  # OPUS_PURPLE
    'Poor / Fast': '#95a5a6',  # Grey
    'Poor / Slow': '#c0392b'   # Red
}

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 2: The Money Map (Opportunity Flow)</span>**", unsafe_allow_html=True)
st.markdown("Visualizing the Total Addressable Market (TAM) per session. This measures the raw volume of money that passed through the screen, contextualized by Market Quality (MQI) and Market Friction (Wait Times).")

# --- THE "0 BS" SQL REVEAL ---
query_moneymap = """
WITH base_offers AS (
    SELECT
        o.offer_id,
        o.session_fk,
        o.offer_timestamp,
        p.category_name AS category,
        o.upfront_fare,
        o.est_trip_time_sec,
        -- CAST the strings to TIMESTAMPS before doing the math
        TIMESTAMP_DIFF(
            CAST(o.offer_timestamp AS TIMESTAMP), 
            LAG(CAST(o.offer_timestamp AS TIMESTAMP)) OVER(PARTITION BY o.session_fk ORDER BY o.offer_timestamp), 
            SECOND
        ) as raw_delta
    FROM `645009831643.pienza_mini.offers` o
    JOIN `645009831643.pienza_mini.product_category` p 
      ON o.product_category_fk = p.product_category_id
    WHERE o.est_trip_time_sec > 0 
      AND o.upfront_fare IS NOT NULL
      AND o.session_fk IS NOT NULL
)
SELECT * FROM base_offers
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (Money Map Ingestion)"):
    st.code(query_moneymap, language="sql")

# --- 1. DATA INGESTION ---
@st.cache_data
def get_moneymap_data():
    client = get_bq_client()
    return client.query(query_moneymap).to_dataframe()

df_money = get_moneymap_data()

# --- 2. DATA ENGINEERING ---
# Clean wait times (fill nulls with median to avoid breaking aggregates)
median_wait = df_money['raw_delta'].median()
df_money['clean_wait'] = df_money['raw_delta'].fillna(median_wait)

# Calculate EPH and Category
df_money['upfront_fare'] = pd.to_numeric(df_money['upfront_fare'], errors='coerce')
df_money['est_trip_time_sec'] = pd.to_numeric(df_money['est_trip_time_sec'], errors='coerce')
df_money['eph_realized'] = (df_money['upfront_fare'] / df_money['est_trip_time_sec']) * 3600
df_money['simplified_category'] = df_money['category'].apply(map_category)

# Filter Core and Build Anchors
df_core_money = df_money[df_money['simplified_category'].isin(['X', 'Mid-tier', 'Premium'])].copy()
global_anchors = df_core_money.groupby('simplified_category')['eph_realized'].median().to_dict()
df_core_money['category_anchor'] = df_core_money['simplified_category'].map(global_anchors)
df_core_money['mqi'] = df_core_money['eph_realized'] / df_core_money['category_anchor']

# --- 3. AGGREGATE SESSION METRICS ---
session_stats = df_core_money.groupby('session_fk').agg(
    velocity_median=('clean_wait', 'median'),
    quality_mean=('mqi', 'mean'),
    offer_count=('offer_id', 'count'),
    total_potential=('upfront_fare', 'sum') # THE HERO METRIC
).reset_index()

# Drop severe outliers in velocity for a cleaner chart (optional, but recommended for UX)
session_stats = session_stats[session_stats['velocity_median'] < session_stats['velocity_median'].quantile(0.98)]

# Define Quadrants
GLOBAL_VELOCITY = session_stats['velocity_median'].median()
GLOBAL_QUALITY = 1.0

def get_quadrant(row):
    is_rich = row['quality_mean'] >= GLOBAL_QUALITY
    is_fast = row['velocity_median'] <= GLOBAL_VELOCITY
    if is_rich and is_fast: return 'Rich / Fast'
    if is_rich and not is_fast: return 'Rich / Slow'
    if not is_rich and is_fast: return 'Poor / Fast'
    return 'Poor / Slow'

session_stats['Quadrant'] = session_stats.apply(get_quadrant, axis=1)

# Format Labels (e.g., $12.5k)
def format_currency_label(val):
    if val >= 1000: return f"${val/1000:.1f}k"
    return f"${val:.0f}"

session_stats['label'] = session_stats['total_potential'].apply(format_currency_label)
session_stats['color'] = session_stats['Quadrant'].map(COLORS)

# --- 4. INTERACTIVE PLOTTING (Plotly) ---
fig_money = go.Figure()

# Add a trace for each quadrant to power the legend correctly
for quad in ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']:
    quad_data = session_stats[session_stats['Quadrant'] == quad]
    
    fig_money.add_trace(go.Scatter(
        x=quad_data['velocity_median'],
        y=quad_data['quality_mean'],
        mode='markers+text',
        name=quad,
        text=quad_data['label'],
        textfont=dict(color='white', size=11, family="Arial Black"),
        marker=dict(
            color=COLORS[quad],
            # BIGGER BALLS LOGIC:
            size=quad_data['total_potential'], 
            sizemode='area',
            sizeref=2.0 * max(session_stats['total_potential']) / (80.**2), # Tweaked for massive scale
            sizemin=20, # Floor size so small sessions don't vanish
            line=dict(width=1, color='white'),
            opacity=0.85
        ),
        customdata=quad_data[['session_fk', 'offer_count', 'total_potential']],
        hovertemplate=(
            "<b>Session:</b> %{customdata[0]}<br>" +
            "<b>Total Potential:</b> $%{customdata[2]:,.2f}<br>" +
            "<b>Offer Count:</b> %{customdata[1]}<br>" +
            "<b>Median Wait:</b> %{x:.0f} sec<br>" +
            "<b>Quality (MQI):</b> %{y:.2f}x<br>" +
            "<extra></extra>"
        )
    ))

# Crosshairs
fig_money.add_vline(x=GLOBAL_VELOCITY, line_width=2, line_dash="dash", line_color="#cccccc")
fig_money.add_hline(y=GLOBAL_QUALITY, line_width=2, line_dash="dash", line_color="#cccccc")

# Quadrant Annotations
y_max = session_stats['quality_mean'].max() * 1.05
y_min = session_stats['quality_mean'].min() * 0.95
x_max = session_stats['velocity_median'].max() * 1.05
x_min = max(0, session_stats['velocity_median'].min() - 10)

annotations = [
    dict(x=x_min, y=y_max, text="PARADISE<br>(High Cash Flow)", showarrow=False, xanchor='left', yanchor='top', font=dict(color=COLORS['Rich / Fast'], size=14, weight='bold')),
    dict(x=x_max, y=y_max, text="SNIPER<br>(Quality over Volume)", showarrow=False, xanchor='right', yanchor='top', font=dict(color=COLORS['Rich / Slow'], size=14, weight='bold')),
    dict(x=x_min, y=y_min, text="GRIND<br>(Low Value Churn)", showarrow=False, xanchor='left', yanchor='bottom', font=dict(color=COLORS['Poor / Fast'], size=14, weight='bold')),
    dict(x=x_max, y=y_min, text="DESERT<br>(Dead Market)", showarrow=False, xanchor='right', yanchor='bottom', font=dict(color=COLORS['Poor / Slow'], size=14, weight='bold')),
]

fig_money.update_layout(
    autosize=True, height=650,
    plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
    title=dict(text="Total Opportunity Value per Session (Gross Potential Earnings)", font=dict(size=16, color=OPUS_TEXT)),
    xaxis_title=dict(text=f"Market Friction (Median Wait: {GLOBAL_VELOCITY:.0f}s)", font=dict(size=14, color=OPUS_TEXT)),
    yaxis_title=dict(text="Market Quality (Mean MQI)", font=dict(size=14, color=OPUS_TEXT)),
    xaxis=dict(gridcolor='lightgrey'),
    yaxis=dict(gridcolor='lightgrey', zeroline=False),
    annotations=annotations,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=1.01),
    margin=dict(l=60, r=120, t=60, b=60)
)

st.plotly_chart(fig_money, use_container_width=True)

# --- 5. FINANCIAL FLOW CENSUS ---
st.markdown("#### 💰 Financial Flow Census")
total_market_value = session_stats['total_potential'].sum()

m1, m2 = st.columns([1, 2])
with m1:
    st.metric(label="Total Market Value Seen", value=f"${total_market_value:,.0f} MXN")

with m2:
    st.markdown("**Top 3 Highest Value Sessions:**")
    top_3 = session_stats.sort_values('total_potential', ascending=False).head(3)
    # Format for elegant display
    display_df = top_3[['session_fk', 'Quadrant', 'total_potential', 'offer_count']].copy()
    display_df['total_potential'] = display_df['total_potential'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)




# ==============================================================================
# PHASE 3: THE VEN PLAYBOOK (EXPECTED VALUE ORACLE)
# ==============================================================================

import plotly.figure_factory as ff
import pandas as pd
import plotly.graph_objects as go

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 3: The VEN Playbook (Strategic Oracle)</span>**", unsafe_allow_html=True)
st.markdown("""
This matrix calculates the **Net Expected Value (VEN - Valor Esperado Neto)**. It answers the ultimate operational question: *If I reject an acceptable baseline offer right now, what is the mathematical probability and expected financial gain (or loss) of waiting for a premium target offer within a specific time window?*
""")

# --- THE "0 BS" SQL REVEAL ---
query_ven = """
SELECT
    o.offer_id,
    o.session_fk,
    CAST(o.offer_timestamp AS TIMESTAMP) AS offer_timestamp,
    o.upfront_fare,
    o.est_trip_time_sec,
    COALESCE(o.time_to_pickup_sec, 300) AS time_to_pickup_sec, 
    r.reason_primary_description AS reason_primary -- Update this column name if your BQ schema differs!
FROM `645009831643.pienza_mini.offers` o
LEFT JOIN `645009831643.pienza_mini.reason_primary` r
  ON o.reason_primary_fk = r.reason_primary_id
WHERE o.est_trip_time_sec > 0 
  AND o.upfront_fare IS NOT NULL
  AND o.session_fk IS NOT NULL
"""

with st.expander("🔍 Click here to view the live BigQuery SQL (VEN Data Ingestion)"):
    st.code(query_ven, language="sql")

# --- 1. DATA INGESTION & ENRICHMENT ---
@st.cache_data
def get_ven_data():
    client = get_bq_client()
    return client.query(query_ven).to_dataframe()

df_playbook_raw = get_ven_data()

# Ensure we have the Quadrants from Phase 2
if 'session_stats' in locals() and not session_stats.empty:
    
    # Merge Quadrants
    df_playbook = pd.merge(
        df_playbook_raw, 
        session_stats[['session_fk', 'Quadrant']], 
        on='session_fk', 
        how='inner'
    )
    
    # Filter Dead Zones
    df_playbook['reason_primary'] = df_playbook['reason_primary'].astype(str).str.lower()
    df_playbook = df_playbook[~df_playbook['reason_primary'].str.contains('dropoff_non_operational')].copy()
    
    df_playbook['eph_real'] = (df_playbook['upfront_fare'] / df_playbook['est_trip_time_sec']) * 3600

    # --- 2. INTERACTIVE STRATEGY INPUTS (FIXED: SINGLE SLIDER) ---
    st.markdown("#### Strategic Parameters")
    
    TARGET_EPH = st.slider(
        "Target Premium Yield ($/hr)", 
        min_value=150, 
        max_value=400, 
        value=200, 
        step=10,
        help="The premium rate you are holding out for. The Baseline is mathematically locked at $30 below this target."
    )
    
    # Strict Mathematical Link: Baseline is always Target - 30
    BASELINE_EPH = TARGET_EPH - 30
    
    # Visual feedback for the user
    st.info(f"**Active Baseline Yield:** ${BASELINE_EPH}/hr *(The acceptable rate you have right in front of you, locked at $30 below Target)*")

    # --- 3. ARCHETYPE CONSTRUCTION ---
    props_target = df_playbook[df_playbook['eph_real'].between(TARGET_EPH - 15, TARGET_EPH + 15)][['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()
    props_base = df_playbook[df_playbook['eph_real'].between(BASELINE_EPH - 15, BASELINE_EPH + 15)][['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()

    if props_target.isnull().any() or props_base.isnull().any():
        st.warning(f"⚠️ Insufficient historical data near ${TARGET_EPH}/hr or ${BASELINE_EPH}/hr to calculate the oracle. Adjust your slider to find a viable range.")
    else:
        # --- 4. VECTORIZED ORACLE ---
        df_sim = df_playbook.sort_values(['session_fk', 'offer_timestamp']).copy()
        df_sim['is_success'] = (df_sim['eph_real'] >= TARGET_EPH).astype(int)
        df_sim = df_sim.set_index('offer_timestamp')
        
        time_windows = {'1m': '60s', '3m': '180s', '5m': '300s', '10m': '600s', '15m': '900s'}
        results = []

        eph_base_immediate = (props_base['upfront_fare'] / (props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec'])) * 3600

        for label, delta_str in time_windows.items():
            delta_sec = int(delta_str[:-1])
            
            found_success = df_sim.groupby('session_fk')['is_success'].apply(
                lambda x: x.iloc[::-1].rolling(window=delta_str).max().iloc[::-1]
            ).reset_index(level=0, drop=True)
            
            df_sim['found_success'] = found_success
            probs = df_sim.groupby('Quadrant')['found_success'].mean()

            for quad, p in probs.items():
                cycle_success = delta_sec + props_target['time_to_pickup_sec'] + props_target['est_trip_time_sec']
                eph_success_scenario = (props_target['upfront_fare'] / cycle_success) * 3600

                cycle_failure = delta_sec + props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec']
                eph_failure_scenario = (props_base['upfront_fare'] / cycle_failure) * 3600

                ev_wait = (p * eph_success_scenario) + ((1 - p) * eph_failure_scenario)
                ven = ev_wait - eph_base_immediate

                results.append({'Quadrant': quad, 'Window': label, 'VEN': ven, 'Prob': p})

        # --- 5. MATRIX FORMATTING ---
        df_res = pd.DataFrame(results)
        df_res['Label'] = df_res.apply(lambda x: f"<b>${x['VEN']:+.0f}</b><br>({x['Prob']:.0%})", axis=1)

        ven_matrix = df_res.pivot(index='Quadrant', columns='Window', values='VEN')
        label_matrix = df_res.pivot(index='Quadrant', columns='Window', values='Label')

        q_order = ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']
        ven_matrix = ven_matrix.reindex([q for q in q_order if q in ven_matrix.index])
        label_matrix = label_matrix.reindex([q for q in q_order if q in label_matrix.index])
        
        cols_order = ['1m', '3m', '5m', '10m', '15m']
        ven_matrix = ven_matrix[cols_order]
        label_matrix = label_matrix[cols_order]

        # --- 6. PLOTLY HEATMAP ---
        fig_heat = go.Figure(data=go.Heatmap(
            z=ven_matrix.values,
            x=ven_matrix.columns,
            y=ven_matrix.index,
            text=label_matrix.values,
            texttemplate="%{text}",
            colorscale="RdYlGn",
            zmid=0,  
            showscale=False, 
            hovertemplate="<b>%{y}</b><br>Wait: %{x}<br>Net Expected Value: $%{z:.2f}<extra></extra>"
        ))

        fig_heat.update_layout(
            autosize=True, height=500,
            plot_bgcolor=OPUS_GREY, paper_bgcolor=OPUS_GREY,
            title=dict(text=f"Playbook: VEN & Probability (Target: ${TARGET_EPH}/hr | Baseline: ${BASELINE_EPH}/hr)", font=dict(size=14, color=OPUS_PURPLE)),
            xaxis_title=dict(text="Search Investment Time", font=dict(size=14, color=OPUS_TEXT)),
            yaxis_title=dict(text="Market Regime", font=dict(size=14, color=OPUS_TEXT)),
            yaxis=dict(autorange="reversed"), 
            margin=dict(l=60, r=20, t=60, b=40)
        )

        st.plotly_chart(fig_heat, use_container_width=True)

else:
    st.error("🔴 Dependency missing: Ensure Phase 2 (Money Map) runs successfully first so Quadrants are calculated.")











# ==============================================================================
# PHASE 4: THE EFFICIENT FRONTIER (TEAL/PURPLE | LIMIT 9m)
# ==============================================================================

import seaborn as sns
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

st.divider()
st.markdown(f"### **<span style='color:{OPUS_PURPLE};'>Phase 4: The Efficient Frontier</span>**", unsafe_allow_html=True)
st.markdown("""
This model simulates the breaking point of the market. For any given Target Ambition, it calculates the **Maximum Rational Search Time**—the exact minute where the Net Expected Value drops below zero.
""")

# --- 1. SAFEGUARD & DATA PIPELINE ---
if 'df_playbook' in locals() and not df_playbook.empty:
    
    # 2. SETUP PARAMETERS
    target_range = range(160, 240, 10) 
    windows_min = [1, 3, 5, 10, 15]
    windows_sec = [60, 180, 300, 600, 900]
    windows_map = dict(zip(windows_min, windows_sec))
    frontier_data = []

    # 3. THE FRONTIER SIMULATOR
    with st.spinner("Simulating the Efficient Frontier..."):
        for target_eph in target_range:
            baseline_eph = target_eph - 30

            # Archetypes
            props_base = df_playbook[df_playbook['eph_real'].between(baseline_eph - 15, baseline_eph + 15)][['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()
            props_target = df_playbook[df_playbook['eph_real'].between(target_eph - 15, target_eph + 15)][['upfront_fare', 'est_trip_time_sec', 'time_to_pickup_sec']].median()

            if props_base.isnull().any() or props_target.isnull().any():
                continue

            eph_base_immediate = (props_base['upfront_fare'] / (props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec'])) * 3600

            # Pre-calculate Session Success States
            df_sim = df_playbook.sort_values(['session_fk', 'offer_timestamp']).copy()
            df_sim['is_success'] = (df_sim['eph_real'] >= target_eph).astype(int)
            
            # --- THE BULLETPROOF INDEX FIX ---
            df_sim['offer_timestamp'] = pd.to_datetime(df_sim['offer_timestamp'])
            df_sim = df_sim.set_index('offer_timestamp')
            # ----------------------------------
            
            quadrant_vens = {q: [] for q in ['Rich / Fast', 'Rich / Slow', 'Poor / Fast', 'Poor / Slow']}

            for w_min, w_sec in windows_map.items():
                window_str = f"{w_sec}s"
                
                # Session-isolated rolling success
                found_success = df_sim.groupby('session_fk')['is_success'].apply(
                    lambda x: x.iloc[::-1].rolling(window=window_str).max().iloc[::-1]
                ).reset_index(level=0, drop=True)
                
                df_sim['found_success'] = found_success
                probs = df_sim.groupby('Quadrant')['found_success'].mean()

                for quad in quadrant_vens.keys():
                    if quad in probs:
                        prob = probs[quad]
                        cycle_success = w_sec + props_target['time_to_pickup_sec'] + props_target['est_trip_time_sec']
                        eph_success = (props_target['upfront_fare'] / cycle_success) * 3600
                        
                        cycle_failure = w_sec + props_base['time_to_pickup_sec'] + props_base['est_trip_time_sec']
                        eph_failure = (props_base['upfront_fare'] / cycle_failure) * 3600

                        ev_wait = (prob * eph_success) + ((1 - prob) * eph_failure)
                        ven = ev_wait - eph_base_immediate
                        quadrant_vens[quad].append(ven)
                    else:
                        quadrant_vens[quad].append(np.nan)

            # 4. INTERPOLATION (Finding the Zero-Cross)
            for quad, vens in quadrant_vens.items():
                valid_indices = [i for i, v in enumerate(vens) if not pd.isna(v)]
                if len(valid_indices) < 2: continue

                x_vals = [windows_min[i] for i in valid_indices]
                y_vals = [vens[i] for i in valid_indices]

                if y_vals[0] < 0:
                    break_even_time = 0
                elif all(y > 0 for y in y_vals):
                    break_even_time = 15.2
                else:
                    f = interp1d(y_vals, x_vals, kind='linear', fill_value="extrapolate")
                    break_even_time = float(f(0))
                    break_even_time = max(0, min(break_even_time, 15.5))

                frontier_data.append({
                    'Target EPH': target_eph,
                    'Quadrant': quad,
                    'Max Wait Time (Minutes)': break_even_time
                })

    # --- 5. THE VISUALIZATION (ORIGINAL SEABORN CANON) ---
    df_frontier = pd.DataFrame(frontier_data)
    
    if not df_frontier.empty:
        # Create a matplotlib figure and bind it to Streamlit
        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OPUS_GREY)
        ax.set_facecolor(OPUS_GREY)

        # Custom Palette: TEAL (Good) -> PURPLE (Bad)
        teal_purple_palette = {
            'Rich / Fast': '#00897B',  
            'Rich / Slow': '#4DB6AC',  
            'Poor / Fast': '#BA68C8',  
            'Poor / Slow': '#6A1B9A'   
        }

        sns.lineplot(
            data=df_frontier,
            x='Target EPH',
            y='Max Wait Time (Minutes)',
            hue='Quadrant',
            palette=teal_purple_palette,
            style='Quadrant',
            markers=True,
            dashes=False,
            linewidth=3,
            markersize=9,
            ax=ax
        )

        # Aesthetics & Limits
        ax.axhline(0, color='black', linewidth=1.5, linestyle='-')
        ax.set_ylim(0, 9) 

        # Labels (Rich/Fast Only)
        rich_fast_points = df_frontier[df_frontier['Quadrant'] == 'Rich / Fast']

        for idx, row in rich_fast_points.iterrows():
            ax.text(
                x=row['Target EPH'],
                y=row['Max Wait Time (Minutes)'] + 0.2,
                s=f"{row['Max Wait Time (Minutes)']:.1f}m",
                color=teal_purple_palette['Rich / Fast'],
                fontsize=10,
                fontweight='bold',
                ha='center'
            )

        # Titles & Legends
        ax.set_title('The Efficient Frontier: Rational Search Time by Ambition', fontsize=18, fontweight='bold', color=OPUS_PURPLE, pad=25)
        
        fig.text(0.5, 0.02, "Baseline Assumption: For any Target $X, the alternative is holding a Base Offer of ($X - 30)", 
                 ha="center", fontsize=11, style='italic', color='#555555', 
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=5))

        ax.set_xlabel('Target Ambition ($/hr)', fontsize=12, fontweight='bold', color=OPUS_TEXT)
        ax.set_ylabel('Max Rational Search Time (Minutes)', fontsize=12, fontweight='bold', color=OPUS_TEXT)
        ax.set_xticks(list(target_range))
        ax.grid(True, alpha=0.15)
        ax.legend(title='Market Context', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)

        plt.subplots_adjust(bottom=0.15)

        # Render the matplotlib figure in Streamlit
        st.pyplot(fig)
        
    else:
        st.warning("⚠️ Insufficient data to plot the Efficient Frontier. Try adjusting your baseline targets.")

else:
    st.error("🔴 Dependency missing: Ensure Phase 3 has generated 'df_playbook' successfully.")