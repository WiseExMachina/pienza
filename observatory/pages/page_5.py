import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# --- 1. PIENZA CANON CONFIGURATION ---
st.set_page_config(layout="wide", page_title="HDBSCAN | Pienza")

# THE "CLEAN SLATE" CSS
# This kills the margins so Kepler hits the edges of the screen
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    iframe {
        border-radius: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ASSET LOCATOR ---
# Points to: observatory/assets/kepler_gl_hdbscan.html
base_path = Path(__file__).resolve().parent.parent
path_to_html = base_path / "assets" / "kepler_gl_hdbscan.html"

# --- 3. RENDER ENGINE ---
if path_to_html.exists():
    with open(path_to_html, 'r', encoding='utf-8') as f:
        html_data = f.read()

    # We use a high pixel height (900+) to ensure the H3 grid feels immersive
    components.html(html_data, height=920, scrolling=False)
else:
    st.error(f"🚨 File Not Found: {path_to_html}")
    st.info("Ensure your exported Kepler HTML is named 'kepler_gl_hdbscan.html' inside the assets folder.")

# --- 4. OPTIONAL FOOTER ---
# If you want a tiny bit of text below the map (visible only when scrolling)
with st.expander("📝 Research Note: Hierarchical Density Analysis"):
    st.markdown("""
    This map represents the **Latent Tissue** of the West-End. 
    Using an **H3 Hexagonal Grid (Resolution 9)** and **HDBSCAN**, we have isolated 
    clusters of urban intensity that transcend traditional neighborhood boundaries.
    """)