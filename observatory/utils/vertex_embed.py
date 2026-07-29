"""
Vertex AI text-embedding-004 REST wrapper — used by both the offline corpus-build
script (observatory/scripts/rag_build_corpus.py) and the live RAG page
(observatory/pages/0605_RAG_Assistant.py) so query-time and precompute-time
embeddings always come from the identical endpoint/model.
No google-cloud-aiplatform SDK dependency — plain REST call via requests,
authenticated with whatever google.auth credentials the caller passes in.
"""
import time

import google.auth
import google.auth.transport.requests
import requests

VERTEX_REGION = "us-central1"
VERTEX_MODEL = "text-embedding-004"
MAX_RETRIES = 6
BATCH_SIZE = 5  # instances per request — this project's default quota is requests/min, not instances/min


def _access_token(credentials) -> str:
    if credentials is None:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    if not credentials.valid:
        credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


def _predict_url(project_id: str) -> str:
    return (
        f"https://{VERTEX_REGION}-aiplatform.googleapis.com/v1/projects/"
        f"{project_id}/locations/{VERTEX_REGION}/publishers/google/models/"
        f"{VERTEX_MODEL}:predict"
    )


def embed_batch(texts: list[str], project_id: str, credentials=None) -> list[list[float]]:
    """Embeds up to BATCH_SIZE texts in a single Vertex AI request. Retries on 429
    with growing backoff (this project's quota is a low requests-per-minute cap)."""
    token = _access_token(credentials)
    url = _predict_url(project_id)
    instances = [{"content": t} for t in texts]
    for attempt in range(MAX_RETRIES):
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"instances": instances},
            timeout=60,
        )
        if resp.status_code == 429 and attempt < MAX_RETRIES - 1:
            wait = min(15 * (attempt + 1), 90)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return [p["embeddings"]["values"] for p in resp.json()["predictions"]]


def embed_text(text: str, project_id: str, credentials=None) -> list[float]:
    return embed_batch([text], project_id, credentials)[0]
