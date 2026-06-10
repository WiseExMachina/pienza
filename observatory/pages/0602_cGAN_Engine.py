import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os
import gc

# --- LOCAL UTILITIES ---
from utils.gcp_client import load_manifold_dimensions 
from utils.bq_client import fetch_data_from_bq


# --- PAGE CONFIG ---
st.set_page_config(page_title="cGAN Engine | Pienza", page_icon="🏭", layout="wide", initial_sidebar_state="collapsed")



# Initialize session state for the manifold
if 'df_manifold' not in st.session_state:
    st.session_state.df_manifold = None

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Libre+Baskerville', serif !important; color: #1E3D3D; }
    .metric-box { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #440154; }
    /* Hide the sidebar completely for VVS1 UX */
    [data-testid="collapsedControl"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 The cGAN Engine (Invisible Backend)")
st.markdown("""
Welcome to the Generative Forge. This engine bypasses pre-computed tables, allowing you to synthesize 
**net-new, hyper-realistic ride-hailing demand** on the fly. Set your market regime below, and the neural network 
will hallucinate the physical forces (Fare, Time, Distance) that obey those exact constraints.
""")
st.markdown("---")


# ==============================================================================
# 0. GLOBAL CONSTANTS
# ==============================================================================
PROJECT_ID = "drivers-dilemma"  # This is the string ID for your GCP project
LATENT_DIM = 100               # Still needed for reference



# ==============================================================================
# 1. LOAD SEMANTIC DIMENSIONS (LIGHTWEIGHT)
# ==============================================================================
# Bypassing Keras backend for VVS1 performance
dim_prod, dim_drop, dim_pick = load_manifold_dimensions()

if dim_prod is None:
    st.error("🚨 Critical Failure: Could not load dimensions from GCP Vault.")
    st.stop()




# ==============================================================================
# 2. EXTRACT SWITCHES & MICRO-SEMANTIC MAPPING
# ==============================================================================
# Hardcoded Pools (Safe & Instant)
days_pool = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hours_pool = [f"{i}" for i in range(24)] # 0 to 23

def format_hour(h): return f"{int(h):02d}:00 Hrs"

# Product Handlers
products_pool = ["1", "2", "3"]
product_map = {"1": "X", "2": "Mid-Tier", "3": "Premium"}
def format_product(p): return product_map.get(p, "Unknown")

# --- GEOGRAPHIC MICRO-MAPPING (The Sovereign Filter) ---
# We use the dimensions loaded from Parquet to build the pools
rev_dict_pick = dict(zip(dim_pick['semantic_name'], dim_pick['zone_key']))
rev_dict_drop = dict(zip(dim_drop['semantic_name'], dim_drop['zone_key']))

# Filter out Unassigned/Entropy for the UI
pickups_pool = sorted([
    n for n in dim_pick[dim_pick['zone_key'].str.startswith('P_')]['semantic_name'].unique() 
    if "unassigned" not in str(n).lower()
])

dropoffs_pool = sorted([
    n for n in dim_drop[dim_drop['zone_key'].str.startswith('P_')]['semantic_name'].unique() 
    if "unassigned" not in str(n).lower()
])
chrono_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
# ==============================================================================
# 3. VVS1 MAIN UI CONTROLS (CLEAN UX)
# ==============================================================================
st.markdown("### 🎛️ Market Regime Switches")

# Row 1: Time & Product
c1, c2, c3 = st.columns(3)

with c1:
    all_days = st.toggle("🗓️ All Days", value=True)
    sel_days = days_pool if all_days else st.multiselect("Select Days", days_pool, default=[])

with c2:
    all_hours = st.toggle("⏰ All Hours", value=True)
    sel_hours = hours_pool if all_hours else st.multiselect("Select Hours", hours_pool, format_func=format_hour, default=[])

with c3:
    all_products = st.toggle("🚗 All Products", value=True)
    sel_products = products_pool if all_products else st.multiselect("Select Products", products_pool, format_func=format_product, default=[])

st.write("") # Spacing

# Row 2: Geospatial
c4, c5 = st.columns(2)

with c4:
    all_pickups = st.toggle("📍 All Pickup Zones", value=True)
    # The multiselect now shows Micro-Names (e.g., "Santa Fe Tec")
    sel_pickup_names = pickups_pool if all_pickups else st.multiselect("Select Pickups", pickups_pool)
    
    # CRITICAL: Map names back to Macro GAN IDs (e.g., "Santa Fe Tec" -> "P_0")
    sel_pickups = [rev_dict_pick[name] for name in sel_pickup_names]

with c5:
    all_dropoffs = st.toggle("🏁 All Dropoff Zones", value=True)
    # The multiselect now shows Micro-Names
    sel_dropoff_names = dropoffs_pool if all_dropoffs else st.multiselect("Select Dropoffs", dropoffs_pool)
    
    # CRITICAL: Map names back to GAN IDs
    sel_dropoffs = [rev_dict_drop[name] for name in sel_dropoff_names]

st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)
ignite_forge = st.button("🔥 IGNITE THE FORGE", use_container_width=True, type="primary")

# --- Safety Check: Ensure no switch is completely empty ---
if ignite_forge:
    if not all([sel_days, sel_hours, sel_products, sel_pickups, sel_dropoffs]):
        st.warning("⚠️ **Generative Starvation Risk:** You must have at least one option selected in every active switch box. The generator cannot synthesize a reality out of nothing.")
        st.stop()


# ==============================================================================
# 4. THE SOVEREIGN ENGINE (MANIFOLD SOT BACKEND)
# ==============================================================================
if ignite_forge:
    start_time = time.time()
    
    # We maintain the UI names but must un-polish them for the SQL query 
    # (Converting "Santa Fe Tec" back to "santa_fe_tec")
    def unpolish(name): return name.lower().replace(' ', '_')
    
    with st.status("Accessing the Pienza Manifold (BigQuery SoT)...", expanded=True) as status:
        
        st.write("📡 Executing Cross-Corridor Extraction...")
        
        # 1. Convert UI selections for SQL
        sql_days = ", ".join([f"'{d}'" for d in sel_days])
        sql_hours = ", ".join([f"'{h}'" for h in sel_hours])
        sql_products = ", ".join([f"'{p}'" for p in sel_products])
        
        # We query by Micro-Names because they are the user's strategic intent
        sql_pickups = ", ".join([f"'{unpolish(n)}'" for n in sel_pickup_names])
        sql_dropoffs = ", ".join([f"'{unpolish(n)}'" for n in sel_dropoff_names])
        
        # 2. THE MASTER QUERY
        # We query the already downscaled 1M row manifold
        query_manifold = f"""
            SELECT 
                day_of_week, 
                hour_of_day, 
                product_name as Product, 
                pickup_name_down as Pickup, 
                dropoff_name_down as Dropoff,
                time_to_pickup_sec, 
                est_trip_dist_km, 
                est_trip_time_sec, 
                upfront_fare
            FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled`
            WHERE day_of_week IN ({sql_days})
              AND CAST(hour_of_day AS STRING) IN ({sql_hours})
              AND CAST(product_category_fk AS STRING) IN ({sql_products})
              AND pickup_name_down IN ({sql_pickups})
              AND dropoff_name_down IN ({sql_dropoffs})
        """
        
        # 3. Execution
        df_manifold = fetch_data_from_bq(query_manifold)
        
        if len(df_manifold) == 0:
            st.error("🚨 Zero results found for this regime in the Manifold. Broaden your filters.")
            st.stop()
            
        # El volumen se vuelve dinámico
        actual_n = len(df_manifold)
        st.write(f"✅ Extracted {actual_n:,} neural-synthesized records.")
        
        # 4. Persistence
        st.session_state.df_manifold = df_manifold.copy()
        
        status.update(label=f"Forge Extinguished. {actual_n:,} Realities Minted.", state="complete", expanded=False)

# ==============================================================================
# 5. THE MANIFOLD ANALYTICS SUITE (PERSISTENT & DYNAMIC)
# ==============================================================================

# This block only executes if the Forge has been ignited at least once in the session
if st.session_state.df_manifold is not None:
    
    # Extract data from persistent session memory
    df_active = st.session_state.df_manifold.copy()

# --- 5.1 PRE-PROCESSING FOR DISPLAY (Reversión a Decimales) ---
if st.session_state.df_manifold is not None:
    df_active = st.session_state.df_manifold.copy()

    # A. Unit Conversion (Tratamos la columna como minutos directamente)
    df_active['TTP (min)'] = df_active['time_to_pickup_sec'] / 60.0
    df_active['Trip Time (min)'] = df_active['est_trip_time_sec'] / 60.0
    df_active['Trip Dist (km)'] = df_active['est_trip_dist_km']
    df_active['Fare ($ MXN)'] = df_active['upfront_fare']
    df_active['Hour'] = df_active['hour_of_day'].apply(lambda x: f"{int(x):02d}:00")

    # B. Micro-Zone Polishing
    df_active['Pickup'] = df_active['Pickup'].str.replace('_', ' ').str.title()
    df_active['Dropoff'] = df_active['Dropoff'].str.replace('_', ' ').str.title()

    # C. THE FINAL SOVEREIGN FILTER
    df_display = df_active[
        (~df_active['Pickup'].str.lower().str.contains('unassigned')) & 
        (~df_active['Dropoff'].str.lower().str.contains('unassigned'))
    ].copy()

    # D. Canonical Column Order (Sincronizado)
    canonical_cols = [
        'day_of_week', 'Hour', 'Product', 'Pickup', 'Dropoff', 
        'TTP (min)', 'Trip Dist (km)', 'Trip Time (min)', 'Fare ($ MXN)'
    ]
    df_display = df_display[canonical_cols]
    
    
    # Este es el punto donde tronaba:
    df_display = df_display[canonical_cols]

    # --- 5.2 METRIC HIGHLIGHTS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        # Usamos 'Fare ($ MXN)' porque ese sí lo definimos como numérico
        st.metric("Avg Fare Synthesized", f"${df_display['Fare ($ MXN)'].mean():.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.metric("Avg Trip Distance", f"{df_display['Trip Dist (km)'].mean():.2f} km")
    with c3:
        # ERROR FIX: Usamos el nombre exacto que definiste en Step 5.1 / A 
        # O mejor aún, usa la columna de segundos original para el cálculo:
        avg_ttp_sec = df_active['time_to_pickup_sec'].mean() 
        st.metric("Avg Time to Pickup", f"{avg_ttp_sec / 60:.1f} min") 
    with c4:
        st.metric("Sovereign Volume", f"{len(df_display):,}")

    # --- 5.3 DYNAMIC AGGREGATION ENGINE ---
    st.markdown("### 🧬 Manifold Exploration")

    agg_mode = st.selectbox(
        "📊 Aggregate Manifold By:",
        ["Hour of Day", "Day of Week", "Product", "Pickup Zone", "Individual Trips (Raw Sample)"],
        index=0,
        key="manifold_agg_selector" # Unique key prevents state reset
    )

    # Aggregation Logic
    if agg_mode == "Individual Trips (Raw Sample)":
        st.dataframe(df_display.head(100).style.format({
            'TTP (min)': '{:.2f}',
            'Trip Dist (km)': '{:.2f}',
            'Trip Time (min)': '{:.2f}',
            'Fare ($ MXN)': '${:.2f}'
        }), use_container_width=True)

    else:
            agg_map = {
                "Hour of Day": "Hour",
                "Day of Week": "day_of_week",
                "Product": "Product",
                "Pickup Zone": "Pickup"
            }
            group_col = agg_map[agg_mode]
            
            # Agregación limpia usando decimales
            df_agg = df_display.groupby(group_col).agg({
                'Fare ($ MXN)': 'mean',
                'TTP (min)': 'mean',
                'Trip Dist (km)': 'mean',
                'Trip Time (min)': 'mean',
                'Product': 'count' 
            }).rename(columns={'Product': 'Volume (N)'})
            
            # Ordenamiento
            if agg_mode == "Day of Week":
                df_agg = df_agg.reindex([d for d in chrono_order if d in df_agg.index])
            elif agg_mode == "Hour of Day":
                df_agg = df_agg.sort_index()
                
            # Formato de tabla agregada
            st.dataframe(
                df_agg.style.format({
                    'Fare ($ MXN)': '${:.2f}',
                    'TTP (min)': '{:.2f}',
                    'Trip Dist (km)': '{:.2f}',
                    'Trip Time (min)': '{:.2f}',
                    'Volume (N)': '{:,}'
                }).background_gradient(cmap="Purples", subset=['Volume (N)']), 
                use_container_width=True
            )

    # --- 5.4 TOPOLOGICAL GRAVITY CHART ---
    st.markdown("### 🏁 Topological Gravity (Top Micro-Destinations)")
    top_destinations = df_display['Dropoff'].value_counts().head(15)
    st.bar_chart(top_destinations, color="#21918c")

# <--- THE PHILOSOPHY REMAINS OUTSIDE THE SESSION STATE CHECK TO BE ALWAYS VISIBLE --->

# ==============================================================================
# 6. THE PHILOSOPHY OF THE cGAN (THEORY VAULT)
# ==============================================================================
st.markdown("---")
with st.expander("📖 The Philosophy of the cGAN (Under the Hood)"):
    st.markdown("""
    **1. If I request 1 offer with certain characteristics, how does the generator decide which one to throw at me?**  
    The generator doesn't "pick" an offer from a database; it *synthesizes* one. At the moment of creation (The Forge), the Keras model mapped your constraints (e.g., Monday, 8:00 AM, UberX) alongside a 100-dimensional vector of pure mathematical noise. This noise ensures that even for the same constraints, every synthesized trip has a unique physical realization (Fare, Time, Distance). What you see in this dashboard is the serving of those neural realizations at scale.

    **2. Is it the same to request the same offer 1 million times sequentially, versus giving me a million of the same offer in one request?**  
    In theory, yes, because the cGAN is stateless. However, in engineering terms, sequential requests suffer from network I/O latency. By serving from the **1-Million Row Sovereign Manifold** in BigQuery, we achieve "Instantaneous Actualization." We can retrieve 50,000 unique neural hallucinations in seconds, whereas live sequential inference would take hours.

    **3. Is it just a "random offer" from the distribution? Does the generator remember me?**  
    The cGAN is completely Stateless (*Independent and Identically Distributed*). Trip #500 has zero knowledge of Trip #499. The "memory" of the system is stored entirely in the **Weights of the Neural Network**, which learned the deep correlations of the Mexico City market during the training phase.

    **4. What is the minimum sample size that approximates the perfect bell curve?**  
    To observe the **Law of Large Numbers** and ensure that the topological weights (Downscaling) distribute correctly across micro-polygons, we recommend a minimum volume of **10,000 trips**. Below this threshold, the "Neural Noise" might outweigh the statistical signal.

    **5. Is the cGAN related to a Markov Chain (e.g., the "canicas in a sack" analogy)?**  
    No. They are mathematical opposites. A Markov Chain models a sequential journey (where you go next depends on where you are). The cGAN is an instantaneous snapshot—it actualizes the entire "physics" of a trip (Fare, Time, Dist, Wait) simultaneously. In this project, the cGAN builds the **Environment**, and the Markov Chain (Phase 7) will eventually **Route** through it.

    **6. What are the terms that distinguish classical statistics from generative models?**  
    Classical statistics (like our Phase 4 XGBoost) uses a **Discriminative** approach: it predicts the past/present by drawing boundaries ($P(Y|X)$). Generative models use a **Synthetic** approach: they learn the joint distribution of the entire marketplace ($P(X,Y)$) to create net-new realities from scratch.

    **7. How do veteran classical statisticians react to cGANs?**  
    Classical statisticians are often skeptical because GANs lack "P-Values" and "Unbiased Estimators"—they are the ultimate "Black Box." However, in Big Tech (Uber, Lyft, DoorDash), these models are becoming the gold standard for **Marketplace Simulation**. While the industry uses generative models for images and text, building a **Tabular cGAN** that obeys the rigid physics of urban logistics is a highly specialized, rare capability.

    **8. Why are we querying BigQuery instead of live Keras inference?**  
    To move from "Experimental" to "Sovereign." Serving from the **Pre-computed Neural Manifold** ensures:
    *   **Zero Hallucination:** Every trip has been geographically validated (The Spatial Firewall).
    *   **Sub-second Latency:** Bypassing the Keras boot-time allows for a VVS1-grade user experience.
    *   **Infinite Stability:** Eliminating the RAM-heavy neural backend ensures the simulator never crashes during a high-stakes demonstration.
    """)