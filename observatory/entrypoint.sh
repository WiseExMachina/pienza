#!/bin/sh
set -e

# Write .streamlit/secrets.toml from injected env vars at container start,
# rather than baking a secrets file into the image. GCP auth needs no entry
# here at all - utils/gcp_auth.py falls back to Application Default
# Credentials, which Cloud Run supplies automatically via the service
# account attached to the service.
mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
MAPBOX_TOKEN = "${MAPBOX_TOKEN}"
GCP_API_KEY = "${GCP_API_KEY}"
EOF

exec streamlit run main.py \
    --server.port="${PORT:-8080}" \
    --server.address=0.0.0.0 \
    --server.headless=true
