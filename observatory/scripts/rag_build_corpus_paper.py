"""
RAG Corpus Builder — The Pienza Papers (LaTeX source)
================================================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).
Reads the paper's .tex chapter source (staged locally at
data/dumped_files/paper_tex/ via `git show origin/paper-dev:...` — the paper itself
was deprecated off main and lives only on the paper-dev branch, see
assets_ignored/claude_docs/paper_migration.md), strips LaTeX markup down to plain
text via utils/latex_strip.py, chunks by \\section/\\subsection/\\subsubsection, embeds
each chunk via Vertex AI text-embedding-004, and writes a parquet with the same
5-column schema as rag_corpus_claude_docs.parquet plus a source_type column, so the
live page can tell which corpus a citation came from.

Usage:
    python observatory/scripts/rag_build_corpus_paper.py
"""
import os
import sys
import glob
import time

import pandas as pd
import google.auth

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.vertex_embed import embed_batch, BATCH_SIZE
from utils.latex_strip import chunk_latex

TEX_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "paper_tex")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_corpus_paper.parquet")
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")

# main.tex is just the preamble + \input{} list of the other files, no prose content.
EXCLUDE = {"main.tex"}


def main():
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    files = sorted(
        f for f in glob.glob(os.path.join(TEX_DIR, "*.tex"))
        if os.path.basename(f) not in EXCLUDE
    )
    print(f"Found {len(files)} .tex files to process (excluded {len(EXCLUDE)})")

    pending = []  # list of (source_file, heading, text)
    for fp in files:
        fname = os.path.basename(fp)
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()
        file_chunks = chunk_latex(text)
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
                "source_type": "paper",
            })
            chunk_id += 1
        print(f"  embedded batch {i // BATCH_SIZE + 1} ({len(rows)}/{len(pending)} chunks)")
        time.sleep(1.0)

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_PATH, index=False)
    print(f"Wrote {len(df)} chunks from {len(files)} files to {OUT_PATH}")


if __name__ == "__main__":
    main()
