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
st.set_page_config(layout="wide", page_title="Pienza Observatory - Vista 2D", page_icon="📍")

st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { padding: 0 !important; }
        .main .block-container {
            max-width: 100% !important;
            padding: 0rem !important;
        }
        [data-testid="stHeader"] { display: none; }
        iframe {
            width: 100% !important;
            height: 95vh !important;
            border: none !important;
        }
        [data-testid="stSidebar"] { background-color: #1a1c24; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CARGA DE DATOS (BIGQUERY + POLÍGONOS + CONFIGURACIÓN)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_bq_data():
    current_dir = Path(__file__).resolve().parent.parent
    KEY_PATH = current_dir / "service-account.json"
    
    credentials = service_account.Credentials.from_service_account_file(str(KEY_PATH))
    client = bigquery.Client(credentials=credentials, project=credentials.project_id) 
    
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
    
    # Cálculo de volumen al vuelo
    counts = df.groupby('dropoff_h3_hex_id').size().reset_index(name='offer_volume')
    df = df.merge(counts, on='dropoff_h3_hex_id')
    
    return df

@st.cache_data
def load_polygons():
    current_dir = Path(__file__).resolve().parent.parent
    BASE_PATH = current_dir / "assets"
    with open(BASE_PATH / "poly_numbered.geojson", "r") as f:
        geojson = json.load(f)
    return geojson

@st.cache_data
def load_config():
    current_dir = Path(__file__).resolve().parent.parent
    BASE_PATH = current_dir / "assets"
    
    # Cargamos tu nuevo JSON para la vista 2D
    with open(BASE_PATH / "kepler_dropoff_2D.json", "r") as f:
        config_2d = json.load(f)
        
    return config_2d

# Ejecución de carga (Mostramos el spinner mientras baja los datos)
with st.spinner('Sincronizando con BigQuery y cargando activos...'):
    df_raw = load_bq_data()
    polygons = load_polygons()
    map_config = load_config()

# ==============================================================================
# 3. INTERFAZ LIMPIA EN SIDEBAR
# ==============================================================================
st.sidebar.title("📍 Nueva Vista 10")
st.sidebar.subheader("Modo Exploración 2D")
st.sidebar.write("*(Los nuevos controles irán aquí)*")

st.sidebar.divider()
st.sidebar.metric("Viajes Totales", f"{len(df_raw):,}")

# ==============================================================================
# 4. RENDER DEL MAPA GIGANTE
# ==============================================================================

# Conectamos las fuentes de datos exactamente con los Data IDs que pide tu nuevo JSON
mapa = KeplerGl(
    height=1000, 
    data={
        "4oa047": df_raw,       # Base de datos de viajes (BigQuery)
        "nprfxg": polygons      # Archivo de zonas y polígonos
    }, 
    config=map_config
)

# Renderizado final
keplergl_static(mapa, height=1000)