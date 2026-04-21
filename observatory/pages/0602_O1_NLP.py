import streamlit as st
import time
import requests

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Inference Engine Room", layout="wide")

# ==========================================
# INFERENCE FUNCTIONS (The Competitors)
# ==========================================

def get_google_maps_latency(address: str) -> tuple:
    """Makes a live call to the Google Maps Geocoding API and measures latency."""
    api_key = st.secrets["GCP_API_KEY"]
    # URL encode the address
    formatted_address = requests.utils.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
    
    start_time = time.perf_counter()
    
    try:
        response = requests.get(url, timeout=5) # 5 second timeout
        response.raise_for_status()
        data = response.json()
        
        # End timer immediately after payload is received
        end_time = time.perf_counter() 
        latency_ms = (end_time - start_time) * 1000
        
        if data['status'] == 'OK':
            # Extracting the formatted address or coordinates as the "result"
            result = data['results'][0]['formatted_address']
            return result, latency_ms
        else:
            return f"API Error: {data['status']}", latency_ms
            
    except requests.exceptions.RequestException as e:
        end_time = time.perf_counter()
        return f"Network Error", (end_time - start_time) * 1000

def get_minibeto_latency(address: str) -> tuple:
    """Executes the local 110M parameter BERT model."""
    start_time = time.perf_counter()
    
    # ---------------------------------------------------
    # TODO: INSERT YOUR PYTORCH/HUGGINGFACE INFERENCE HERE
    # input_ids = tokenizer(address, return_tensors="pt")
    # outputs = beto_model(**input_ids)
    # prediction = torch.argmax(outputs.logits)
    # ---------------------------------------------------
    
    time.sleep(0.045) # Placeholder simulating ~45ms compute
    end_time = time.perf_counter()
    
    return "del_valle_hub (84% conf)", (end_time - start_time) * 1000

def get_minibabel_latency(address: str) -> tuple:
    """Executes the custom 1.5M parameter Transformer."""
    start_time = time.perf_counter()
    
    # ---------------------------------------------------
    # TODO: INSERT YOUR CUSTOM TRANSFORMER INFERENCE HERE
    # signal = linguistic_pipeline(address)
    # prediction = minibabel_model(signal)
    # ---------------------------------------------------
    
    time.sleep(0.008) # Placeholder simulating ~8ms compute
    end_time = time.perf_counter()
    
    return "del_valle_hub (91% conf)", (end_time - start_time) * 1000


# ==========================================
# UI & TOURNAMENT EXECUTION
# ==========================================
st.title("⚡ The O(1) Engine Room")
st.markdown("Benchmarking geometric API latency vs. local neural inference.")

# User Input
raw_address = st.text_input("Enter CDMX Address:", value="Eje 6 Sur esq. Insurgentes")

if st.button("Execute Inference Tournament"):
    
    # Create the visual columns
    col1, col2, col3 = st.columns(3)
    
    # 1. Google Maps Execution
    with col1:
        st.subheader("Google Maps API")
        st.caption("O(N x M) Geometric PiP")
        with st.spinner("Awaiting network response..."):
            gmap_result, gmap_lat = get_google_maps_latency(raw_address)
        
        st.metric(label="Inference Latency", value=f"{gmap_lat:.2f} ms")
        st.info(f"**Result:** {gmap_result}")

    # 2. miniBETO Execution
    with col2:
        st.subheader("miniBETO")
        st.caption("110M Param Spanish BERT")
        with st.spinner("Computing attention..."):
            beto_result, beto_lat = get_minibeto_latency(raw_address)
            
        st.metric(label="Inference Latency", value=f"{beto_lat:.2f} ms")
        st.success(f"**Result:** {beto_result}")

    # 3. miniBabel Execution
    with col3:
        st.subheader("miniBabel")
        st.caption("1.5M Param Custom Transformer")
        # miniBabel is so fast you likely won't see the spinner
        with st.spinner("Inferring..."): 
            babel_result, babel_lat = get_minibabel_latency(raw_address)
            
        st.metric(label="Inference Latency", value=f"{babel_lat:.2f} ms")
        st.success(f"**Result:** {babel_result}")
        
    # --- Performance Summary ---
    st.divider()
    speedup = gmap_lat / babel_lat if babel_lat > 0 else 0
    st.markdown(f"### 🏆 miniBabel was **{speedup:.1f}x faster** than the Google Maps API.")