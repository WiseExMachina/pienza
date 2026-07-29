"""Data literals and pure helpers used by 0010_RAG_Assistant.py (Layer 1 extraction)."""

import numpy as np
import requests
import streamlit as st

from utils.gcp_client import fetch_parquet_from_gcp
from utils.gcp_auth import get_gcp_credentials
from utils.vertex_embed import embed_text

PROJECT_ID = "drivers-dilemma"
CORPUS_BUCKET = "pienza-streamlit"
TOP_K = 4
CLAUDE_MODEL = "claude-haiku-4-5"

# Each corpus is its own precomputed parquet (see rag_build_corpus.py /
# rag_build_corpus_paper.py). More candidates from the 5-source roadmap
# (see rag_workflow.md §0) get appended here as they're built.
CORPORA = [
    {
        "key": "claude_docs",
        "label": "Project Docs",
        "sub": "Markdown corpus",
        "file": "rag_corpus_claude_docs.parquet",
    },
    {
        "key": "paper",
        "label": "The Pienza Papers",
        "sub": "LaTeX source",
        "file": "rag_corpus_paper.parquet",
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
