import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Credenciales: en Codespaces se usa el JSON local; en Streamlit Community Cloud
# (donde .streamlit/service-account.json no existe, ver assets/CLAUDE.md) se usa
# st.secrets["gcp_service_account"] en su lugar.
if "gcp_service_account" not in st.secrets:
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ".streamlit/service-account.json")


def _bigquery_client() -> bigquery.Client:
    if "gcp_service_account" in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        return bigquery.Client(credentials=creds, project=creds.project_id)
    return bigquery.Client()


@st.cache_data(show_spinner="Querying the Pienza Data Warehouse...")
def fetch_data_from_bq(query: str) -> pd.DataFrame:
    """
    Executes a SQL query against Google BigQuery and returns a Pandas DataFrame.
    """
    try:
        # Initialize the BigQuery Client
        client = _bigquery_client()
        
        # Execute the query and convert directly to a DataFrame
        # (This leverages the 'db-dtypes' library for massive speed improvements)
        df = client.query(query).to_dataframe()
        
        return df
        
    except Exception as e:
        st.error(f"Failed to execute BigQuery SQL: {e}")
        return pd.DataFrame() # Return an empty DataFrame to prevent hard app crashes