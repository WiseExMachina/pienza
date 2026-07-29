"""
RAG Corpus Builder — Project Pienza Observatory
================================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).
Reads assets_ignored/claude_docs/*.md locally, chunks by markdown heading, embeds
each chunk via Vertex AI text-embedding-004, and writes a single parquet to
data/dumped_files/rag_corpus_claude_docs.parquet. That parquet (not the raw .md
files) is what later gets uploaded to GCS via gcs_deploy.py for page 0010 to read.

Usage:
    python observatory/scripts/rag_build_corpus.py
"""
import os
import re
import sys
import glob
import time

import pandas as pd
import google.auth

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.vertex_embed import embed_batch, BATCH_SIZE

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets_ignored", "claude_docs")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_corpus_claude_docs.parquet")
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")

# Excluded: personal/career docs, not project documentation.
EXCLUDE = {"STAR_stories.md", "neoris_prep.md", "job_tracker.md"}

MAX_CHARS = 1500
OVERLAP = 150


def chunk_markdown(text: str):
    """Split on ## / ### headings, then hard-cap any oversized section with overlap."""
    sections = re.split(r"\n(?=#{2,3}\s)", text)
    chunks = []
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        heading_match = re.match(r"#{2,3}\s*(.+)", sec)
        heading = heading_match.group(1).strip() if heading_match else ""
        if len(sec) <= MAX_CHARS:
            chunks.append((heading, sec))
        else:
            start = 0
            while start < len(sec):
                end = start + MAX_CHARS
                chunks.append((heading, sec[start:end]))
                if end >= len(sec):
                    break
                start = end - OVERLAP
    return chunks


def main():
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    files = sorted(
        f for f in glob.glob(os.path.join(DOCS_DIR, "*.md"))
        if os.path.basename(f) not in EXCLUDE
    )
    print(f"Found {len(files)} files to process (excluded {len(EXCLUDE)})")

    # Collect all chunks up front so they can be embedded in batches (fewer
    # requests => stays under this project's low requests-per-minute quota).
    pending = []  # list of (source_file, heading, text)
    for fp in files:
        fname = os.path.basename(fp)
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()
        file_chunks = chunk_markdown(text)
        print(f"  {fname}: {len(file_chunks)} chunk(s)")
        for heading, chunk_text in file_chunks:
            pending.append((fname, heading, chunk_text))

    print(f"Total chunks: {len(pending)} -> {len(pending) // BATCH_SIZE + 1} batch(es) of {BATCH_SIZE}")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    rows = []
    chunk_id = 0
    for i in range(0, len(pending), BATCH_SIZE):
        batch = pending[i:i + BATCH_SIZE]
        texts = [t for _, _, t in batch]
        try:
            vecs = embed_batch(texts, project_id, credentials)
        except Exception as e:
            print(f"Failed at batch starting index {i}: {e}")
            if rows:
                df = pd.DataFrame(rows)
                df.to_parquet(OUT_PATH, index=False)
                print(f"Saved partial progress: {len(df)} chunks to {OUT_PATH}")
            raise
        for (fname, heading, chunk_text), vec in zip(batch, vecs):
            rows.append({
                "chunk_id": chunk_id,
                "source_file": fname,
                "heading": heading,
                "text": chunk_text,
                "embedding": vec,
            })
            chunk_id += 1
        print(f"  embedded batch {i // BATCH_SIZE + 1} ({len(rows)}/{len(pending)} chunks)")
        time.sleep(1.0)

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {len(df)} chunks from {len(files)} files to {OUT_PATH}")


if __name__ == "__main__":
    main()
