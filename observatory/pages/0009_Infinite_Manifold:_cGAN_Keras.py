import streamlit as st
from components.styles import GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Infinite Manifold: cGAN Keras | Pienza")

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
        st.page_link("pages/0009_Infinite_Manifold:_cGAN_Keras.py", label="Infinite Manifold: cGAN Keras")
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
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("# Infinite Manifold: cGAN Keras")
st.markdown("""
<div style='font-size:0.95rem;color:#64748b;line-height:1.7;max-width:860px;margin-bottom:24px;'>
The generative frontier of Project Pienza — synthesizing behavioral manifolds, topological network metrics,
and a side-by-side audit of real vs. synthetic offer distributions.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## Mobility Tensor Dashboard")
st.markdown("""
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — Mobility Tensor Dashboard</span><br><br>
  Visualization of the cGAN-generated mobility tensor across CDMX zones. Coming soon.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## Network Metrics")
st.markdown("""
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — Network Metrics</span><br><br>
  Topological and tensor-based graph metrics derived from the offer network. Coming soon.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## Real vs. Synthetic")
st.markdown("""
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — Real vs. Synthetic Table</span><br><br>
  Side-by-side distributional audit comparing real offer records against cGAN-synthesized rows. Coming soon.
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align:center;padding:48px 0 24px;font-size:2rem;font-weight:300;
     color:#21918c;letter-spacing:0.12em;'>
  THE END.
</div>
""", unsafe_allow_html=True)
