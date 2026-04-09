import streamlit as st
import pandas as pd
import geopandas as gpd
import networkx as nx
import plotly.graph_objects as go
from networkx.algorithms.community import greedy_modularity_communities
from shapely.affinity import translate
from pathlib import Path

# --- 1. PIENZA CANON CONFIGURATION ---
st.set_page_config(layout="wide")

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

# --- 2. DATA LOAD ---
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

# --- 3. ROUTES DATA ---
ROUTES = [['anzures', 'polanco_gandhi', 'polanco_parque_lincoln', 'lomas_virreyes', 'lomas_trastevere', 'nodo_reforma_palmas', 'reforma_regina', 'lomas_altas'], ['anzures', 'rios', 'juarez_rosa', 'bosque_1', 'bosque_2', 'bosque_3', 'lomas_altas', 'reforma_bnp', 'sante_fe_patio', 'santa_fe_quintana'], ['anzures', 'polanco_5', 'polanco_parroquia', 'polanco_palacio', 'polanco_uber_hq', 'palmas_jp_morgan', 'fuentes_casino', 'nodo_monte_libano', 'nodo_reforma_palmas'], ['lomas_barrilaco','lomas_olimpo', 'lomas_prado_norte'], ['lomas_virreyes', 'campo_marte', 'polanco_parque_lincoln'], ['carso_antara_miyana', 'polanco_palacio', 'polanco_grupo_mexico', 'polanco_parque_lincoln', 'lomas_virreyes', 'lomas_fc_cuernavaca', 'lomas_prado_norte', 'lomas_barrilaco', 'nodo_reforma_palmas' ], ['juarez_soho_house', 'juarez_rosa', 'rios', 'bahias', 'anahuac_1', 'lagos', 'carso_antara_miyana', 'irrigacion', 'sotelo', 'herradura_conscripto', 'interlomas_magnocentro', 'bosque_real'], ['roma_condesa_2', 'roma_condesa_1', 'juarez_rosa', 'anzures', 'polanco_5', 'polanco_parroquia', 'polanco_palacio', 'polanco_uber_hq', 'sedena', 'reforma_social', 'fuentes_casino', 'de_las_fuentes', 'de_los_bosques', 'universidad_anahuac', 'interlomas_magnocentro', 'vialidad_de_la_barranca', 'ave_club_de_golf_lomas', 'lomas_country_club'], ['herradura_conscripto', 'de_las_fuentes'], ['herradura_conscripto', 'universidad_anahuac'], ['jesus_del_monte', 'interlomas_haciendas', 'vialidad_de_la_barranca', 'carretera_al_olivo', 'cruce_echanove', 'santa_fe_centro_comercial', 'santa_fe_colegios', 'santa_fe_cumbres_de'], ['santa_fe_bosques_de', 'santa_fe_centro_comercial'], ['nodo_reforma_palmas', 'ahuehuetes_norte', 'ahuehuetes_sur', 'tamarindos', 'santa_fe_ibero', 'santa_fe_centro_comercial', 'cruce_echanove', 'carretera_libre','agwa_bezares', 'reforma_bnp'], ['santa_fe_tec', 'santa_fe_ibero', 'santa_fe_colegios', 'santa_fe_tec'], ['carretera_libre', 'vistahermosa', 'cruce_echanove', 'carretera_al_olivo', 'loma_de_la_palma', 'bosques_pabellon', 'de_los_bosques', 'universidad_anahuac', 'blvrd_anahuac', 'el_olivo', 'vialidad_de_la_barranca'], ['jesus_del_monte', 'herradura_conscripto'], ['interlomas_magnocentro', 'jesus_del_monte'], ['vistahermosa', 'bosques_pabellon', 'loma_de_la_palma', 'el_olivo'], ['blvrd_anahuac', 'interlomas_magnocentro'], ['santa_fe_ibero', 'sante_fe_patio'], ['tamarindos', 'ahuehuetes_sur', 'bosques_pabellon', 'ahuehuetes_norte', 'de_los_bosques'], ['ahuehuetes_norte', 'de_las_fuentes', 'tecamachalco', 'fuentes_casino', 'lomas_barrilaco'], ['lomas_prado_norte', 'fuentes_casino', 'palmas_jp_morgan', 'lomas_fc_cuernavaca'], ['bosques_pabellon', 'tamarindos', 'agwa_bezares'], ['reforma_social','herradura_conscripto'], ['irrigacion', 'sedena', 'sotelo'], ['bondojito_asf', 'bosque_3'], ['irrigacion', 'polanco_uber_hq', 'polanco_grupo_mexico', 'palmas_jp_morgan'], ['carso_antara_miyana','frontera_polanco', 'lagos', 'polanco_parroquia', 'polanco_parque_lincoln'], ['frontera_polanco', 'anahuac_1'], ['lomas_virreyes', 'bosque_2', 'campo_marte', 'bosque_1', 'polanco_gandhi', 'polanco_5', 'lagos'], ['bahias', 'anzures', 'anahuac_1'], ['bosque_2','roma_condesa_2', 'bosque_1'], ['rios', 'juarez_soho_house', 'roma_condesa_2'], ['lomas_altas', 'nodo_reforma_palmas', 'bosque_3', 'lomas_trastevere'], ['fuentes_casino', 'palmas_jp_morgan', 'lomas_prado_norte', 'lomas_trastevere', 'lomas_barrilaco', 'nodo_monte_libano', 'de_las_fuentes']]

centrality_data = {
    "Degree": {"nodo_reforma_palmas": {"Rank": 1, "Score": 0.0985, "Info": "Maximum physical permeability."}, "fuentes_casino": {"Rank": 2, "Score": 0.0985, "Info": "Highest level of local routing options."}, "de_las_fuentes": {"Rank": 3, "Score": 0.0845, "Info": "Strong secondary distributor (NW)."}, "anzures": {"Rank": 4, "Score": 0.0845, "Info": "Main distribution hub (East/Center)."}, "lomas_prado_norte": {"Rank": 5, "Score": 0.0845, "Info": "Key hub within the Lomas cluster."}},
    "Betweenness": {"nodo_reforma_palmas": {"Rank": 1, "Score": 0.2054, "Info": "Controls 20.5% of optimal network paths."}, "bosque_3": {"Rank": 2, "Score": 0.1958, "Info": "Vital bridge connecting the deep west."}, "herradura_conscripto": {"Rank": 3, "Score": 0.1956, "Info": "Critical funnel; high risk of isolation."}, "ahuehuetes_norte": {"Rank": 4, "Score": 0.1823, "Info": "Main connector in the NW corridor."}, "bosque_2": {"Rank": 5, "Score": 0.1700, "Info": "Critical link in the topographic forests chain."}},
    "Closeness": {"ahuehuetes_norte": {"Rank": 1, "Score": 0.2795, "Info": "Topologically most central zone."}, "nodo_reforma_palmas": {"Rank": 2, "Score": 0.2784, "Info": "Exact center of gravity."}, "de_las_fuentes": {"Rank": 3, "Score": 0.2699, "Info": "Highly efficient dispatch point."}, "bosque_3": {"Rank": 4, "Score": 0.2619, "Info": "Strategic bridge and central node."}, "fuentes_casino": {"Rank": 5, "Score": 0.2610, "Info": "Central and highly connected to exits."}},
    "Eigenvector": {"lomas_barrilaco": {"Rank": 1, "Score": 0.3424, "Info": "The most influential node; neighbor to power."}, "fuentes_casino": {"Rank": 2, "Score": 0.3367, "Info": "Positioned within the elite mesh."}, "nodo_reforma_palmas": {"Rank": 3, "Score": 0.3091, "Info": "Maintains elite influence status."}, "lomas_prado_norte": {"Rank": 4, "Score": 0.3038, "Info": "Lomas-Palmas cluster dominance."}, "lomas_trastevere": {"Rank": 5, "Score": 0.2728, "Info": "High neighbor interconnectivity."}}
}

# --- 4. GRAPH CONSTRUCTION & ON-THE-FLY METRICS ---
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

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("Network Tools")
    tool_category = st.selectbox("Select Category:", ["Overview", "Small World Theory", "Centrality Metrics", "Vulnerability Audit", "Excentricity", "Geodesic Distance", "Latent Structure"])
    
    metric_choice, target_node, excentricity_focus, geo_source, geo_target, geo_obstacle = None, None, None, None, None, "None"
    
    if tool_category == "Centrality Metrics":
        metric_choice = st.selectbox("Metric:", ["Degree", "Betweenness", "Closeness", "Eigenvector"])
    elif tool_category == "Vulnerability Audit":
        st.subheader("Collapse Simulator")
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

# --- 6. PAGE LOGIC ---
st.title("🕸️ Phase 2: Topological Graph Analysis")

current_top_5, islands_map, community_map, active_path = [], {}, {}, []
center_nodes = nx.center(G_giant)
periphery_nodes = nx.periphery(G_giant)

if tool_category == "Overview":
    st.markdown("### 🗺️ Network Overview")
    st.info("Hover over any node to view its complete topological profile.")

elif tool_category == "Small World Theory":
    st.markdown("### 📊 Small-World Hypothesis Test")
    st.success("🏆 **VERDICT: The Pienza infrastructure IS A SMALL-WORLD.**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sigma (σ)", "4.9297"); c2.metric("Omega (ω)", "-0.3009")
    c3.metric("Clustering (C)", "0.2677"); c4.metric("Path Length (L)", "4.8052")

elif tool_category == "Centrality Metrics":
    st.markdown(f"### 👑 Top Nodes: {metric_choice} Centrality")
    current_metrics = centrality_data[metric_choice]
    current_top_5 = list(current_metrics.keys())
    df_display = pd.DataFrame.from_dict(current_metrics, orient='index').sort_values('Rank')
    st.dataframe(df_display, use_container_width=True)

elif tool_category == "Vulnerability Audit":
    G_sim = G.copy()
    G_sim.remove_node(target_node)
    islands = sorted(list(nx.connected_components(G_sim)), key=len, reverse=True)
    st.markdown(f"### 🚨 Damage Report: Collapse at '{target_node.upper()}'")
    st.markdown(f"> The network fragmented into **{len(islands)} independent islands**.")
    for i, island in enumerate(islands):
        for node in island: islands_map[node] = i

elif tool_category == "Excentricity":
    st.markdown("### 🌍 Excentricity Report")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Density", f"{nx.density(G):.4f}"); c2.metric("Diameter", nx.diameter(G_giant))
    c3.metric("Radius", nx.radius(G_giant)); c4.metric("Avg. Distance", f"{nx.average_shortest_path_length(G_giant):.2f}")
    if excentricity_focus == "Diameter in Action":
        start_node = periphery_nodes[0]
        path_dict = nx.single_source_shortest_path(G_giant, start_node)
        active_path = path_dict[max(path_dict, key=lambda k: len(path_dict[k]))]
    elif excentricity_focus == "Radius in Action":
        start_node = center_nodes[0]
        path_dict = nx.single_source_shortest_path(G_giant, start_node)
        active_path = path_dict[[n for n, p in path_dict.items() if len(p)-1 == nx.radius(G_giant)][0]]

elif tool_category == "Geodesic Distance":
    st.markdown(f"### 📍 Navigator: Shortest Path Analysis")
    G_temp = G_giant.copy()
    if geo_obstacle != "None": G_temp.remove_node(geo_obstacle)
    try:
        active_path = nx.shortest_path(G_temp, source=geo_source, target=geo_target)
        st.metric("Geodesic Path Length", f"{len(active_path)-1} Jumps")
    except nx.NetworkXNoPath: st.error("No path exists.")

elif tool_category == "Latent Structure":
    communities = list(greedy_modularity_communities(G))
    for i, comm in enumerate(communities):
        for node in comm: community_map[node] = i
    st.markdown("### 🏘️ Latent Structure: Organic Community Detection")

# --- 7. RENDER ENGINE ---
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
    
    # NEW: Overview Super-Hover
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