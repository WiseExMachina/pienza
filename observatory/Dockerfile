# Pienza Observatory - Cloud Run image.
# Build context is this directory (observatory/), not the repo root - keeps
# research_core/research_full/data out of the build entirely, no need to
# exclude them via .dockerignore. See assets_ignored/CLAUDE.md for why this
# uses observatory/requirements.txt instead of the repo-root one.
FROM python:3.11-slim

WORKDIR /app

# System libs some of the trimmed deps still need at import time (torch's
# CPU wheel and a couple of others link against libgomp).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

# Cloud Run injects $PORT at runtime (defaults to 8080); Streamlit must bind
# to that, not a hardcoded port.
EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
