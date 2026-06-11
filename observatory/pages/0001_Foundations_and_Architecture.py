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






import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Approach 3: HTML Injection", layout="centered")

st.header("Approach #3: The Browser Brain (HTML/CSS Injection)")
st.markdown("""
This carousel runs entirely inside an invisible HTML `iframe`. It uses a professional web library called **Swiper.js**. 

**Try it out:** Click and drag with your mouse to swipe between the slides. Notice how perfectly smooth the animation is compared to the native Python state approach, and how it auto-plays in the background!
""")

st.divider()

# ==========================================
# THE HTML / CSS / JS PAYLOAD
# ==========================================
# We define the raw web code as a massive Python string.
custom_carousel_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Swiper Carousel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">
    
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
    
    <style>
    html, body {
        position: relative;
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: transparent; /* Matches Streamlit's background */
    }
    .swiper {
        width: 100%;
        height: 400px;
        border-radius: 12px;
    }
    .swiper-slide {
        text-align: center;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .slide-content {
        padding: 40px;
    }
    .slide-content h2 {
        margin-top: 0;
        color: #1f1f1f;
        font-size: 28px;
    }
    .slide-content p {
        color: #555;
        font-size: 18px;
        line-height: 1.5;
    }
    /* Customizing the arrows and dots to match your UI */
    .swiper-button-next, .swiper-button-prev {
        color: #2c3e50;
    }
    .swiper-pagination-bullet-active {
        background: #2c3e50;
    }
    </style>
</head>
<body>

    <div class="swiper mySwiper">
        <div class="swiper-wrapper">
            
            <div class="swiper-slide">
                <div class="slide-content">
                    <h2>🔍 Layer 1: The Filter</h2>
                    <p>Surgically isolating deterministic noise from nuanced strategic intent using an optimized 0.40 threshold.</p>
                </div>
            </div>
            
            <div class="swiper-slide">
                <div class="slide-content">
                    <h2>🧠 Layer 2: Nuance Engine</h2>
                    <p>Mapping complex behavioral mechanics like the Sunk Cost Fallacy and Target Income heuristics.</p>
                </div>
            </div>
            
            <div class="swiper-slide">
                <div class="slide-content">
                    <h2>🧬 SHAP DNA Atlas</h2>
                    <p>Quantifying the non-linear psychological shifts of the expert agent from empirical telemetry.</p>
                </div>
            </div>

        </div>
        
        <div class="swiper-pagination"></div>
        <div class="swiper-button-next"></div>
        <div class="swiper-button-prev"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

    <script>
    var swiper = new Swiper(".mySwiper", {
        spaceBetween: 30,
        centeredSlides: true,
        loop: true,
        grabCursor: true, /* Turns the mouse into a grab hand! */
        autoplay: {
            delay: 3500,
            disableOnInteraction: false,
        },
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });
    </script>
</body>
</html>
"""

# ==========================================
# INJECT INTO STREAMLIT
# ==========================================
# We pass the giant string into Streamlit's HTML component builder.
# We set the height slightly larger than the CSS height to avoid scrollbars.
components.html(custom_carousel_html, height=450)

st.divider()
st.info("💡 **The Catch:** Because this is running inside its own web container, you cannot put Streamlit widgets (like `st.plotly_chart` or `st.dataframe`) inside these slides. You can only use standard web images and text!")