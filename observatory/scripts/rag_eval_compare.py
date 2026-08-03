"""
RAG Eval Comparison — aggregates all rag_eval.py / rag_eval_judge.py run JSONs
================================================================================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).

Reads every *_<config>.json (retrieval) and *_<config>_judge.json (faithfulness +
cost) file in data/dumped_files/rag_eval_runs/, picks the LATEST run per config
(by timestamp), and builds one flat comparison table plus the corpus build-cost
table (computed once, from CORPORA token counts, see rag_eval.md #0 for the
derivation of the $/char ratio). Writes _comparison.json — the single file the
live "RAG Eval" tab on 0010_RAG_Assistant.py reads (from GCS, not local disk).

Usage:
    python observatory/scripts/rag_eval_compare.py
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pages._0010_data import CORPORA  # noqa: E402

RUNS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_eval_runs")
OUT_PATH = os.path.join(RUNS_DIR, "_comparison.json")

# Real ratio measured from the 2026-08-01 Project Docs rebuild ($0.008 / 310,706
# chars), see rag_eval.md #0. 2.85 chars/token holds for this project's dense
# technical content across all 4 corpora.
CHARS_PER_TOKEN = 2.85
COST_PER_CHAR = 0.008 / 310_706

ADOPTION_NOTES = {
    "baseline": "Reference config — today's production behavior (plain top-k=4 cosine similarity).",
    "query_rewrite": "ADOPT. Only phase with a large, clear win: follow-up hit-rate 25% -> 75% on "
                      "pronoun/reference-ambiguous questions, at the cost of one short Haiku call "
                      "per turn with history. No regression on any other metric.",
    "hybrid": "DO NOT ADOPT. Only phase that regressed hit-rate (95.8% -> 91.7%) and raised "
              "Anthropic cost (longer generated answers). Untuned alpha=0.5 is a likely cause, "
              "not investigated further to preserve scope for this build.",
    "rerank": "NEUTRAL / NOT YET ADOPTED. Ties baseline hit-rate and faithfulness, but adds ~51% "
              "latency and a new PyTorch/sentence-transformers dependency with no measurable net "
              "gain on this 24-question dataset. May help more on a larger/harder corpus, "
              "unverified here.",
}


def corpus_build_cost() -> list[dict]:
    rows = []
    total = 0.0
    for c in CORPORA:
        tokens = c.get("tokens", 0)
        chars = round(tokens * CHARS_PER_TOKEN)
        cost = round(chars * COST_PER_CHAR, 6)
        total += cost
        rows.append({
            "corpus_key": c["key"],
            "corpus_label": c["label"],
            "tokens": tokens,
            "chars_estimated": chars,
            "build_cost_usd": cost,
        })
    rows.append({
        "corpus_key": "TOTAL",
        "corpus_label": "All corpora",
        "tokens": sum(r["tokens"] for r in rows),
        "chars_estimated": sum(r["chars_estimated"] for r in rows),
        "build_cost_usd": round(total, 6),
    })
    return rows


def latest_runs_by_config(suffix: str) -> dict[str, dict]:
    """suffix is '' for retrieval runs, '_judge' for judge runs. Returns
    {config: parsed_json} keeping only the latest timestamp per config."""
    latest: dict[str, dict] = {}
    if not os.path.isdir(RUNS_DIR):
        return latest
    for fname in sorted(os.listdir(RUNS_DIR)):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        is_judge = fname.endswith(f"{suffix}.json") if suffix else not fname.endswith("_judge.json")
        if not is_judge:
            continue
        with open(os.path.join(RUNS_DIR, fname)) as f:
            data = json.load(f)
        config = data.get("config")
        if config is None:
            continue
        existing = latest.get(config)
        if existing is None or data.get("timestamp", "") > existing.get("timestamp", ""):
            latest[config] = data
    return latest


def build_comparison() -> dict:
    retrieval_runs = latest_runs_by_config("")
    judge_runs = latest_runs_by_config("_judge")

    configs = sorted(set(retrieval_runs) | set(judge_runs))
    rows = []
    for config in configs:
        r = retrieval_runs.get(config, {}).get("overall", {})
        j = judge_runs.get(config, {}).get("overall", {})
        rows.append({
            "config": config,
            "hit_rate": r.get("hit_rate"),
            "context_precision": r.get("context_precision"),
            "context_recall": r.get("context_recall"),
            "mean_latency_ms": r.get("mean_latency_ms"),
            "embed_cost_usd": r.get("total_cost_usd"),
            "faithfulness": j.get("mean_faithfulness"),
            "generation_cost_usd": j.get("total_generation_cost_usd"),
            "judge_cost_usd": j.get("total_judge_cost_usd"),
            "anthropic_cost_usd": j.get("total_cost_usd"),
            "adoption_note": ADOPTION_NOTES.get(config, ""),
        })

    # Per-corpus breakdown: {config: {corpus_key: {...}}}, same field names as
    # the overall rows above, merging retrieval (r_pc) and judge (j_pc) per_corpus
    # blocks that already exist in each run's raw JSON.
    per_corpus_comparison: dict[str, dict[str, dict]] = {}
    for config in configs:
        r_pc = retrieval_runs.get(config, {}).get("per_corpus", {})
        j_pc = judge_runs.get(config, {}).get("per_corpus", {})
        corpus_keys = sorted(set(r_pc) | set(j_pc))
        per_corpus_comparison[config] = {}
        for corpus_key in corpus_keys:
            rc = r_pc.get(corpus_key, {})
            jc = j_pc.get(corpus_key, {})
            per_corpus_comparison[config][corpus_key] = {
                "hit_rate": rc.get("hit_rate"),
                "context_precision": rc.get("context_precision"),
                "context_recall": rc.get("context_recall"),
                "mean_latency_ms": rc.get("mean_latency_ms"),
                "embed_cost_usd": rc.get("cost_usd"),
                "faithfulness": jc.get("mean_faithfulness"),
                "generation_cost_usd": jc.get("generation_cost_usd"),
                "judge_cost_usd": jc.get("judge_cost_usd"),
            }

    followup = None
    qr = retrieval_runs.get("query_rewrite")
    if qr and qr.get("followup_results"):
        fr = qr["followup_results"]
        followup = {
            "n_pairs": fr.get("n_pairs"),
            "raw_hit_rate": fr.get("raw_hit_rate"),
            "rewritten_hit_rate": fr.get("rewritten_hit_rate"),
            "pairs": fr.get("per_pair", []),
        }

    return {
        "generated_at": max(
            (d.get("timestamp", "") for d in list(retrieval_runs.values()) + list(judge_runs.values())),
            default=None,
        ),
        "corpus_build_cost": corpus_build_cost(),
        "config_comparison": rows,
        "per_corpus_comparison": per_corpus_comparison,
        "followup_comparison": followup,
    }


def main():
    comparison = build_comparison()
    os.makedirs(RUNS_DIR, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"Wrote {OUT_PATH}")
    print(f"Configs compared: {[r['config'] for r in comparison['config_comparison']]}")
    if comparison["followup_comparison"]:
        fc = comparison["followup_comparison"]
        print(f"Follow-up hit-rate: raw {fc['raw_hit_rate']:.0%} -> rewritten {fc['rewritten_hit_rate']:.0%}")


if __name__ == "__main__":
    main()
