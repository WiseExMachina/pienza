import streamlit as st
import pandas as pd
import geopandas as gpd
import networkx as nx
import plotly.graph_objects as go
from networkx.algorithms.community import greedy_modularity_communities
from shapely.affinity import translate
from pathlib import Path

import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Bridge to Markov: Graph Tensor",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# CUSTOM FONT & SIZE INJECTION (SAFE VERSION)
# ==========================================
st.markdown("""
    <style>
        /* Import Crimson Pro (Serif) and Inter (Sans-Serif) from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');
        
        /* 1. Body Text (Crimson Pro) - Target semantic content tags only! */
        p, li, td, th {
            font-family: 'Crimson Pro', serif !important;
            font-size: 18px !important;  
            line-height: 1.6 !important; 
        }

        /* 2. Headers Base Setup (Inter) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }

        /* 2a. Individual Header Sizes */
        h1 { font-size: 38px !important; } 
        h2 { font-size: 28px !important; } 
        h3 { font-size: 22px !important; } 

        /* 3. Expander Headers (Force them to match H3 Inter styling) */
        [data-testid="stExpander"] details summary p {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }

        /* 4. Code Blocks & Terminal (Monospace) */
        code, pre {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 15px !important; 
        }
    </style>
""", unsafe_allow_html=True)











# ==========================================
# 1. NETWORK GRAPH ANALYSIS: AV SANDBOX (Non-Collapsible Intro)
# ==========================================
st.header("Network Graph Analysis: A Sandbox for Autonomous Vehicles")

st.markdown("""
The final technical module of the Pienza framework transitions from retrospective row-wise analysis to forward-looking graph-based intelligence. In this stage, the network is no longer conceptualized as a record of human labor, but as a **high-fidelity sandbox for Autonomous Vehicle (AV) fleet prototyping**. By treating Pienza as a strictly **geofenced sovereign ecosystem**, the study evaluates the viability of autonomous agents operating within a closed-loop urban environment.
""")

st.markdown("""
The network analysis establishes the **Bridge to Markov** for autonomous navigation by applying the *Bellman Equation* to the internal mobility tensor. By calculating the **State-Value Function** ($V(s)$), the framework transforms the geofenced urban grid into a series of interconnected decision nodes. This enables the derivation of a prescriptive $Q$-Matrix policy, allowing a prototype autonomous fleet to execute optimized five-jump mission sequences that prioritize long-term economic sovereignty over myopic fare-chasing. 
""")

st.info("""
**Strategic Boundary:** It must be explicitly noted that a **Stationary MDP** is a static approximation of a non-linear, time-variant system. While this model provides a robust steady-state baseline for strategic positioning, it remains a necessary oversimplification of the high-frequency volatility that a full-scale **Markov Chain Monte Carlo (MCMC)** simulation or a dynamic **Reinforcement Learning (RL)** agent would encounter. 

Consequently, the **Generative Moonshot** phase concludes here: it does not attempt to execute dynamic learning or stochastic sampling. Instead, it successfully delivers the **functional scaffolding**—mathematically defining the state space ($\\mathcal{S}$), transition probabilities ($\\mathcal{P}$), and reward manifolds ($\\mathcal{R}$)—required to transition from descriptive science to autonomous execution in *Pienza 2.0: The Knowledge*.
""")

# ==========================================
# TABS ARCHITECTURE
# ==========================================
tab_topology, tab_tensor, tab_markov = st.tabs([
    "🕸️ Topological Undirected Graph", 
    "📈 Mobility Tensor: Flow & State", 
    "🤖 Bridge to Markov: AV Sandbox"
])

# ==========================================
# TAB 1: TOPOLOGICAL UNDIRECTED GRAPH
# ==========================================
with tab_topology:
    
    with st.expander("Base Topology: The Geofence Blueprint", expanded=False):

        st.markdown("""
        To define the physical boundaries and navigational constraints of the **Autonomous Sovereign Zone**, a custom undirected graph was architected using `networkX`. This model serves as the **Geofence Blueprint**, transforming the 72 geographic polygons into discrete schematic nodes where an edge exists strictly if a verified, viable road path connects the two areas.
        """)

        # Figure: Base Topology (Using absolute path directly)
        try:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_base_topology.png")
            st.caption("**Figure:** Base Topology: Undirected Graph with 'Bubble Effect' Visualization. Nodes represent atomic operational units; edges indicate the **allowed traversal paths** for a prototype autonomous fleet. The graph highlights the non-Euclidean nature of the city, where geographic proximity does not guarantee topological access.")
        except Exception as e:
            st.error("Image not found: fig_base_topology.png")

        st.markdown("""
        ---
        ### Connectivity Logic & Constraints

        The graph was manually crafted based on the Agent’s ground-truth street exploration, prioritizing real-world traversal over official cadastral data. The connectivity logic follows two primary mandates essential for autonomous fleet logic:

        * **Topological Friction and Labyrinths:** While the grid-based layout of *Polanco* facilitates linear navigation, sectors such as *Interlomas, Lomas,* and *Santa Fe* exhibit high topological complexity. In these zones, geographic proximity is a misleading metric; adjacent polygons often lack viable road connections due to topographic barriers (ravines), creating "labyrinth-like" detours. This model forces the AV agent to account for **Topological Distance** rather than Euclidean radius, directly impacting search and positioning efficiency.
        * **Boundary Integrity and Access Constraints:** The geofence blueprint explicitly excludes restricted-access connectors (resident-only gates), reflecting the **logical barriers** encountered in the field. By modeling specific gaps where road access is denied to third-party agents—such as the boundaries between *Jesús del Monte – Lomas Country Club* and *Blvrd Anáhuac – Vialidad de la Barranca*—the graph ensures that the autonomous simulation respects the actual sovereignty of the urban terrain.
        """)
        
        st.info("""
        **Architectural Note:** This undirected graph represents a **pure topological skeleton** modeled as a **strictly closed system**. It contains no transactional data, mission volumes, or financial weights. The objective is to establish the **Hardware Layer** of the ecosystem—the physical baseline of the 72 polygons—before projecting the **Software Layer**: the economic forces and stochastic pressures of the internal mobility tensor.
        """)


import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 1: TOPOLOGICAL UNDIRECTED GRAPH (Continued)
# ==========================================
with tab_topology:
    
    with st.expander("Morphological Analysis: Small-World Dynamics", expanded=False):

        st.markdown("""
        To assess the structural efficiency of the network, the study utilized the **Watts-Strogatz** framework to evaluate the balance between local redundancy (cluster density) and global reachability (long-range shortcuts). The results mathematically certify the Pienza operational environment as a high-efficiency **Small-World Network**.
        
        > **Architectural Caveat (Efficiency):** Efficiency is defined here strictly by topological connectivity. While the network structure facilitates rapid navigation under fluid conditions, systemic gridlock effectively neutralizes these advantages, transforming the connected graph into a static, high-friction state.
        """)

        # ------------------------------------------
        # Table A: Macro-Dimensions
        # ------------------------------------------
        st.markdown("### 1. Macro-Dimensions")
        
        macro_data = {
            "Metric": ["Network Density", "Network Diameter", "Network Radius"],
            "Value": ["0.053", "11 Jumps", "7 Jumps"],
            "Operational Interpretation": [
                "**Arterial Infrastructure:** Connectivity is concentrated on primary transit veins rather than a uniform grid, reflecting urban geographic constraints.",
                "**Maximum Friction:** The longest shortest path across the theatre, representing the travel limit between extreme poles.",
                "**Reachability Limit:** The maximum distance from the topological center to the farthest peripheral node."
            ]
        }
        df_macro = pd.DataFrame(macro_data)
        st.markdown(df_macro.to_markdown(index=False))

        # ------------------------------------------
        # Table B: Watts-Strogatz Coefficients
        # ------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 2. Watts-Strogatz Small-World Coefficients")
        
        ws_data = {
            "Metric": ["Transitivity ($C$)", "Avg. Path Length ($L$)", "Sigma ($\sigma$)", "Omega ($\omega$)"],
            "Value": ["0.2677", "4.8052", "4.1137", "-0.2740"],
            "Operational Interpretation": [
                "**Local Redundancy:** High for an urban network; indicates a 27% probability of triangular connectivity between adjacent nodes for alternate routing.",
                "**Global Efficiency:** High theoretical reachability; any zone is accessible within a median of 4.8 topological transitions.",
                "**Small-World Proof:** Since $\sigma > 1$, the network is mathematically certified. It exhibits local clustering significantly superior to a random graph.",
                "**Structural Balance:** A value near zero indicates an optimized topology supported by 'shortcuts' (*e.g., bridges*) that bypass local impediments."
            ]
        }
        df_ws = pd.DataFrame(ws_data)
        st.markdown(df_ws.to_markdown(index=False))

        st.caption("**Table 1:** Consolidated structural and morphological metrics of the Pienza undirected graph.")

        st.markdown("""
        ---
        The **Sigma ($\sigma = 4.11$)** result confirms that while the western sector of Mexico City appears fragmented by complex terrain, it is topologically optimized for rapid traversal via strategic shortcuts. This structural baseline ensures high system liquidity, provided that traffic conditions do not collapse into a zero-velocity state.
        """)







        import streamlit as st
import pandas as pd

# ==========================================
# TAB 1: TOPOLOGICAL UNDIRECTED GRAPH (Continued)
# ==========================================
with tab_topology:
    
    with st.expander("Centrality & Vulnerability Analysis", expanded=False):

        st.markdown("""
        ### Centrality Assessment: The Operational Hierarchy
        
        Identifying the nodes that govern network flow and structural vulnerability establishes a formal hierarchy of the operational environment. The diagnostic review identifies an absolute **Super-Node**: `reforma_palmas`. It is the only zone to rank in the top five across all centrality categories, serving as the primary distributive hub, the system's center of gravity, and its critical transit axis.
        """)

        # ------------------------------------------
        # Table A: Centrality Summary
        # ------------------------------------------
        centrality_data = {
            "Zone Name": ["`reforma_palmas`", "`lomas_barrilaco`", "`ahuehuetes_norte`", "`herradura_conscripto`", "`fuentes_casino`"],
            "Metric Type": ["All (Leader)", "Eigenvector", "Closeness", "Betweenness", "Degree"],
            "Hierarchy Role": ["**Super-Node**", "**Elite Influence**", "**System Center**", "**Critical Bridge**", "**Tactical Hub**"],
            "Operational Significance": [
                "Controls 20.5% of all optimal routing paths; the absolute distributive hub.",
                "Maximum influence through proximity to high-power neighbors (*The Power Mesh*).",
                "Containing the 'Glorieta de los Ahuehuetes' (roundabout), this is the most central node; minimizes transitions to all other zones.",
                "High-vulnerability bottleneck; lacks redundant routing for peripheral access.",
                "Maximum local permeability; provides the highest volume of immediate routing options."
            ]
        }
        df_centrality = pd.DataFrame(centrality_data)
        st.markdown(df_centrality.to_markdown(index=False))
        st.caption("**Table:** Topological Hierarchy Summary: Primary actors within the structural network.")

        st.markdown("""
        ---
        The interaction of these metrics reveals two distinct regimes:

        * **The Power Mesh (Redundancy):** A high-influence cluster defined by `barrilaco`, `prado_norte`, and `trastevere`. These nodes form a highly interconnected "elite mesh" with the Super-Node, providing with high navigational resilience and multiple low-friction routing alternatives.
        * **Strategic Bottlenecks (Vulnerability):** Nodes such as `herradura_conscripto` and `bosque_3` (Constituyentes) exhibit high *Betweenness* but low *Eigenvector* influence. These act as "operational pipelines"; they are essential for connecting the core to the periphery but lack redundant alternatives. Increased friction at these specific nodes presents the highest risk of systemic operational paralysis.""")
        









import streamlit as st
import pandas as pd

# Note: Assuming tab_topology was defined previously
# tab_topology, tab_tensor, tab_markov = st.tabs([...])

# ==========================================
# TAB 1: TOPOLOGICAL UNDIRECTED GRAPH (Continued)
# ==========================================
with tab_topology:
    
    with st.expander("Vulnerability Analysis: Choke Points", expanded=False):

        st.markdown("""
        The diagnostic review identified **7 Critical Bridges** within the undirected graph; these represent single-points-of-failure where a zone’s access to the wider marketplace is entirely dependent on a single transit axis. As detailed below, the zones on the right are topologically isolated "islands" that require traversal through a specific hub to access the global network.
        """)

        # ------------------------------------------
        # Table: Topological Bridges
        # ------------------------------------------
        bridges_data = {
            "Access Hub (Left)": ["`interlomas_magnocentro`", "`vialidad_de_la_barranca`", "`santa_fe_centro_comercial`", "`bosque_3 (Constituyentes)`"],
            "Connection": ["↔", "↔", "↔", "↔"],
            "Dependent Zone (Right)": ["`bosque_real`", "`ave_club_de_golf_lomas`", "`santa_fe_bosques_de`", "`bondojito_asf`"],
            "Operational Risk": [
                "**Isolated Enclave:** High-yield node with zero redundant egress.",
                "**Sequential Dependency:** Forms a chain that terminates at *Lomas Country Club*.",
                "**Enclave Access:** Isolated residential sector with single-point entry logic via Parque La Mexicana.",
                "**Arterial Constraint:** Primary connection for the western depth."
            ]
        }
        df_bridges = pd.DataFrame(bridges_data)
        
        # Render the dataframe cleanly via Markdown
        st.markdown(df_bridges.to_markdown(index=False))
        st.caption("**Table:** Topological Bridges: Identifying critical dependencies and mission isolation points.")






import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE
# ==========================================
with tab_tensor:
    
    with st.expander("The Mobility Tensor: Directed Flow and State Space", expanded=False):

        st.markdown("""
        While the undirected graph established the physical road-connectivity skeleton, the economic layer of the marketplace is governed by directed, asymmetric capital flows. This is operationalized through a **Directed Graph** $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ powered by the **Internal Pienza Flow (IPF)**: a refined subset of $N = 461,003$ synthetic observations (45.6% of the generative manifold) where both origin and destination remain strictly within the geofence. 
        
        This refined dataset forms the basis of a high-dimensional **Mobility Tensor**, which serves as the framework's economic engine by mapping every potential internal state transition:
        """)

        # Tensor Equation
        st.latex(r"\mathcal{T} \in \mathbb{R}^{Z \times Z \times H \times D \times P \times C}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ------------------------------------------
        # Table: Mobility Tensor Architecture
        # ------------------------------------------
        tensor_data = {
            "Dimension": [
                "Spatial Axis ($Z \\times Z$)", 
                "Temporal Axis ($H \\times D$)", 
                "Economic Axis ($P$)", 
                "Dual-Channel Signal ($C$)"
            ],
            "Operational Mapping": [
                "A $72 \\times 72$ origin-destination matrix capturing all directed internal mission vectors.",
                "18 hourly blocks over a 7-day cycle, tracking circadian and weekly demand shifts within the geofence.",
                "Three discrete product tiers (Economy, Mid-Tier, Premium) available for the autonomous fleet.",
                "A 2-element output vector recording **Volume** (transactional frequency) and **Value** (weighted average realized EPH)."
            ]
        }
        df_tensor = pd.DataFrame(tensor_data)
        st.markdown(df_tensor.to_markdown(index=False))
        st.caption("**Table:** Multi-Dimensional Architecture of the Internal Mobility Tensor.")

        st.markdown("""
        > **Architectural Note (Product Tiers):** While an AV fleet would typically constitute a distinct product tier, this project retains the standard market categories to simulate the deployment of autonomous vehicles across the entire service spectrum.
        """)

        st.markdown("""
        ---
        ### Volume-Weighted State Contraction
        
        To transition from a multi-dimensional state space to a functional routing network, the high-dimensional Mobility Tensor is collapsed into a flat $72 \\times 72$ weighted adjacency matrix. This is achieved by calculating the **Volume-Weighted Average EPH** for every directed origin-destination pair ($i \\to j$):
        """)

        # Weight Formulation Equation
        st.latex(r"\text{Weight}_{i,j} = \frac{\sum (\text{Volume} \times \text{EPH})}{\sum \text{Volume}}")

        st.markdown("""
        This formulation ensures that the resulting matrix identifies where capital flows reliably, naturally diluting low-volume statistical anomalies and penalizing unprofitable high-traffic corridors. The contraction represents the extraction of the network's **Steady-State**, providing the baseline environment for the stationary Markov Decision Process (MDP) evaluated in this phase.
        """)










import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE (Continued)
# ==========================================
with tab_tensor:
    
    with st.expander("Market Capture and the Decoupling Index", expanded=False):

        st.markdown("""
        To identify the structural discrepancies between urban infrastructure and capital flow, the framework introduces the **Decoupling Index ($DI$)**. This metric quantifies the divergence between **Structural Centrality** (normalized Betweenness Centrality, $BC$) and **Value Centrality** (normalized PageRank on the Mobility Tensor, $PR$):
        """)

        # Equation Rendering
        st.latex(r"DI = PR_{norm} - BC_{norm}")

        st.markdown("""
        By contrasting these two dimensions, the study isolates "High-Yield Attractors" from "Structural Efficiency Traps" within the operational domain. The table below summarizes the most significant deviations observed in the 72-node ecosystem (see Appendix for the comprehensive censo).
        """)

        # ------------------------------------------
        # Table: Market Capture Audit
        # ------------------------------------------
        capture_data = {
            "Urban Zone": [
                "Santa Fe Centro Comercial", 
                "Santa Fe Quintana", 
                "Roma Condesa 2", 
                "Bosque 3 (Constituyentes)", 
                "Bosque 2 (Constituyentes)"
            ],
            "BC (Struct)": ["0.257", "0.000", "0.250", "0.953", "0.828"],
            "PR (Value)": ["1.000", "0.648", "0.708", "0.579", "0.578"],
            "DI (Delta)": ["**+0.743**", "**+0.648**", "+0.458", "**-0.374**", "**-0.250**"],
            "Operational Profile": [
                "Primary Value Attractor", 
                "High-Capture Terminal", 
                "Stable Market Core", 
                "Transit-Only Infrastructure", 
                "Transit-Only Infrastructure"
            ]
        }
        df_capture = pd.DataFrame(capture_data)
        st.markdown(df_capture.to_markdown(index=False))
        st.caption("**Table:** Market Capture Audit: Identifying Value Attractors and Structural Traps.")

        st.markdown("""
        ---
        ### Critical Insights for Autonomous Deployment
        
        The audit identifies three critical insights for autonomous fleet deployment:

        1. **The Primary Attractor:** *Santa Fe Centro Comercial* represents the peak value node ($PR=1.0$). Its high positive $DI$ (+0.74) identifies it as the dominant capital sink in the network. For an autonomous agent, this node represents the highest-priority target for proactive relocation, regardless of its moderate structural connectivity.
        2. **High-Capture Terminals:** Zones such as *Santa Fe Quintana* and *Bondojito ASF* exhibit a $BC$ of 0.0, indicating they are terminal "dead-ends" in the road network. However, their high PageRank scores prove they are critical receptors of high-yield missions. These **Retention Hubs** are vital for fleet positioning but would be overlooked by routing algorithms relying solely on road topology.
        3. **Transit-Only Infrastructure:** The Constituyentes corridor dominates the physical infrastructure with a $BC$ of 0.95, yet fails to translate this pass-through frequency into significant market capture ($DI = -0.37$).
        """)




import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE (Continued)
# ==========================================
with tab_tensor:
    
    with st.expander("Functional Morphology and Topological Classification", expanded=False):

        st.markdown("""
        The functional graph—representing the 72-node closed ecosystem—reveals an environment of extreme saturation and high liquidity. By contrasting structural road constraints with the functional connectivity of the mobility tensor, the study identifies a transition from a "Small-World" physical topology to a **Random Mesh** economic regime. 
        """)

        # ------------------------------------------
        # Table: Functional Metrics (Watts-Strogatz)
        # ------------------------------------------
        functional_data = {
            "Metric": ["Density ($p$)", "Clustering ($C$)", "Path Length ($L$)", "**Sigma ($\\sigma$)**"],
            "Value": ["0.6933", "0.7525", "1.3259", "**1.0545**"],
            "Operational Interpretation": [
                "**System Saturation:** 69.3% of all possible internal connections are active and profitable.",
                "**Transactional Cohesion:** A 75.2% probability that 'economic neighbors' also transact with each other.",
                "**Logistical Liquidity:** Average traversal of 1.32 jumps, a significant reduction from the 4.8 jumps required by road topology.",
                "**Topological Verdict:** A result of $\\sigma \\approx 1.0$ classifies the network as a **Random Mesh**, statistically indistinguishable from an *Erdős-Rényi* model."
            ]
        }
        df_functional = pd.DataFrame(functional_data)
        st.markdown(df_functional.to_markdown(index=False))
        st.caption("**Table:** Functional Metrics and Watts-Strogatz Test Results (72-Node Ecosystem).")

        st.markdown("""
        ---
        ### The Operational Verdict
        
        This finding demonstrates that economic demand has effectively "melted" the geographic barriers of the city. Within the geofence, the optimization problem for an autonomous fleet controller shifts from complex pathfinding to **probabilistic positioning** within a near-complete graph.
        """)









import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE (Continued)
# ==========================================
with tab_tensor:
    
    with st.expander("Micro-Dynamics of Capital: Edge Centrality and Vector Analysis", expanded=False):

        st.markdown("""
        To move beyond the static evaluation of zones, the framework executes an **Edge-Level Audit** using a Dual Graph representation (Line Graph $L(\mathcal{G})$). By transforming the 2,441 active trajectories into nodes, the study identifies the "Economic Arteries" of the city. This analysis reveals a clear hierarchy where immediate yield and long-term transactional prestige are often decoupled.
        
        ### Hierarchical Trajectory Audit
        
        The following table summarizes the leading trajectories according to four distinct operational dimensions: **Yield Intensity** (Weight), **Network Dominance** (Betweenness), **Operational Liquidity** (Closeness), and **Flow Prestige** (PageRank).
        """)

        # ------------------------------------------
        # Table: Edge Centrality Audit
        # ------------------------------------------
        edge_data = {
            "Trajectory (Vector)": [
                "*[Yield]* Tamarindos → Santa Fe CC", 
                "*[Yield]* Lincoln → Irrigación",
                "*[Dominance]* Tamarindos → Santa Fe CC", 
                "*[Dominance]* Vialidad de la Barranca → Tamarindos",
                "*[Liquidity]* Roma Condesa 2 → Bosque 1", 
                "*[Liquidity]* Santa Fe CC → Bosque 1",
                "*[Prestige]* Lomas FC Cuernavaca → Reforma Regina", 
                "*[Prestige]* Sotelo → Polanco Uber HQ"
            ],
            "Metric": [
                "Expected EPH", "Expected EPH", 
                "Betweenness", "Betweenness", 
                "Closeness", "Closeness", 
                "PageRank", "PageRank"
            ],
            "Value": ["Max", "High", "1.000", "0.330", "1.000", "0.988", "1.000", "0.700"],
            "Operational Profile": [
                "**High-Intensity Corridor**", "Corporate Surge Vector",
                "**Critical Economic Bridge**", "Supply Chain Inflow",
                "**Strategic Pivot Point**", "High-Availability Exit",
                "**Elite Market Hub**", "High-Capture Transition"
            ]
        }
        df_edge = pd.DataFrame(edge_data)
        st.markdown(df_edge.to_markdown(index=False))
        st.caption("**Table:** Edge Centrality Audit: Leading Trajectories by Operational Dimension.")

        st.markdown("""
        ---
        ### Analysis of Vector Forces
        
        The audit identifies three primary behavioral mechanics that define the "Thermodynamics of Value" within the geofence:

        1. **The Golden Bottleneck (Tamarindos Corridor):** The trajectory *Tamarindos → Santa Fe Centro Comercial* emerges as the most vital artery in the ecosystem. It ranks **#1 in both Yield Intensity and Network Dominance**. This vector represents the primary conduit through which capital from elite residential clusters is injected into the commercial core. For an autonomous fleet, maintaining a presence in this vector is equivalent to capturing the highest-density revenue stream in the network.
        2. **Prestige Monopolies (Lomas FC Cuernavaca):** A significant finding is the dominance of *Lomas FC Cuernavaca* as an originating hub. Eight of the top-ranking prestige trajectories originate from this node. While these trips may not always represent the absolute peak in raw currency, they provide the highest **Market Stability**. Entering these vectors ensures the agent remains within a high-value "closed loop" of elite zones (*e.g., Reforma, Polanco, Lomas*), minimizing exposure to low-yield peripheral zones.
        3. **Liquidity Refuges and Buffers (Bosque 1):** The *Closeness* metric identifies *Bosque 1* as the supreme "Safe Harbor" of the network. Trajectories terminating in this zone provide the agent with the shortest possible economic distance to any other point in the graph. These are not necessarily the most profitable destinations in a single jump, but they are the most **tactically advantageous positionings** for minimizing idle time when market demand is uncertain.
        """)






import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE (Continued)
# ==========================================
with tab_tensor:
    
    with st.expander("Structural Resilience and Functional Robustness", expanded=False):

        st.markdown("""
        To evaluate the operational stability of the geofenced ecosystem, the framework executes a comparative resilience audit between the **Physical Infrastructure** (road connectivity) and the **Economic Manifold** (capital flow). Resilience is quantified by identifying single points of failure (cut-vertices and bridges) and calculating the structural $k$-connectivity of the network core.

        ### Comparative Vulnerability Audit
        
        The audit reveals a profound discrepancy between the fragility of the asphalt and the robustness of the market. While the physical network is susceptible to fragmentation, the economic tensor functions as a hyper-resilient mesh.
        """)

        # ------------------------------------------
        # Table: Comparative Resilience
        # ------------------------------------------
        resilience_data = {
            "Network Layer": ["Physical Infrastructure", "Economic Tensor (IPF)"],
            "Cut-Vertices": ["7", "0"],
            "Bridges": ["7", "0"],
            "Operational Verdict": [
                "**Structurally Fragile:** Local closures or blockages trigger immediate network fragmentation.",
                "**Highly Resilient:** Capital flow persists regardless of any single node or edge failure."
            ]
        }
        df_resilience = pd.DataFrame(resilience_data)
        st.markdown(df_resilience.to_markdown(index=False))
        st.caption("**Table:** Resilience Comparison: Physical Fragility vs. Economic Redundancy.")

        st.markdown("""
        ---
        ### Topological Robustness: The K-Connectivity Metric
        
        Beyond simple connectivity, the study evaluates the **Structural Robustness** of the Economic core using the *Menger Theorem* ($k$-node connectivity). The analysis identifies a connectivity value of **$k=21$**.

        Mathematically, this implies that a minimum of **21 nodes must fail simultaneously** to disconnect the economic core of Pienza. The *Minimum Node Cut* set includes primary attractors and hubs such as *Tamarindos, Anzures, Santa Fe Centro Comercial,* and *Vialidad de la Barranca*. This high degree of redundancy ensures that the autonomous fleet can maintain transactional continuity even under extreme operational disruption; if one profitable corridor is blocked, the high density of the tensor provides 20 alternative high-yield paths.

        ---
        ### Macro-Morphology and the Autocentric Singularity
        
        The removal of external noise (pruning the Exilio) reveals the internal morphology of the 72-node sovereign ecosystem. The resulting graph exhibits a rare topological state known as **Autocentricity**.
        """)

        # ------------------------------------------
        # Table: Macro-Morphological Report
        # ------------------------------------------
        morphology_data = {
            "Morphological Metric": ["Economic Density ($p$)", "Economic Diameter ($D$)", "Economic Radius ($R$)"],
            "Value": ["0.4775", "2 jumps", "2 jumps"],
            "Strategic Interpretation": [
                "Nearly 50% of all internal origin-destination pairs are active and yield-positive.",
                "The maximum distance between any two points in the network is only two transitions.",
                "The center is equidistant from every point in the sovereign domain."
            ]
        }
        df_morphology = pd.DataFrame(morphology_data)
        st.markdown(df_morphology.to_markdown(index=False))
        st.caption("**Table:** Macro-Morphological Report of the 72-Node Sovereign Ecosystem.")

        st.markdown("""
        This **Diameter of 2** represents an economic collapse of space. In the physical world, moving from the periphery to the core requires traversing multiple layers of traffic and intersections ($L=4.8$). However, within the Economic Tensor, the network is so saturated that the agent is never more than two transitions away from any other point of value. In an autocentric graph, the distinction between "center" and "periphery" evaporates; the entire geofence functions as a singular, high-liquidity economic unit.

        > **Architectural Note (Steady-State):** It is imperative to clarify that the observed Autocentricity is a property of the system's **Steady-State Equilibrium**. By aggregating the longitudinal flow into a singular manifold, the temporal gaps of the marketplace are bridged, revealing the **Potential Connectivity** of the geofence. While instantaneous snapshots of the network (e.g., off-peak hours) may exhibit higher eccentricity and fragmentation, the aggregate steady-state proves that the underlying economic structure of the city is designed for maximum liquidity, effectively collapsing the distance between the geographical periphery and the functional core.
        """)


import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 2: MOBILITY TENSOR: FLOW & STATE (Continued)
# ==========================================
with tab_tensor:
    
    with st.expander("Market Asymmetry: The Topological Trade Balance", expanded=False):

        st.markdown("""
        By transitioning from a bidirectional road view to a **Net Economic Flow** evaluation, the Mobility Tensor reveals that the ecosystem operates under a regime of high asymmetry. The city functions as a system of **Flow Valves**, where certain nodes act as capital originators while others function as terminal receptors. 
        
        This thermodynamic behavior is quantified by the **Asymmetry Index ($A_i$)**, which ranges from -1.0 (pure receptor) to +1.0 (pure originator).
        """)

        # ------------------------------------------
        # Table: Topological Trade Balance
        # ------------------------------------------
        trade_data = {
            "Urban Zone": [
                "*Top 5 Capital Originators*",
                "Polanco Parque Lincoln",
                "Anzures",
                "Tamarindos",
                "Vialidad de la Barranca",
                "Lomas Virreyes",
                "---",
                "*Top 5 Capital Receptors*",
                "Polanco Uber HQ",
                "Irrigación",
                "Cruce Echanove",
                "Santa Fe Centro Comercial",
                "Roma Condesa 2"
            ],
            "Asymmetry Index ($A_i$)": [
                "", "+0.78", "+0.77", "+0.73", "+0.39", "+0.33", "---", "", "-0.92", "-0.85", "-0.75", "-0.67", "-0.40"
            ]
        }
        df_trade = pd.DataFrame(trade_data)
        st.markdown(df_trade.to_markdown(index=False))
        st.caption("**Table:** Topological Trade Balance: Identifying Originators and Retention Nodes.")

        st.markdown("""
        ---
        ### Operational Implications of Flow Asymmetry
        
        The analysis reveals a profound structural divide that dictates autonomous agent performance:

        1. **Retention Vortices (Structural Sinks):** *Santa Fe Centro Comercial* and *Polanco Uber HQ* function as the primary sinks of the network. While these zones are high-value targets for incoming missions, their extreme negative asymmetry ($A_i < -0.60$) creates an **Operational Entrapment Risk**. Entering these nodes provides high immediate yield but significantly reduces the probability of a profitable exit mission.
        2. **Value Engines (Structural Sources):** *Tamarindos* and *Polanco Parque Lincoln* act as the primary radiators of capital. These zones exhibit high positive asymmetry, meaning they consistently generate more value through outgoing missions than they absorb through incoming ones.
        """)




import streamlit as st

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 3: BRIDGE TO MARKOV: AV SANDBOX
# ==========================================
with tab_markov:
    
    with st.expander("Scaffolding the Markov Decision Process (MDP)", expanded=False):

        st.markdown("""
        To transition from market observation to autonomous optimization, the Mobility Tensor must be converted into a mathematical environment compatible with **Dynamic Programming**. This stage establishes the **Markov Decision Process (MDP)** scaffolding, enabling an agent to evaluate not just the immediate value of a mission, but the long-term potential of the resulting urban positioning.

        The transition is operationalized by extracting two fundamental matrices from the Internal Pienza Flow (IPF) manifold: the **Transition Matrix ($\mathcal{P}$)** and the **Reward Matrix ($\mathcal{R}$)**.

        1. **Transition Matrix ($P_{ij}$):** This matrix represents the "behavioral gravity" of the marketplace. For every zone $i$, the model calculates the empirical probability that the next assigned mission will terminate in zone $j$. This captures the stochastic nature of the algorithm: if an agent is in *Anzures*, what is the statistical likelihood that the market will "propel" them toward *Santa Fe* versus *Polanco*?
        2. **Reward Matrix ($R_{ij}$):** This defines the expected instantaneous payoff for each jump. It records the weighted average EPH (Earnings Per Hour) for a mission starting in $i$ and ending in $j$. This matrix acts as the economic fuel of the system, quantifying the immediate return of any specific movement.
        """)




import streamlit as st

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 3: BRIDGE TO MARKOV: AV SANDBOX (Continued)
# ==========================================
with tab_markov:
    
    with st.expander("Structural Stability: Absorbing States and Total Retention", expanded=False):

        st.markdown("""
        A critical requirement for Markovian stability is that the transition matrix must be **row-stochastic**—meaning the probabilities for every origin node must sum exactly to 1.0 to ensure that no "probability mass" is lost during the simulation. During the construction phase, the framework identified four **Absorbing States** within the 72-node geofence: `bosque_1`, `campo_marte`, `lomas_olimpo`, and `santa_fe_bosques_de`.

        In stochastic modeling, an absorbing state is a node with zero recorded outgoing trajectories—a "dead-end" for capital flow within the current dataset. To preserve mathematical integrity and prevent the simulation from collapsing into a null state, these nodes are assigned a self-loop probability of $P_{ii} = 1.0$. 

        Strategically, these are identified as **Terminal Retention Nodes**. They represent zones where the agent captures high-value arrivals but finds zero market liquidity to exit the area. Identifying these "economic sinks" is a prerequisite for the next phase; it allows the agent to calculate the true cost of entering a zone from which there is no statistical escape, mathematically justifying the rejection of high-upfront offers that lead to terminal absorption.

        > **Operational Caveat:** While in operational reality an autonomous vehicle could capture offers from adjacent nodes or simply execute a relocation traversal to a nearby hub, this simulation strictly enforces these boundaries to isolate and evaluate the structural risks of the existing demand manifold.
        """)



import streamlit as st

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 3: BRIDGE TO MARKOV: AV SANDBOX (Continued)
# ==========================================
with tab_markov:
    
    with st.expander("Strategic Valuation: The State-Value Function $V(s)$", expanded=False):

        st.markdown("""
        To determine the long-term potential of each urban zone, the framework applies the **Bellman Equation** to the mobility tensor. This process shifts the analytical focus from immediate profitability (*Expected EPH*) to the **State-Value Function ($V(s)$)**, which represents the total cumulative value an agent can expect to capture starting from a specific node, accounting for all future transitions.

        The function was solved using the **Value Iteration** algorithm with a discount factor of $\gamma = 0.85$ and a convergence threshold of $\theta = 10^{-7}$. The resulting hierarchy identifies the "True Value" of urban positioning within a closed-loop ecosystem.
        """)

        # Figure: Bellman Valuation
        try:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_bellman_valuation.png")
            st.caption("**Figure:** The Real Value of Pienza: Comparing Immediate EPH ($R_s$) vs. Total State-Value ($V_s$). The red dashed line indicates the 'Myopic Horizon'—the maximum value visible to an agent relying solely on instantaneous signals.")
        except Exception as e:
            st.error("Image not found: fig_bellman_valuation.png")

        st.markdown("""
        ---
        ### Equilibrium and the Topological Premium

        The results reveal a state of **Dynamic Equilibrium**. While immediate rewards ($R_s$) vary significantly across the city, the total state-values ($V_s$) exhibit a high degree of uniformity, converging near a system-wide capacity limit. This homogeneity is a mathematical property of the **Autocentric Steady-State**: in a high-liquidity mesh with an economic diameter of 2, value is distributed ergodically across the core.

        However, the critical differentiator is the **Future Value Ratio**. The audit identifies two distinct node profiles:

        * **Extraction Nodes:** Zones like *Polanco Parque Lincoln* exhibit high immediate yield but a low future-value ratio (+60%). These are "Harvesting" zones where the agent captures peak currency but has limited upward topological potential.
        * **Gateway Hubs:** Zones such as *Anzures* (+813%) or *Roma Condesa 1* (+888%) show low immediate EPH but massive topological premiums. These nodes act as **Economic Trampolines**; while the current mission might be suboptimal, the node's connectivity ensures a near-certain transition into high-yield corridors.

        By internalizing these premiums, the autonomous fleet can justify the acceptance of low-upfront "positioning missions" that place the vehicle in a Gateway Hub, effectively utilizing the city's topology as a **Strategic Insurance** against future inactivity.
        """)




import streamlit as st

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 3: BRIDGE TO MARKOV: AV SANDBOX (Continued)
# ==========================================
with tab_markov:
    
    with st.expander("Operational Command: The Action-Value Matrix & Fleet Orchestration", expanded=False):

        st.markdown("""
        To move from the passive valuation of states to an active decision-making framework, the system derives the **Action-Value Matrix ($Q$-Matrix)**. This manifold represents the definitive command layer for the autonomous fleet, where each potential mission is evaluated not by its isolated payout, but as a vector for strategic re-positioning. 

        The value of taking action $a$ (accepting a specific destination) in state $s$ (current origin zone) is defined by the expected sum of the immediate reward and the discounted future potential of the resulting state $s'$:
        """)

        # Equation: Q-Value
        st.latex(r"Q(s, a) = R(s, a) + \gamma V(s')")

        st.markdown("""
        By operationalizing this equation, the framework forces the agent to internalize the **Opportunity Cost** inherent in every market offer. Within the Pienza geofence, an action is deemed optimal if it maximizes the agent's long-term **Economic Inertia**, effectively prioritizing transitions that terminate in high-prestige hubs over myopic, high-upfront "Trap Offers" that lead to terminal economic sinks.
        
        ---
        ### Multi-Agent Coordination: The Fleet Orchestrator
        
        To move from a single-agent theory to a scalable operational model, the framework introduces the **Fleet Orchestrator**. This module simulates the coordinated deployment of an autonomous fleet originating from three strategic urban hubs: *Carso Antara, Santa Fe Centro Comercial,* and *Interlomas Magnocentro*. The orchestrator utilizes a **Depth-First Search (DFS)** algorithm to project optimized five-jump mission sequences for multiple concurrent units.
        
        ---
        ### Demand Depletion and Swarm Neutralization
        
        The primary challenge in fleet management is the **Swarm Effect**: a phenomenon where multiple independent agents cluster in a single high-value zone, leading to oversaturation and individual yield decay. To neutralize this, the framework implements a **Demand Depletion Mechanic**. 
        
        As each agent selects an optimal trajectory, the corresponding edges in the $Q$-Matrix undergo a **90% Value Attrition** ($Q_{u,v} \leftarrow Q_{u,v} \times 0.10$). This mathematical penalty simulates the "consumption" of market demand by the preceding vehicle. By treating the city’s liquidity as a finite resource, the orchestrator forces subsequent agents to seek spatially diverse "second-best" paths that are structurally more profitable for the collective fleet. This transformation shifts the objective from individual greed to **Distributed Network Capture**, ensuring maximum coverage of the mobility mesh while maintaining systemic stability.
        """)




import streamlit as st
import pandas as pd

# Note: Assuming tab_topology, tab_tensor, tab_markov were defined previously

# ==========================================
# TAB 3: BRIDGE TO MARKOV: AV SANDBOX (Continued)
# ==========================================
with tab_markov:
    
    with st.expander("Tactical Deployment: The Five-Jump Mission Manifold", expanded=False):

        st.markdown("""
        The simulation concludes with the generation of optimized flight plans for nine concurrent autonomous units, deployed from three primary logistical warehouses. By enforcing the **Demand Depletion** mechanic, the orchestrator prevents unit clustering and ensures maximum spatial coverage. The table below presents the resulting mission sequences, where each jump represents a transition designed to maximize the collective $Q$-value of the fleet.
        """)

        # ------------------------------------------
        # Table: Autonomous Fleet Deployment
        # ------------------------------------------
        fleet_data = {
            "Warehouse Origin": [
                "**Carso Antara Miyana**", "", "",
                "**Santa Fe Centro Comercial**", "", "",
                "**Interlomas Magnocentro**", "", ""
            ],
            "ID": ["AV1", "AV2", "AV3", "AV4", "AV5", "AV6", "AV7", "AV8", "AV9"],
            "Jump 1": ["Tamarindos", "Irrigación", "Polanco Uber HQ", "Sedena", "Reforma Social", "Fuentes Casino", "Ave Club de Golf Lomas", "Santa Fe Quintana", "Anzures"],
            "Jump 2": ["Santa Fe Centro Comercial", "Tamarindos", "Tamarindos", "Vialidad de la Barranca", "Interlomas Magnocentro", "Vialidad de la Barranca", "Tamarindos", "Tamarindos", "Irrigación"],
            "Jump 3": ["Tamarindos", "Cruce Echanove", "Vistahermosa", "Tamarindos", "Tamarindos", "Lomas Virreyes", "Lagos", "Carretera al Olivo", "Sante Fe Patio"],
            "Jump 4": ["Santa Fe Centro Comercial", "Anzures", "Interlomas Haciendas", "Jesús del Monte", "Interlomas Haciendas", "Tamarindos", "Roma Condesa 1", "Jesús del Monte", "Tamarindos"],
            "Jump 5": ["Tamarindos", "Tamarindos", "Tamarindos", "Tamarindos", "Santa Fe Centro Comercial", "Carretera Libre", "Tamarindos", "Santa Fe Centro Comercial", "Lomas Virreyes"],
            "Score": ["27,304", "11,447", "11,399", "11,817", "11,513", "11,481", "11,443", "10,972", "10,668"]
        }
        
        df_fleet = pd.DataFrame(fleet_data)
        
        # Render the dataframe cleanly via Markdown
        st.markdown(df_fleet.to_markdown(index=False))
        st.caption("**Table:** Autonomous Fleet Deployment: Coordinated Mission Sequences with Full Nomenclatures.")

        st.markdown("""
        ---
        ### Systemic Distribution Strategy
        
        The deployment data confirms the structural dominance of the **Economic Arteries** previously identified in the edge centrality audit. Notably, while the first unit (*AV1*) captures the high-prestige circularity between *Tamarindos* and *Santa Fe Centro Comercial*, the depletion of demand in those edges forces the remaining fleet to branch into auxiliary hubs. 

        By the third unit of each warehouse, the orchestrator successfully pushes the fleet toward **Network Buffers** such as *Anzures* and *Lomas Virreyes*. This demonstrates that the Pienza framework does not merely identify "the best place to be," but rather identifies a **Systemic Distribution Strategy**. For an autonomous fleet, this transition from individual optimization to coordinated network capture represents the definitive shift from reactive labor to industrial-grade logistics, ensuring that the geofence remains saturated with value while minimizing internal competition.
        """)




import streamlit as st

# Note: This code should be placed OUTSIDE and BELOW the tabbed architecture.

st.divider()

# ==========================================
# CONCLUSION: THE GENERATIVE MOONSHOT
# ==========================================
st.header("Conclusion: The Generative Moonshot & Pienza 2.0")

st.markdown("""
The **Generative Moonshot** represents the final structural evolution of Project Pienza, transitioning from the observation of individual human heuristics to the orchestration of a scalable economic engine. By synthesizing generative neural manifolds with the steady-state rationality of the *Bellman Equation*, the framework effectively maps the "Economic Limit" of the urban environment. The resulting tactical flight plans prove that the city is not merely a physical grid to be traversed, but a **Tensor of Potentials** where value can be systematically captured through coordinated agent distribution and demand-aware positioning.
""")

st.success("""
**The Boundary of Inquiry:** This functional scaffolding marks the boundary of the current inquiry, delivering the mathematical architecture required for the next generation of autonomous intelligence. By defining the state space ($\mathcal{S}$), transition probabilities ($\mathcal{P}$), and reward manifolds ($\mathcal{R}$) within a strictly closed operational domain, the framework provides the necessary baseline for transition into **Pienza 2.0: The Knowledge**. 

In this future iteration, the static scaffolding established here will serve as the training environment for high-frequency Reinforcement Learning (RL) and complex *Markov Chain Monte Carlo* (MCMC) simulations, moving beyond the steady-state and into the dynamic, real-time optimization of autonomous urban economies.
""")



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


