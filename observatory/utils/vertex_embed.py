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
# instances per request. text-embedding-004's online :predict endpoint has a
# real hard ceiling here — empirically verified 2026-07-30: 250 succeeds,
# 251 fails with 400 Bad Request. Kept at 200 (not the exact max) for a
# small safety margin. The original value of 5 was an overly conservative
# guess made while first debugging a 429 requests-per-minute quota error —
# it worked around the quota but was never actually the API's real limit.
BATCH_SIZE = 200

# text-embedding-004 also caps TOTAL tokens per request at 20,000 (separate
# from the 250-instance ceiling above) — empirically hit 2026-08-01 rebuilding
# RAG #1's corpus: a 200-chunk batch of dense technical markdown totaled
# 72,489 tokens against a 20,000 limit (real error body: "input token count
# is 72489 but the model supports up to 20000"). Measured real ratio for this
# content: 2.85 chars/token (denser than plain prose — code blocks, paths,
# symbols tokenize less efficiently). CHAR_BUDGET below is conservative
# (~15,000 tokens worth) so mixed content with an even denser mix still has
# margin. embed_batch() sub-batches on whichever limit (instance count or
# char budget) binds first — callers never need to know either ceiling exists.
CHAR_BUDGET = 42000


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


def _split_into_subbatches(texts: list[str]) -> list[list[str]]:
    """Splits texts into sub-batches respecting BOTH the 250-instance ceiling
    and the 20,000-token (CHAR_BUDGET-as-proxy) ceiling — whichever binds
    first for a given text, per-text."""
    batches = []
    current: list[str] = []
    current_chars = 0
    for t in texts:
        would_exceed_chars = current and (current_chars + len(t) > CHAR_BUDGET)
        would_exceed_count = len(current) >= BATCH_SIZE
        if would_exceed_chars or would_exceed_count:
            batches.append(current)
            current = []
            current_chars = 0
        current.append(t)
        current_chars += len(t)
    if current:
        batches.append(current)
    return batches


def _embed_single_request(texts: list[str], token: str, url: str) -> list[list[float]]:
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


def embed_batch(texts: list[str], project_id: str, credentials=None) -> list[list[float]]:
    """Embeds an arbitrary number of texts, transparently sub-batching into
    multiple Vertex AI requests to respect both the 250-instance ceiling and
    the 20,000-token-per-request ceiling (see CHAR_BUDGET above) — callers
    never need to know either limit exists. Retries on 429 with growing
    backoff (this project's quota is a low requests-per-minute cap)."""
    token = _access_token(credentials)
    url = _predict_url(project_id)
    results: list[list[float]] = []
    for sub_batch in _split_into_subbatches(texts):
        results.extend(_embed_single_request(sub_batch, token, url))
    return results


def embed_text(text: str, project_id: str, credentials=None) -> list[float]:
    return embed_batch([text], project_id, credentials)[0]
