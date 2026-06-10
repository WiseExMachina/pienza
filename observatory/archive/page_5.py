import streamlit as st
import pandas as pd
import json
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from google.cloud import bigquery
from google.oauth2 import service_account
from pathlib import Path

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS "NIVEL DIOS" (BORDE A BORDE)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Pienza Observatory", page_icon="📍")

# Este CSS es más agresivo: mata los paddings de Streamlit que generan el "cuadro"
st.markdown("""
    <style>
        /* 1. Eliminamos el padding del contenedor principal de Streamlit */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        
        /* 2. Forzamos al bloque de contenido a usar el 100% del ancho sin márgenes */
        .main .block-container {
            max-width: 100% !important;
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        
        /* 3. Ocultamos el header y decoradores de Streamlit */
        [data-testid="stHeader"] {
            display: none;
        }
        
        /* 4. Hack para el iframe: lo hacemos ocupar el viewport casi completo */
        iframe {
            width: 100% !important;
            height: 95vh !important;
            border: none !important;
        }
        
        /* 5. Ajuste opcional: hace el sidebar un poco más elegante */
        [data-testid="stSidebar"] {
            background-color: #1a1c24;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CARGA DE DATOS (BIGQUERY - PIENZA_MINI)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_bq_data():
    # Ruta al service account (ajustada a tu estructura)
    current_dir = Path(__file__).resolve().parent.parent
    KEY_PATH = current_dir / "service-account.json"
    
    credentials = service_account.Credentials.from_service_account_file(str(KEY_PATH))
    client = bigquery.Client(credentials=credentials, project=credentials.project_id) 
    
    # Query optimizada con tus columnas reales
    query = f"""
        SELECT 
            o.offer_id,
            pc.category_name AS product_category,              
            o.upfront_fare,
            COALESCE(rp.reason_primary_description, 'NULL (Accepted)') AS rejection_reason, 
            ef.eph_operational,
            sp.dropoff_h3_hex_id,
            sp.dropoff_hdbscan_name
        FROM `645009831643.pienza_mini.offers` o
        LEFT JOIN `645009831643.pienza_mini.engineered_features` ef ON o.offer_id = ef.offer_id_fk
        LEFT JOIN `645009831643.pienza_mini.product_category` pc ON o.product_category_fk = pc.product_category_id
        LEFT JOIN `645009831643.pienza_mini.reason_primary` rp ON o.reason_primary_fk = rp.reason_primary_id
        INNER JOIN `645009831643.pienza_mini.silver_palette` sp ON o.offer_id = sp.offer_id
        WHERE sp.dropoff_hdbscan_name != 'unassigned'
    """
    df = client.query(query).to_dataframe()
    
    # Cálculo de volumen al vuelo (Densidad por hexágono)
    counts = df.groupby('dropoff_h3_hex_id').size().reset_index(name='offer_volume')
    df = df.merge(counts, on='dropoff_h3_hex_id')
    return df

@st.cache_data
def load_assets():
    current_dir = Path(__file__).resolve().parent.parent
    BASE_PATH = current_dir / "assets"
    
    with open(BASE_PATH / "poly_numbered.geojson", "r") as f:
        geojson = json.load(f)
    with open(BASE_PATH / "kepler_dropoff_config.json", "r") as f:
        config = json.load(f)
    
    # --- LIMPIEZA DINÁMICA DEL CONFIG (Look Profesional) ---
    # Esto quita los botones de Kepler para que el usuario use solo tus filtros de Streamlit
    if "config" in config and "visState" in config["config"]:
        config["config"]["uiState"] = {
            "readOnly": True,
            "sidePanel": {"show": False},
            "mapControls": {
                "visibleLayers": {"show": False},
                "mapLegend": {"show": True, "active": False},
                "toggle3d": {"show": True},
                "splitMap": {"show": False}
            }
        }
    
    return geojson, config

# Ejecución de carga
with st.spinner('Sincronizando con BigQuery...'):
    df_raw = load_bq_data()
    polygons, map_config = load_assets()

# ==============================================================================
# 3. INTERFAZ Y FILTROS EN SIDEBAR
# ==============================================================================
st.sidebar.title("📍 Pienza Observatory")
st.sidebar.subheader("Centro de Control")

# Selectores dinámicos
cats_disponibles = sorted(df_raw['product_category'].dropna().unique())
reasons_disponibles = sorted(df_raw['rejection_reason'].dropna().unique())

filtro_cat = st.sidebar.multiselect("🚕 Categoría de Producto", cats_disponibles, default=cats_disponibles)
filtro_reason = st.sidebar.multiselect("❌ Razón de Rechazo", reasons_disponibles, default=reasons_disponibles)

# Lógica de filtrado reactivo
df_filtrado = df_raw[
    (df_raw['product_category'].isin(filtro_cat)) & 
    (df_raw['rejection_reason'].isin(filtro_reason))
]

st.sidebar.divider()
st.sidebar.metric("Ofertas en Mapa", f"{len(df_filtrado):,}")
st.sidebar.caption("Dataset: pienza_mini (BigQuery)")

# ==============================================================================
# 4. RENDER (EL MAPA GIGANTE)
# ==============================================================================
# Usamos un height alto (1000) para asegurar que el CSS tenga material para estirar
mapa_operativo = KeplerGl(
    height=1000, 
    data={
        "-3f694b": df_filtrado, 
        "qyrepx": polygons
    },
    config=map_config
)

# Renderizado final
keplergl_static(mapa_operativo, height=1000)