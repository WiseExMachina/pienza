import pandas as pd
from google.cloud import storage
from io import BytesIO
import os
import streamlit as st

# Ensure the credentials environment variable is set
# (Assuming the script is run from the observatory root where the JSON lives)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".streamlit/service-account.json"

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

def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
    """
    Downloads a physical file from a GCP bucket to a local directory.
    Crucial for retrieving ML models (.pth) and JSON dictionaries.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        # Download the file to the specified local path (e.g., /tmp/pienza_models/...)
        blob.download_to_filename(destination_file_name)
        
    except Exception as e:
        st.error(f"Failed to download {source_blob_name} from GCP: {e}")
        raise e  # We raise the error here so the Streamlit @cache_resource knows it failed