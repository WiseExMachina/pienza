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