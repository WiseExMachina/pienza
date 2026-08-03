"""
RAG Retrieval Evaluation Harness
================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).

Measures retrieval quality (hit-rate, context precision, context recall), latency,
and cost for the 24-question golden dataset (observatory/scripts/eval_data/
rag_golden_dataset.py) against retrieval functions in pages/_0010_data.py — the
exact same code the deployed page runs (via --config baseline), or one of the
incremental upgrade variants (query rewriting, hybrid search, reranking), so
results can never silently drift from production behavior and every config is
measured with the identical metric set for apples-to-apples comparison.

Retrieval-only: never calls ask_claude(), so this stays near-free to re-run and
its numbers aren't contaminated by generation variance. Faithfulness/generation
cost metrics live in a separate script, rag_eval_judge.py.

--config selects which retrieval function runs — everything else (golden dataset
loop, metric computation, cost/latency measurement, JSON schema) stays identical:
    --config baseline       (today's plain top-k=4 cosine similarity)
    --config query_rewrite  (rewrite follow-up questions via Haiku before retrieval)
    --config hybrid         (BM25 + cosine blend)
    --config rerank         (retrieve wide, rerank narrow via a local cross-encoder)

Context precision/recall simplification (documented explicitly, not hidden): the
golden dataset has ONE verified expected_source/expected_chunk_id per question, not
a full multi-passage relevance-labeled set. So here:
  - context_recall == hit (1.0 if the expected item is anywhere in top-k, else 0.0)
  - context_precision == 1/rank if hit (rewards the expected item ranking higher
    among the k retrieved), else 0.0
This is the honest version achievable with a single-label golden set — not RAGAS's
deeper multi-passage precision/recall, which needs a richer labeled dataset this
project doesn't have. A real, scoped number beats a fabricated curve.

Each run writes a timestamped JSON to data/dumped_files/rag_eval_runs/, so configs
accumulate as a flat, diffable series instead of overwriting each other.

Usage:
    python observatory/scripts/rag_eval.py --config baseline
    python observatory/scripts/rag_eval.py --config query_rewrite
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json"),
)

from pages._0010_data import CORPORA, load_corpus, retrieve, retrieve_trips, rewrite_query
from scripts.eval_data.rag_golden_dataset import GOLDEN_DATASET, GOLDEN_FOLLOWUPS

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_eval_runs")

# Real measured ratio from the 2026-08-01 corpus rebuild (tech_debt.md): a full
# .claude/claude_docs/ rebuild (310,706 chars) cost $0.008 via Vertex AI
# text-embedding-004. Using this project's own measured number, not a possibly
# stale published rate card.
COST_PER_CHAR = 0.008 / 310_706

VALID_CONFIGS = ["baseline", "query_rewrite", "hybrid", "rerank"]


def estimate_embed_cost(question_text: str) -> float:
    return len(question_text) * COST_PER_CHAR


def compute_hit(entry: dict, retrieved_df, corpus_key: str) -> tuple[bool, int | None]:
    """Returns (hit, rank). rank is 1-indexed position in the retrieved set, or None
    if not found. Trip Records discriminates on chunk_id (source_file is a constant
    for that corpus); the other 3 corpora discriminate on source_file."""
    if corpus_key == "trips":
        target = entry["expected_chunk_id"]
        values = retrieved_df["chunk_id"].tolist()
    else:
        target = entry["expected_source"]
        values = retrieved_df["source_file"].tolist()
    if target in values:
        return True, values.index(target) + 1
    return False, None


def compute_context_metrics(hit: bool, rank: int | None) -> tuple[float, float]:
    """Returns (context_precision, context_recall) — see module docstring for the
    single-label simplification this implements."""
    recall = 1.0 if hit else 0.0
    precision = (1.0 / rank) if hit else 0.0
    return precision, recall


def retrieve_for_config(config: str, question: str, corpus_key: str, df, matrix):
    """Dispatches to the retrieval function for the given --config. Every config
    returns the same chunk_id/source_file/heading/text/similarity DataFrame contract,
    so compute_hit()/compute_context_metrics() work unchanged regardless of config."""
    if config == "baseline":
        return retrieve_trips(question) if corpus_key == "trips" else retrieve(question, df, matrix)
    if config == "query_rewrite":
        # Standalone questions have nothing to rewrite against — query_rewrite's
        # effect is only visible on the follow-up pairs (see run_followup_eval),
        # so for the standalone 24 questions it behaves identically to baseline.
        return retrieve_trips(question) if corpus_key == "trips" else retrieve(question, df, matrix)
    if config == "hybrid":
        from pages._0010_data import retrieve_hybrid
        if corpus_key == "trips":
            return retrieve_trips(question)  # hybrid scoped to parquet corpora, see plan
        corpus_file = next(c["file"] for c in CORPORA if c["key"] == corpus_key)
        return retrieve_hybrid(question, df, matrix, corpus_file=corpus_file)
    if config == "rerank":
        from pages._0010_data import retrieve_with_rerank
        if corpus_key == "trips":
            return retrieve_trips(question)  # rerank scoped to parquet corpora, see plan
        return retrieve_with_rerank(question, df, matrix)
    raise ValueError(f"Unknown config: {config}")


def run_retrieval_only(config: str, question: str, corpus_key: str, df, matrix):
    t0 = time.perf_counter()
    retrieved = retrieve_for_config(config, question, corpus_key, df, matrix)
    latency_ms = (time.perf_counter() - t0) * 1000
    return retrieved, latency_ms


def run_followup_eval(loaded: dict) -> dict:
    """query_rewrite-specific: for each golden follow-up pair, measures retrieval on
    the RAW follow-up question (baseline behavior — no rewrite) vs. retrieval on the
    REWRITTEN question (query_rewrite behavior), in the same run, so the before/after
    delta from rewriting is directly visible."""
    results = {"raw": {"hits": [], "n": 0}, "rewritten": {"hits": [], "n": 0}}
    per_pair = []

    for corpus_key, pairs in GOLDEN_FOLLOWUPS.items():
        df, matrix = loaded[corpus_key]
        for pair in pairs:
            seed_q = pair["seed_question"]
            followup_q = pair["followup_question"]
            expected = pair.get("expected_source") or pair.get("expected_chunk_id")

            raw_df = retrieve_trips(followup_q) if corpus_key == "trips" else retrieve(followup_q, df, matrix)
            raw_hit, raw_rank = compute_hit(
                {"expected_source": pair.get("expected_source"), "expected_chunk_id": pair.get("expected_chunk_id")},
                raw_df, corpus_key,
            )

            rewritten_q = rewrite_query(followup_q, [{"question": seed_q, "answer": pair.get("seed_answer_hint", "")}])
            rewritten_df = retrieve_trips(rewritten_q) if corpus_key == "trips" else retrieve(rewritten_q, df, matrix)
            rewritten_hit, rewritten_rank = compute_hit(
                {"expected_source": pair.get("expected_source"), "expected_chunk_id": pair.get("expected_chunk_id")},
                rewritten_df, corpus_key,
            )

            results["raw"]["hits"].append(raw_hit)
            results["raw"]["n"] += 1
            results["rewritten"]["hits"].append(rewritten_hit)
            results["rewritten"]["n"] += 1

            print(f"  [{corpus_key}] followup: {followup_q[:45]:45s} raw_hit={raw_hit!s:5s} "
                  f"rewritten='{rewritten_q[:40]}...' rewritten_hit={rewritten_hit!s:5s}")

            per_pair.append({
                "corpus": corpus_key,
                "seed_question": seed_q,
                "followup_question": followup_q,
                "rewritten_question": rewritten_q,
                "expected": expected,
                "raw_hit": raw_hit,
                "raw_rank": raw_rank,
                "rewritten_hit": rewritten_hit,
                "rewritten_rank": rewritten_rank,
            })

    return {
        "raw_hit_rate": round(sum(results["raw"]["hits"]) / results["raw"]["n"], 3) if results["raw"]["n"] else None,
        "rewritten_hit_rate": round(sum(results["rewritten"]["hits"]) / results["rewritten"]["n"], 3) if results["rewritten"]["n"] else None,
        "n_pairs": results["raw"]["n"],
        "per_pair": per_pair,
    }


def main():
    parser = argparse.ArgumentParser(description="RAG retrieval evaluation harness")
    parser.add_argument("--config", default="baseline", choices=VALID_CONFIGS, help="Which retrieval config to measure")
    args = parser.parse_args()

    print(f"Running RAG eval — config: {args.config}")
    print(f"Golden dataset: {sum(len(v) for v in GOLDEN_DATASET.values())} questions "
          f"across {len(GOLDEN_DATASET)} corpora\n")

    loaded = {}
    for corpus in CORPORA:
        if corpus["kind"] == "parquet":
            print(f"Loading corpus: {corpus['label']}...")
            loaded[corpus["key"]] = load_corpus(corpus["file"])
        else:
            loaded[corpus["key"]] = (None, None)

    per_corpus_results = {}
    per_question = []

    for corpus_key, questions in GOLDEN_DATASET.items():
        df, matrix = loaded[corpus_key]
        hits, precisions, recalls, latencies, costs = [], [], [], [], []
        for entry in questions:
            question = entry["question"]
            retrieved_df, latency_ms = run_retrieval_only(args.config, question, corpus_key, df, matrix)
            hit, rank = compute_hit(entry, retrieved_df, corpus_key)
            precision, recall = compute_context_metrics(hit, rank)
            cost = estimate_embed_cost(question)

            hits.append(hit)
            precisions.append(precision)
            recalls.append(recall)
            latencies.append(latency_ms)
            costs.append(cost)

            print(f"  [{corpus_key}] {question[:50]:50s} hit={hit!s:5s} rank={rank} "
                  f"prec={precision:.2f} rec={recall:.1f} ({latency_ms:.0f}ms)")

            per_question.append({
                "corpus": corpus_key,
                "question": question,
                "expected_source": entry.get("expected_source"),
                "expected_chunk_id": entry.get("expected_chunk_id"),
                "retrieved_top_k": retrieved_df["source_file"].tolist() if corpus_key != "trips"
                                   else retrieved_df["chunk_id"].tolist(),
                "hit": hit,
                "rank": rank,
                "context_precision": round(precision, 3),
                "context_recall": round(recall, 3),
                "latency_ms": round(latency_ms, 1),
                "cost_usd": round(cost, 8),
            })

        n = len(questions)
        per_corpus_results[corpus_key] = {
            "hit_rate": round(sum(hits) / n, 3),
            "context_precision": round(sum(precisions) / n, 3),
            "context_recall": round(sum(recalls) / n, 3),
            "n": n,
            "mean_latency_ms": round(sum(latencies) / n, 1),
            "cost_usd": round(sum(costs), 6),
        }

    all_hits = [q["hit"] for q in per_question]
    all_precisions = [q["context_precision"] for q in per_question]
    all_recalls = [q["context_recall"] for q in per_question]
    all_latencies = [q["latency_ms"] for q in per_question]
    all_costs = [q["cost_usd"] for q in per_question]

    overall = {
        "hit_rate": round(sum(all_hits) / len(all_hits), 3),
        "context_precision": round(sum(all_precisions) / len(all_precisions), 3),
        "context_recall": round(sum(all_recalls) / len(all_recalls), 3),
        "mean_latency_ms": round(sum(all_latencies) / len(all_latencies), 1),
        "total_cost_usd": round(sum(all_costs), 6),
    }

    followup_results = None
    if args.config == "query_rewrite":
        print("\nRunning follow-up eval (raw vs. rewritten retrieval)...")
        followup_results = run_followup_eval(loaded)

    result = {
        "run_id": f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{args.config}",
        "config": args.config,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "golden_dataset_version": f"{sum(len(v) for v in GOLDEN_DATASET.values())}_questions",
        "per_corpus": per_corpus_results,
        "overall": overall,
        "per_question": per_question,
        "followup_results": followup_results,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{result['run_id']}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nOverall hit-rate: {overall['hit_rate']:.1%}")
    print(f"Overall context precision: {overall['context_precision']:.3f}")
    print(f"Overall context recall: {overall['context_recall']:.3f}")
    print(f"Mean latency: {overall['mean_latency_ms']:.0f}ms")
    print(f"Total embed cost: ${overall['total_cost_usd']:.6f}")
    if followup_results:
        print(f"Follow-up hit-rate — raw: {followup_results['raw_hit_rate']:.1%}, "
              f"rewritten: {followup_results['rewritten_hit_rate']:.1%}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
