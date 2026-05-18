import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import pydeck as pdk
from pathlib import Path
from shapely.affinity import translate

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="Markov Fleet Bridge", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@200..900&family=Inter:wght@400;600;700&display=swap');
        p, li, td, th { font-family: 'Crimson Pro', serif !important; font-size: 18px !important; }
        h1, h2, h3 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 The Markov Bridge: Fleet Optimization")
st.markdown("---")

# ==========================================
# DATA LOADING (MOCK & TOPOLOGY)
# ==========================================
@st.cache_data
def load_mock_topology():
    # Intentamos cargar tu GeoJSON real si existe, si no, fall-back a estructura vacía
    path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    try:
        gdf = gpd.read_file(str(path))
        gdf['name'] = gdf['name'].str.strip().str.lower()
        
        # Tu lógica de escalado Pienza (0.8)
        b = gdf.total_bounds
        mx, my = (b[0]+b[2])/2, (b[1]+b[3])/2
        gdf['geometry'] = gdf.geometry.apply(lambda g: translate(g, xoff=(g.centroid.x-mx)*0.8, yoff=(g.centroid.y-my)*0.8))
        gdf['lat'] = gdf.geometry.centroid.y
        gdf['lon'] = gdf.geometry.centroid.x
        return gdf
    except:
        st.error("GeoJSON not found. Running with mock spatial nodes.")
        # Mock de 72 nodos si no hay archivo
        return pd.DataFrame({
            'name': [f'node_{i}' for i in range(72)],
            'lat': np.random.uniform(19.35, 19.45, 72),
            'lon': np.random.uniform(-99.28, -99.20, 72)
        })

gdf_nodes = load_mock_topology()
node_names = gdf_nodes['name'].tolist()

# ==========================================
# SIDEBAR - BELLMAN & MARKOV CONTROLS
# ==========================================
with st.sidebar:
    st.header("⚙️ Agent Hyperparameters")
    gamma = st.slider("Discount Factor (γ) - Future Vision", 0.0, 1.0, 0.9, help="How much we value future rewards vs immediate ones.")
    alpha = st.slider("Learning Rate (α)", 0.01, 0.5, 0.1)
    epsilon = st.slider("Exploration (ε)", 0.0, 1.0, 0.2, help="Probability of choosing a random route to discover new payouts.")
    
    st.divider()
    st.header("🚢 Fleet Strategy")
    fleet_size = st.number_input("Number of Agents", 1, 500, 50)
    initial_node = st.selectbox("Deployment Base", node_names)
    
    run_sim = st.button("🚀 Run Bellman Iteration", use_container_width=True)

# ==========================================
# MARKOV ENGINE (MOCK LOGIC)
# ==========================================
# Aquí creamos una V-Table (Valor del nodo) aleatoria para el Mock
if 'v_table' not in st.session_state:
    st.session_state.v_table = {name: np.random.uniform(10, 100) for name in node_names}

def simulate_step():
    # Simulamos que el valor de los nodos cambia (como si los agentes aprendieran)
    for name in node_names:
        reward = np.random.normal(50, 10) # El payout real de Pienza entrará aquí
        # Ecuación simplificada de Bellman: V(s) = R + γ * max(V(s'))
        st.session_state.v_table[name] = (1 - alpha) * st.session_state.v_table[name] + \
                                         alpha * (reward + gamma * max(st.session_state.v_table.values()))

if run_sim:
    simulate_step()

# Preparar datos para el mapa
df_map = gdf_nodes.copy()
df_map['value'] = df_map['name'].map(st.session_state.v_table)
# Normalizar para color (Verde = Alto Valor, Rojo = Bajo Valor)
v_max = df_map['value'].max()
v_min = df_map['value'].min()
df_map['color'] = df_map['value'].apply(lambda v: [
    int(255 * (1 - (v-v_min)/(v_max-v_min))), # R
    int(255 * (v-v_min)/(v_max-v_min)),       # G
    150, 200                                  # B, A
])

# ==========================================
# DASHBOARD LAYOUT
# ==========================================
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.subheader("📍 State-Value Map (V-Matrix)")
    
    view_state = pdk.ViewState(
        latitude=df_map['lat'].mean(),
        longitude=df_map['lon'].mean(),
        zoom=12, pitch=45
    )
    
    layer_nodes = pdk.Layer(
        "ScatterplotLayer",
        df_map,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=200,
        pickable=True
    )
    
    # Capa de "Flujo Óptimo" (Mock de política de Markov)
    # Dibujamos arcos hacia los nodos de mayor valor
    top_nodes = df_map.nlargest(5, 'value')
    df_arcs = pd.DataFrame({
        's_lon': [df_map[df_map['name']==initial_node]['lon'].values[0]] * 5,
        's_lat': [df_map[df_map['name']==initial_node]['lat'].values[0]] * 5,
        'e_lon': top_nodes['lon'].values,
        'e_lat': top_nodes['lat'].values,
    })
    
    layer_arcs = pdk.Layer(
        "ArcLayer",
        df_arcs,
        get_source_position=["s_lon", "s_lat"],
        get_target_position=["e_lon", "e_lat"],
        get_source_color=[255, 255, 255, 80],
        get_target_color=[0, 255, 0, 200],
        get_width=3
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer_nodes, layer_arcs],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={"text": "Node: {name}\nValue: {value}"}
    ))

with col_stats:
    st.subheader("📊 Policy Metrics")
    
    # Métricas de convergencia
    st.metric("Avg Node Value", f"${df_map['value'].mean():.2f}")
    st.metric("System Entropy", f"{np.random.uniform(0.1, 0.5):.4f}", delta="-0.02")
    
    st.markdown("### 🏆 Top Profit States")
    st.dataframe(
        df_map.nlargest(10, 'value')[['name', 'value']].style.background_gradient(cmap='Greens'),
        use_container_width=True,
        hide_index=True
    )
    
    st.info("""
    **Markov Logic:**
    In this view, the fleet learns which states are 'absorbing' (high payout) 
    and which routes represent the *Optimal Policy* using the Bellman Equation.
    """)

# ==========================================
# FOOTER / DEBUG
# ==========================================
st.divider()
st.caption(f"Fleet Optimizer MVP | Nodes: {len(gdf_nodes)} | Convergence Mode: Value Iteration")