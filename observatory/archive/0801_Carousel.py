import streamlit as st
from streamlit_carousel import carousel

# ==========================================
# CAROUSEL 1: Third-Party Component
# ==========================================
# Note: Requires `pip install streamlit-carousel`
carousel_items = [
    {
        "title": "Phase 1: Generative Manifold",
        "text": "1,000,000-row synthetic market physics.",
        "img": "https://via.placeholder.com/800x400/000000/FFFFFF/?text=Manifold",
    },
    {
        "title": "Phase 2: AV Sandbox",
        "text": "Volatility injection and surge mechanics.",
        "img": "https://via.placeholder.com/800x400/000000/FFFFFF/?text=AV+Sandbox",
    }
]

st.subheader("System Architecture Flows (Third-Party)")
carousel(items=carousel_items, width=1)


st.divider()


# ==========================================
# CAROUSEL 2: Native State-Driven (Instance 1)
# ==========================================
st.subheader("Native Carousel: Instance 1")

# 1. UNIQUE STATE VARIABLE: 'carousel_idx_1'
if 'carousel_idx_1' not in st.session_state:
    st.session_state.carousel_idx_1 = 0

assets_1 = [
    {"caption": "Layer 1: Filtering Noise", "data": "Visualizing deterministic bounds..."},
    {"caption": "Layer 2: Nuance Engine", "data": "Evaluating the Sunk Cost Mechanic..."},
    {"caption": "Layer 3: Generative Gap", "data": "Injecting localized volatility..."}
]

col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    # 2. UNIQUE KEY: "prev_btn_1"
    if st.button("◀", key="prev_btn_1"):
        st.session_state.carousel_idx_1 = (st.session_state.carousel_idx_1 - 1) % len(assets_1)

with col3:
    # 2. UNIQUE KEY: "next_btn_1"
    if st.button("▶", key="next_btn_1"):
        st.session_state.carousel_idx_1 = (st.session_state.carousel_idx_1 + 1) % len(assets_1)

current_asset_1 = assets_1[st.session_state.carousel_idx_1]

with col2:
    st.markdown(f"### {current_asset_1['caption']}")
    st.info(current_asset_1['data'])
    st.progress((st.session_state.carousel_idx_1 + 1) / len(assets_1))


st.divider()


# ==========================================
# CAROUSEL 3: Native State-Driven (Instance 2)
# ==========================================
st.subheader("Native Carousel: Instance 2")

# 1. UNIQUE STATE VARIABLE: 'carousel_idx_2'
if 'carousel_idx_2' not in st.session_state:
    st.session_state.carousel_idx_2 = 0

# (I changed the mock data slightly so you can see they act independently)
assets_2 = [
    {"caption": "Metric A: Spatial Accuracy", "data": "Validating the 42 Macro-Zones..."},
    {"caption": "Metric B: Temporal Pulse", "data": "Circadian rhythm alignment..."},
    {"caption": "Metric C: Financial Physics", "data": "Baseline fare preservation..."}
]

col4, col5, col6 = st.columns([1, 8, 1])

with col4:
    # 2. UNIQUE KEY: "prev_btn_2"
    if st.button("◀", key="prev_btn_2"):
        st.session_state.carousel_idx_2 = (st.session_state.carousel_idx_2 - 1) % len(assets_2)

with col6:
    # 2. UNIQUE KEY: "next_btn_2"
    if st.button("▶", key="next_btn_2"):
        st.session_state.carousel_idx_2 = (st.session_state.carousel_idx_2 + 1) % len(assets_2)

current_asset_2 = assets_2[st.session_state.carousel_idx_2]

with col5:
    st.markdown(f"### {current_asset_2['caption']}")
    st.info(current_asset_2['data'])
    st.progress((st.session_state.carousel_idx_2 + 1) / len(assets_2))