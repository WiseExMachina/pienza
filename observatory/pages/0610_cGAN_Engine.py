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
st.set_page_config(page_title="cGAN Engine | Pienza", page_icon="🏭", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Libre+Baskerville', serif !important; color: #1E3D3D; }
    .metric-box { background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #440154; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏭 The cGAN Engine (Invisible Backend)")
st.markdown("""
Welcome to the Generative Forge. This engine bypasses pre-computed tables, allowing you to synthesize 
**net-new, hyper-realistic ride-hailing demand** on the fly. The neural network generates the physical forces 
(Fare, Time, Distance), while the deterministic downscaler ensures topological precision at the neighborhood level.
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
# 2. SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Forge Parameters")
    st.markdown("Set the synthesis volume. *Minimum 10,000 trips required to maintain mathematical integrity during downscaling.*")
    
    n_trips = st.slider("Target Volume (N)", min_value=10000, max_value=250000, step=10000, value=50000)
    
    st.markdown("---")
    ignite_forge = st.button("🔥 IGNITE THE FORGE", use_container_width=True, type="primary")

# ==============================================================================
# 3. THE INVISIBLE BACKEND (EXECUTION)
# ==============================================================================
if ignite_forge:
    start_time = time.time()
    
    # ---------------------------------------------------------
    # STEP A: Fetch Contextual Seeds
    # ---------------------------------------------------------
    with st.status("Initiating Pienza Pipeline...", expanded=True) as status:
        
        st.write("📡 Fetching contextual seeds from BigQuery...")
        # Query a random sample of actual contexts to feed the Generator
        query_seeds = f"""
            SELECT hour_of_day, day_of_week, product_category_fk, 
                   pickup_id_GAN AS pickup_zone_id, dropoff_id_GAN AS dropoff_zone_id, reason_primary_fk
            FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled`
            ORDER BY RAND() 
            LIMIT {n_trips}
        """
        df_context = fetch_data_from_bq(query_seeds)
        
        # Check if query returned data
        if df_context.empty:
            status.update(label="Failed to fetch seeds from BigQuery.", state="error")
            st.stop()

        # ---------------------------------------------------------
        # STEP B: Neural Synthesis (Keras)
        # ---------------------------------------------------------
        st.write("🧠 Synthesizing physical reality via Keras Generator...")
        
        # Encode contexts for the model
        encoded_inputs = []
        for col in SWITCH_COLS:
            le = label_encoders[col]
            # Handle unseen labels gracefully, though sampling from the same table should prevent this
            known_classes = set(le.classes_)
            safe_data = df_context[col].astype(str).apply(lambda x: x if x in known_classes else le.classes_[0])
            encoded_inputs.append(tf.convert_to_tensor(le.transform(safe_data).reshape(-1, 1), dtype=tf.float32))
            
        noise = tf.random.normal([n_trips, LATENT_DIM])
        
        # Inference!
        fake_physics = generator([noise] + encoded_inputs, training=False)
        df_synth_physics = pd.DataFrame(fake_physics.numpy(), columns=PHYSICS_COLS)
        
        # ---------------------------------------------------------
        # STEP C: Inverse Transformation (Denormalization)
        # ---------------------------------------------------------
        st.write("📏 Denormalizing physical limits and executing Log-Inversions...")
        df_synth_physics[PHYSICS_COLS] = physics_scaler.inverse_transform(df_synth_physics[PHYSICS_COLS])
        
        # Invert Logarithms for Fare and Distance (Based on Notebook 6.11 logic)
        df_synth_physics['upfront_fare'] = np.expm1(df_synth_physics['upfront_fare'])
        df_synth_physics['est_trip_dist_km'] = np.expm1(df_synth_physics['est_trip_dist_km'])
        
        # Combine Context and Physics
        df_manifold = pd.concat([df_context.reset_index(drop=True), df_synth_physics.reset_index(drop=True)], axis=1)
        
        # ---------------------------------------------------------
        # STEP D: Fetch Downscaling Weights (BigQuery)
        # ---------------------------------------------------------
        st.write("🗺️ Fetching topological weights for micro-downscaling...")
        
        query_pickups = f"""
            SELECT pickup_id_GAN AS pickup_zone_id, pickup_name_down AS pickup_micro_name, COUNT(*) as hist_pickups
            FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled`
            GROUP BY 1, 2
        """
        query_dropoffs = f"""
            SELECT dropoff_id_GAN AS dropoff_zone_id, dropoff_name_down AS dropoff_micro_name, COUNT(*) as hist_dropoffs
            FROM `{PROJECT_ID}.pienza_big.synthetic_manifold_v8_downscaled`
            GROUP BY 1, 2
        """
        
        df_hist_pickups = fetch_data_from_bq(query_pickups)
        df_hist_dropoffs = fetch_data_from_bq(query_dropoffs)
        
        # ---------------------------------------------------------
        # STEP E: The Downscaling Math (Outer Join + Rounding)
        # ---------------------------------------------------------
        st.write("⚖️ Executing deterministic downscaling math...")
        
        # PICKUPS
        df_hist_pickups['macro_total'] = df_hist_pickups.groupby('pickup_zone_id')['hist_pickups'].transform('sum')
        df_hist_pickups['weight'] = df_hist_pickups['hist_pickups'] / df_hist_pickups['macro_total']
        
        gan_p = df_manifold.groupby('pickup_zone_id').size().reset_index(name='gan_pickups')
        downscale_p = pd.merge(df_hist_pickups, gan_p, on='pickup_zone_id', how='outer').fillna({'weight': 1.0, 'gan_pickups': 0})
        downscale_p['pickup_micro_name'] = downscale_p['pickup_micro_name'].fillna(downscale_p['pickup_zone_id'])
        
        downscale_p['micro_gan_pickups'] = (downscale_p['gan_pickups'] * downscale_p['weight']).round(0).astype(int)
        
        # Adjust Rounding Deltas
        diff_p = int(n_trips - downscale_p['micro_gan_pickups'].sum())
        if diff_p != 0:
            max_idx = downscale_p['micro_gan_pickups'].idxmax()
            downscale_p.loc[max_idx, 'micro_gan_pickups'] += diff_p

        # DROPOFFS
        df_hist_dropoffs['macro_total'] = df_hist_dropoffs.groupby('dropoff_zone_id')['hist_dropoffs'].transform('sum')
        df_hist_dropoffs['weight'] = df_hist_dropoffs['hist_dropoffs'] / df_hist_dropoffs['macro_total']
        
        gan_d = df_manifold.groupby('dropoff_zone_id').size().reset_index(name='gan_dropoffs')
        downscale_d = pd.merge(df_hist_dropoffs, gan_d, on='dropoff_zone_id', how='outer').fillna({'weight': 1.0, 'gan_dropoffs': 0})
        downscale_d['dropoff_micro_name'] = downscale_d['dropoff_micro_name'].fillna(downscale_d['dropoff_zone_id'])
        
        downscale_d['micro_gan_dropoffs'] = (downscale_d['gan_dropoffs'] * downscale_d['weight']).round(0).astype(int)
        
        diff_d = int(n_trips - downscale_d['micro_gan_dropoffs'].sum())
        if diff_d != 0:
            max_idx = downscale_d['micro_gan_dropoffs'].idxmax()
            downscale_d.loc[max_idx, 'micro_gan_dropoffs'] += diff_d
            
        # ---------------------------------------------------------
        # STEP F: Stochastic Identity Injection
        # ---------------------------------------------------------
        st.write("💉 Injecting semantic identities into the final manifold...")
        
        # Create Pools
        p_pool = downscale_p.loc[downscale_p.index.repeat(downscale_p['micro_gan_pickups'])][['pickup_zone_id', 'pickup_micro_name']].sample(frac=1).reset_index(drop=True)
        d_pool = downscale_d.loc[downscale_d.index.repeat(downscale_d['micro_gan_dropoffs'])][['dropoff_zone_id', 'dropoff_micro_name']].sample(frac=1).reset_index(drop=True)
        
        # Sort to map safely, inject, then shuffle
        df_manifold = df_manifold.sort_values('pickup_zone_id').reset_index(drop=True)
        p_pool = p_pool.sort_values('pickup_zone_id').reset_index(drop=True)
        df_manifold['pickup_name_down'] = p_pool['pickup_micro_name'].values
        
        df_manifold = df_manifold.sort_values('dropoff_zone_id').reset_index(drop=True)
        d_pool = d_pool.sort_values('dropoff_zone_id').reset_index(drop=True)
        df_manifold['dropoff_name_down'] = d_pool['dropoff_micro_name'].values
        
        # Final Shuffle
        df_manifold = df_manifold.sample(frac=1).reset_index(drop=True)
        
        status.update(label=f"Synthesis Complete! {n_trips:,} trips generated.", state="complete", expanded=False)
        
    # ==============================================================================
    # 4. RESULTS & DASHBOARD
    # ==============================================================================
    st.success(f"Successfully minted **{n_trips:,}** hyper-realistic trips in {time.time() - start_time:.2f} seconds.")
    
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
    # Show user-friendly columns first
    display_cols = ['pickup_name_down', 'dropoff_name_down', 'upfront_fare', 'est_trip_dist_km', 'time_to_pickup_sec', 'hour_of_day']
    st.dataframe(df_manifold[display_cols].head(50), use_container_width=True)
    
    st.markdown("### 📊 Topological Gravity (Top Micro-Destinations)")
    # Simple bar chart of top destinations
    top_destinations = df_manifold['dropoff_name_down'].value_counts().head(15)
    st.bar_chart(top_destinations, color="#21918c")

    st.info("""If I request 1 offer only with certain characteristics, how does the generator decide which one to throw at me?Is it the same (or different) to request the same offer 1 million times sequentially, versus giving me a million of the same offer in one single request batch?Is it just a "random offer" from the distribution, meaning the generator does not keep track of what I have requested in the past to make sure I get the full distribution or the whole spectrum of the marketplace?What is the minimum sample size that approximates that perfect bell curve (the Law of Large Numbers convergence) we talked about?Is the cGAN related to a Markov Chain in any way (e.g., the "canicas in a sack" analogy with sequential states and replacement)?What are the philosophical and mathematical terms that distinguish classical statistics (predicting $Y$ / the past) from generative models (creating the future)?How do veteran classical statisticians react to cGANs, and what is the actual proficiency level of academia and ML practitioners regarding generative tabular models?""")
    