import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("📊 Phase 3: Market Dynamics")

# --- Mock Data Generation ---
def get_mock_data():
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['EPH Direct', 'EPH Operational', 'EPH Realized']
    )
    return chart_data

def get_mock_map():
    # Focused on Mexico City (approx coordinates)
    df = pd.DataFrame(
        np.random.randn(100, 2) / [50, 50] + [19.4326, -99.1332],
        columns=['lat', 'lon']
    )
    return df

# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.write("### Profitability Funnel (Mock)")
    data = get_mock_data()
    st.line_chart(data)

with col2:
    st.write("### Geospatial Density (Mock)")
    map_data = get_mock_map()
    st.map(map_data)

st.write("### Distribution Analysis")
fig = px.histogram(data, x="EPH Realized", nbins=20, title="Realized Earnings Distribution")
st.plotly_chart(fig, use_container_width=True)

st.success("Interactivity check: Try zooming in on the map or hovering over the charts.")