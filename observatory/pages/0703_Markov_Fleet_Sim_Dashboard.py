import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import pydeck as pdk
from shapely.affinity import translate
from pathlib import Path

# ==========================================
# 1. PAGE CONFIG & STYLING (Homologado Pienza)
# ==========================================
st.set_page_config(page_title="Markov Fleet Simulator", page_icon="🤖", layout="wide")
st.title("🤖 The Markov Bridge: Tactical Fleet Deployment")
st.markdown("Observatorio Prescriptivo de Flotilla. Despliegue secuencial simulado con Absorción de Demanda.")
st.divider()

# ==========================================
# 2. DATA LOADING (GeoJSON - Topología Fiel)
# ==========================================
@st.cache_data
def load_topology():
    base_path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    
    try:
        gdf = gpd.read_file(str(base_path))
        
        # Corrección quirúrgica de Tecamachalco
        tecas = gdf[gdf['name'] == 'tecamachalco']
        if len(tecas) > 1:
            idx_norte = tecas.geometry.centroid.x.idxmax()
            idx_sur = tecas.geometry.centroid.x.idxmin()
            gdf.at[idx_norte, 'name'] = 'reforma_social'
            gdf.at[idx_sur, 'name'] = 'tecamachalco'
            
        gdf['name'] = gdf['name'].str.strip().str.lower()
        
        # Diccionario de coordenadas de centroides reales {nodo: [lon, lat]}
        coords = {row['name']: [row.geometry.centroid.x, row.geometry.centroid.y] for _, row in gdf.iterrows()}
        zonas = sorted(gdf['name'].unique().tolist())
        
        # Color del Polígono gris oscuro translúcido como el Tensor Global
        gdf['fill_color'] = [[108, 117, 125, 120]] * len(gdf) # '#6c757d' con alpha
        
        return gdf, zonas, coords
    except Exception as e:
        st.error(f"Error cargando poly.geojson: {e}")
        return None, [], {}

gdf_poly, zonas_ordenadas, coords_dict = load_topology()

# ==========================================
# 3. CONTROLES SUPERIORES (Cuerpo de la Pantalla)
# ==========================================
st.markdown("#### 🎛️ Panel de Mando Táctico")

# Layout de controles en línea (estilo Tensor Global)
c1, cMetric, cBalance = st.columns(3)

with c1:
    # Restricción estricta a los Warehouses oficiales, agregando "TODOS"
    warehouses_oficiales = ['carso_antara_miyana', 'santa_fe_centro_comercial', 'interlomas_magnocentro']
    
    warehouses_validos = [w for w in warehouses_oficiales if w in zonas_ordenadas]
    
    # Agregar la opción TODOS al principio
    warehouses_opciones = ['TODOS'] + warehouses_validos
    if not warehouses_validos and len(zonas_ordenadas) > 0:
        warehouses_opciones = ['TODOS'] + zonas_ordenadas[:3] 
        
    origen_despliegue = st.selectbox("🎯 Deployment Warehouse:", warehouses_opciones, index=0)

with cMetric:
    # Lógica de Bellman (Miopía estratégica)
    gamma = st.slider("Future Value Discount (γ):", 0.0, 1.0, 0.85, step=0.05)

with cBalance:
    # Lógica de Saltos Múltiples (Profundidad de la política Rollout)
    saltos_totales = st.slider("System Total Hops (T):", 1, 8, 5)

# Espaciado y botón destacado
st.markdown("<br>", unsafe_allow_html=True) 
_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    run_sim = st.button("🚀 CALCULAR VECTORES DE DESPLIEGUE", use_container_width=True)

# ==========================================
# 4. ENGINE: MARKOV DEMAND DEPLETION (TODOS Support)
# ==========================================
def simular_enjambre(origen_str, hops, gamma_val):
    N = len(zonas_ordenadas)
    
    np.random.seed(42)
    Q_real = np.random.uniform(10, 500, (N, N))
    np.fill_diagonal(Q_real, 0)
    
    if origen_str == 'TODOS':
        sources_to_simulate = warehouses_validos
    else:
        sources_to_simulate = [origen_str]
        
    all_arcos_generados = []
    all_bitacoras_generadas = []
    
    opciones_salida_warehouse = 10 
    opciones_por_salto = 3
    
    # EL FIX DEL COMETA: Transparente en Origen (Alpha 30), Sólido en Destino (Alpha 255)
    flota_conf = [
        {'id': 'AV-1', 'name': 'Pionero', 'col_orig': [231, 76, 60, 30], 'col_dest': [231, 76, 60, 255], 'tilt': 0},
        {'id': 'AV-2', 'name': 'Flanco N', 'col_orig': [41, 128, 185, 30], 'col_dest': [41, 128, 185, 255], 'tilt': 45},
        {'id': 'AV-3', 'name': 'Flanco S', 'col_orig': [39, 174, 96, 30], 'col_dest': [39, 174, 96, 255], 'tilt': -45}
    ]

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
                limite = opciones_salida_warehouse if profundidad == 0 else opciones_por_salto
                
                for dst in validas[:limite]:
                    buscar_rutas(dst, path + [dst], score_acumulado + Q_real[zona_actual, dst], profundidad + 1)
            
            buscar_rutas(idx_origen, [idx_origen], 0, 0)
            
            if rutas_candidatas:
                mejor_ruta = sorted(rutas_candidatas, key=lambda x: x['score'], reverse=True)[0]
                path_ganador = mejor_ruta['path_indices']
                nombres_ruta = [zonas_ordenadas[i].replace('_', ' ').title() for i in path_ganador]
                
                vehicle_fullname = f"{source_base_name} {av_conf['id']} ({av_conf['name']})"

                all_bitacoras_generadas.append({
                    'Almacén Origen': source_base_name,
                    'Vehículo ID': vehicle_fullname,
                    'Secuencia Táctica': " → ".join(nombres_ruta),
                    'Score (pts)': f"${mejor_ruta['score']:,.0f}"
                })
                
                for i in range(len(path_ganador) - 1):
                    u = path_ganador[i]
                    v = path_ganador[i+1]
                    
                    all_arcos_generados.append({
                        'source_pos': coords_dict[zonas_ordenadas[u]],
                        'target_pos': coords_dict[zonas_ordenadas[v]],
                        'color_origen': av_conf['col_orig'],
                        'color_destino': av_conf['col_dest'],
                        'tilt': av_conf['tilt'],
                        'av_fullname': vehicle_fullname,
                        'origen_n': nombres_ruta[i],
                        'destino_n': nombres_ruta[i+1],
                        'step': i + 1
                    })
                    
                    Q_real[u, v] *= 0.10
                
    return pd.DataFrame(all_bitacoras_generadas), pd.DataFrame(all_arcos_generados)


# ==========================================
# 5. RENDERIZADO (Paginación Táctica)
# ==========================================
if run_sim:
    df_bitacora, df_arcos = simular_enjambre(origen_despliegue, saltos_totales, gamma)
    st.session_state['bitacora'] = df_bitacora
    st.session_state['arcos'] = df_arcos
    st.session_state['sim_activa'] = True
    st.session_state['paso_actual'] = 1

if st.session_state.get('sim_activa', False):
    st.divider()
    
    ware_display = origen_despliegue.replace('_', ' ').upper()
    st.markdown(f"### 🗺️ Abanico Táctico de Markov (Warehouse(s): {ware_display})")
    
    if 'paso_actual' not in st.session_state:
        st.session_state['paso_actual'] = 1

    c_prev, c_info, c_next = st.columns([1, 2, 1])
    
    with c_prev:
        if st.button("◀️ Salto Anterior", use_container_width=True, disabled=(st.session_state['paso_actual'] <= 1)):
            st.session_state['paso_actual'] -= 1
            
    with c_info:
        st.markdown(
            f"<div style='text-align: center; font-size: 18px; font-weight: bold; padding-top: 5px; color: #2C3E50;'>"
            f"Mostrando Salto: <span style='color: #E74C3C;'>{st.session_state['paso_actual']}</span> de {saltos_totales}</div>", 
            unsafe_allow_html=True
        )
            
    with c_next:
        if st.button("Siguiente Salto ▶️", use_container_width=True, disabled=(st.session_state['paso_actual'] >= saltos_totales)):
            st.session_state['paso_actual'] += 1

    paso = st.session_state['paso_actual']
    df_arcos_t = st.session_state['arcos']
    df_arcos_visible = df_arcos_t[df_arcos_t['step'] <= paso]
    
    layer_poly = pdk.Layer(
        "GeoJsonLayer",
        gdf_poly,
        opacity=0.8,
        stroked=True,
        filled=True,
        get_fill_color=[230, 230, 230, 50],
        get_line_color=[150, 150, 150, 120],
        get_line_width=15,
        lineWidthMinPixels=1, 
    )
    
    layer_arcos = pdk.Layer(
        "ArcLayer",
        data=df_arcos_visible,
        get_source_position="source_pos",
        get_target_position="target_pos",
        get_source_color="color_origen",   # Nace transparente
        get_target_color="color_destino",  # Termina brillante
        get_tilt="tilt",
        get_width=7, # Un poco más gruesos para que luzca el gradiente
        pickable=True,
        auto_highlight=True
    )
    
    view_state = pdk.ViewState(
        latitude=19.4093, longitude=-99.2423,
        zoom=12.2, pitch=50, bearing=0
    )
    
    tooltip = {
        "html": "<b>{av_fullname}</b><br/>Salto #{step}<br/>{origen_n} → {destino_n}",
        "style": {"backgroundColor": "#2C3E50", "color": "white", "font-family": "sans-serif", "font-size": "13px"}
    }
    
    TOKEN_MAPBOX = "pk.eyJ1IjoiYmVybmFyZG9sdzg4IiwiYSI6ImNtcDMxcmphZjBtM3Eyc3Bwemc2OHhmbHIifQ.nRURL7plankvRicGkLIKDQ"
    
    st.pydeck_chart(pdk.Deck(
        layers=[layer_poly, layer_arcos], 
        initial_view_state=view_state,
        map_provider="mapbox",
        map_style="mapbox://styles/mapbox/light-v11",    
        api_keys={"mapbox": TOKEN_MAPBOX},
        tooltip=tooltip
    ), use_container_width=True, height=650)

    st.markdown("---")
    st.markdown("#### 📋 Bitácora de Despliegue Secuencial (Full Fleet Manual)")
    st.dataframe(st.session_state['bitacora'], hide_index=True, use_container_width=True)
    
else:
    st.info("💡 Configura los parámetros superiores y presiona Calcular Vectores de Despliegue para iniciar.")