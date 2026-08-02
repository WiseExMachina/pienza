"""
RAG Corpus Builder — Codebase corpus (Candidate #6)
====================================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).
Reads observatory/{pages,utils,components,scripts}/*.py plus the three root
observatory/*.py files (main.py, _main_data.py, config.py) — deliberately excludes
observatory/archive/ (deprecated pages, not representative of the live app).

Chunking is AST-based, not line-split: each top-level function and class becomes
its own chunk (source text + docstring + a metadata header naming the file,
symbol, and its imports), so retrieval can return "here's the actual
ask_claude_agentic() function" instead of an entire multi-hundred-line file.
Module-level code outside any function/class (constants, top-level calls) is
kept as one additional "module-level" chunk per file so it isn't lost.

Each chunk is embedded via Vertex AI text-embedding-004 and written to a single
parquet at data/dumped_files/rag_corpus_codebase.parquet — same artifact shape
(chunk_id/source_file/heading/text/embedding) as rag_corpus_claude_docs.parquet,
so it's a drop-in fourth corpus for 0010_RAG_Assistant.py's existing retrieve().

Usage:
    python observatory/scripts/rag_build_corpus_codebase.py
"""
import ast
import glob
import os
import sys
import time

import google.auth
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.vertex_embed import embed_batch, BATCH_SIZE

OBS_DIR = os.path.join(os.path.dirname(__file__), "..")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_corpus_codebase.parquet")
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")

INCLUDE_SUBDIRS = ["pages", "utils", "components", "scripts"]
ROOT_FILES = ["main.py", "_main_data.py", "config.py"]


def _imports_of(tree: ast.Module) -> list[str]:
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def chunk_python(text: str, fname: str):
    """Returns a list of (heading, chunk_text) — one per top-level function/class,
    plus one "module-level" chunk for anything not inside a def/class."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [("(unparseable)", text[:1500])]

    imports = _imports_of(tree)
    import_line = f"Imports: {', '.join(imports[:12])}" if imports else "Imports: (none)"

    chunks = []
    covered_lines = set()
    lines = text.splitlines()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = node.end_lineno
            covered_lines.update(range(start, end))
            symbol_text = "\n".join(lines[start:end])
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            heading = f"{kind} {node.name}"
            header = f"File: {fname}\n{import_line}\nSymbol: {heading}\n\n"
            chunks.append((heading, header + symbol_text))

    module_lines = [
        line for i, line in enumerate(lines)
        if i not in covered_lines and line.strip()
    ]
    if module_lines:
        heading = "module-level"
        header = f"File: {fname}\n{import_line}\nSymbol: {heading}\n\n"
        chunks.append((heading, header + "\n".join(module_lines)))

    return chunks


def _collect_files():
    files = []
    for f in ROOT_FILES:
        fp = os.path.join(OBS_DIR, f)
        if os.path.exists(fp):
            files.append(fp)
    for sub in INCLUDE_SUBDIRS:
        files.extend(sorted(glob.glob(os.path.join(OBS_DIR, sub, "*.py"))))
    return sorted(set(files))


def main():
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    files = _collect_files()
    print(f"Found {len(files)} files to process")

    pending = []  # list of (source_file, heading, text)
    for fp in files:
        fname = os.path.relpath(fp, OBS_DIR)
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read()
        file_chunks = chunk_python(text, fname)
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
