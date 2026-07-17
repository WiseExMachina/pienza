"""Canonical sidebar — single source of truth for the nav shared by every page and main.py."""

import base64
from pathlib import Path

import streamlit as st


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


def build_sidebar():
    with st.sidebar:
        st.markdown(
            "<div class='sb-brand'>"
            "<div class='sb-brand-mark'>"
            f"<img src='data:image/png;base64,{load_favicon_b64()}' width='40' height='40' /></div>"
            "<div><div class='sb-brand-text-title'>Project Pienza</div>"
            "<div class='sb-brand-text-sub'>Digital Twin · CDMX</div></div>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.page_link("main.py", label="Home", icon=":material/home:")
        st.markdown("<div class='sb-section-label'>Modules</div>", unsafe_allow_html=True)
        st.page_link("pages/0001_Foundations.py", label="Foundations", icon=":material/layers:")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines", icon=":material/sync:")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store", icon=":material/database:")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics", icon=":material/search:")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping", icon=":material/report:")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference", icon=":material/account_tree:")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning", icon=":material/shield:")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer", icon=":material/bolt:")
        st.page_link("pages/0009_Generative_Moonshots:_pienza_big.py", label="Generative Moonshots: pienza_big", icon=":material/send:")

        with st.container(key="sb-footer"):
            st.markdown("---")
            pdf_link = (
                "<a href='app/static/Pienza_Papers.pdf' target='_blank' "
                "class='sb-pdf-link'>Download PDF</a>"
            )

            st.markdown(
                "<div class='sb-meta-line'><b>Author:</b> Bernardo Lozano Wise<br>"
                "<b>LinkedIn:</b> <a href='https://www.linkedin.com/in/bernardolw/' target='_blank' class='sb-pdf-link'>/bernardolw</a><br>"
                "<b>GitHub:</b> <a href='https://github.com/WiseExMachina/pienza' target='_blank' class='sb-pdf-link'>/pienza</a><br>"
                "<b>Domain:</b> Data Science — Mobility & Logistics<br>"
                "<b>Stack:</b> Python, XGBoost, TensorFlow, BigQuery, PySpark, NetworkX<br>"
                f"<b>AI Knowledge Base:</b> {pdf_link}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("---")
