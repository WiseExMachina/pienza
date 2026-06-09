import streamlit as st
import streamlit.components.v1 as components
from utils.sidebar import build_sidebar

# --- 1. CANONICAL CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Project Pienza | Digital Twin",
    page_icon="🛰️"
)

# Custom CSS for "Industrial-Grade" Paper Look (Strictly Inter)
st.markdown("""
   <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* Main Typography - Enforce Inter globally */
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* --- 1. TAMAÑO DEL HEADER PRINCIPAL --- */
    h1 { 
        font-size: 36px !important; /* <-- CAMBIA ESTE NÚMERO A TU GUSTO */
        font-weight: 350 !important; 
        color: #121212; 
        letter-spacing: -1px; 
    }
    
    h4 { 
        color: #21918c; 
        font-weight: 400 !important; 
        margin-top: -10px; 
    }
    
    /* --- 2. TAMAÑO DE LAS PAGES EN EL SIDEBAR --- */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        font-size: 12px !important; /* <-- CAMBIA ESTE NÚMERO A TU GUSTO */
        /* font-weight: 600 !important; Opcional: descomenta esto si las quieres en negritas */
    }

    .block-container { padding-top: 2rem; }
    
    /* Executive KPI styling */
    .kpi-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #21918c; 
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (Executive Info) ---
build_sidebar()

# --- 3. HERO HEADER ---
st.title("Project Pienza: An AI Digital Twin to Navigate the Ride-Hailing Dynamics of Mexico City")
st.markdown("""
    <h4 style='color: #21918c; font-weight: 400; margin-top: -10px;'>
        From Field Acquisition to Markov Generative Simulations
    </h4>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# --- 4. THE KILLER NARRATIVE ---
col_intro, col_spacing, col_stats = st.columns([2.5, 0.2, 1.2])

with col_intro:
    st.markdown("""
    Project Pienza is an end-to-end decision science framework that transforms street-level gig-economy fieldwork into a generative digital twin. Engineered to overcome the survivorship bias inherent in ride-hailing algorithms, the project captures the total market liquidity of an expert agent via custom OCR and telemetry pipelines. This sovereign dataset powers a hierarchical imitation learning engine (XGBoost), an $O(1)$ NLP spatial transformer, and a Conditional GAN that synthesizes a 1,000,000-row market manifold. Ultimately, Pienza bridges the gap between human behavioral cloning and autonomous execution, culminating in a graph-based Markov sandbox for strategic fleet orchestration.
    """)

st.markdown("---")

# --- 5. THE HERO VISUAL (3D MANIFOLD) ---
st.subheader("The Playground: Machine-Discovered Hubs")

try:
    with open("/workspaces/pienza/observatory/assets/kepler_3D.html", 'r', encoding='utf-8') as f:
        html_data = f.read()
        
    # Mantenemos el CSS de fuerza blanca por si las moscas, 
    # pero ya no necesitamos el div contenedor externo.
    force_white_css = "<style>body { background-color: white !important; }</style>"
    components.html(force_white_css + html_data, height=600)
    
except FileNotFoundError:
    st.error("Map file not found. Check path: /workspaces/pienza/observatory/assets/kepler_3D.html")

st.caption("Manifold Visualization: 44 HDBSCAN clusters defining the primary decision playground. Height represents offer density; color encodes topological gravity wells. Clusters are highlighted against the Agent's hand-crafted polygons representing the operational zone theatre.")

st.markdown("---")

# --- 6. THE 4 PILLARS OF PIENZA ---
st.markdown("### The Framework Architecture")
p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown("#### 1. Forensic Engineering")
    st.write("Transmuting raw OCR captures and GPS telemetry into an idempotent, relational SSoT (Single Source of Truth).")
    if st.button("Explore Pipeline", key="btn_p1", use_container_width=True):
        st.switch_page("pages/0101_Acquisition_and_Ground_Truth.py") 

with p2:
    st.markdown("#### 2. Decision Science")
    st.write("Causal analysis of the Agent's decision boundary: Sunk Costs, Optimal Stopping, and the Fraud Prevention Response.")
    if st.button("Explore Statistics", key="btn_p2", use_container_width=True):
        st.switch_page("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py") 

with p3:
    st.markdown("#### 3. Supervised Imitation")
    st.write("**Real-Data Cloning.** Encoding the expert policy via XGBoost hierarchical classification with 90%+ recall.")
    if st.button("Explore ML Model", key="btn_p3", use_container_width=True):
        st.switch_page("pages/0405_XGB_Coliseum.py") 

with p4:
    st.markdown("#### 4. Generative Moonshots")
    st.write("Scaling the study via cGANs to synthesize a 1M-row manifold, enabling the construction of the Mobility Tensor.")
    if st.button("Explore Synthesis", key="btn_p4", use_container_width=True):
        st.switch_page("pages/0610_cGAN_Engine.py") 

# --- 7. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "Lozano Wise, B. (2026). Project Pienza: From Field Acquisition to Generative Simulation. Independent Research Initiative."
    "</div>", 
    unsafe_allow_html=True
)