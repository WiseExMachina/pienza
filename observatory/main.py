import streamlit as st

# --- 1. CONFIGURACIÓN CANÓNICA ---
st.set_page_config(
    layout="wide", 
    page_title="Pienza | Observatorio Urbano",
    page_icon="🛰️"
)

# Estética de Paper (Limpia los márgenes superiores)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("🛰️ Observatorio Urbano Pienza")
st.subheader("Digital Twin: West-End, CDMX")

st.markdown("---")

# --- 3. INTRODUCCIÓN AL PROYECTO ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### El Manifiesto de Conectividad
    Este observatorio es una herramienta de análisis de **Grafos Topológicos** y 
    **Densidades Latentes** diseñada para entender la infraestructura del West-End 
    como un sistema vivo.
    
    A través de las pestañas laterales, puedes navegar por las distintas capas del modelo:
    
    1.  **Intro (Naked Map):** Glosario espacial y reconocimiento del territorio.
    2.  **HDBSCAN Cluster:** Visualización de la estructura latente mediante celdas H3.
    3.  **VEN Playbook:** Estrategia de redes de intercambio de valor (Próximamente).
    """)

with col2:
    st.info("""
    **Estado del Sistema:**
    - Fase 2 (Topología): Completada ✅
    - Fase 3 (Densidad): En Integración 🛰️
    - Fase 4 (VEN): En Diseño ✍️
    """)

# --- 4. GUÍA DE NAVEGACIÓN ---
st.warning("👈 Selecciona un módulo en el sidebar de la izquierda para comenzar la exploración.")