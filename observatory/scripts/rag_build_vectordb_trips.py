"""
RAG Vector DB Builder — Trip rows serialized to natural language (Candidate #4)
================================================================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).
Unlike rag_build_corpus.py / rag_build_corpus_paper.py (which embed free-text
documents into a flat parquet), this script demonstrates row-to-text serialization:
each row of v_ML_Supervised (a structured, mostly-numeric/categorical BigQuery view)
is converted into one descriptive natural-language sentence, then embedded via
Vertex AI. This is the pattern documented as "Caso B" in Agentic_Knowledge.md —
genuine RAG over structured data, only valid because the resulting corpus supports
real semantic queries ("find trips similar to X"), unlike the retired candidate #3.

Storage is a real vector DB (ChromaDB, persistent, local-embedded — no external
server) instead of a flat parquet + numpy, specifically to get hands-on practice
with a vector DB's actual API (collections, add, query, metadata filtering) rather
than reimplementing cosine similarity by hand again. ChromaDB's persistent client
writes a directory of files (chroma.sqlite3 + index segments), which is why this
is the one exception to the repo's "no subfolders in the GCS bucket" rule — see
gcs_deploy.py's upload_dir() and rag_workflow.md §4 for the full reasoning.

Usage:
    python observatory/scripts/rag_build_vectordb_trips.py
"""
import os
import re
import sys
import time

import chromadb
import google.auth
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.vertex_embed import embed_batch, BATCH_SIZE
from utils.bq_client import fetch_data_from_bq

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "chroma_trips")
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")
COLLECTION_NAME = "trip_offers"

QUERY = """
SELECT
  ml.offer_id,
  ml.upfront_fare,
  ml.pickup_address,
  ml.dropoff_address,
  ml.hour_of_day,
  ml.day_of_week,
  ml.time_of_day_block,
  ml.day_type,
  ml.is_surge,
  ml.is_vip,
  ml.is_long_trip,
  ml.is_reservation,
  ml.dropoff_polygon_name,
  ml.dropoff_hdbscan_name,
  ml.eph_realized_label_ML,
  ml.eph_complete_label_ML,
  oa.offer_action_description AS str_action,
  pc.category_name AS str_product,
  rp.reason_primary_description AS str_reason,
  ds.driver_state_at_request_description AS str_driver_state
FROM `645009831643.pienza_mini.v_ML_Supervised` ml
LEFT JOIN `645009831643.pienza_mini.offer_action` oa
  ON oa.offer_action_id = ml.offer_action_fk
LEFT JOIN `645009831643.pienza_mini.product_category` pc
  ON pc.product_category_id = ml.product_category_fk
LEFT JOIN `645009831643.pienza_mini.reason_primary` rp
  ON rp.reason_primary_id = ml.reason_primary_fk
LEFT JOIN `645009831643.pienza_mini.driver_state_at_request` ds
  ON ds.driver_state_at_request_id = ml.driver_state_at_request_fk
"""


# Canonical anonymization helpers (assets_ignored/CLAUDE.md) — reimplemented
# here since no shared utility module exists yet across pages (known debt).
def _obf_fare(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    return re.sub(r"\d", "#", f"{float(v):.0f}")


def _obf_address(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    mask_digits = lambda m: re.sub(r"\d", "#", m.group(0))
    return re.sub(r"\b(?!\d{5}\b)\d+[\w-]*\b", mask_digits, str(v), count=1)


def _strip_uber(label) -> str:
    """Brand convention (assets_ignored/CLAUDE.md): never display 'Uber' in
    product/category labels shown to the user, e.g. uberx -> x."""
    if pd.isna(label):
        return "unknown product"
    return re.sub(r"(?i)uber_?", "", str(label)).strip("_").strip() or "unknown product"


def _clean(v, default="unknown"):
    """NaN-safe fallback — pandas NaN is truthy in Python, so a bare `or`
    check silently lets it through. Also catches the literal string "nan":
    some source columns (e.g. eph_realized_label_ML) store real NaN values
    stringified to text upstream in the ETL rather than as true NULLs."""
    if pd.isna(v) or str(v).strip().lower() == "nan":
        return default
    return v


def row_to_sentence(row) -> str:
    """Serializes one structured BigQuery row into a descriptive NL sentence —
    the "row-to-text serialization" step that makes semantic search over
    otherwise-structured/numeric attributes possible (Agentic_Knowledge.md,
    "Caso B")."""
    product = _strip_uber(row.str_product)
    action = str(_clean(row.str_action, "unknown outcome")).lower()
    driver_state = _clean(row.str_driver_state, "unknown state")
    fare = _obf_fare(row.upfront_fare)
    zone = _clean(row.dropoff_hdbscan_name, None) or _clean(row.dropoff_polygon_name, "an unclassified zone")
    reason = _clean(row.str_reason, None)

    parts = [
        f"A {product} offer on a {row.day_of_week} during the {row.time_of_day_block} "
        f"({row.day_type}), around hour {row.hour_of_day}.",
        f"Upfront fare was ${fare}.",
        f"The driver's state at request was '{driver_state}' and the decision was '{action}'"
        + (f", reason: {reason}." if action == "reject" and reason else "."),
        f"Destination zone: {zone}.",
    ]
    eph_label = _clean(row.eph_realized_label_ML, None)
    if eph_label:
        parts.append(f"Realized earnings-per-hour efficiency: {eph_label}.")
    flags = []
    if row.is_surge:
        flags.append("surge pricing")
    if row.is_vip:
        flags.append("VIP rider")
    if row.is_long_trip:
        flags.append("long trip")
    if row.is_reservation:
        flags.append("reservation")
    if flags:
        parts.append("Flags: " + ", ".join(flags) + ".")

    return " ".join(parts)


def main():
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", KEY_PATH)
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    print("Querying v_ML_Supervised (joined with dimension tables)...")
    df = fetch_data_from_bq(QUERY)
    print(f"Fetched {len(df)} rows")

    sentences = [row_to_sentence(row) for row in df.itertuples()]
    ids = [str(oid) for oid in df["offer_id"].tolist()]
    metadatas = [
        {
            "str_product": row.str_product or "",
            "str_action": row.str_action or "",
            "day_type": row.day_type or "",
            "is_vip": bool(row.is_vip),
        }
        for row in df.itertuples()
    ]

    print(f"Total sentences: {len(sentences)} -> {len(sentences) // BATCH_SIZE + 1} batch(es) of {BATCH_SIZE}")

    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    client.delete_collection(COLLECTION_NAME) if COLLECTION_NAME in [c.name for c in client.list_collections()] else None
    collection = client.create_collection(COLLECTION_NAME)

    for i in range(0, len(sentences), BATCH_SIZE):
        batch_sentences = sentences[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]
        batch_metas = metadatas[i:i + BATCH_SIZE]
        try:
            vecs = embed_batch(batch_sentences, project_id, credentials)
        except Exception as e:
            print(f"Failed at batch starting index {i}: {e}")
            print(f"Partial progress preserved in ChromaDB at {CHROMA_DIR} ({collection.count()} rows added)")
            raise
        collection.add(ids=batch_ids, embeddings=vecs, documents=batch_sentences, metadatas=batch_metas)
        print(f"  embedded batch {i // BATCH_SIZE + 1} ({collection.count()}/{len(sentences)} rows)")
        time.sleep(1.0)

    print(f"Wrote {collection.count()} rows to ChromaDB collection '{COLLECTION_NAME}' at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
