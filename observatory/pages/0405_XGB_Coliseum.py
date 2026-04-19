import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
import io
from google.cloud import storage
from google.cloud import bigquery

# ==========================================
# 1. ASSET LOADING (GCP & BIGQUERY)
# ==========================================

@st.cache_resource
def load_cascade_brains_from_gcp(bucket_name, blob_name):
    """Downloads the joblib directly from GCP Bucket into memory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Download as bytes and load with joblib
    buffer = io.BytesIO()
    blob.download_to_file(buffer)
    buffer.seek(0)
    return joblib.load(buffer)

@st.cache_data
def get_session_data(session_id):
    """Queries BigQuery for a specific session joining offers and features."""
    client = bigquery.Client()
    query = f"""
    SELECT o.*, f.* 
    FROM `drivers-dilemma.pienza_mini.offers` o
    JOIN `drivers-dilemma.pienza_mini.engineered_features` f 
      ON o.offer_id = f.offer_id_fk
    WHERE o.session_fk = '{session_id}'
    ORDER BY o.offer_timestamp ASC
    """
    return client.query(query).to_dataframe()

# --- INITIALIZE BRAIN ---
# Replace with your actual GCP details
BUCKET = "pienza-streamlit"
BLOB = "260419_XGB_models.joblib"
brain = load_cascade_brains_from_gcp(BUCKET, BLOB)

# ==========================================
# 2. THE INFERENCE ENGINE (HONEST CORE)
# ==========================================

def coliseum_inference(row, brain):
    """
    Performs live inference for Human, Full, and Spartan.
    Matches the Notebook Preprocessing logic exactly.
    """
    # 1. PRE-PROCESSING (LOGS & SCALING)
    def preprocess(df_row, features, scaler):
        # Filter columns
        X = df_row[features].copy()
        # Log Transformations (The 'Fare/Sec/Km' Logic)
        skewed = ['fare', 'sec', 'km', 'index', 'earnings', 'volatility', 'amount']
        for col in X.columns:
            if any(key in col.lower() for key in skewed):
                X[col] = np.log1p(X[col].clip(lower=0))
        # Scale
        return scaler.transform(X)

    # 2. LAYER 1: THE BOUNCER (Wide Features)
    X_l1 = preprocess(row, brain['features_wide'], brain['scaler_wide'])
    l1_probs = brain['model_L1'].predict_proba(X_l1)[0]
    
    # Sync with L1 Classes
    l1_classes = brain['le_l1'].classes_
    nuanced_idx = np.where(l1_classes == "THE_NUANCED_REST")[0][0]
    
    # THE BOUNCER'S VERDICT
    p_nuanced = l1_probs[nuanced_idx]
    passed_l1 = p_nuanced >= brain['threshold_bouncer']
    l1_label = l1_classes[np.argmax(l1_probs)] if not passed_l1 else "AUTHORIZED"

    # 3. LAYER 2: THE DUEL (If authorized)
    full_decision = "TRIAGED"
    spartan_decision = "TRIAGED"
    
    if passed_l1:
        # Full Feature Inference
        X_l2_full = preprocess(row, brain['features_wide'], brain['scaler_wide'])
        full_idx = brain['model_L2_full'].predict(X_l2_full)[0]
        full_decision = brain['le_l2'].classes_[full_idx]

        # Spartan Inference
        X_l2_spartan = preprocess(row, brain['features_spartan'], brain['scaler_spartan'])
        spart_idx = brain['model_L2_lightweight'].predict(X_l2_spartan)[0]
        spartan_decision = brain['le_l2'].classes_[spart_idx]

    return {
        "l1_passed": passed_l1,
        "l1_label": l1_label,
        "full_decision": full_decision,
        "spartan_decision": spartan_decision,
        "p_nuanced": p_nuanced
    }

# ==========================================
# 3. THE ARENA UI (VERTICAL FUNNEL)
# ==========================================

st.title("🏟️ The Coliseum: Live Policy Duel")
st.markdown("---")

# --- SESSION STATE FOR PLAYBACK ---
if 'arena_idx' not in st.session_state:
    st.session_state.arena_idx = 0
if 'arena_running' not in st.session_state:
    st.session_state.arena_running = False

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Arena Master")
    session_id = st.selectbox("Select Week 6 Session:", [
        "S060 (Monday Sep 29)", "S061 (Tuesday Sep 30)", "S063 (Friday Oct 03)"
    ])
    speed = st.slider("Playback Speed", 0.1, 2.0, 0.5)
    
    if st.button("🚀 INITIATE TOURNAMENT"):
        st.session_state.arena_running = True
        st.session_state.arena_idx = 0

# --- DATA FETCH ---
df_session = get_session_data(session_id)

# --- THE DROP ZONE ---
c1, c2, c3 = st.columns([1, 1, 2])

with c1:
    st.subheader("📋 Queue")
    # Show next 5 offers
    queue_df = df_session.iloc[st.session_state.arena_idx : st.session_state.arena_idx+5]
    for _, r in queue_df.iterrows():
        st.caption(f"ID: {r['offer_id']} | ${r['upfront_fare']}")

with c2:
    st.subheader("🛡️ Bouncer")
    if st.session_state.arena_running:
        current_row = df_session.iloc[[st.session_state.arena_idx]]
        res = coliseum_inference(current_row, brain)
        
        if res['l1_passed']:
            st.success(f"AUTHORIZED\n(Prob: {res['p_nuanced']:.2%})")
        else:
            st.error(f"REJECTED:\n{res['l1_label']}")

with c3:
    st.subheader("🧠 Strategist Duel")
    if st.session_state.arena_running and res['l1_passed']:
        # 3-Way Bucket display
        bc1, bc2, bc3 = st.columns(3)
        with bc1: 
            st.info(f"Human\n**{current_row['reason_primary_description'].values[0]}**")
        with bc2: 
            st.warning(f"Full Feature\n**{res['full_decision']}**")
        with bc3: 
            st.error(f"Spartan\n**{res['spartan_decision']}**")

# --- PLAYBACK LOOP ---
if st.session_state.arena_running:
    if st.session_state.arena_idx < len(df_session) - 1:
        st.session_state.arena_idx += 1
        time.sleep(speed)
        st.rerun()
    else:
        st.session_state.arena_running = False
        st.balloons()