# pages/0001_Foundations_and_Architecture.py
import streamlit as st
import streamlit.components.v1 as components


# --- 1. CONFIGURACIÓN CANÓNICA ---
st.set_page_config(
    layout="wide",
    page_title="Pienza | Foundations",
    page_icon="🕸️"
)

# Inyectar estilos globales idénticos a main.py
st.markdown("""
   <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span {
        font-family: 'Inter', sans-serif !important;
    }
    
    h1 { 
        font-size: 36px !important;
        font-weight: 400 !important; 
        color: #121212; 
        letter-spacing: -1px; 
    }
    h2 { 
        color: #21918c;
        font-size: 22px !important;
        font-weight: 400 !important; 
        margin-top: 25px;
    }
    h3 {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #121212;
    }
    
    /* Bento Grid Layout */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    .bento-card {
        background: #ffffff;
        border: 1px solid #eaeaea;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    .bento-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.06);
        border-color: #21918c;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: #21918c;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #121212;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
   </style>
""", unsafe_allow_html=True)

# Construir Sidebar

# --- HEADER ---
st.title("System Architecture & Experimental Foundations")
st.markdown("<p style='color: #555; font-size: 1.1rem; margin-top: -10px;'>High-fidelity digitization of the expert agent's decision boundary.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- MULTICLASS CLASSIFICATION TABS ---
st.write("## 1. Ground Truth & Target Class Distribution")
st.write("Explore the multiclass formulation engineered to neutralize platform survivorship bias.")

tab1, tab2 = st.tabs(["📊 Target Class Weights", "🧪 Dual-Engine Telemetry Ingestion"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("### Target Imbalance Overview")
        st.write("""
        Nearly **50% of the observation space** resides within the non-operational category (`dropoff_non_operational`). 
        Isolating this structural majority-class noise was critical to prevent the machine learning models from 
        succumbing to a severe 'gravitational well' effect.
        """)
        # Métricas Bento integradas en la pestaña
        st.markdown("""
        <div class="bento-grid" style="grid-template-columns: 1fr 1fr;">
            <div class="bento-card" style="padding:15px;">
                <div class="metric-label">Reject Rate</div>
                <div class="metric-value">92.74%</div>
            </div>
            <div class="bento-card" style="padding:15px;">
                <div class="metric-label">Accept Rate</div>
                <div class="metric-value">7.26%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        # Usar st.dataframe estilizada con el tema del contenedor
        st.dataframe(
            {
                "Target Class Label": [
                    "dropoff_non_operational", "low_profitability", "long_pickup_time", 
                    "ACCEPTED (Implicit)", "expected_value_gamble", "dropoff_strategic_mismatch", 
                    "dropoff_proxy", "system_logic_failure"
                ],
                "Observation Count": [2366, 838, 366, 346, 330, 275, 239, 5],
                "Distribution Ratio": [0.4965, 0.1759, 0.0768, 0.0726, 0.0693, 0.0577, 0.0502, 0.0010]
            },
            column_config={
                "Distribution Ratio": st.column_config.ProgressColumn(
                    "Relative Proportion",
                    format="%.2%",
                    min_value=0.0,
                    max_value=0.5
                )
            },
            use_container_width=True,
            hide_index=True
        )

with tab2:
    st.write("### Ingestion Infrastructure: In-Field Digitization")
    p1, p2 = st.columns(2)
    with p1:
         st.markdown("""
         <div class="bento-card" style="height:100%;">
             <span style="font-size:1.5rem;">📱</span>
             <h4 style="color:#21918c; margin-top:8px;">Engine 1: Telemetry (GTS Webapp)</h4>
             <p style="font-size:13px; color:#444;">
                 A Progress Web Application logging five critical transitions with high precision: 
                 <strong>T0</strong> (Search) ➔ <strong>T1</strong> (Accept) ➔ <strong>T2</strong> (Arrival) ➔ 
                 <strong>T3</strong> (In-Progress) ➔ <strong>T4</strong> (Completion).
             </p>
         </div>
         """, unsafe_allow_html=True)
    with p2:
         st.markdown("""
         <div class="bento-card" style="height:100%;">
             <span style="font-size:1.5rem;">🤖</span>
             <h4 style="color:#21918c; margin-top:8px;">Engine 2: Optical State Archival (OCR)</h4>
             <p style="font-size:13px; color:#444;">
                 Single-gesture macro captures raw screenshots. Text-extraction performed by the 
                 <strong>Google Gemini Pro API</strong>, followed by same-day manual backtagging to prevent 
                 cognitive memory decay.
             </p>
         </div>
         """, unsafe_allow_html=True)

# --- 2. PROJECT TIMELINE ---
st.write("## 2. Experimental Development Roadmap")

components.html("""
    <div class="mermaid" style="display: flex; justify-content: center; background-color: transparent;">
    gantt
        title Technical Progression Timeline
        dateFormat  YYYY-MM-DD
        axisFormat  %b
        section Ground Truth
        Acquisition Sprint (N=4765)      :active, a1, 2025-08-22, 2025-10-01
        section Engineering
        Star Schema & ETL Stabilization  :crit, a2, 2025-10-02, 2025-11-20
        section Inference
        Causal Audits & Risk Modeling    :a3, 2025-11-21, 2025-12-03
        section Topology
        Unsupervised Zone Discovery     :a4, 2025-12-04, 2026-01-02
        section Imitation
        Cognitive Cascade Deployment     :a5, 2026-01-03, 2026-01-12
        section Moonshots
        cGAN Synthesis & Graph Routing   :a6, 2026-01-13, 2026-03-31
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({ startOnLoad: true, theme: 'neutral', securityLevel: 'loose' });
    </script>
""", height=350)

# --- 3. BENTO SUITE OF STATEFUL FEATURES ---
st.write("## 3. Stateful Feature Engine & Data Lineage")
st.write("To preserve temporal boundaries and prevent look-ahead bias, features are computed exclusively in historical retrospect:")

st.markdown("""
<div class="bento-grid">
    <div class="bento-card">
        <div class="metric-label">Temporal Momentum</div>
        <div class="metric-value">time_in_session_sec</div>
        <p style="font-size: 12px; color: #555; line-height: 1.4; margin-top:8px;">
            Captures real-time session duration and linear progression to calculate psychological decay factors during the shift endgame.
        </p>
    </div>
    <div class="bento-card">
        <div class="metric-label">Uncompensated Load</div>
        <div class="metric-value">total_acc_deadhead_sec</div>
        <p style="font-size: 12px; color: #555; line-height: 1.4; margin-top:8px;">
            Aggregates full session search, dispatch, and pickup delays to quantify structural sunk cost pressure.
        </p>
    </div>
    <div class="bento-card">
        <div class="metric-label">Market Volatility</div>
        <div class="metric-value">traffic_volatility_index</div>
        <p style="font-size: 12px; color: #555; line-height: 1.4; margin-top:8px;">
            Measures predictive error against historical baselines to identify systemic duration overruns.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("### Relational Lineage Chain")
st.latex(r"\text{offers} \xrightarrow{1:1} \text{trip\_events} \xrightarrow{1:0..1} \text{lifetime\_trips} \xrightarrow{1:1} \text{activity\_earnings}")