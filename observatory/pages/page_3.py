import streamlit as st
from pathlib import Path
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(layout="wide")
st.title("📄 Pienza Papers")

# Ruta exacta que confirmaste
pdf_path = Path(__file__).resolve().parent.parent / "Pienza_Papers.pdf"

if pdf_path.exists():
    # Renderizador nativo optimizado para Streamlit
    pdf_viewer(str(pdf_path), width=1200, height=850)
else:
    st.error(f"No se encontró el archivo PDF en la ruta: {pdf_path}")