import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS AGRESIVO (PANTALLA COMPLETA)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Observatory - HDBSCAN Map")

# Este CSS fuerza al contenedor de Streamlit a desaparecer y al iframe a ser gigante
st.markdown("""
    <style>
        /* Eliminar el padding de la app */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        /* Ocultar el header (barra blanca superior) */
        header {
            display: none !important;
        }
        /* Forzar el contenedor del componente a usar el 100% del alto y ancho */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
        }
        /* Estilizar el iframe para que no tenga bordes y sea inmersivo */
        iframe {
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Quitar el scroll lateral molesto de Streamlit */
        .main {
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CARGA DEL ARCHIVO HTML
# ==============================================================================
def load_kepler_html():
    # Ruta absoluta que proporcionaste
    html_path = "/workspaces/pienza/observatory/assets/kepler_gl_hdbscan.html"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo en: {html_path}")
        return None

html_data = load_kepler_html()

# ==============================================================================
# 3. RENDERIZADO
# ==============================================================================
if html_data:
    # Renderizamos el HTML directamente. 
    # Usamos un height muy alto para que el CSS tenga de donde estirar.
    components.html(html_data, height=1200, scrolling=False)

    