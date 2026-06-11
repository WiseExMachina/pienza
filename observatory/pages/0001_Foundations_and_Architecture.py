import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Foundations & Architecture", page_icon="🏗️", layout="wide")

# Industrial Opus Theme CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700;800&display=swap');
        
        p, li, td, th { font-family: 'Crimson Pro', serif !important; font-size: 18px !important; line-height: 1.6 !important; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; }
        h1 { font-size: 38px !important; letter-spacing: -1px; } 
        h2 { font-size: 28px !important; color: #21918c; } 
        h3 { font-size: 22px !important; color: #121212; } 
        
        /* Metric Box styling */
        .metric-card {
            background: #f8f9fa; border: 1px solid #eaeaea; border-left: 4px solid #21918c;
            border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .metric-val { font-size: 2rem; font-weight: 800; color: #121212; line-height: 1; font-family: 'Inter', sans-serif; }
        .metric-label { font-size: 0.8rem; text-transform: uppercase; color: #555; font-weight: 700; font-family: 'Inter', sans-serif; }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER & EXECUTIVE SUMMARY
# ==========================================
st.title("Foundations & Data Architecture")
st.markdown("""
Unlike traditional "top-down" studies relying on aggregated, biased platform data, Project Pienza employs a **"Bottom-Up"** methodology. 
By capturing the *total operational reality* of a single Expert Agent (N=1)—including the critical rejected offers—we establish a mathematically complete Digital Twin of the Mexico City ride-hailing ecosystem.
""")

st.write("")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown('<div class="metric-card"><div class="metric-val">4,700+</div><div class="metric-label">Market Interactions</div></div>', unsafe_allow_html=True)
with c2: st.markdown('<div class="metric-card"><div class="metric-val">6 Weeks</div><div class="metric-label">Observation Window</div></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="metric-card"><div class="metric-val">Dual</div><div class="metric-label">Ingestion Engines</div></div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="metric-card"><div class="metric-val">N=1</div><div class="metric-label">Expert Agent Policy</div></div>', unsafe_allow_html=True)
st.write("")
st.divider()


# ==========================================
# INTERACTIVE TABS: ACQUISITION & ENGINEERING
# ==========================================
tab1, tab2, tab3 = st.tabs(["📡 Dual-Engine Acquisition", "🧠 Target Engineering (The Brain)", "⏱️ Stateful Physics"])

# --- TAB 1: ACQUISITION ---
with tab1:
    st.markdown("### Defeating Survivorship Bias")
    st.markdown("To map the exact decision boundary of the agent, the system must capture the **Negative Class** (rejected offers). We deployed a dual-engine architecture to synthesize physical movement and algorithmic intent.")
    
    col_text, col_chart = st.columns([1, 1.2])
    with col_text:
        st.markdown("#### Engine 1: Telemetry (GTS Webapp)")
        st.write("A custom Progressive Web App (PWA) optimized for low-cognitive-load fieldwork. It logs the exact GPS coordinates and timestamps of the five critical state transitions of a gig economy mission.")
        
        st.markdown("#### Engine 2: Total Offer OCR")
        st.write("An iOS Assistive Touch Macro captured the screen for every single offer presented. Google Gemini Pro Vision API transformed these visual artifacts into structured tabular data, ensuring zero system filters corrupted the liquidity stream.")
        
    with col_chart:
        # Visualizing the T0-T4 funnel interactively
        funnel_data = dict(
            State=["T0: Search (Idle)", "T1: Accept (Quoted Fare)", "T2: Arrive (Wait)", "T3: In-Progress", "T4: Complete (Net Fare)"],
            Value=[100, 25, 24, 23, 22] # Mock representation of funnel drop-off
        )
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data["State"],
            x=funnel_data["Value"],
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#007BFF", "#FFC107", "#FD7E14", "#17A2B8", "#28A745"]}
        ))
        fig_funnel.update_layout(title="Mission Lifecycle Telemetry (T0 - T4)", margin=dict(t=40, b=0, l=0, r=0), height=350, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_funnel, use_container_width=True)

# --- TAB 2: TARGET ENGINEERING (SUNBURST) ---
with tab2:
    st.markdown("### The Cognitive Cascade: `reason_primary`")
    st.markdown("The multiclass target variable is a hierarchical filtration system. Instead of random labels, every rejected offer is assigned a mutually exclusive failure point across a three-tiered triage: Geospatial, Economic, and Strategic.")
    
    # Sunburst chart replaces the boring Markdown table
    sunburst_data = dict(
        id=["All Offers", "Geospatial Triage", "Economic Triage", "Strategic Triage", "Accepted", 
            "Dropoff Non-Op", "Dropoff Proxy", "Low Profitability", "Long Pickup", 
            "Strategic Mismatch", "EV Gamble"],
        parent=["", "All Offers", "All Offers", "All Offers", "All Offers", 
                "Geospatial Triage", "Geospatial Triage", "Economic Triage", "Economic Triage", 
                "Strategic Triage", "Strategic Triage"],
        value=[100, 40, 35, 15, 10, 25, 15, 20, 15, 8, 7],
    )
    fig_sun = go.Figure(go.Sunburst(
        ids=sunburst_data['id'],
        labels=sunburst_data['id'],
        parents=sunburst_data['parent'],
        values=sunburst_data['value'],
        branchvalues="total",
        marker=dict(colorscale='Viridis')
    ))
    fig_sun.update_layout(margin=dict(t=10, l=0, r=0, b=10), height=450, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sun, use_container_width=True)


# --- TAB 3: STATEFUL PHYSICS ---
with tab3:
    st.markdown("### Stateful Intelligence: Session Memory")
    st.markdown("Physical parameters (fare, distance) alone fail to capture operational context. Risk tolerance is a dynamic function of session history. We engineered persistent 'memory' features across critical dimensions.")
    
    st.write("")
    c_feat1, c_feat2, c_feat3 = st.columns(3)
    
    with c_feat1:
        with st.container(border=True):
            st.markdown("#### ⏳ Sunk Costs")
            st.write("**`total_acc_deadhead_sec`**")
            st.write("Aggregates unpaid time (Search + Pickup + Wait) in the current cycle, quantifying the pressure to accept sub-optimal offers.")
            
    with c_feat2:
        with st.container(border=True):
            st.markdown("#### 🚥 Market Friction")
            st.write("**`traffic_index_base_120`**")
            st.write("A normalized congestion metric. Tracks real-time gridlock against a baseline of 120 seconds per kilometer.")

    with c_feat3:
        with st.container(border=True):
            st.markdown("#### 🎯 Convergence")
            st.write("**`eph_complete_ML`**")
            st.write("Holistic Expected Payout per Hour. Models how the agent forces long-term mean convergence toward the $200/hr North Star.")

st.divider()

# ==========================================
# OPTIONAL: KEEP GTS SIMULATOR
# ==========================================
with st.expander("🕹️ Explore the Interactive GTS Telemetry Simulator", expanded=False):
    st.markdown('*(You can paste the code for the interactive iPhone Webapp Simulator here. Tucking it inside an expander keeps the page lean but leaves the "wow" factor available for those who want to play with it.)*')