import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import time
import os

# --- LOCAL UTILITIES ---
from utils.gcp_client import load_cgan_assets
from utils.bq_client import fetch_data_from_bq

# --- PAGE CONFIG ---
st.set_page_config(page_title="cGAN Engine | Pienza", page_icon="🏭", layout="wide", initial_sidebar_state="collapsed")

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
# 2. EXTRACT SWITCHES & SEMANTIC MAPPING
# ==============================================================================
raw_days = list(label_encoders['day_of_week'].classes_)
chrono_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_pool = sorted(raw_days, key=lambda d: chrono_order.index(d))
# Extract and Sort Hours Chronologically
raw_hours = list(label_encoders['hour_of_day'].classes_)
hours_pool = sorted(raw_hours, key=lambda x: int(x))
# Formatter to make them look like "05:00 Hrs"
def format_hour(h): 
    return f"{int(h):02d}:00 Hrs"
products_pool = list(label_encoders['product_category_fk'].classes_)
product_map = {
    1: "X", '1': "X",
    2: "Mid-Tier", '2': "Mid-Tier",
    3: "Premium", '3': "Premium"
}

def format_product(p):
    return product_map.get(p, f"Unknown Tier ({p})")

# Extract Zones, explicitly dropping 'unassigned' and asymmetric 'C_' dropoff zones
pickups_pool = [z for z in label_encoders['pickup_zone_id'].classes_ if 'unassigned' not in str(z).lower()]
dropoffs_pool = [z for z in label_encoders['dropoff_zone_id'].classes_ if 'unassigned' not in str(z).lower() and not str(z).startswith('C_')]

# ==============================================================================
# Build Semantic Dictionaries for the UI (ID -> Human Name)
# ==============================================================================
dict_pick = dict(zip(dim_pick['zone_key'], dim_pick['semantic_name']))
dict_drop = dict(zip(dim_drop['zone_key'], dim_drop['semantic_name']))

def format_pickup(zone_id): 
    return dict_pick.get(zone_id, f"Unknown Zone ({zone_id})")

def format_dropoff(zone_id): 
    return dict_drop.get(zone_id, f"Unknown Zone ({zone_id})")

# Sort the pools alphabetically based on their semantic UI names
pickups_pool = sorted(pickups_pool, key=lambda x: format_pickup(x).lower())
dropoffs_pool = sorted(dropoffs_pool, key=lambda x: format_dropoff(x).lower())

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
    sel_pickups = pickups_pool if all_pickups else st.multiselect("Select Pickups", pickups_pool, format_func=format_pickup, default=[])

with c5:
    all_dropoffs = st.toggle("🏁 All Dropoff Zones", value=True)
    sel_dropoffs = dropoffs_pool if all_dropoffs else st.multiselect("Select Dropoffs", dropoffs_pool, format_func=format_dropoff, default=[])

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
# 4. THE INVISIBLE BACKEND (EXECUTION)
# ==============================================================================
if ignite_forge:
    start_time = time.time()
    
    def format_sql_list(lst):
        return ", ".join([f"'{str(x)}'" for x in lst])
    
    with st.status("Initiating Pienza Pipeline...", expanded=True) as status:
        
        # --- STEP A: Fetch Contextual Seeds ---
        st.write("📡 Fetching contextual seeds from BigQuery based on your switches...")
        
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

        # --- SAFETY LOGIC & SMART CLUTCH ---
        num_seeds = len(df_context)
        
        if num_seeds == 0:
            status.update(label="No seeds found in BigQuery. Broaden your switches.", state="error")
            st.stop()

        if num_seeds < 10000:
            st.warning(f"⚠️ Niche Regime Detected: Only {num_seeds:,} historical seeds found. To prevent memory overload, we are generating exactly {num_seeds:,} trips (No Oversampling).")
            final_generation_volume = num_seeds
        else:
            final_generation_volume = n_trips
            if num_seeds < n_trips:
                st.write(f"⚠️ Oversampling to reach {n_trips:,} from {num_seeds:,} seeds...")
                df_context = df_context.sample(n=n_trips, replace=True).reset_index(drop=True)

        # --- STEP B: Neural Synthesis (Keras) ---
        st.write("🧠 Synthesizing physical reality via Keras Generator...")
        
        encoded_inputs = []
        for col in SWITCH_COLS:
            le = label_encoders[col]
            known_classes = set(le.classes_)
            safe_data = df_context[col].astype(str).apply(lambda x: x if x in known_classes else le.classes_[0])
            encoded_inputs.append(tf.convert_to_tensor(le.transform(safe_data).reshape(-1, 1), dtype=tf.float32))
            
        noise = tf.random.normal([final_generation_volume, LATENT_DIM])
        fake_physics = generator([noise] + encoded_inputs, training=False)
        df_synth_physics = pd.DataFrame(fake_physics.numpy(), columns=PHYSICS_COLS)
        
        # --- STEP C: Inverse Transformation ---
        st.write("📏 Denormalizing physical limits and executing Log-Inversions...")
        df_synth_physics[PHYSICS_COLS] = physics_scaler.inverse_transform(df_synth_physics[PHYSICS_COLS])
        df_synth_physics['upfront_fare'] = np.expm1(df_synth_physics['upfront_fare'])
        df_synth_physics['est_trip_dist_km'] = np.expm1(df_synth_physics['est_trip_dist_km'])
        
        df_manifold = pd.concat([df_context.reset_index(drop=True), df_synth_physics.reset_index(drop=True)], axis=1)
        
        # --- STEP D: Fetch Downscaling Weights ---
        st.write("🗺️ Fetching topological weights for micro-downscaling...")
        query_pickups = f"SELECT pickup_id_GAN AS pickup_zone_id, pickup_name_down AS pickup_micro_name, COUNT(*) as hist_pickups FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled` GROUP BY 1, 2"
        query_dropoffs = f"SELECT dropoff_id_GAN AS dropoff_zone_id, dropoff_name_down AS dropoff_micro_name, COUNT(*) as hist_dropoffs FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled` GROUP BY 1, 2"
        
        df_hist_pickups = fetch_data_from_bq(query_pickups)
        df_hist_dropoffs = fetch_data_from_bq(query_dropoffs)
        
        # --- STEP E: Downscaling Math ---
        st.write("⚖️ Executing deterministic downscaling math...")
        
        # Pickups
        df_hist_pickups['macro_total'] = df_hist_pickups.groupby('pickup_zone_id')['hist_pickups'].transform('sum')
        df_hist_pickups['weight'] = df_hist_pickups['hist_pickups'] / df_hist_pickups['macro_total']
        gan_p = df_manifold.groupby('pickup_zone_id').size().reset_index(name='gan_pickups')
        downscale_p = pd.merge(df_hist_pickups, gan_p, on='pickup_zone_id', how='outer').fillna({'weight': 1.0, 'gan_pickups': 0})
        downscale_p['micro_gan_pickups'] = (downscale_p['gan_pickups'] * downscale_p['weight']).round(0).astype(int)
        
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
        st.write("💉 Injecting semantic identities into the final manifold...")
        p_pool = downscale_p.loc[downscale_p.index.repeat(downscale_p['micro_gan_pickups'])][['pickup_zone_id', 'pickup_micro_name']].sample(frac=1).reset_index(drop=True)
        d_pool = downscale_d.loc[downscale_d.index.repeat(downscale_d['micro_gan_dropoffs'])][['dropoff_zone_id', 'dropoff_micro_name']].sample(frac=1).reset_index(drop=True)
        
        df_manifold = df_manifold.sort_values('pickup_zone_id').reset_index(drop=True)
        df_manifold['pickup_name_down'] = p_pool['pickup_micro_name'].values[:final_generation_volume]
        
        df_manifold = df_manifold.sort_values('dropoff_zone_id').reset_index(drop=True)
        df_manifold['dropoff_name_down'] = d_pool['dropoff_micro_name'].values[:final_generation_volume]
        
        df_manifold = df_manifold.sample(frac=1).reset_index(drop=True)
        status.update(label=f"Synthesis Complete! {final_generation_volume:,} trips generated.", state="complete", expanded=False)
        
    # ==============================================================================
    # 5. RESULTS & DASHBOARD
    # ==============================================================================
    st.success(f"Successfully minted **{final_generation_volume:,}** hyper-realistic trips in {time.time() - start_time:.2f} seconds.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Avg Fare Synthesized", f"${df_manifold['upfront_fare'].mean():.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Avg Trip Distance", f"{df_manifold['est_trip_dist_km'].mean():.1f} km")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Avg Time to Pickup", f"{df_manifold['time_to_pickup_sec'].mean()/60:.1f} min")
        st.markdown('</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("Unique Micro-Zones", f"{df_manifold['dropoff_name_down'].nunique()}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🧬 Synthetic Manifold (Sample View)")
    display_cols = ['pickup_name_down', 'dropoff_name_down', 'upfront_fare', 'est_trip_dist_km', 'time_to_pickup_sec', 'hour_of_day']
    st.dataframe(df_manifold[display_cols].head(50), use_container_width=True)
    
    st.markdown("### 📊 Topological Gravity (Top Micro-Destinations)")
    top_destinations = df_manifold['dropoff_name_down'].value_counts().head(15)
    st.bar_chart(top_destinations, color="#21918c")

    # ==============================================================================
    # 6. THE PHILOSOPHY OF THE cGAN (THEORY VAULT)
    # ==============================================================================
    st.markdown("---")
    with st.expander("📖 The Philosophy of the cGAN (Under the Hood)"):
        st.markdown("""
        **1. If I request 1 offer only with certain characteristics, how does the generator decide which one to throw at me?**  
        It doesn't "pick" an offer; it *synthesizes* one. The engine maps your constraints (e.g., 8:00 AM, UberX) alongside a 100-dimensional vector of pure mathematical noise. This noise collapses a wave of infinite possibilities into a single, concrete reality that obeys the physics of the Mexico City market.

        **2. Is it the same to request the same offer 1 million times sequentially, versus giving me a million of the same offer in one single request batch?**  
        Sequential requests take time because of network I/O, but batch requests process almost instantly through parallel matrix multiplication in the neural network. As you saw, synthesizing 50,000 trips takes mere seconds. 

        **3. Is it just a "random offer" from the distribution, meaning the generator does not keep track of what I have requested in the past?**  
        Exactly. The cGAN is completely Stateless (*Independent and Identically Distributed*). Trip #500 has absolutely zero knowledge of Trip #499. It drops 50,000 balls down a Plinko board simultaneously. 

        **4. What is the minimum sample size that approximates that perfect bell curve (the Law of Large Numbers)?**  
        To ensure the deterministic downscaling math doesn't break and the true topological distributions reveal themselves, the engine requires a minimum of **10,000** trips per run. 

        **5. Is the cGAN related to a Markov Chain in any way (e.g., the "canicas in a sack" analogy)?**  
        No. They are mathematical opposites. A Markov Chain models a sequential journey through time (where you go next depends on where you are now). The cGAN is an instantaneous snapshot of the entire marketplace frozen in time. To simulate an autonomous fleet, we use the cGAN to *build* the environment, and a Markov Decision Process (MDP) to *route* through it.

        **6. What are the philosophical and mathematical terms that distinguish classical statistics from generative models?**  
        Classical statistics (like our Phase 4 XGBoost) uses an **Analytic/Discriminative** approach: it predicts the past/present by drawing a boundary ($P(Y|X)$). Generative models use a **Synthetic/Generative** approach: they actualize the future by learning the joint distribution of everything ($P(X,Y)$) to create realities from scratch.

        **7. How do veteran classical statisticians react to cGANs, and what is the actual proficiency level in the industry?**  
        Classical statisticians often view them with skepticism because they lack P-Values and unbiased estimators (the "Black Box" problem). Furthermore, while the industry widely uses generative models for pixels and text, building a tabular cGAN that perfectly mimics the rigid physics of urban logistics is a highly specialized, rare capability. 
        """)