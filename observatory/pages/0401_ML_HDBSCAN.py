import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS (PANTALLA COMPLETA + HEADER)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Observatory - HDBSCAN Map")

st.markdown("""
    <style>
        /* Eliminar el padding general de la app */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        /* Ocultar el header (barra blanca superior) */
        header {
            display: none !important;
        }
        /* Le damos un pequeño respiro arriba (1rem) para el título y los botones */
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        /* Ajustamos el iframe para que deje espacio a los botones (88vh en vez de 100vh) */
        iframe {
            width: 100% !important;
            height: 88vh !important; 
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            border-radius: 8px; /* Un toque elegante para las esquinas del mapa */
        }
        /* Quitar el scroll lateral molesto de Streamlit */
        .main {
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. TOP BAR (TÍTULO Y BOTONES)
# ==============================================================================
# Usamos columnas para poner el título a la izquierda y los botones a la derecha
col1, col2 = st.columns([1, 4]) 

with col1:
    st.markdown("### 📍 HDBSCAN Results")

with col2:
    # Usamos radio horizontal porque nativamente guarda el estado y el diseño es limpio
    vista_activa = st.radio(
        "Selecciona la vista:",
        ["2D", "3D (offer_volume)"],
        horizontal=True,
        label_visibility="collapsed" # Ocultamos el texto de arriba para que se vean solo los botones
    )

st.markdown("<br>", unsafe_allow_html=True) # Un pequeño salto de línea para separar del mapa

# ==============================================================================
# 3. LÓGICA DE CARGA DE HTML
# ==============================================================================
@st.cache_data
def load_kepler_html(file_name):
    html_path = f"/workspaces/pienza/observatory/assets/{file_name}"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo en: {html_path}")
        return None

# El switch principal: decide qué archivo cargar
if vista_activa == "2D":
    html_data = load_kepler_html("kepler_2D.html")
else:
    html_data = load_kepler_html("kepler_3D.html")

# ==============================================================================
# 4. RENDERIZADO
# ==============================================================================
if html_data:
    # Renderizamos el HTML inyectando el código cargado
    components.html(html_data, height=900, scrolling=False)