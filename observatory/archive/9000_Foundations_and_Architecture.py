import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="System Foundations", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for an "Industrial & Sleek" look
st.markdown("""
    <style>
    .sleek-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        color: white;
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("System Foundations")
st.markdown("### Architecture, Scope, and Temporal Mechanics")
st.divider()

# ==========================================
# 1. INTRO: MULTICLASS FRAMEWORK
# ==========================================
st.markdown("#### 1. The Multiclass Framework")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    This environment is not a static dashboard; it is a live analytical manifold. 
    The system is designed to evaluate **Multiclass Strategic Intent**, moving beyond standard deterministic modeling. By leveraging high-dimensional synthetic market physics, we isolate noise from genuine behavioral nuance.
    
    * **Objective:** Quantify non-linear psychological shifts.
    * **Methodology:** Component-based state retention.
    * **Output:** Interactive telemetry and predictive bounds.
    """)
with col2:
    # A sleek visual metric to ground the intro
    st.metric(label="System Complexity", value="High-Dimensional", delta="Active Pipeline")
    st.metric(label="State Variables", value="Isolated & Persistent", delta="Zero-Leakage", delta_color="normal")

st.divider()

# ==========================================
# 2. DUAL ENGINE PIPELINE
# ==========================================
st.markdown("#### 2. Dual Engine Pipeline")
st.markdown("Processing is split into two asynchronous, deeply integrated layers.")

engine1, engine2 = st.columns(2)

with engine1:
    st.markdown("""
    <div class="sleek-card" style="border-left-color: #2196F3;">
        <h3 style="margin-top:0;">⚙️ Engine A: The Generative Manifold</h3>
        <p class="metric-label">Macro-State Processing</p>
        <p>Generates 1,000,000+ row synthetic environments. It handles baseline physics, temporal rhythms, and standard variance bounds. It acts as the immutable bedrock of the simulation.</p>
    </div>
    """, unsafe_allow_html=True)

with engine2:
    st.markdown("""
    <div class="sleek-card" style="border-left-color: #FF9800;">
        <h3 style="margin-top:0;">🧠 Engine B: The AV Sandbox</h3>
        <p class="metric-label">Micro-State Volatility</p>
        <p>Injects localized volatility, Sunk Cost mechanics, and Surge variables. This engine is highly interactive, reacting directly to state-driven parameter adjustments on the fly.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. MERMAID TIMELINE (HTML INJECTION)
# ==========================================
st.markdown("#### 3. Development & Execution Timeline")

# Injecting Mermaid.js directly so you don't need a third-party Streamlit package
mermaid_html = """
<!DOCTYPE html>
<html>
<head>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ 
          startOnLoad: true, 
          theme: 'base',
          themeVariables: {
              primaryColor: '#2b2b2b',
              primaryTextColor: '#fff',
              primaryBorderColor: '#4CAF50',
              lineColor: '#888',
              secondaryColor: '#1e1e1e',
              tertiaryColor: '#1e1e1e'
          }
      });
    </script>
</head>
<body style="background-color: transparent; margin: 0; padding: 0;">
    <div class="mermaid">
    gantt
        title Architecture Rollout
        dateFormat  YYYY-MM-DD
        axisFormat  %m/%d
        
        section Foundations
        Multiclass Logic defined   :done,    des1, 2026-05-01, 2026-05-15
        UI Prototyping             :done,    des2, 2026-05-16, 2026-05-25
        
        section Dual Engine
        Generative Manifold Core   :active,  eng1, 2026-05-26, 14d
        AV Sandbox Volatility      :         eng2, after eng1, 10d
        
        section Deployment
        Stateful Integration       :         dep1, after eng2, 7d
        Final Polish               :         dep2, after dep1, 5d
    </div>
</body>
</html>
"""

components.html(mermaid_html, height=220)

st.divider()

# ==========================================
# 4. SUMMARY OF STATEFUL FEATURES
# ==========================================
st.markdown("#### 4. Stateful Mechanics Overview")
st.markdown("To prevent data leakage and ensure seamless UX, this environment relies heavily on isolated `st.session_state` architectures.")

f1, f2, f3 = st.columns(3)

with f1:
    with st.expander("🔄 Component Isolation", expanded=True):
        st.write("Widgets operate autonomously. Index keys (e.g., `carousel_idx_1`) ensure interactive elements never cross-contaminate logic.")

with f2:
    with st.expander("💾 Persistent Context", expanded=True):
        st.write("User inputs and threshold definitions are preserved across navigation, eliminating the need for redundant parameter entry.")

with f3:
    with st.expander("⚡ Conditional Rendering", expanded=True):
        st.write("UI elements natively adapt to the presence of data. Visualizations only compute when the requisite state variables are fully populated.")







# --- TARGET DISTRIBUTION & DATA CENSUS DASHBOARD ---
st.markdown("## Operational Baseline: Data Census")
st.markdown("""
A diagnostic audit of the $N = 4,765$ offers to isolate structural imbalances, product-mix 
distributions, and downstream mission outcomes within the geofence.
""")

st.markdown("""
<style>
/* 1. DISEÑO DE LA GRILLA DEL CENSO */
.census-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
    gap: 20px;
    margin-top: 15px;
}

/* 2. CONTENEDOR ESTILO BENTO */
.census-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    transition: all 0.3s ease;
}
.census-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    border-color: #21918c;
}

/* 3. TIPOGRAFÍA INTERNA */
.census-header {
    font-size: 1rem;
    font-weight: 700;
    color: #121212;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
    border-bottom: 2px solid #f1f1f1;
    padding-bottom: 8px;
}

/* 4. TABLAS INDUSTRIALES */
.census-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    text-align: left;
}
.census-table th {
    color: #888888;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 8px 4px;
    border-bottom: 1px solid #eaeaea;
}
.census-table td {
    padding: 8px 4px;
    border-bottom: 1px solid #fafafa;
    color: #222222;
}
.census-table tr:last-child td {
    border-bottom: none;
}

/* 5. MICRO-BARRAS DE PROGRESO (SPARKLINES) */
.spark-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
}
.spark-bg {
    background-color: #f1f1f1;
    border-radius: 3px;
    width: 60px;
    height: 5px;
    overflow: hidden;
    display: inline-block;
}
.spark-fill {
    background-color: #21918c;
    height: 100%;
    border-radius: 3px;
}
.bold-row {
    font-weight: 700;
    color: #121212 !important;
}
</style>

<div class="census-grid">

    <!-- Card 1: Decision Action (Liquidity) -->
    <div class="census-card">
        <div class="census-header">⚖️ Decision Action Census</div>
        <table class="census-table">
            <thead>
                <tr>
                    <th>Action</th>
                    <th>Count</th>
                    <th>Rate (%)</th>
                    <th>Proportion</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Reject (Negative Class)</td>
                    <td>4,419</td>
                    <td>92.74%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 92.74%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td class="bold-row">Accepted</td>
                    <td class="bold-row">346</td>
                    <td class="bold-row">7.26%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 7.26%;"></div></div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Card 2: Product Tier Distribution -->
    <div class="census-card">
        <div class="census-header">🚗 Product Tier Mix</div>
        <table class="census-table">
            <thead>
                <tr>
                    <th>Tier</th>
                    <th>Rate (%)</th>
                    <th>Proportion</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>UberX</td>
                    <td>75.93%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 75.93%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Comfort</td>
                    <td>17.17%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 17.17%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Business Comfort</td>
                    <td>3.69%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 3.69%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Envíos Uber</td>
                    <td>1.49%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 1.49%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Other (Black, Planet, Pet)</td>
                    <td>1.72%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 1.72%;"></div></div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Card 3: Target Labels (Objection Drivers) -->
    <div class="census-card" style="grid-column: span 1;">
        <div class="census-header">🎯 Target Labels & Objection Drivers</div>
        <table class="census-table">
            <thead>
                <tr>
                    <th>Target Class Label</th>
                    <th>Count</th>
                    <th>Rate (%)</th>
                    <th>Proportion</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>dropoff_non_operational</td>
                    <td>2,366</td>
                    <td>49.65%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 49.65%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>low_profitability</td>
                    <td>838</td>
                    <td>17.59%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 17.59%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>long_pickup_time</td>
                    <td>366</td>
                    <td>7.68%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 7.68%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr style="background-color: #fafafa;">
                    <td class="bold-row">ACCEPTED (Implicit)</td>
                    <td class="bold-row">346</td>
                    <td class="bold-row">7.26%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 7.26%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>expected_value_gamble</td>
                    <td>330</td>
                    <td>6.93%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 6.93%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>dropoff_strategic_mismatch</td>
                    <td>275</td>
                    <td>5.77%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 5.77%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>dropoff_proxy</td>
                    <td>239</td>
                    <td>5.02%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 5.02%;"></div></div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Card 4: Mission Outcomes (Fulfillment Funnel) -->
    <div class="census-card">
        <div class="census-header">🏁 Mission Outcomes (Accepted Cohort)</div>
        <table class="census-table">
            <thead>
                <tr>
                    <th>Outcome</th>
                    <th>Count</th>
                    <th>Rate (%)</th>
                    <th>Proportion</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background-color: #fafafa;">
                    <td class="bold-row">Completed</td>
                    <td class="bold-row">250</td>
                    <td class="bold-row">72.0%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 72.0%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>System Failure</td>
                    <td>43</td>
                    <td>12.4%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 12.4%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Rider Canceled</td>
                    <td>24</td>
                    <td>8.1%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 8.1%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>Driver Canceled</td>
                    <td>26</td>
                    <td>7.5%</td>
                    <td>
                        <div class="spark-wrapper">
                            <div class="spark-bg"><div class="spark-fill" style="width: 7.5%;"></div></div>
                        </div>
                    </td>
                </tr>
                <tr style="border-top: 2px solid #eaeaea; font-weight: bold;">
                    <td>Total Accepted Cohort</td>
                    <td>347</td>
                    <td>100.0%</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
    </div>

</div>
""", unsafe_allow_html=True)