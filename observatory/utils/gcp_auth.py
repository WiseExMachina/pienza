import os

import streamlit as st
from google.oauth2 import service_account

# Credenciales: en Codespaces se usa el JSON local; en Streamlit Community Cloud
# (donde .streamlit/service-account.json no existe, ver assets/CLAUDE.md) se usa
# st.secrets["gcp_service_account"] en su lugar.
if "gcp_service_account" not in st.secrets:
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ".streamlit/service-account.json")


def get_gcp_credentials():
    """Returns explicit credentials from st.secrets when deployed, else None
    (None makes the google-cloud clients fall back to GOOGLE_APPLICATION_CREDENTIALS)."""
    if "gcp_service_account" in st.secrets:
        return service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
    return None
