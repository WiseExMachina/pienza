import streamlit as st

def :
    with st.sidebar:
        st.markdown("### Project Pieeeenza")   
        st.markdown("---")
        
        # Navegación: El primer argumento es la ruta desde la raíz, 
        # el label es el texto que quieres que aparezca.
        st.page_link("main.py", label="Home", icon="🏠")
        
        st.markdown("**1. Estrategia y Adquisición**")
        st.page_link("pages/0101_Project_Strategy_and_Scope.py", label="Estrategia y Alcance")
        st.page_link("pages/0102_Acquisition_and_Ground_Truth.py", label="Adquisición y Ground Truth")
        
        st.markdown("**2. Pipeline de Datos**")
        st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Sandbox")
        st.page_link("pages/0202_Target_and_Feature_Engineering.py", label="Ingeniería de Características")
        
        st.markdown("**3. Ciencia de la Decisión**")
        st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping")
        st.page_link("pages/0302_Causal_Inference.py", label="Inferencia Causal")
        
        st.markdown("**4. Modelado y Generación**")
        st.page_link("pages/0401_Unsupervised_Learning.py", label="Aprendizaje No Supervisado")
        st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Coliseum")
        st.page_link("pages/0601_O1_NLP1.py", label="NLP Transformer")
        st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/0603_Network_Graph.py", label="Análisis de Redes")
        st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")

        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("---")
        
        # Carga del PDF
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="📄 Descargar Reporte (PDF)", 
                data=pdf_data, 
                file_name="Project_Pienza_Full_Report.pdf",
                mime="application/pdf"
            )
        except FileNotFoundError:
            st.warning("Reporte PDF no encontrado.")
            
        st.markdown("[🔗 GitHub Repository](https://github.com/your-repo)")