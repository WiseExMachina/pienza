import streamlit as st
import streamlit.components.v1 as components
from components.styles import GLOBAL_CSS
from config import FAVICON
from utils.gcp_client import fetch_bytes_from_gcs


# --- 0. SIDEBAR INTEGRADA ---
def build_sidebar():
    with st.sidebar:
        st.markdown("Project Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer")
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big")
        st.markdown("---")
        st.markdown("**Archive**")
        st.page_link("pages/9001_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/9002_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/9003_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        
        try:
            if st.button("📄 Download 91-Page Report (PDF)", key="pdf_prep_btn", use_container_width=True):
                pdf_data = fetch_bytes_from_gcs("pienza-streamlit", "Pienza_Papers.pdf")
                st.download_button("⬇️ Save PDF", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf", key="pdf_dl_btn")
        except Exception:
            pass
            
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")
        if st.button("🧹 Flush Cache", key="flush_cache_btn", use_container_width=True, help="Clears st.cache_data/st.cache_resource and forces all cached data/assets to reload, without restarting the process."):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()



# --- 1. CANONICAL CONFIGURATION ---
st.set_page_config(
    layout="wide", 
    page_title="Project Pienza | Digital Twin",
    page_icon=FAVICON
)

# --- 2. SIDEBAR CALL ---
build_sidebar()


st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Page-specific overrides (kept empty on purpose — matches the vertical
# rhythm of 0001/0002's own style block so the title sits at the same
# height across pages; this extra st.markdown() call is what supplies
# Streamlit's default inter-widget gap before the H1)
st.markdown("<style></style>", unsafe_allow_html=True)

# --- 3. HERO HEADER ---
st.markdown("# Project Pienza")
st.markdown("""
    <h4 style='color: #21918c; font-weight: 300 !important; margin-top: -10px;'>
        An AI Digital Twin, From Field Acquisition to Generative Simulation
    </h4>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# --- 4. THE KILLER NARRATIVE & ACHIEVEMENTS ---
st.markdown("<h3 style='margin-top: 0;'>The Mission</h3>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;">
<b>Project Pienza</b> transforms street-level gig-economy fieldwork into a generative digital twin.
<br><br>
Engineered to overcome algorithmic survivorship bias, it captures the total market liquidity of a human agent -including rejected offers- to build a proprietary dataset that powers a hierarchical imitation engine, an NLP spatial transformer, and a conditional Generative Adversarial Network (cGAN).
<br><br>
Ultimately, Pienza bridges the gap between human behavioral cloning and autonomous execution via a graph-based Markov sandbox for fleet orchestration.
</div>
""", unsafe_allow_html=True)

st.write("") # Spacer

st.markdown("""

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
    html_data = fetch_bytes_from_gcs("pienza-streamlit", "kepler_3D.html").decode("utf-8")

    force_white_css = "<style>body { background-color: white !important; }</style>"
    components.html(force_white_css + html_data, height=600)

except Exception as e:
    st.error(f"Failed to load Kepler map from GCS: {e}")

st.markdown(
    "<div style='margin-top:-15px;margin-bottom:32px;font-size:0.65rem;color:#64748b;font-style:italic;'>"
    "Manifold Visualization: 44 HDBSCAN clusters defining the primary decision playground. "
    "Height represents offer density; color encodes topological gravity wells. Clusters are "
    "highlighted against the Agent's hand-crafted polygons representing the operational zone theatre."
    "</div>",
    unsafe_allow_html=True,
)

# --- 6. NAVIGATE THE OBSERVATORY ---
st.markdown("### The Observatory Architecture")
st.markdown(
    "<div style=\"font-family:'Inter',sans-serif;font-size:13px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:4px;\">"
    "Navigate through the core modules of the Pienza digital twin.</div>",
    unsafe_allow_html=True,
)

# Inject the Bento Aesthetic CSS targeting our specific containers with high specificity
st.markdown("""
<style>
/* All nav-card rules target [class*="st-key-nav-card-"] - the stable class Streamlit
   attaches to a container via st.container(key=...). Deliberately NOT using :has() -
   div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card) was confirmed unreliable
   in this Streamlit version (height/background/hover rules silently didn't apply; see
   project_tech_debt.md). Plain descendant selectors (no :has) worked fine throughout,
   so this keyed-class approach avoids the broken mechanism entirely. */

/* 1. ESTILO BASE DE LA TARJETA (Mimic de ingestion-panel) */
div[class*="st-key-nav-card-"] {
    background-color: #ffffff !important;
    border: 1px solid #eaeaea !important;
    border-radius: 16px !important;
    padding: 20px !important;
    transition: transform 0.25s ease-out, box-shadow 0.25s ease-out, border-color 0.25s ease-out !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    height: 300px !important;
    overflow: hidden !important;
}

/* 1b. Stack card contents vertically and pin the button to the bottom */
div[class*="st-key-nav-card-"] > div[data-testid="stVerticalBlock"] {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}

/* 2. EFECTO HOVER EN LA TARJETA (Elevación + Escala + Delineado en Teal) */
div[class*="st-key-nav-card-"]:hover {
    transform: translateY(-6px) scale(1.015) !important;
    box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
    border-color: #21918c !important; /* Delineado Teal */
}

/* 3. ESTILO DEL BOTÓN DE NAVEGACIÓN (st.page_link) - target both the legacy class
   and the data-testid, since Streamlit versions differ in which one is present */
div[class*="st-key-nav-card-"] .stPageLink a,
div[class*="st-key-nav-card-"] [data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    background-color: transparent !important;
    color: #64748b !important;
    padding: 6px 10px !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out !important;
    width: 100% !important;
    border: none !important;
}

/* 4. HOVER DEL BOTÓN (Gris un poco más oscuro) */
div[class*="st-key-nav-card-"] .stPageLink a:hover,
div[class*="st-key-nav-card-"] [data-testid="stPageLink"] a:hover {
    background-color: #f0f2f5 !important;
    color: #21918c !important;
}

/* 5. TEXTO CENTRADO DEL BOTÓN */
div[class*="st-key-nav-card-"] .stPageLink a p,
div[class*="st-key-nav-card-"] [data-testid="stPageLink"] a p {
    color: inherit !important;
    margin: 0 !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    text-align: center !important;
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# Teal, single-color (feather-style) icon set - replaces emoji so nav-card icons
# match the canonical teal accent instead of the OS's full-color emoji glyphs.
NAV_ICONS = {
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline>',
    "refresh-cw": '<polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"></path>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>',
    "search": '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
    "alert-octagon": '<polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>',
    "git-branch": '<line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 01-9 9"></path>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>',
    "send": '<line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>',
}

def _nav_icon(name, size=20):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="#21918c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:-4px;margin-right:8px;">{NAV_ICONS[name]}</svg>')

# 9-Module List for the 3x3 Grid
modules = [
    ("pages/0001_Foundations.py", "layers", "Foundations",
     "Bottom-up strategy, pivot to classification, and the target variable definition."),
    ("pages/0002_Acquisition_Pipelines.py", "refresh-cw", "Acquisition Pipelines",
     "Dual-engine data collection: GTS Telemetry Simulator and Gemini OCR Pipeline with live BigQuery output."),

    ("pages/0003_Feature_Store.py", "database", "Feature Store",
     "Documents the Bronze/Silver/Gold medallion pipeline that enriches raw OCR output into the model's feature vector."),

    ("pages/0004_Data_Census_(The_Basics).py", "search", "Data Census (The Basics)",
     "Documents the Star Schema architecture and provides a live BigQuery SQL environment for data auditing."),

    ("pages/0005_The_Cost_of_Patience.py", "alert-octagon", "The Cost of Patience",
     "Analyzes market volatility, opportunity flow, and derives rational search time boundaries via Continuation Value."),

    ("pages/0006_Payout_Physics_Causal_Inference.py", "git-branch", "Payout Physics",
     "Audits payout stability, prediction errors, and mathematically formalizes the platform's fraud prevention mechanisms."),

    ("pages/0007_Human_vs_AI_Behavioral_Cloning.py", "shield", "Human vs AI",
     "An interactive coliseum comparing the decision-making of the human agent against hierarchical AI models."),

    ("pages/0008_The_Quest_to_O1_NLP.py", "zap", "The Quest to (O)1",
     "A real-time diagnostic pipeline contrasting Cloud API latency against a custom local neural engine for spatial inference."),

    ("pages/0009_Generative_Moonshots:_pienza_big.py", "send", "Generative Moonshots",
     "cGAN synthetic manifold, network graph analysis, and Markov Decision Process scaffolding for autonomous fleet simulation."),
]

# Create a 3-column grid layout for visually stunning, concise cards
cols = st.columns(3)

for i, (path, icon, title, desc) in enumerate(modules):
    with cols[i % 3]:
        with st.container(border=True, key=f"nav-card-{i}"):
            # Fixed-height content block (icon+title+desc) we fully control, so total
            # card height stays constant regardless of description length.
            st.markdown(
                f"<div style='height:135px;display:flex;flex-direction:column;overflow:hidden;'>"
                f"<div style='font-size:1.05rem;font-weight:700;line-height:1.3;margin-bottom:8px;'>{_nav_icon(icon)}{title}</div>"
                f"<p style='font-size:13px;font-weight:400;color:#475569;line-height:1.7;flex:1;overflow:hidden;"
                f"display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;margin:0;'>{desc}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.page_link(path, label="Explore Module", use_container_width=True)

st.markdown("---")

# --- 7. CALL TO ACTION (The LLM Ingestion Gateway) ---
st.markdown("""
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