import streamlit as st
import pandas as pd
from google.cloud import bigquery
import os

# Ensure the credentials environment variable is set
# (Assuming the script is run from the observatory root where the JSON lives)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

@st.cache_data(show_spinner="Querying the Pienza Data Warehouse...")
def fetch_data_from_bq(query: str) -> pd.DataFrame:
    """
    Executes a SQL query against Google BigQuery and returns a Pandas DataFrame.
    """
    try:
        # Initialize the BigQuery Client
        client = bigquery.Client()
        
        # Execute the query and convert directly to a DataFrame
        # (This leverages the 'db-dtypes' library for massive speed improvements)
        df = client.query(query).to_dataframe()
        
        return df
        
    except Exception as e:
        st.error(f"Failed to execute BigQuery SQL: {e}")
        return pd.DataFrame() # Return an empty DataFrame to prevent hard app crashes