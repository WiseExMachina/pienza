import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.affinity import translate
from pathlib import Path
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

# ==========================================
# 1. PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="Markov Fleet Simulator", page_icon="🤖", layout="wide")
st.title("🤖 The Markov Bridge: Tactical Fleet Deployment")
st.markdown("Observatorio Prescriptivo de Flotilla. Renderizado Fluido con Kepler.gl (Uber).")
st.divider()

# ==========================================
# 2. DATA LOADING (GeoJSON - Topología Fiel)
# ==========================================
@st.cache_data
def load_topology():
    base_path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    try:
        gdf = gpd.read_file(str(base_path))
        
        tecas = gdf[gdf['name'] == 'tecamachalco']
        if len(tecas) > 1:
            idx_norte = tecas.geometry.centroid.x.idxmax()
            idx_sur = tecas.geometry.centroid.x.idxmin()
            gdf.at[idx_norte, 'name'] = 'reforma_social'
            gdf.at[idx_sur, 'name'] = 'tecamachalco'
            
        gdf['name'] = gdf['name'].str.strip().str.lower()
        coords = {row['name']: [row.geometry.centroid.x, row.geometry.centroid.y] for _, row in gdf.iterrows()}
        zonas = sorted(gdf['name'].unique().tolist())
        return gdf, zonas, coords
    except Exception as e:
        st.error(f"Error cargando poly.geojson: {e}")
        return None, [], {}

gdf_poly, zonas_ordenadas, coords_dict = load_topology()

# ==========================================
# 3. CONTROLES SUPERIORES 
# ==========================================
st.markdown("#### 🎛️ Panel de Mando Táctico")

c1, cMetric, cBalance = st.columns(3)

with c1:
    warehouses_oficiales = ['carso_antara_miyana', 'santa_fe_centro_comercial', 'interlomas_magnocentro']
    warehouses_validos = [w for w in warehouses_oficiales if w in zonas_ordenadas]
    warehouses_opciones = ['TODOS'] + warehouses_validos
    if not warehouses_validos and len(zonas_ordenadas) > 0:
        warehouses_opciones = ['TODOS'] + zonas_ordenadas[:3] 
        
    origen_despliegue = st.selectbox("🎯 Deployment Warehouse:", warehouses_opciones, index=0)

with cMetric:
    gamma = st.slider("Future Value Discount (γ):", 0.0, 1.0, 0.85, step=0.05)

with cBalance:
    saltos_totales = st.slider("System Total Hops (T):", 1, 8, 5)

st.markdown("<br>", unsafe_allow_html=True) 
_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    run_sim = st.button("🚀 INICIALIZAR MOTOR KEPLER.GL", use_container_width=True)

# ==========================================
# 4. ENGINE: MARKOV DEMAND DEPLETION
# ==========================================
def simular_enjambre_kepler(origen_str, hops, gamma_val):
    N = len(zonas_ordenadas)
    np.random.seed(42) 
    Q_real = np.random.uniform(10, 500, (N, N))
    np.fill_diagonal(Q_real, 0) 
    
    if origen_str == 'TODOS':
        sources_to_simulate = warehouses_validos
    else:
        sources_to_simulate = [origen_str]
        
    all_arcos = []
    all_bitacoras = []
    
    # HEX Colors para Kepler auto-mapping
    flota_conf = [
        {'id': 'AV-1', 'name': 'Pionero', 'hex': '#e74c3c'},  # Rojo
        {'id': 'AV-2', 'name': 'Flanco N', 'hex': '#2980b9'}, # Azul
        {'id': 'AV-3', 'name': 'Flanco S', 'hex': '#27ae60'}  # Verde
    ]

    # Reloj base ficticio para engañar a Kepler
    base_time = pd.Timestamp("2026-05-20 10:00:00")

    for source_node in sources_to_simulate:
        idx_origen = zonas_ordenadas.index(source_node)
        source_base_name = source_node.replace('_', ' ').split()[0].title()

        for av_conf in flota_conf:
            rutas_candidatas = []
            
            def buscar_rutas(zona_actual, path, score_acumulado, profundidad):
                if profundidad == hops:
                    rutas_candidatas.append({'path_indices': path, 'score': score_acumulado})
                    return
                    
                opciones = np.argsort(Q_real[zona_actual, :])[::-1]
                validas = [dst for dst in opciones if Q_real[zona_actual, dst] > 0 and dst != zona_actual]
                limite = 10 if profundidad == 0 else 3
                
                for dst in validas[:limite]:
                    buscar_rutas(dst, path + [dst], score_acumulado + Q_real[zona_actual, dst], profundidad + 1)
            
            buscar_rutas(idx_origen, [idx_origen], 0, 0)
            
            if rutas_candidatas:
                mejor_ruta = sorted(rutas_candidatas, key=lambda x: x['score'], reverse=True)[0]
                path_ganador = mejor_ruta['path_indices']
                nombres_ruta = [zonas_ordenadas[i].replace('_', ' ').title() for i in path_ganador]
                
                vehicle_fullname = f"{source_base_name} {av_conf['id']}"

                all_bitacoras.append({
                    'Origen': source_base_name,
                    'Vehículo': vehicle_fullname,
                    'Manual de Vuelo': " → ".join(nombres_ruta),
                    'Score': f"${mejor_ruta['score']:,.0f}"
                })
                
                for i in range(len(path_ganador) - 1):
                    u = path_ganador[i]
                    v = path_ganador[i+1]
                    
                    # Generar un timestamp basado en el número de salto
                    # Le sumamos 1 hora por salto para que la línea de tiempo avance
                    step_time = (base_time + pd.Timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
                    
                    all_arcos.append({
                        's_lon': coords_dict[zonas_ordenadas[u]][0],
                        's_lat': coords_dict[zonas_ordenadas[u]][1],
                        't_lon': coords_dict[zonas_ordenadas[v]][0],
                        't_lat': coords_dict[zonas_ordenadas[v]][1],
                        'av_id': vehicle_fullname,
                        'color_hex': av_conf['hex'],
                        'step': i + 1,
                        'timestamp': step_time  # <--- LA CLAVE DE LA ANIMACIÓN
                    })
                    
                    Q_real[u, v] *= 0.10
                
    return pd.DataFrame(all_bitacoras), pd.DataFrame(all_arcos)

# ==========================================
# 5. RENDERIZADO: KEPLER.GL (The Real Deal)
# ==========================================
if run_sim:
    df_bitacora, df_arcos = simular_enjambre_kepler(origen_despliegue, saltos_totales, gamma)
    
    st.divider()
    st.markdown(f"### 🗺️ Simulador Cinemático Kepler.gl")
    st.info("💡 **Instrucciones:** Dale click al botón de **PLAY (▶️)** en la barra de tiempo que aparece en la parte inferior del mapa. Ajusta la velocidad de reproducción a tu gusto en la esquina de la misma barra.")
    
    # ---------------------------------------------------------
    # CONFIGURACIÓN MÁGICA DE KEPLER (Para que no tengas que picarle nada)
    # ---------------------------------------------------------
    kepler_config = {
        "version": "v1",
        "config": {
            "visState": {
                "filters": [
                    {
                        "dataId": ["Vectores_Tacticos"],
                        "id": "time-play",
                        "name": ["timestamp"],
                        "type": "timeRange",
                        "enlarged": True # Esto abre el reproductor de video automáticamente
                    }
                ],
                "layers": [
                    {
                        "id": "poly",
                        "type": "geojson",
                        "config": {
                            "dataId": "Geocerca",
                            "label": "Zonas Operativas",
                            "color": [220, 220, 220],
                            "columns": {"geojson": "geometry"},
                            "isVisible": True,
                            "visConfig": {"opacity": 0.3, "stroked": True, "filled": True}
                        }
                    },
                    {
                        "id": "arcs",
                        "type": "arc",
                        "config": {
                            "dataId": "Vectores_Tacticos",
                            "label": "Vuelos Tácticos",
                            "columns": {
                                "lat0": "s_lat", "lng0": "s_lon",
                                "lat1": "t_lat", "lng1": "t_lon"
                            },
                            "isVisible": True,
                            "colorField": {"name": "av_id", "type": "string"},
                            "visConfig": {
                                "opacity": 0.8,
                                "thickness": 4,
                                "colorRange": {
                                    "name": "Custom", "type": "custom", "category": "Custom",
                                    # Kepler asigna colores en orden alfabético del ID. 
                                    # AV-1, AV-2, AV-3 mapean exacto a Rojo, Azul, Verde.
                                    "colors": ["#e74c3c", "#2980b9", "#27ae60"] 
                                }
                            }
                        }
                    }
                ]
            },
            "mapState": {
                "bearing": 0,
                "dragRotate": False,
                "latitude": 19.4093,
                "longitude": -99.2423,
                "pitch": 45,
                "zoom": 11.5
            },
            "mapStyle": {
                "styleType": "light"
            }
        }
    }
    
    # Instanciamos el mapa e inyectamos los datos y la configuración
    # --- RENDERIZADO DEL MAPA ---
    TOKEN_MAPBOX = "pk.eyJ1IjoiYmVybmFyZG9sdzg4IiwiYSI6ImNtcDMxcmphZjBtM3Eyc3Bwemc2OHhmbHIifQ.nRURL7plankvRicGkLIKDQ"
    
    # 🎯 FIX: Instanciamos Kepler pasando el token en el constructor
    kmap = KeplerGl(height=650, token=TOKEN_MAPBOX)
    
    kmap.add_data(data=gdf_poly, name="Geocerca")
    kmap.add_data(data=df_arcos, name="Vectores_Tacticos")
    kmap.config = kepler_config
    
    # Streamlit inyecta el HTML de Kepler
    keplergl_static(kmap)
    kmap = KeplerGl(height=650, token=TOKEN_MAPBOX)
    kmap.add_data(data=gdf_poly, name="Geocerca")
    kmap.add_data(data=df_arcos, name="Vectores_Tacticos")
    kmap.config = kepler_config
    
    # Streamlit inyecta el HTML de Kepler
    keplergl_static(kmap)

    # --- TABLA Y ESTADÍSTICAS ---
    st.markdown("---")
    st.markdown("#### 📋 Bitácora de Despliegue Secuencial (Full Fleet Manual)")
    st.dataframe(df_bitacora, hide_index=True, use_container_width=True)
    
else:
    st.info("💡 Configura los parámetros superiores y presiona Inicializar Motor Kepler.gl para iniciar.")