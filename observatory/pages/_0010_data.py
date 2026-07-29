"""Data literals and pure helpers used by 0010_RAG_Assistant.py (Layer 1 extraction)."""

import os

import numpy as np
import pandas as pd
import requests
import streamlit as st

from utils.gcp_client import fetch_parquet_from_gcp, download_prefix_from_gcs
from utils.gcp_auth import get_gcp_credentials
from utils.vertex_embed import embed_text

PROJECT_ID = "drivers-dilemma"
CORPUS_BUCKET = "pienza-streamlit"
TOP_K = 4
CLAUDE_MODEL = "claude-haiku-4-5"

CHROMA_GCS_PREFIX = "chroma_trips"
CHROMA_LOCAL_DIR = "/tmp/chroma_trips"
CHROMA_COLLECTION_NAME = "trip_offers"

# Each corpus is its own precomputed artifact. "kind": "parquet" (default)
# loads a flat parquet + numpy cosine similarity (rag_build_corpus.py /
# rag_build_corpus_paper.py). "kind": "chromadb" loads a persistent ChromaDB
# store instead (rag_build_vectordb_trips.py) — row-to-text serialization
# over BigQuery, candidate #4 in rag_workflow.md §0. More candidates from the
# 5-source roadmap append here as they're built.
CORPORA = [
    {
        "key": "claude_docs",
        "label": "Project Docs",
        "sub": "Markdown corpus",
        "file": "rag_corpus_claude_docs.parquet",
        "kind": "parquet",
    },
    {
        "key": "paper",
        "label": "The Pienza Papers",
        "sub": "LaTeX source",
        "file": "rag_corpus_paper.parquet",
        "kind": "parquet",
    },
    {
        "key": "trips",
        "label": "Trip Records",
        "sub": "ChromaDB — serialized rows",
        "kind": "chromadb",
    },
]


@st.cache_data(show_spinner="Loading RAG corpus...")
def load_corpus(corpus_file: str):
    df = fetch_parquet_from_gcp(CORPUS_BUCKET, corpus_file)
    if df.empty:
        return df, None
    matrix = np.stack(df["embedding"].to_numpy())
    return df, matrix


def retrieve(question: str, df, matrix, k: int = TOP_K):
    credentials = get_gcp_credentials()
    query_vec = np.array(embed_text(question, PROJECT_ID, credentials))
    sims = matrix @ query_vec / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vec) + 1e-10)
    top_idx = np.argsort(-sims)[:k]
    return df.iloc[top_idx].assign(similarity=sims[top_idx])


@st.cache_resource(show_spinner="Loading trip vector DB...")
def load_trip_collection():
    """Downloads the ChromaDB persistent store from GCS to /tmp (once per
    session — the repo's GCS-only rule: never read a checked-in local copy,
    always fetch fresh from the bucket) and returns the live collection."""
    import chromadb

    if not os.path.exists(os.path.join(CHROMA_LOCAL_DIR, "chroma.sqlite3")):
        download_prefix_from_gcs(CORPUS_BUCKET, CHROMA_GCS_PREFIX, CHROMA_LOCAL_DIR)
    client = chromadb.PersistentClient(path=CHROMA_LOCAL_DIR)
    return client.get_collection(CHROMA_COLLECTION_NAME)


def retrieve_trips(question: str, k: int = TOP_K):
    """Same retrieval contract as retrieve() (returns source_file/heading/
    text/similarity columns) so ask_claude() and the page's rendering code
    work unchanged regardless of which corpus kind is active."""
    credentials = get_gcp_credentials()
    query_vec = embed_text(question, PROJECT_ID, credentials)
    collection = load_trip_collection()
    res = collection.query(query_embeddings=[query_vec], n_results=k)

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    ids = res["ids"][0]
    # Chroma's cosine space returns distance = 1 - cosine_similarity.
    similarities = [1 - d for d in res["distances"][0]]

    return pd.DataFrame({
        "chunk_id": ids,
        "source_file": ["v_ML_Supervised"] * len(ids),
        "heading": [m.get("str_product", "") for m in metas],
        "text": docs,
        "similarity": similarities,
    })


def ask_claude(question: str, chunks) -> str:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "ANTHROPIC_API_KEY missing from secrets — cannot generate an answer."

    context = "\n\n".join(
        f"[Source: {row.source_file} — {row.heading}]\n{row.text}" for row in chunks.itertuples()
    )
    system_prompt = (
        "You are a documentation assistant for Project Pienza, a Streamlit Observatory. "
        "Answer the user's question using ONLY the provided context passages. "
        "If the context doesn't contain the answer, say so plainly instead of guessing. "
        "Cite the source_file of the passage(s) you used in your answer."
    )
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": CLAUDE_MODEL,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": f"Context:\n\n{context}\n\nQuestion: {question}"}
            ],
        },
        timeout=30,
    )
    if resp.status_code != 200:
        return f"Claude API error ({resp.status_code}): {resp.text[:300]}"
    data = resp.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
