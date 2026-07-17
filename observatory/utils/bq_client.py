import streamlit as st
import pandas as pd
from google.cloud import bigquery

from utils.gcp_auth import get_gcp_credentials


def _bigquery_client() -> bigquery.Client:
    creds = get_gcp_credentials()
    if creds is not None:
        return bigquery.Client(credentials=creds, project=creds.project_id)
    return bigquery.Client()


@st.cache_data(show_spinner="Querying the Pienza Data Lakehouse...")
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