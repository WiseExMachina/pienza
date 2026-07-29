import pandas as pd
from google.cloud import storage
from io import BytesIO
import streamlit as st

from utils.gcp_auth import get_gcp_credentials


def _storage_client() -> storage.Client:
    creds = get_gcp_credentials()
    if creds is not None:
        return storage.Client(credentials=creds, project=creds.project_id)
    return storage.Client()

# ==========================================
# GCP CONNECTIVITY UTILS
# ==========================================

@st.cache_data(show_spinner="Loading telemetry...")
def fetch_parquet_from_gcp(bucket_name: str, file_name: str) -> pd.DataFrame:
    """
    Fetches a Parquet file securely from a GCP bucket.
    """
    try:
        client = _storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        parquet_bytes = blob.download_as_bytes()
        return pd.read_parquet(BytesIO(parquet_bytes))
    except Exception as e:
        st.error(f"Failed to connect to GCP Vault: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def fetch_bytes_from_gcs(bucket_name: str, blob_name: str) -> bytes:
    """
    Fetches raw bytes for a static asset (PDF, HTML, JS, PNG, geojson) from GCS.
    Use for anything previously read via a local open() on observatory/assets/.
    """
    client = _storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
    """
    Downloads physical ML artifacts (.pth, .json) to local /tmp storage.
    """
    try:
        client = _storage_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)
    except Exception as e:
        st.error(f"Failed to download {source_blob_name} from GCP: {e}")
        raise e


def download_prefix_from_gcs(bucket_name: str, gcs_prefix: str, destination_dir: str) -> None:
    """
    Downloads every blob under gcs_prefix into destination_dir (local /tmp
    storage), preserving the relative structure — the download-side counterpart
    to gcs_deploy.py's upload_dir(). Used for multi-file artifacts like a
    ChromaDB persistent store (chroma.sqlite3 + index segment directories),
    which can't be read directly from GCS the way a single blob can.
    """
    import os
    try:
        client = _storage_client()
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=gcs_prefix))
        for blob in blobs:
            if blob.name.endswith("/"):
                continue  # skip directory placeholder objects
            rel_path = blob.name[len(gcs_prefix):].lstrip("/")
            local_path = os.path.join(destination_dir, rel_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
    except Exception as e:
        st.error(f"Failed to download prefix {gcs_prefix} from GCP: {e}")
        raise e
