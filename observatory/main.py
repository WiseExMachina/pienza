import streamlit as st
import streamlit.components.v1 as components
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from utils.gcp_client import load_fast_assets

# --- 1. CANONICAL CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Project Pienza | Digital Twin",
    page_icon="🛰️"
)

# ==========================================
# ASYNC CACHE WARMING (Fire & Forget)
# ==========================================
def pre_warm_engines():
    """Silently loads O(1) models into server RAM in the background."""
    try:
        load_fast_assets()
    except Exception as e:
        print(f"Background warming failed: {e}")

# Only trigger the thread ONCE per session
if 'engines_warming' not in st.session_state:
    st.session_state['engines_warming'] = True
    
    warmup_thread = threading.Thread(target=pre_warm_engines)
    add_script_run_ctx(warmup_thread) # Attaches Streamlit context to the thread
    warmup_thread.start()
    
    # Optional: A subtle notification so recruiters know you did something cool
    st.toast("⚡ O(1) Neural Engines warming up in the background...", icon="🤖")

# Custom CSS for "Industrial-Grade" Paper Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

    /* Main Typography */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* LaTeX-style Titles */
    h1, h2, h3 {
        font-family: 'Libre+Baskerville', serif !important;
        color: #1E3D3D;
    }

    .block-container { padding-top: 2rem; }
    
    /* Executive KPI styling */
    .kpi-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E6B6B;
        text-align: center;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Executive Info) ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/2E6B6B/satellite-sending-signal.png", width=80)
    st.markdown("## Project Pienza")
    st.markdown("---")
    st.markdown("**Author:** Bernardo Lozano Wise")
    st.markdown("**Phase:** 6 (Generative Simulation)")
    st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
    st.markdown("---")
    st.download_button("📄 Download 91-Page Report (PDF)", data="PDF_DATA_HERE", file_name="Project_Pienza_Full_Report.pdf")
    st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")

# --- 3. HERO HEADER ---
st.title("10:10:01, A Decision Science Framework for Ride-Hailing Dynamics")
st.markdown("""
    #### *From Tactical Fieldwork to the Synthesis of a Generative Digital Twin*
    """)

# --- 4. THE GRADUATION NARRATIVE (Author's Note) ---
col_intro, col_stats = st.columns([2, 1])

with col_intro:
    st.markdown("""
    ### Graduating from the Streets
    After 24 months of field operations in Mexico City, Project Pienza was born from a single objective: 
    **Can an expert's intuition be encoded?**
    
    This research documents the transition from the steering wheel to the architect of a digital twin. 
    By capturing a converged policy at an $N=1$ expert level, we move beyond simple price prediction 
    into the domain of **Behavioral Cloning** and **Market Synthesis**. This observatory is the 
    mathematical legacy of thousands of kilometers logged across the urban manifold.
    """)

with col_stats:
    st.markdown('<div class="kpi-box">', unsafe_allow_html=True)
    st.metric("Total Offers Captured (Real Data)", "4,765")
    st.metric("Predictive Recall (Triage Layer)", "90.2%")
    st.metric("Synthetic Manifold Rows", "1,000,000")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- 5. THE HERO VISUAL (3D MANIFOLD) ---
st.subheader("The Topology of the Expert: Machine-Discovered Hubs")
# Embedding your Kepler HTML
try:
    with open("/workspaces/pienza/observatory/assets/kepler_3D.html", 'r', encoding='utf-8') as f:
        html_data = f.read()
    components.html(html_data, height=600)
    st.caption("Manifold Visualization: 44 HDBSCAN clusters defining the primary decision playground. Height represents offer density; color encodes topological gravity wells.")
except FileNotFoundError:
    st.error("Map file not found. Check path: /workspaces/pienza/observatory/assets/kepler_3D.html")

st.markdown("---")

# --- 6. THE 4 PILLARS OF PIENZA ---
st.markdown("### The Framework Architecture")
p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown("#### 1. Forensic Engineering")
    st.write("Transmuting raw OCR captures and GPS telemetry into an idempotent, relational SSoT (Single Source of Truth).")
    if st.button("Explore Pipeline", key="btn_p1"):
        st.switch_page("pages/1_Engineering.py")

with p2:
    st.markdown("#### 2. Decision Science")
    st.write("Causal analysis of the Agent's decision boundary: Sunk Costs, Optimal Stopping, and the Fraud Prevention Response.")
    if st.button("Explore Statistics", key="btn_p2"):
        st.switch_page("pages/2_Economics.py")

with p3:
    st.markdown("#### 3. Supervised Imitation")
    st.write("**Real-Data Cloning.** Encoding the expert policy via XGBoost hierarchical classification with 90%+ recall.")
    if st.button("Explore ML Model", key="btn_p3"):
        st.switch_page("pages/3_MachineLearning.py")

with p4:
    st.markdown("#### 4. Generative Moonshots")
    st.write("Scaling the study via cGANs to synthesize a 1M-row manifold, enabling the construction of the Mobility Tensor.")
    if st.button("Explore Synthesis", key="btn_p4"):
        st.switch_page("pages/4_Generative.py")

# --- 7. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "Lozano Wise, B. (2026). Project Pienza: From Field Acquisition to Generative Simulation. Independent Research Initiative."
    "</div>", 
    unsafe_allow_html=True
)