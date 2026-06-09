# utils/sidebar.py
import streamlit as st

def build_sidebar():
    with st.sidebar:
        st.markdown("Proyect Pienza")   
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0101_Project_Strategy_and_Scope.py", label="Project Strategy and Scope")
        st.page_link("pages/0102_Acquisition_and_Ground_Truth.py", label="Acquisition and Ground Truth")
        st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox")
        st.page_link("pages/0202_Target_and_Feature_Engineering.py", label="Target and Feature Engineering")
        st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping & The Efficient Frontier")
        st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
        st.page_link("pages/0401_Unsupervised_Learning.py", label="Unsupervised Learning")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGB Coliseum")
        st.page_link("pages/0601_O1_NLP1.py", label="O1 NLP1")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Network Graph")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Sim Dashboard")

        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        st.download_button("📄 Download 91-Page Report (PDF)", data="PDF_DATA_HERE", file_name="Project_Pienza_Full_Report.pdf")
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")