import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os
import gc

# --- LOCAL UTILITIES ---
from utils.gcp_client import load_cgan_assets
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
# 1. LOAD ML ARTIFACTS
# ==============================================================================
generator, physics_scaler, label_encoders, dim_prod, dim_drop, dim_pick = load_cgan_assets()

if generator is None:
    st.error("🚨 Critical Failure: Could not load cGAN artifacts from GCP Vault. Check credentials and paths.")
    st.stop()

# Constants
LATENT_DIM = 100
SWITCH_COLS = ['hour_of_day', 'day_of_week', 'product_category_fk', 'dropoff_zone_id', 'pickup_zone_id', 'reason_primary_fk']
PHYSICS_COLS = ['upfront_fare', 'est_trip_time_sec', 'est_trip_dist_km', 'time_to_pickup_sec', 'dist_to_pickup_km']
PROJECT_ID = "drivers-dilemma" # Ensure this matches your BQ project


# ==============================================================================
# 2. EXTRACT SWITCHES & MICRO-SEMANTIC MAPPING
# ==============================================================================
# --- Chronological Handlers ---
chrono_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_pool = sorted(list(label_encoders['day_of_week'].classes_), key=lambda d: chrono_order.index(d))
hours_pool = sorted(list(label_encoders['hour_of_day'].classes_), key=lambda x: int(x))
def format_hour(h): return f"{int(h):02d}:00 Hrs"

# --- Product Handlers ---
products_pool = list(label_encoders['product_category_fk'].classes_)
product_map = {1: "X", '1': "X", 2: "Mid-Tier", '2': "Mid-Tier", 3: "Premium", '3': "Premium"}
def format_product(p): return product_map.get(p, f"Unknown Tier ({p})")

# --- GEOGRAPHIC MICRO-MAPPING (The Loophole Fix) ---
# A. Create the Reverse Dictionaries (Name -> ID)
rev_dict_pick = dict(zip(dim_pick['semantic_name'], dim_pick['zone_key']))
rev_dict_drop = dict(zip(dim_drop['semantic_name'], dim_drop['zone_key']))

# B. Create the UI Pools (Strict Sovereign Theatre)
# We filter out any name containing 'unassigned' and only allow 'P_' macro parents.
pickups_pool = sorted([
    n for n in dim_pick[dim_pick['zone_key'].str.startswith('P_')]['semantic_name'].unique() 
    if "unassigned" not in str(n).lower()
])

dropoffs_pool = sorted([
    n for n in dim_drop[dim_drop['zone_key'].str.startswith('P_')]['semantic_name'].unique() 
    if "unassigned" not in str(n).lower()
])

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
st.markdown("### ⚙️ Production Constraints")
n_trips = st.slider(
    "Target Volume (N)", 
    min_value=10000, 
    max_value=50000, 
    value=50000, 
    step=5000, 
    help="Minimum 10,000 trips required to maintain the Law of Large Numbers and statistical integrity during deterministic micro-downscaling."
)

st.markdown("<br>", unsafe_allow_html=True)
ignite_forge = st.button("🔥 IGNITE THE FORGE", use_container_width=True, type="primary")

# --- Safety Check: Ensure no switch is completely empty ---
if ignite_forge:
    if not all([sel_days, sel_hours, sel_products, sel_pickups, sel_dropoffs]):
        st.warning("⚠️ **Generative Starvation Risk:** You must have at least one option selected in every active switch box. The generator cannot synthesize a reality out of nothing.")
        st.stop()


# ==============================================================================
# 4. THE SOVEREIGN FORGE (REVERTED TO SQL-SEED CONSTRAINTS)
# ==============================================================================
if ignite_forge:
    start_time = time.time()
    
    def format_sql_list(lst):
        return ", ".join([f"'{str(x)}'" for x in lst])
    
    with st.status("Initiating Sovereign Pipeline...", expanded=True) as status:
        
        # --- STEP A: Fetch Contextual Seeds (The Skeleton) ---
        # This ensures O-D pairs are geographically valid
        st.write("📡 Fetching historical regimes from BigQuery...")
        
        query_seeds = f"""
            SELECT hour_of_day, day_of_week, product_category_fk, 
                   pickup_id_GAN AS pickup_zone_id, dropoff_id_GAN AS dropoff_zone_id, reason_primary_fk
            FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled`
            WHERE day_of_week IN ({format_sql_list(sel_days)})
              AND CAST(hour_of_day AS STRING) IN ({format_sql_list(sel_hours)})
              AND product_category_fk IN ({format_sql_list(sel_products)})
              AND pickup_id_GAN IN ({format_sql_list(sel_pickups)})
              AND dropoff_id_GAN IN ({format_sql_list(sel_dropoffs)})
            ORDER BY RAND() 
            LIMIT {n_trips}
        """
        df_context = fetch_data_from_bq(query_seeds)

        num_seeds = len(df_context)
        if num_seeds == 0:
            status.update(label="No seeds found in BigQuery. Broaden your switches.", state="error")
            st.stop()

        # Handle Niche Regimes via Oversampling
        if num_seeds < n_trips:
            st.write(f"⚠️ Oversampling to reach target volume...")
            df_context = df_context.sample(n=n_trips, replace=True).reset_index(drop=True)
            final_generation_volume = n_trips
        else:
            final_generation_volume = num_seeds

        # --- STEP B: Neural Synthesis (Keras) ---
        st.write("🧠 Hallucinating physical forces via Keras...")
        
        encoded_inputs = []
        for col in SWITCH_COLS:
            le = label_encoders[col]
            # Safety: ensuring labels exist in encoder
            known_classes = set(le.classes_)
            safe_data = df_context[col].astype(str).apply(lambda x: x if x in known_classes else le.classes_[0])
            encoded_inputs.append(tf.convert_to_tensor(le.transform(safe_data).reshape(-1, 1), dtype=tf.float32))
            
        noise = tf.random.normal([final_generation_volume, LATENT_DIM])
        fake_physics = generator([noise] + encoded_inputs, training=False)
        df_synth_physics = pd.DataFrame(fake_physics.numpy(), columns=PHYSICS_COLS)
        
        # --- STEP C: Inverse Transformation ---
        st.write("📏 Executing Log-Inversions...")
        df_synth_physics[PHYSICS_COLS] = physics_scaler.inverse_transform(df_synth_physics[PHYSICS_COLS])
        df_synth_physics['upfront_fare'] = np.expm1(df_synth_physics['upfront_fare'])
        df_synth_physics['est_trip_dist_km'] = np.expm1(df_synth_physics['est_trip_dist_km'])
        
        df_manifold = pd.concat([df_context.reset_index(drop=True), df_synth_physics.reset_index(drop=True)], axis=1)
        
        # --- STEP D: Fetch Downscaling Weights ---
        st.write("🗺️ Fetching topological weights...")
        query_pickups = f"SELECT pickup_id_GAN AS pickup_zone_id, pickup_name_down AS pickup_micro_name, COUNT(*) as hist_pickups FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled` GROUP BY 1, 2"
        query_dropoffs = f"SELECT dropoff_id_GAN AS dropoff_zone_id, dropoff_name_down AS dropoff_micro_name, COUNT(*) as hist_dropoffs FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled` GROUP BY 1, 2"
        
        df_hist_pickups = fetch_data_from_bq(query_pickups)
        df_hist_dropoffs = fetch_data_from_bq(query_dropoffs)
        
        # --- STEP E: Downscaling Math ---
        st.write("⚖️ Executing deterministic downscaling...")
        # Pickups
        df_hist_pickups['macro_total'] = df_hist_pickups.groupby('pickup_zone_id')['hist_pickups'].transform('sum')
        df_hist_pickups['weight'] = df_hist_pickups['hist_pickups'] / df_hist_pickups['macro_total']
        gan_p = df_manifold.groupby('pickup_zone_id').size().reset_index(name='gan_pickups')
        downscale_p = pd.merge(df_hist_pickups, gan_p, on='pickup_zone_id', how='outer').fillna({'weight': 1.0, 'gan_pickups': 0})
        downscale_p['micro_gan_pickups'] = (downscale_p['gan_pickups'] * downscale_p['weight']).round(0).astype(int)
        
        # Adjust rounding diffs
        diff_p = int(final_generation_volume - downscale_p['micro_gan_pickups'].sum())
        if diff_p != 0: downscale_p.loc[downscale_p['micro_gan_pickups'].idxmax(), 'micro_gan_pickups'] += diff_p

        # Dropoffs
        df_hist_dropoffs['macro_total'] = df_hist_dropoffs.groupby('dropoff_zone_id')['hist_dropoffs'].transform('sum')
        df_hist_dropoffs['weight'] = df_hist_dropoffs['hist_dropoffs'] / df_hist_dropoffs['macro_total']
        gan_d = df_manifold.groupby('dropoff_zone_id').size().reset_index(name='gan_dropoffs')
        downscale_d = pd.merge(df_hist_dropoffs, gan_d, on='dropoff_zone_id', how='outer').fillna({'weight': 1.0, 'gan_dropoffs': 0})
        downscale_d['micro_gan_dropoffs'] = (downscale_d['gan_dropoffs'] * downscale_d['weight']).round(0).astype(int)
        
        diff_d = int(final_generation_volume - downscale_d['micro_gan_dropoffs'].sum())
        if diff_d != 0: downscale_d.loc[downscale_d['micro_gan_dropoffs'].idxmax(), 'micro_gan_dropoffs'] += diff_d
            
        # --- STEP F: Stochastic Identity Injection ---
        st.write("💉 Injecting semantic identities...")
        p_pool = downscale_p.loc[downscale_p.index.repeat(downscale_p['micro_gan_pickups'])][['pickup_zone_id', 'pickup_micro_name']].sample(frac=1).reset_index(drop=True)
        d_pool = downscale_d.loc[downscale_d.index.repeat(downscale_d['micro_gan_dropoffs'])][['dropoff_zone_id', 'dropoff_micro_name']].sample(frac=1).reset_index(drop=True)
        
        df_manifold = df_manifold.sort_values('pickup_zone_id').reset_index(drop=True)
        df_manifold['pickup_name_down'] = p_pool['pickup_micro_name'].values[:final_generation_volume]
        
        df_manifold = df_manifold.sort_values('dropoff_zone_id').reset_index(drop=True)
        df_manifold['dropoff_name_down'] = d_pool['dropoff_micro_name'].values[:final_generation_volume]
        
        # --- STEP G: PERSIST TO SESSION STATE ---
        st.session_state.df_manifold = df_manifold.sample(frac=1).reset_index(drop=True)
        
        status.update(label=f"Synthesis Complete! {final_generation_volume:,} trips generated.", state="complete", expanded=False)

# ==============================================================================
# 5. THE MANIFOLD ANALYTICS SUITE (PERSISTENT & DYNAMIC)
# ==============================================================================

# This block only executes if the Forge has been ignited at least once in the session
if st.session_state.df_manifold is not None:
    
    # Extract data from persistent session memory
    df_active = st.session_state.df_manifold.copy()

    # --- 5.1 PRE-PROCESSING FOR DISPLAY (Refreshes on every UI change) ---
    # A. Unit Conversion & Labeling
    df_active['TTP (min)'] = (df_active['time_to_pickup_sec'] / 60)
    df_active['Trip Time (min)'] = (df_active['est_trip_time_sec'] / 60)
    df_active['Trip Dist (km)'] = df_active['est_trip_dist_km']
    df_active['Fare ($ MXN)'] = df_active['upfront_fare']
    df_active['Hour'] = df_active['hour_of_day'].apply(lambda x: f"{int(x):02d}:00")
    df_active['Product'] = df_active['product_category_fk'].map(product_map)

    # B. Micro-Zone Polishing (Using your specific Logic)
    df_active['Pickup'] = df_active['pickup_name_down'].str.replace('_', ' ').str.title()
    df_active['Dropoff'] = df_active['dropoff_name_down'].str.replace('_', ' ').str.title()

    # C. THE FINAL SOVEREIGN FILTER (Firewall against Unassigned Entropy)
    df_display = df_active[
        (~df_active['Pickup'].str.lower().str.contains('unassigned')) & 
        (~df_active['Dropoff'].str.lower().str.contains('unassigned'))
    ].copy()

    # D. Canonical Column Order
    canonical_cols = [
        'day_of_week', 'Hour', 'Product', 'Pickup', 'Dropoff', 
        'TTP (min)', 'Trip Dist (km)', 'Trip Time (min)', 'Fare ($ MXN)'
    ]
    df_display = df_display[canonical_cols] 

    st.markdown("---")
    # --- 5.2 METRIC HIGHLIGHTS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Avg Fare Synthesized", f"${df_display['Fare ($ MXN)'].mean():.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.metric("Avg Trip Distance", f"{df_display['Trip Dist (km)'].mean():.2f} km")
    with c3:
        st.metric("Avg Time to Pickup", f"{df_display['TTP (min)'].mean():.1f} min")
    with c4:
        st.metric("Sovereign Volume", f"{len(df_display):,}")

    st.markdown("<br>", unsafe_allow_html=True)

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
        # Map selection to actual columns
        agg_map = {
            "Hour of Day": "Hour",
            "Day of Week": "day_of_week",
            "Product": "Product",
            "Pickup Zone": "Pickup"
        }
        group_col = agg_map[agg_mode]
        
        # Calculate Mean for Physics, Count for Volume
        df_agg = df_display.groupby(group_col).agg({
            'Fare ($ MXN)': 'mean',
            'TTP (min)': 'mean',
            'Trip Dist (km)': 'mean',
            'Trip Time (min)': 'mean',
            'Product': 'count' # Use any col for volume count
        }).rename(columns={'Product': 'Volume (N)'})
        
        # Chronological Sort Enforcer
        if agg_mode == "Day of Week":
            df_agg = df_agg.reindex([d for d in chrono_order if d in df_agg.index])
        elif agg_mode == "Hour of Day":
            df_agg = df_agg.sort_index()
            
        # VVS1 Display with Heatmap on Volume
        st.dataframe(df_agg.style.format({
            'Fare ($ MXN)': '${:.2f}',
            'TTP (min)': '{:.2f}',
            'Trip Dist (km)': '{:.2f}',
            'Trip Time (min)': '{:.2f}',
            'Volume (N)': '{:,}'
        }).background_gradient(cmap="Purples", subset=['Volume (N)']), use_container_width=True)

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
    **1. If I request 1 offer only with certain characteristics, how does the generator decide which one to throw at me?**  
    It doesn't "pick" an offer; it *synthesizes* one... (content continues)

    **2. Is it the same to request the same offer 1 million times sequentially...?**  
    Sequential requests take time because... (content continues)
    
    ... (rest of your philosophy points)
    """)