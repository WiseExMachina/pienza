import pandas as pd
from google.cloud import storage
from io import BytesIO
import os
import streamlit as st

# Ensure the credentials environment variable is set
# (Assuming the script is run from the observatory root where the JSON lives)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

@st.cache_data(show_spinner="Decrypting GCP Telemetry...")
def fetch_parquet_from_gcp(bucket_name: str, file_name: str) -> pd.DataFrame:
    """
    Fetches a Parquet file securely from a GCP bucket and loads it into a Pandas DataFrame.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Download into memory (RAM) as bytes
        parquet_bytes = blob.download_as_bytes()
        
        # Read the bytes directly into a Pandas DataFrame
        return pd.read_parquet(BytesIO(parquet_bytes))
        
    except Exception as e:
        st.error(f"Failed to connect to GCP Vault: {e}")
        return pd.DataFrame() # Return empty DF so the app doesn't hard crash