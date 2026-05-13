# SECTION 1

import streamlit as st
import pandas as pd
import geopandas as gpd
import networkx as nx
import plotly.graph_objects as go
from networkx.algorithms.community import greedy_modularity_communities
from shapely.affinity import translate
from pathlib import Path
import numpy as np
import json
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import json
import pandas as pd
import geopandas as gpd
import streamlit.components.v1 as components  # <- El salvavidas nativo
from keplergl import KeplerGl

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Network Observatory",
    page_icon="🔭",
    layout="wide"
)

# ==========================================
# CUSTOM FONT INJECTION
# ==========================================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');
        
        p, li, td, th { font-family: 'Crimson Pro', serif !important; font-size: 18px !important; line-height: 1.6 !important; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; }
        h1 { font-size: 38px !important; } 
        h2 { font-size: 28px !important; } 
        h3 { font-size: 22px !important; } 
        
        [data-testid="stExpander"] details summary p { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-size: 16px !important; }
        code, pre { font-family: 'Courier New', Courier, monospace !important; font-size: 15px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🔭 Pienza Network Observatory")
st.markdown("Welcome to the operational command center. Here we observe both the physical constraints of the urban geofence and the directed flow of capital within it.")


# =
# =
# =
# =
# =


# ==========================================
# CHUNK 2: CONSTANTS & DATA CACHE
# ==========================================

# Colorscales
ISLAND_COLORS = ['#3498DB', '#E67E22', '#2ECC71', '#F1C40F', '#9B59B6', '#1ABC9C']
COMMUNITY_COLORS = ['#FD7F6F', '#7EB0D5', '#B2E061', '#BD7EBE', '#FFB55A', '#FFEE65', '#BEB9DB', '#FDCCE5', '#8BD3C7']
COLLAPSED_COLOR = '#2C3E50' 
OPUS_BLUE_FILL  = '#E1F5FE'
OPUS_BLUE_EDGE  = '#0288D1'
NETWORK_GREY    = '#9CA3AF' 
HIGHLIGHT_VIOLET = '#A5B4FC'
CORE_BLUE       = '#1E3A8A'
BORDER_ORANGE   = '#FDBA74'
PATH_HIGHLIGHT  = '#FACC15'

# --- DATA LOAD ---
@st.cache_data
def get_topology_data():
    base_path = Path(__file__).resolve().parent.parent / "assets" / "poly.geojson"
    gdf = gpd.read_file(str(base_path))
    tecas = gdf[gdf['name'] == 'tecamachalco']
    if len(tecas) > 1:
        idx_norte, idx_sur = tecas.geometry.centroid.x.idxmax(), tecas.geometry.centroid.x.idxmin()
        gdf.at[idx_norte, 'name'], gdf.at[idx_sur, 'name'] = 'reforma_social', 'tecamachalco'
    gdf['name'] = gdf['name'].str.strip().str.lower()
    
    b = gdf.total_bounds
    mx, my = (b[0]+b[2])/2, (b[1]+b[3])/2
    gdf['geometry'] = gdf.geometry.apply(lambda g: translate(g, xoff=(g.centroid.x-mx)*0.8, yoff=(g.centroid.y-my)*0.8))
    gdf['centroid'] = gdf.geometry.centroid
    return gdf

# --- ROUTES DATA ---
ROUTES = [['anzures', 'polanco_gandhi', 'polanco_parque_lincoln', 'lomas_virreyes', 'lomas_trastevere', 'nodo_reforma_palmas', 'reforma_regina', 'lomas_altas'], ['anzures', 'rios', 'juarez_rosa', 'bosque_1', 'bosque_2', 'bosque_3', 'lomas_altas', 'reforma_bnp', 'sante_fe_patio', 'santa_fe_quintana'], ['anzures', 'polanco_5', 'polanco_parroquia', 'polanco_palacio', 'polanco_uber_hq', 'palmas_jp_morgan', 'fuentes_casino', 'nodo_monte_libano', 'nodo_reforma_palmas'], ['lomas_barrilaco','lomas_olimpo', 'lomas_prado_norte'], ['lomas_virreyes', 'campo_marte', 'polanco_parque_lincoln'], ['carso_antara_miyana', 'polanco_palacio', 'polanco_grupo_mexico', 'polanco_parque_lincoln', 'lomas_virreyes', 'lomas_fc_cuernavaca', 'lomas_prado_norte', 'lomas_barrilaco', 'nodo_reforma_palmas' ], ['juarez_soho_house', 'juarez_rosa', 'rios', 'bahias', 'anahuac_1', 'lagos', 'carso_antara_miyana', 'irrigacion', 'sotelo', 'herradura_conscripto', 'interlomas_magnocentro', 'bosque_real'], ['roma_condesa_2', 'roma_condesa_1', 'juarez_rosa', 'anzures', 'polanco_5', 'polanco_parroquia', 'polanco_palacio', 'polanco_uber_hq', 'sedena', 'reforma_social', 'fuentes_casino', 'de_las_fuentes', 'de_los_bosques', 'universidad_anahuac', 'interlomas_magnocentro', 'vialidad_de_la_barranca', 'ave_club_de_golf_lomas', 'lomas_country_club'], ['herradura_conscripto', 'de_las_fuentes'], ['herradura_conscripto', 'universidad_anahuac'], ['jesus_del_monte', 'interlomas_haciendas', 'vialidad_de_la_barranca', 'carretera_al_olivo', 'cruce_echanove', 'santa_fe_centro_comercial', 'santa_fe_colegios', 'santa_fe_cumbres_de'], ['santa_fe_bosques_de', 'santa_fe_centro_comercial'], ['nodo_reforma_palmas', 'ahuehuetes_norte', 'ahuehuetes_sur', 'tamarindos', 'santa_fe_ibero', 'santa_fe_centro_comercial', 'cruce_echanove', 'carretera_libre','agwa_bezares', 'reforma_bnp'], ['santa_fe_tec', 'santa_fe_ibero', 'santa_fe_colegios', 'santa_fe_tec'], ['carretera_libre', 'vistahermosa', 'cruce_echanove', 'carretera_al_olivo', 'loma_de_la_palma', 'bosques_pabellon', 'de_los_bosques', 'universidad_anahuac', 'blvrd_anahuac', 'el_olivo', 'vialidad_de_la_barranca'], ['jesus_del_monte', 'herradura_conscripto'], ['interlomas_magnocentro', 'jesus_del_monte'], ['vistahermosa', 'bosques_pabellon', 'loma_de_la_palma', 'el_olivo'], ['blvrd_anahuac', 'interlomas_magnocentro'], ['santa_fe_ibero', 'sante_fe_patio'], ['tamarindos', 'ahuehuetes_sur', 'bosques_pabellon', 'ahuehuetes_norte', 'de_los_bosques'], ['ahuehuetes_norte', 'de_las_fuentes', 'tecamachalco', 'fuentes_casino', 'lomas_barrilaco'], ['lomas_prado_norte', 'fuentes_casino', 'palmas_jp_morgan', 'lomas_fc_cuernavaca'], ['bosques_pabellon', 'tamarindos', 'agwa_bezares'], ['reforma_social','herradura_conscripto'], ['irrigacion', 'sedena', 'sotelo'], ['bondojito_asf', 'bosque_3'], ['irrigacion', 'polanco_uber_hq', 'polanco_grupo_mexico', 'palmas_jp_morgan'], ['carso_antara_miyana','frontera_polanco', 'lagos', 'polanco_parroquia', 'polanco_parque_lincoln'], ['frontera_polanco', 'anahuac_1'], ['lomas_virreyes', 'bosque_2', 'campo_marte', 'bosque_1', 'polanco_gandhi', 'polanco_5', 'lagos'], ['bahias', 'anzures', 'anahuac_1'], ['bosque_2','roma_condesa_2', 'bosque_1'], ['rios', 'juarez_soho_house', 'roma_condesa_2'], ['lomas_altas', 'nodo_reforma_palmas', 'bosque_3', 'lomas_trastevere'], ['fuentes_casino', 'palmas_jp_morgan', 'lomas_prado_norte', 'lomas_trastevere', 'lomas_barrilaco', 'nodo_monte_libano', 'de_las_fuentes']]

centrality_data = {
    "Degree": {"nodo_reforma_palmas": {"Rank": 1, "Score": 0.0985, "Info": "Maximum physical permeability."}, "fuentes_casino": {"Rank": 2, "Score": 0.0985, "Info": "Highest level of local routing options."}, "de_las_fuentes": {"Rank": 3, "Score": 0.0845, "Info": "Strong secondary distributor (NW)."}, "anzures": {"Rank": 4, "Score": 0.0845, "Info": "Main distribution hub (East/Center)."}, "lomas_prado_norte": {"Rank": 5, "Score": 0.0845, "Info": "Key hub within the Lomas cluster."}},
    "Betweenness": {"nodo_reforma_palmas": {"Rank": 1, "Score": 0.2054, "Info": "Controls 20.5% of optimal network paths."}, "bosque_3": {"Rank": 2, "Score": 0.1958, "Info": "Vital bridge connecting the deep west."}, "herradura_conscripto": {"Rank": 3, "Score": 0.1956, "Info": "Critical funnel; high risk of isolation."}, "ahuehuetes_norte": {"Rank": 4, "Score": 0.1823, "Info": "Main connector in the NW corridor."}, "bosque_2": {"Rank": 5, "Score": 0.1700, "Info": "Critical link in the topographic forests chain."}},
    "Closeness": {"ahuehuetes_norte": {"Rank": 1, "Score": 0.2795, "Info": "Topologically most central zone."}, "nodo_reforma_palmas": {"Rank": 2, "Score": 0.2784, "Info": "Exact center of gravity."}, "de_las_fuentes": {"Rank": 3, "Score": 0.2699, "Info": "Highly efficient dispatch point."}, "bosque_3": {"Rank": 4, "Score": 0.2619, "Info": "Strategic bridge and central node."}, "fuentes_casino": {"Rank": 5, "Score": 0.2610, "Info": "Central and highly connected to exits."}},
    "Eigenvector": {"lomas_barrilaco": {"Rank": 1, "Score": 0.3424, "Info": "The most influential node; neighbor to power."}, "fuentes_casino": {"Rank": 2, "Score": 0.3367, "Info": "Positioned within the elite mesh."}, "nodo_reforma_palmas": {"Rank": 3, "Score": 0.3091, "Info": "Maintains elite influence status."}, "lomas_prado_norte": {"Rank": 4, "Score": 0.3038, "Info": "Lomas-Palmas cluster dominance."}, "lomas_trastevere": {"Rank": 5, "Score": 0.2728, "Info": "High neighbor interconnectivity."}}
}

# --- GRAPH CONSTRUCTION & ON-THE-FLY METRICS ---
gdf = get_topology_data()
G = nx.Graph()
for r in ROUTES: G.add_edges_from([(r[i], r[i+1]) for i in range(len(r)-1)])
gdf_active = gdf[gdf['name'].isin(G.nodes())].copy()

giant_nodes = max(nx.connected_components(G), key=len)
G_giant = G.subgraph(giant_nodes).copy()

# Dynamic metrics for Overview
deg_cent = nx.degree_centrality(G_giant)
bet_cent = nx.betweenness_centrality(G_giant)
clo_cent = nx.closeness_centrality(G_giant)
eig_cent = nx.eigenvector_centrality(G_giant, max_iter=1000)
eccentricity = nx.eccentricity(G_giant)

# =
# =
# =
# =
# =
# =

# ==========================================
# CHUNK 3: THE OBSERVATORY TABS & UI LOGIC
# ==========================================

# Create the Tabs (Actualizado a PyDeck)
tab_tensor_global, tab_topo, tab_tensor_live = st.tabs([
    "Global Tensor Graph", 
    "Undirected Topological Graph",
    "📈 Live Slicing"
])

# ==============================================================================
# CARGA DE DATOS PYDECK (Declarado fuera de los tabs por buenas prácticas)
# ==============================================================================
import pydeck as pdk

@st.cache_data
def load_pydeck_assets():
    df_arcos = pd.read_csv('/workspaces/pienza/observatory/assets/0608_260513_tensor_arcos_w_edge_centrality.csv')
    gdf_poly = gpd.read_file('/workspaces/pienza/observatory/assets/poly.geojson')
    return df_arcos, gdf_poly

df_arcos_pd, gdf_poly_pd = load_pydeck_assets()

# --- TAB 1: TOPOLOGICAL SANDBOX ---
with tab_topo:
    # Set up the column layout: narrow left for tools, wide right for map
    col_tools, col_map = st.columns([1, 3])
    
    # Initialize variables used for plotting
    current_top_5, islands_map, community_map, active_path = [], {}, {}, []
    center_nodes = nx.center(G_giant)
    periphery_nodes = nx.periphery(G_giant)
    
    with col_tools:
        st.subheader("Network Tools")
        tool_category = st.selectbox("Select Category:", [
            "Overview", "Small World Theory", "Centrality Metrics", 
            "Vulnerability Audit", "Excentricity", "Geodesic Distance", "Latent Structure"
        ])
        
        # State variables for UI selections
        metric_choice, target_node, excentricity_focus, geo_source, geo_target, geo_obstacle = None, None, None, None, None, "None"
        
        # UI Input Logic
        if tool_category == "Centrality Metrics":
            metric_choice = st.selectbox("Metric:", ["Degree", "Betweenness", "Closeness", "Eigenvector"])
        elif tool_category == "Vulnerability Audit":
            st.markdown("#### Collapse Simulator")
            cut_vertices = sorted(list(nx.articulation_points(G)))
            target_node = st.selectbox("Node to Collapse (Cut-Vertex):", cut_vertices)
        elif tool_category == "Excentricity":
            excentricity_focus = st.selectbox("Focus:", ["Nucleus", "Border", "Diameter in Action", "Radius in Action"])
        elif tool_category == "Geodesic Distance":
            nodes_list = sorted(list(G_giant.nodes()))
            geo_source = st.selectbox("Source Node (i):", nodes_list, index=0)
            geo_target = st.selectbox("Target Node (j):", nodes_list, index=len(nodes_list)-1)
            k_options = ["None", "herradura_conscripto", "cruce_echanove", "santa_fe_ibero", "nodo_reforma_palmas", "bosque_2"]
            geo_obstacle = st.selectbox("Drop Node (k):", k_options)

        st.markdown("---")
        
        # Page State Output Logic
        if tool_category == "Overview":
            st.markdown("### 🗺️ Network Overview")
            st.info("Hover over any node on the map to view its complete topological profile.")

        elif tool_category == "Small World Theory":
            st.markdown("### 📊 Small-World Hypothesis Test")
            st.success("🏆 **VERDICT: The Pienza infrastructure IS A SMALL-WORLD.**")
            c1, c2 = st.columns(2)
            c1.metric("Sigma (σ)", "4.9297")
            c2.metric("Omega (ω)", "-0.3009")
            c3, c4 = st.columns(2)
            c3.metric("Clustering (C)", "0.2677")
            c4.metric("Path (L)", "4.8052")

        elif tool_category == "Centrality Metrics":
            st.markdown(f"### 👑 Top Nodes")
            current_metrics = centrality_data[metric_choice]
            current_top_5 = list(current_metrics.keys())
            df_display = pd.DataFrame.from_dict(current_metrics, orient='index').sort_values('Rank')
            st.dataframe(df_display, use_container_width=True)

        elif tool_category == "Vulnerability Audit":
            G_sim = G.copy()
            G_sim.remove_node(target_node)
            islands = sorted(list(nx.connected_components(G_sim)), key=len, reverse=True)
            st.markdown(f"### 🚨 Damage Report")
            st.markdown(f"Collapse at **{target_node.upper()}**.")
            st.markdown(f"> The network fragmented into **{len(islands)} independent islands**.")
            for i, island in enumerate(islands):
                for node in island: islands_map[node] = i

        elif tool_category == "Excentricity":
            st.markdown("### 🌍 Excentricity Report")
            c1, c2 = st.columns(2)
            c1.metric("Density", f"{nx.density(G):.4f}")
            c2.metric("Diameter", nx.diameter(G_giant))
            c3, c4 = st.columns(2)
            c3.metric("Radius", nx.radius(G_giant))
            c4.metric("Avg. Dist.", f"{nx.average_shortest_path_length(G_giant):.2f}")
            
            if excentricity_focus == "Diameter in Action":
                start_node = periphery_nodes[0]
                path_dict = nx.single_source_shortest_path(G_giant, start_node)
                active_path = path_dict[max(path_dict, key=lambda k: len(path_dict[k]))]
            elif excentricity_focus == "Radius in Action":
                start_node = center_nodes[0]
                path_dict = nx.single_source_shortest_path(G_giant, start_node)
                active_path = path_dict[[n for n, p in path_dict.items() if len(p)-1 == nx.radius(G_giant)][0]]

        elif tool_category == "Geodesic Distance":
            st.markdown(f"### 📍 Navigator")
            G_temp = G_giant.copy()
            if geo_obstacle != "None": G_temp.remove_node(geo_obstacle)
            try:
                active_path = nx.shortest_path(G_temp, source=geo_source, target=geo_target)
                st.metric("Geodesic Path Length", f"{len(active_path)-1} Jumps")
            except nx.NetworkXNoPath: 
                st.error("No path exists.")

        elif tool_category == "Latent Structure":
            communities = list(greedy_modularity_communities(G))
            for i, comm in enumerate(communities):
                for node in comm: community_map[node] = i
            st.markdown("### 🏘️ Latent Structure")
            st.info("Organic Community Detection active.")

    with col_map:
        # --- RENDER ENGINE ---
        fig = go.Figure()

        # Edges
        ex, ey = [], []
        for u, v in G.edges():
            if tool_category == "Vulnerability Audit" and (u == target_node or v == target_node): continue
            if tool_category == "Geodesic Distance" and (u == geo_obstacle or v == geo_obstacle): continue
            if u in gdf_active['name'].values and v in gdf_active['name'].values:
                p1, p2 = gdf_active[gdf_active['name']==u]['centroid'].values[0], gdf_active[gdf_active['name']==v]['centroid'].values[0]
                ex.extend([p1.x, p2.x, None]); ey.extend([p1.y, p2.y, None])
        fig.add_trace(go.Scatter(x=ex, y=ey, line=dict(width=0.8, color=NETWORK_GREY, dash='dash'), mode='lines', hoverinfo='skip', showlegend=False))

        # Path Highlight
        if active_path:
            px, py = [], []
            for i in range(len(active_path)-1):
                p1, p2 = gdf_active[gdf_active['name']==active_path[i]]['centroid'].values[0], gdf_active[gdf_active['name']==active_path[i+1]]['centroid'].values[0]
                px.extend([p1.x, p2.x, None]); py.extend([p1.y, p2.y, None])
            fig.add_trace(go.Scatter(x=px, y=py, line=dict(width=6, color=PATH_HIGHLIGHT), mode='lines', hoverinfo='skip', showlegend=False))

        # Polygons
        for _, row in gdf_active.iterrows():
            name = row['name']
            x, y = row.geometry.exterior.xy
            color, border_color, border_width = OPUS_BLUE_FILL, OPUS_BLUE_EDGE, 0.8
            hover_text = f"<b>NODE: {name.upper()}</b>" 
            
            # Overview Super-Hover
            if tool_category == "Overview":
                if name in G_giant.nodes():
                    hover_text += f"<br><br>Degree: {deg_cent[name]:.4f}"
                    hover_text += f"<br>Betweenness: {bet_cent[name]:.4f}"
                    hover_text += f"<br>Closeness: {clo_cent[name]:.4f}"
                    hover_text += f"<br>Eigenvector: {eig_cent[name]:.4f}"
                    hover_text += f"<br>Excentricity: {eccentricity[name]} Jumps"
                else:
                    hover_text += "<br><br><i>Disconnected Node</i>"

            elif tool_category == "Vulnerability Audit":
                if name == target_node: color, border_color, border_width = COLLAPSED_COLOR, '#E74C3C', 3
                elif name in islands_map: color, border_color = ISLAND_COLORS[islands_map[name] % len(ISLAND_COLORS)], 'white'
            
            elif tool_category == "Centrality Metrics" and name in current_top_5:
                color, border_color, border_width = HIGHLIGHT_VIOLET, 'white', 2
                hover_text += f"<br><br>Rank: {current_metrics[name]['Rank']} | Score: {current_metrics[name]['Score']}<br>Info: {current_metrics[name]['Info']}"
                
            elif tool_category == "Excentricity" or tool_category == "Geodesic Distance":
                if tool_category == "Excentricity":
                    if excentricity_focus == "Nucleus" and name in center_nodes: color, border_color, border_width = CORE_BLUE, 'white', 2
                    elif excentricity_focus == "Border" and name in periphery_nodes: color, border_color, border_width = BORDER_ORANGE, '#E67E22', 2
                if active_path and name in [active_path[0], active_path[-1]]: color, border_color, border_width = '#FFFFFF', '#333', 3
                elif active_path and name in active_path: color, border_color = HIGHLIGHT_VIOLET, 'white'
                if tool_category == "Geodesic Distance" and name == geo_obstacle: color, border_color, border_width = COLLAPSED_COLOR, '#E74C3C', 3
            elif tool_category == "Latent Structure" and name in community_map:
                color, border_color = COMMUNITY_COLORS[community_map[name] % len(COMMUNITY_COLORS)], 'white'

            fig.add_trace(go.Scatter(x=list(x), y=list(y), fill="toself", mode='lines', fillcolor=color, line=dict(color=border_color, width=border_width), text=hover_text, hoverinfo="text", showlegend=False))

        # Labels & Layout
        fig.add_trace(go.Scatter(x=gdf_active['centroid'].apply(lambda p: p.x), y=gdf_active['centroid'].apply(lambda p: p.y), mode='text', text=gdf_active['name'].str.replace('_', '<br>'), textfont=dict(size=7, color="#4B5563" if tool_category != "Vulnerability Audit" else "white", family="Arial Black"), hoverinfo='skip', showlegend=False))
        fig.update_layout(plot_bgcolor='white', showlegend=False, height=800, margin=dict(l=0, r=0, t=0, b=0), dragmode='pan', xaxis=dict(visible=False, fixedrange=False), yaxis=dict(visible=False, fixedrange=False, scaleanchor="x", scaleratio=1))
        
        st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# CHUNK 4.5: TAB 2 - TENSOR GLOBAL (PYDECK MVP)
# ==============================================================================
with tab_tensor_global:
    st.markdown("### 🌍 Observatorio del Tensor Global (PyDeck)")
    st.markdown("Aislando la Telaraña de Vectores: Flujos de capital y volumen.")



    # ==============================================================================
    # 1. UI CONTROLS & DATA FILTERING (SMART SUB-FILTERS - 100% ENGLISH)
    # ==============================================================================
    
    if 'sel_origin' not in st.session_state:
        st.session_state.sel_origin = 'lomas_virreyes'
    if 'sel_metric' not in st.session_state:
        st.session_state.sel_metric = '---'

    def update_origin():
        if st.session_state.sel_origin != '---':
            st.session_state.sel_metric = '---' 

    def update_metric():
        if st.session_state.sel_metric != '---':
            st.session_state.sel_origin = '---' 

    zones_available = sorted(df_arcos_pd['origen_id'].unique())
    origin_options = ['---'] + zones_available
    
    metric_mapping = {
        "Flow Sovereignty (PageRank)": "edge_pagerank",
        "Connector Power (Betweenness)": "edge_betweenness",
        "Economic Proximity (Closeness)": "edge_closeness"
    }
    metric_options = ['---'] + list(metric_mapping.keys())

    st.selectbox("🎯 Isolate Origin:", origin_options, key='sel_origin', on_change=update_origin)
    st.selectbox("📈 Centrality Leaders:", metric_options, key='sel_metric', on_change=update_metric)

    # --- FILTERING LOGIC ---
    if st.session_state.sel_metric != '---':
        # CENTRALITY LEADERS LOGIC
        active_metric = metric_mapping[st.session_state.sel_metric]
        color_metric = active_metric 
        
        # 1. Calculate the Top 3 Origins DYNAMICALLY
        top_3_origins = df_arcos_pd.groupby('origen_id')[active_metric].max().nlargest(3).index.tolist()
        
        # 2. Render the "Smart" Sub-filter UI (With 'All' option as default)
        radio_options = ["🌟 All Top 3 Leaders"] + top_3_origins
        selected_leader = st.radio(
            "👑 Inspect Leader Node:", 
            options=radio_options,
            horizontal=True
        )
        
        # 3. Extract edges based on the sub-filter selection
        if selected_leader == "🌟 All Top 3 Leaders":
            frames = []
            for origin in top_3_origins:
                top_edges = df_arcos_pd[df_arcos_pd['origen_id'] == origin].nlargest(5, active_metric)
                frames.append(top_edges)
            df_filtrado = pd.concat(frames).copy()
        else:
            # Only show the 5 edges for the specifically selected leader
            df_filtrado = df_arcos_pd[df_arcos_pd['origen_id'] == selected_leader].nlargest(5, active_metric).copy()

    else:
        # SINGLE ORIGIN LOGIC
        target = st.session_state.sel_origin if st.session_state.sel_origin != '---' else 'lomas_virreyes'
        color_metric = 'volumen_historico' 
        
        df_filtrado = df_arcos_pd[df_arcos_pd['origen_id'] == target].nlargest(15, 'volumen_historico').copy()

    # ==============================================================================
    # 2. DYNAMIC STYLE ENGINE (ABSOLUTE SCALING FIX)
    # ==============================================================================
    # We now calculate the min and max from the GLOBAL dataframe (df_arcos_pd),
    # not the filtered one. This prevents colors from resetting when isolating a node.
    v_min = df_arcos_pd[color_metric].min()
    v_max = df_arcos_pd[color_metric].max()

    def calculate_color(val):
        paleta = [
            [255, 195, 0, 200],  # 0: Yellow
            [239, 145, 0, 200],  # 1: Light Orange
            [214, 97, 10, 200],  # 2: Orange
            [183, 47, 21, 200],  # 3: Red-Orange
            [136, 0, 48, 200],   # 4: Dark Red
            [76, 0, 53, 200]     # 5: Purple/Black
        ]
        if v_max == v_min: return paleta[5] 
        
        # Calculate ratio and ensure it strictly stays between 0.0 and 1.0
        ratio = max(0.0, min(1.0, (val - v_min) / (v_max - v_min)))
        idx = int(ratio * 5.99) 
        return paleta[idx]

    def calculate_width(val):
        if v_max == v_min: return 5 
        ratio = max(0.0, min(1.0, (val - v_min) / (v_max - v_min)))
        return 3 + (8 * ratio)

    # Inject visual columns based on the ABSOLUTE metric
    df_filtrado['color_arco'] = df_filtrado[color_metric].apply(calculate_color)
    df_filtrado['ancho_arco'] = df_filtrado[color_metric].apply(calculate_width)


    # ==============================================================================
    # 2.5 DYNAMIC POLYGON HIGHLIGHTING & LABELS (Dark Origin & Z-Fighting Fix)
    # ==============================================================================
    active_origins = df_filtrado['origen_id'].unique().tolist()
    active_destinations = df_filtrado['destino_id'].unique().tolist()

    def get_poly_color(zone_name):
        if zone_name in active_origins:
            # Origin Node: Darker, solid gray
            return [100, 100, 100, 220] 
        elif zone_name in active_destinations:
            # Destination Node: Lighter, transparent gray
            return [170, 170, 170, 160]
        else:
            # Background Nodes: Faint, almost invisible gray
            return [230, 230, 230, 60] 

    gdf_poly_pd['fill_color'] = gdf_poly_pd['name'].apply(get_poly_color)

    # 3. Create Labels DataFrame
    active_nodes = set(active_origins + active_destinations)
    gdf_active_poly = gdf_poly_pd[gdf_poly_pd['name'].isin(active_nodes)]

    df_labels = pd.DataFrame({
        'nombre': gdf_active_poly['name'].astype(str).str.lower(),
        'lon': gdf_active_poly.geometry.centroid.x,
        'lat': gdf_active_poly.geometry.centroid.y
    }).dropna()




    # ==============================================================================
    # 2.8 DYNAMIC MAP LEGEND (Explains the color scale to the user)
    # ==============================================================================
    # Map the internal metric name back to a readable UI title
    legend_titles = {
        'volumen_historico': 'Historical Volume',
        'edge_pagerank': 'Flow Sovereignty (PageRank)',
        'edge_betweenness': 'Connector Power (Betweenness)',
        'edge_closeness': 'Economic Proximity (Closeness)'
    }
    
    active_title = legend_titles.get(color_metric, 'Active Metric')
    
    # Render an elegant HTML legend with a CSS gradient matching your PyDeck palette
    legend_html = f"""
    <div style="background-color: rgba(240, 242, 246, 0.5); padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e0e0e0;">
        <p style="margin-top: 0px; margin-bottom: 8px; font-weight: 600; color: #31333F; font-size: 14px;">
            🎨 Visualizing: <span style="color: #FF4B4B;">{active_title}</span>
        </p>
        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: #555;">
            <span style="font-weight: bold;">Low</span>
            <div style="flex-grow: 1; height: 12px; margin: 0 15px; border-radius: 6px; 
                        background: linear-gradient(to right, 
                        rgb(255, 195, 0), 
                        rgb(239, 145, 0), 
                        rgb(214, 97, 10), 
                        rgb(183, 47, 21), 
                        rgb(136, 0, 48), 
                        rgb(76, 0, 53));">
            </div>
            <span style="font-weight: bold;">High</span>
        </div>
    </div>
    """
    
    # Display the legend in Streamlit
    st.markdown(legend_html, unsafe_allow_html=True)



    

    # ==============================================================================
    # 3. PYDECK LAYER CONSTRUCTION
    # ==============================================================================
    layer_poly = pdk.Layer(
        "GeoJsonLayer",
        gdf_poly_pd,
        opacity=0.8,
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color="fill_color",         
        get_line_color=[85, 85, 85, 150],    # Softer borders
        get_line_width=15,                   
    )

    # (Your layer_arcos remains the same here)
    layer_arcos = pdk.Layer(
        "ArcLayer",
        data=df_filtrado,
        get_source_position=["start_lon", "start_lat"],
        get_target_position=["end_lon", "end_lat"],
        get_source_color="color_arco",
        get_target_color="color_arco",
        get_width="ancho_arco",
        auto_highlight=True,
        pickable=True, 
    )

    # Bulletproof TextLayer (Scales with zoom, only on active nodes)
    layer_text = pdk.Layer(
        "TextLayer",
        data=df_labels,
        get_position=["lon", "lat"],
        get_text="nombre",
        get_size=350,                  
        size_units="meters",           
        size_min_pixels=0,             
        size_max_pixels=14,            
        get_color=[40, 40, 40, 255],   # Darkest gray for maximum readability
        parameters={"depthTest": False} # <--- EL HACK: Forza a renderizar sobre los polígonos
    )

    view_state = pdk.ViewState(
        latitude=19.4093,
        longitude=-99.2423,
        zoom=13,
        pitch=50,
        bearing=0
    )

    tooltip = {
        "html": """
        <b>Trayecto:</b> {origen_id} → {destino_id} <br/>
        <b>Volumen:</b> {volumen_historico} <br/>
        <b>Soberanía (PageRank):</b> {edge_pagerank:.4f} <br/>
        <b>Poder Conector:</b> {edge_betweenness:.4f}
        """,
        "style": {"backgroundColor": "#2C3E50", "color": "white"}
    }

# ==============================================================================
    # 4. RENDERIZADO CON MAPBOX NATIVO (El fondo del Screenshot)
    # ==============================================================================
    
    # Pega tu token NUEVO y sin restricciones aquí:
    TOKEN_MAPBOX = "pk.eyJ1IjoiYmVybmFyZG9sdzg4IiwiYSI6ImNtcDMxcmphZjBtM3Eyc3Bwemc2OHhmbHIifQ.nRURL7plankvRicGkLIKDQ"

    r = pdk.Deck(
        layers=[layer_poly, layer_arcos, layer_text], # <- Aquí está la capa añadida
        initial_view_state=view_state,
        map_provider="mapbox", 
        map_style="mapbox://styles/mapbox/light-v11",
        api_keys={"mapbox": TOKEN_MAPBOX}, 
        tooltip=tooltip
    )

    st.pydeck_chart(r, use_container_width=True, height=850)


# ==========================================
# CHUNK 5: TAB 3 - MOBILITY TENSOR (LIVE SLICING)
# ==========================================
with tab_tensor_live:
    st.markdown("### 📈 Análisis de Dinámica de Flujos (Mobility Tensor)")
    st.markdown("Corta el tensor multidimensional para observar cómo mutan los flujos de capital según el día y la hora.")
    
    # --- 1. LAYOUT HORIZONTAL (CONTROLES ARRIBA) ---
    st.markdown("#### 🎛️ Panel de Control de Flujos")
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    
    with ctrl_col1:
        tensor_day = st.selectbox("📅 Día de la Semana:", 
                                  ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    with ctrl_col2:
        tensor_hour = st.slider("⏰ Hora del Día:", min_value=5, max_value=22, value=14, step=1, format="%d:00")
    with ctrl_col3:
        tensor_metric = st.selectbox("Lente Analítico:", 
                                     ["EPH Bruto (Rentabilidad)", "Asimetría (Fuentes vs Sumideros)", "Prestigio (HITS Authority)"])
    with ctrl_col4:
        # Filtro para limpiar el ruido visual y dejar solo las "Autopistas"
        edge_threshold = st.slider("Umbral de Flujo (Filtrar Ruido):", min_value=0, max_value=100, value=25, 
                                   help="Oculta las aristas con peso relativo menor a este porcentaje.")

    st.divider()

    # --- 2. ÁREA DEL MAPA (ABAJO) ---
    st.markdown(f"**Visualizando:** Flujos de las `{tensor_hour}:00 hrs` del `{tensor_day}`")
    
    G_dir = nx.DiGraph()
    G_dir.add_nodes_from(G_giant.nodes())
    # Simulamos un flujo dirigido (Solo el 30% de las calles físicas tienen flujo rentable en esta hora)
    import random
    for u, v in G_giant.edges():
        if random.random() > (edge_threshold / 100.0):
            # Asignamos pesos aleatorios para simular el EPH
            G_dir.add_edge(u, v, weight=random.uniform(50, 300))
            if random.random() > 0.5: # Flujo bidireccional asimétrico
                G_dir.add_edge(v, u, weight=random.uniform(50, 300))

    # --- 3. MOTOR DE RENDERIZADO (GRAFO DIRIGIDO) ---
    fig_tensor = go.Figure()

    # A. Dibujar las Aristas (Vectores de Flujo)
    edge_x, edge_y, edge_weights = [], [], []
    for u, v, data in G_dir.edges(data=True):
        if u in gdf_active['name'].values and v in gdf_active['name'].values:
            p1 = gdf_active[gdf_active['name']==u]['centroid'].values[0]
            p2 = gdf_active[gdf_active['name']==v]['centroid'].values[0]
            
            # Líneas base
            edge_x.extend([p1.x, p2.x, None])
            edge_y.extend([p1.y, p2.y, None])
            
            # Opcional en Plotly: Añadir flechas mediante annotations
            fig_tensor.add_annotation(
                x=(p1.x + p2.x)/2, y=(p1.y + p2.y)/2,
                ax=p1.x, ay=p1.y,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=1.5, arrowcolor='rgba(41, 128, 185, 0.4)'
            )

    fig_tensor.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='rgba(189, 195, 199, 0.3)'),
        mode='lines', hoverinfo='none', showlegend=False
    ))

    # B. Dibujar los Nodos (Polígonos)
    for _, row in gdf_active.iterrows():
        name = row['name']
        x, y = row.geometry.exterior.xy
        
        # Color dinámico basado en el lente analítico seleccionado
        node_color = OPUS_BLUE_FILL
        hover_text = f"<b>{name.replace('_', ' ').upper()}</b>"
        
        if tensor_metric == "Asimetría (Fuentes vs Sumideros)":
            asimetria = random.uniform(-1, 1) 
            if asimetria > 0.2: node_color = '#A9DFBF' # Verde suave (Fuente)
            elif asimetria < -0.2: node_color = '#F5B7B1' # Rojo suave (Sumidero)
            hover_text += f"<br>Índice de Asimetría: {asimetria:+.2f}"
            
        elif tensor_metric == "Prestigio (HITS Authority)":
            auth = random.uniform(0, 1)
            if auth > 0.8: node_color = '#D2B4DE' # Morado (Apex)
            hover_text += f"<br>Authority Score: {auth:.2f}"

        fig_tensor.add_trace(go.Scatter(
            x=list(x), y=list(y),
            fill="toself", fillcolor=node_color,
            mode='lines', line=dict(color=OPUS_BLUE_EDGE, width=0.8),
            text=hover_text, hoverinfo="text", showlegend=False
        ))

    # C. Etiquetas de texto
    fig_tensor.add_trace(go.Scatter(
        x=gdf_active['centroid'].apply(lambda p: p.x), 
        y=gdf_active['centroid'].apply(lambda p: p.y), 
        mode='text', text=gdf_active['name'].str.replace('_', '<br>'), 
        textfont=dict(size=7, color="#2C3E50", family="Arial Black"), 
        hoverinfo='skip', showlegend=False
    ))

    fig_tensor.update_layout(
        plot_bgcolor='white', showlegend=False, height=750, 
        margin=dict(l=0, r=0, t=0, b=0), dragmode='pan',
        xaxis=dict(visible=False, fixedrange=False), 
        yaxis=dict(visible=False, fixedrange=False, scaleanchor="x", scaleratio=1)
    )
    
    st.plotly_chart(fig_tensor, use_container_width=True)