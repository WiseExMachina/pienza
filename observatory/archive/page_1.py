import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- MOCK DATA GENERATORS ---
def get_mock_data():
    return pd.DataFrame({
        'Mission': range(1, 21),
        'EPH Realized': np.random.normal(120, 20, 20),
        'Cost per KM': np.random.uniform(5, 8, 20)
    })

def get_mock_map():
    # CDMX Coordinates (Approx)
    return pd.DataFrame({
        'lat': np.random.uniform(19.35, 19.45, 50),
        'lon': np.random.uniform(-99.18, -99.10, 50)
    })

# --- UI Layout ---
st.title("📊 Phase 0: Exploratory Dashboard")
st.markdown("Initial sanity checks and distribution analysis.")

col1, col2 = st.columns(2)

with col1:
    st.write("### Profitability Funnel (Mock)")
    data = get_mock_data()
    st.line_chart(data.set_index('Mission')['EPH Realized'])

with col2:
    st.write("### Geospatial Density (Mock)")
    map_data = get_mock_map()
    st.map(map_data)

st.write("### Distribution Analysis")
fig = px.histogram(data, x="EPH Realized", nbins=20, 
                   title="Realized Earnings Distribution",
                   color_discrete_sequence=['#21918c']) # OPUS_TEAL
st.plotly_chart(fig, use_container_width=True)

st.success("Interactivity check: Try zooming in on the map or hovering over the charts.")