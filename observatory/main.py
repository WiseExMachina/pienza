import streamlit as st
import streamlit.components.v1 as components


# --- 0. SIDEBAR INTEGRADA ---
def build_sidebar():
    with st.sidebar:
        st.markdown("Proyect Pienza")   
        st.markdown("---")
        
        # Resolve path dynamically for home page and subpages
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations_and_Architecture.py", label="Foundations & Architecture")
        st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox")
        st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping & The Efficient Frontier")
        st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
        st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")

        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button(
                "📄 Download 91-Page Report (PDF)", 
                data=pdf_data, 
                file_name="Project_Pienza_Full_Report.pdf",
                mime="application/pdf"
            )
        except FileNotFoundError:
            pass
            
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")



# --- 1. CANONICAL CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Project Pienza | Digital Twin",
    page_icon="🛰️"
)

# --- 2. SIDEBAR CALL ---
build_sidebar()


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
        font-weight: 400 !important; 
        color: #121212; 
        letter-spacing: -1px; 
    }
            
    h2 { 
        color: #21918c;
        font-size: 30px !important;
        font-weight: 300 !important; 
        margin-top: -10px; 
    }
            
    h3 { 
        color: #21918c;
        font-size: 26px !important;
        font-weight: 400 !important; 
        margin-top: -10px; 
    }
    
    h4 { 
        color: #21918c;
        font-weight: 100 !important; 
        margin-top: -10px; 
    }
    
    /* --- 2. TAMAÑO DE LAS PAGES EN EL SIDEBAR --- */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        font-size: 12px !important; /* <-- CAMBIA ESTE NÚMERO A TU GUSTO */
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


# --- 3. HERO HEADER ---
st.title("Project Pienza: An AI Digital Twin to Navigate the Ride-Hailing Dynamics of Mexico City")
st.markdown("""
    <h4 style='color: #21918c; font-weight: 400; margin-top: -10px;'>
        From Field Acquisition to Generative Simulation
    </h4>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# --- 4. THE KILLER NARRATIVE & ACHIEVEMENTS ---
st.markdown("<h3 style='margin-top: 0;'>The Mission</h3>", unsafe_allow_html=True)
st.markdown("""
**Project Pienza** transforms street-level gig-economy fieldwork into a generative digital twin. 

Engineered to overcome algorithmic survivorship bias, it captures the total market liquidity of a human agent -including rejected offers- to build a proprietary dataset that powers a hierarchical imitation engine, an NLP spatial transformer, and a conditional Generative Adversarial Network (cGAN).

Ultimately, Pienza bridges the gap between human behavioral cloning and autonomous execution via a graph-based Markov sandbox for fleet orchestration.
""")

st.write("") # Spacer

st.markdown("""
<style>
.bento-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    margin-top: 10px; 
}
.bento-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.bento-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    border-color: #21918c;
}
.bento-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #121212;
    line-height: 1.1;
    letter-spacing: -1px;
    margin-bottom: 5px;
}
.bento-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #21918c;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.bento-desc {
    font-size: 0.8rem;
    color: #555;
    line-height: 1.4;
}
</style>

<div class="bento-grid">
    <div class="bento-card">
        <div class="bento-title">Telemetry Ledger</div>
        <div class="bento-value">4,700+</div>
        <div class="bento-desc">Ride offers and market interactions captured via a dual-engine OCR system.</div>
    </div>
    <div class="bento-card">
        <div class="bento-title">Generative Scale</div>
        <div class="bento-value">1M Rows</div>
        <div class="bento-desc">Operational manifold synthesized using cGANs.</div>
    </div>
    <div class="bento-card">
        <div class="bento-title">Spatial Latency</div>
        <div class="bento-value">< 10ms</div>
        <div class="bento-desc">Real-time inference via the miniBabel NLP Transformer.</div>
    </div>
    <div class="bento-card">
        <div class="bento-title">Markov Decision Process</div>
        <div class="bento-value">5-Jump</div>
        <div class="bento-desc">Optimized mission sequences derived via a prescriptive Q-Matrix policy.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="height: 50px;"></div>
""", unsafe_allow_html=True)

# --- 5. THE HERO VISUAL (3D MANIFOLD) ---
st.markdown("### The Playground: Machine Discovered Hubs")

try:
    with open("/workspaces/pienza/observatory/assets/kepler_3D.html", 'r', encoding='utf-8') as f:
        html_data = f.read()
        
    force_white_css = "<style>body { background-color: white !important; }</style>"
    components.html(force_white_css + html_data, height=600)
    
except FileNotFoundError:
    st.error("Map file not found. Check path: /workspaces/pienza/observatory/assets/kepler_3D.html")

st.caption("Manifold Visualization: 44 HDBSCAN clusters defining the primary decision playground. Height represents offer density; color encodes topological gravity wells. Clusters are highlighted against the Agent's hand-crafted polygons representing the operational zone theatre.")


# --- 6. NAVIGATE THE OBSERVATORY ---
st.markdown("### The Observatory Architecture")
st.markdown("Navigate through the core modules of the Pienza digital twin.")

# Inject the Bento Aesthetic CSS targeting our specific containers with high specificity
st.markdown("""
<style>
/* 1. ESTILO BASE DE LA TARJETA (Mimic de ingestion-panel) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card) {
    background-color: #ffffff !important;
    border: 1px solid #eaeaea !important;
    border-radius: 12px !important;
    padding: 10px !important;
    transition: all 0.3s ease-in-out !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
}

/* 2. EFECTO HOVER EN LA TARJETA (Elevación + Delineado en Teal) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card):hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 10px 20px rgba(0,0,0,0.06) !important;
    border-color: #21918c !important; /* Delineado Teal */
}

/* 3. ESTILO DEL BOTÓN DE NAVEGACIÓN (st.page_link) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card) .stPageLink a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #21918c !important; /* Fondo Teal */
    color: #ffffff !important;
    padding: 10px 14px !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    transition: background-color 0.2s ease-in-out !important;
    width: 100% !important;
    border: none !important;
}

/* 4. HOVER DEL BOTÓN (Teal Oscuro) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card) .stPageLink a:hover {
    background-color: #1a7576 !important;
}

/* 5. FORZAR TEXTO BLANCO EN EL BOTÓN */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card) .stPageLink a p {
    color: #ffffff !important;
    margin: 0 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* Ocultar el marcador de destino */
.nav-card { display: none; }
</style>
""", unsafe_allow_html=True)

# 9-Module List for the 3x3 Grid
modules = [
    ("pages/0001_Foundations_and_Architecture.py", "🏗️", "Foundations & Architecture", 
     "Bottom-up strategy, dual-engine field acquisition, and stateful feature engineering cascade."),
     
    ("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", "💾", "SQL Pipeline & Sandbox", 
     "Documents the Star Schema architecture and provides a live BigQuery SQL environment for data auditing."),
     
    ("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", "🛑", "Optimal Stopping", 
     "Analyzes market volatility, opportunity flow, and calculates the Net Expected Value for optimal search boundaries."),
     
    ("pages/0302_Causal_Inference.py", "🔍", "Causal Inference", 
     "Audits payout stability, prediction errors, and mathematically formalizes the platform's fraud prevention mechanisms."),
     
    ("pages/0501_XGB_Coliseum.py", "⚔️", "XGBoost Tournament", 
     "An interactive coliseum comparing the decision-making of the human agent against hierarchical AI models."),
     
    ("pages/0601_O1_NLP1.py", "⚡", "The Quest to (O)1: NLP", 
     "A real-time diagnostic pipeline contrasting Cloud API latency against a custom local neural engine for spatial inference."),
     
    ("pages/0602_cGAN_Engine.py", "🏭", "cGAN Keras Engine", 
     "The Generative Forge: dynamically synthesizes hyper-realistic ride-hailing demand from a 1M-row neural manifold."),
     
    ("pages/0603_Network_Graph.py", "🔭", "Network Graph Analysis", 
     "Analyzes the urban geofence using network graph theory to observe topological centrality and dynamic capital flows."),
     
    ("pages/0604_Markov_Fleet_Sim_Dashboard.py", "🤖", "Markov Fleet Simulator", 
     "A tactical fleet deployment simulator using a Markov Decision Process for sequential routing and demand absorption.")
]

# Create a 3-column grid layout for visually stunning, concise cards
st.write("") # Spacer
cols = st.columns(3)

for i, (path, icon, title, desc) in enumerate(modules):
    with cols[i % 3]:
        with st.container(border=True):
            # Inject the hidden marker so the CSS knows to style this specific container
            st.markdown("<span class='nav-card'></span>", unsafe_allow_html=True)
            st.markdown(f"#### {icon} {title}")
            st.markdown(f"<p style='font-size: 0.85rem; color: #555; height: 60px;'>{desc}</p>", unsafe_allow_html=True)
            st.page_link(path, label="Explore Module", use_container_width=True)

st.markdown("---")

# --- 8. CALL TO ACTION (The LLM Ingestion Gateway) ---
st.markdown("""
<style>
.ingestion-panel {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 30px;
    margin: 40px 0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.ingestion-panel:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    border-color: #21918c;
}
.ingestion-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #21918c;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.ingestion-heading {
    font-size: 1.6rem;
    font-weight: 800;
    color: #121212;
    letter-spacing: -0.5px;
    margin-bottom: 12px;
}
.ingestion-body {
    font-size: 0.9rem;
    color: #555555;
    line-height: 1.5;
    margin-bottom: 24px;
}
.ingestion-action {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: #21918c;
    color: #ffffff !important;
    padding: 12px 28px;
    border-radius: 6px;
    text-decoration: none !important;
    font-size: 0.85rem;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
.ingestion-action:hover {
    background-color: #1a7576;
}
</style>

<div class="ingestion-panel">
    <div class="ingestion-title">LLM Knowledge Base</div>
    <div class="ingestion-heading">Interact with the AI</div>
    <div class="ingestion-body">
        100 pages of deep learning and market physics is a lot of reading. Download the PDF, feed it to your favorite LLM, and get the executive summary on demand.
    </div>
    <a href="main.pdf" class="ingestion-action" download>
        📥 Download PDF
    </a>
</div>
""", unsafe_allow_html=True)

# --- 7. FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8rem;'>"
    "Lozano Wise, B. (2026). Project Pienza. Independent Research Initiative."
    "</div>", 
    unsafe_allow_html=True
)