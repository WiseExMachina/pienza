"""
RAG Faithfulness Judge
=======================
Offline precompute script (run manually in Codespaces, never at Streamlit runtime).

Measures generation quality (faithfulness) for the golden dataset — separate script,
separate run from rag_eval.py, deliberately, so retrieval-only re-runs stay near-free
and generation-quality checks stay a distinct, more deliberate step (this script DOES
call ask_claude()-equivalent generation, incurring real Anthropic cost).

Path A (hand-written Haiku-as-judge, not RAGAS): reuses this project's own
_claude_request() exactly as the live page calls it, instead of pulling in RAGAS +
the anthropic SDK. RAGAS was attempted first (per the plan's explicit override
decision) and abandoned after confirming, across three ragas versions (0.4.3, 0.3.9,
0.2.15), that ragas.llms.llm_factory unconditionally imports
langchain_community.chat_models.vertexai at module load time — a submodule that does
not exist in any installable langchain-community release (0.4.2, the only version on
PyPI, doesn't have it; langchain-community is itself sunset/deprecated). Installing
langchain-google-vertexai (the real Vertex SDK) does not fix this, since the missing
module belongs to a different, unrelated package. This is a genuine upstream bug in
RAGAS, not a project-side dependency choice — logged in tech_debt.md. Zero new
dependencies beyond what this repo already has.

For each golden question: retrieves real context (same retrieve()/retrieve_trips()
rag_eval.py uses), generates a real answer, then asks a second, independent Haiku
call to score that answer's faithfulness 1-5 against the retrieved context, with a
one-sentence justification — simple, inspectable, no black-box scoring formula.

Cost is captured from the REAL Anthropic API `usage` field on every call (not
estimated) — generation cost and judge cost are recorded SEPARATELY per question, so
"how much did GCP embedding cost vs. how much did Anthropic generation/judging cost"
is answered with real numbers, not blended into one figure.

Usage:
    python observatory/scripts/rag_eval_judge.py --config baseline
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

from pages._0010_data import (
    CORPORA, CLAUDE_MODEL, load_corpus, retrieve, retrieve_trips,
    compact_if_needed, SYSTEM_PROMPT, _claude_request,
)
from scripts.eval_data.rag_golden_dataset import GOLDEN_DATASET

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files", "rag_eval_runs")

# Real Haiku 4.5 pricing (confirmed live, claude-api skill model table): $1/MTok
# input, $5/MTok output. Using the model's real per-call `usage` field, not an
# estimate — this is just the $/token conversion.
HAIKU_INPUT_PER_TOKEN = 1.0 / 1_000_000
HAIKU_OUTPUT_PER_TOKEN = 5.0 / 1_000_000

VALID_CONFIGS = ["baseline", "query_rewrite", "hybrid", "rerank"]

JUDGE_SYSTEM_PROMPT = (
    "You are a faithfulness judge for a RAG (Retrieval-Augmented Generation) system. "
    "Given a question, the retrieved context passages, and a generated answer, score "
    "how faithful the answer is to the retrieved context on a 1-5 scale:\n"
    "5 = every claim in the answer is directly supported by the retrieved context.\n"
    "4 = the answer is supported, with minor reasonable inference clearly flagged as such.\n"
    "3 = the answer is mostly supported but includes some ungrounded or unclear claims.\n"
    "2 = the answer includes a significant claim not supported by the retrieved context.\n"
    "1 = the answer largely contradicts or ignores the retrieved context.\n\n"
    "Respond in exactly this format, nothing else:\n"
    "SCORE: <1-5>\n"
    "REASON: <one sentence explaining the score>"
)


def usage_cost(data: dict) -> float:
    """Real $ cost from the Anthropic API's own usage field, not an estimate."""
    usage = data.get("usage", {})
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    return input_tokens * HAIKU_INPUT_PER_TOKEN + output_tokens * HAIKU_OUTPUT_PER_TOKEN


def generate_answer(question: str, chunks, corpus_label: str) -> tuple[str, dict]:
    """Same prompt-building logic as ask_claude() (pages/_0010_data.py), called
    directly via _claude_request so the raw `usage` field is captured — ask_claude()
    itself doesn't expose usage, only the final answer text."""
    context = "\n\n".join(
        f"[Source: {row.source_file} — {row.heading}]\n{row.text}" for row in chunks.itertuples()
    )
    messages = [{"role": "user", "content": f"Context:\n\n{context}\n\nQuestion: {question}"}]
    system = SYSTEM_PROMPT.format(corpus_label=corpus_label)
    data = _claude_request(messages, system=system)
    if "error" in data:
        return data["error"], {}
    answer = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return answer, data


def judge_faithfulness(question: str, context: str, answer: str) -> tuple[int | None, str, dict]:
    prompt = (
        f"Question: {question}\n\n"
        f"Retrieved context:\n{context}\n\n"
        f"Generated answer: {answer}"
    )
    data = _claude_request(
        [{"role": "user", "content": prompt}],
        system=JUDGE_SYSTEM_PROMPT,
        max_tokens=100,
    )
    if "error" in data:
        return None, data["error"], {}

    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    score = None
    reason = text.strip()
    for line in text.splitlines():
        if line.strip().upper().startswith("SCORE:"):
            try:
                score = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.strip().upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
    return score, reason, data


def retrieve_for_config(config: str, question: str, corpus_key: str, df, matrix):
    """Same --config dispatch as rag_eval.py, kept in sync so faithfulness is
    measured against the same retrieval config being evaluated for hit-rate."""
    if config in ("baseline", "query_rewrite"):
        return retrieve_trips(question) if corpus_key == "trips" else retrieve(question, df, matrix)
    if config == "hybrid":
        from pages._0010_data import retrieve_hybrid
        if corpus_key == "trips":
            return retrieve_trips(question)
        corpus_file = next(c["file"] for c in CORPORA if c["key"] == corpus_key)
        return retrieve_hybrid(question, df, matrix, corpus_file=corpus_file)
    if config == "rerank":
        from pages._0010_data import retrieve_with_rerank
        if corpus_key == "trips":
            return retrieve_trips(question)
        return retrieve_with_rerank(question, df, matrix)
    raise ValueError(f"Unknown config: {config}")


def main():
    parser = argparse.ArgumentParser(description="RAG faithfulness judge (Path A, hand-written Haiku judge)")
    parser.add_argument("--config", default="baseline", choices=VALID_CONFIGS, help="Which retrieval config to measure")
    args = parser.parse_args()

    print(f"Running RAG faithfulness judge — config: {args.config}")
    n_questions = sum(len(v) for v in GOLDEN_DATASET.values())
    print(f"Golden dataset: {n_questions} questions across {len(GOLDEN_DATASET)} corpora")
    print("Calls generation + a judge call per question — real Anthropic cost, "
          "captured from the API's own usage field (not estimated).\n")

    loaded = {}
    for corpus in CORPORA:
        if corpus["kind"] == "parquet":
            loaded[corpus["key"]] = load_corpus(corpus["file"])
        else:
            loaded[corpus["key"]] = (None, None)

    per_corpus_results = {}
    per_question = []

    for corpus in CORPORA:
        corpus_key = corpus["key"]
        if corpus_key not in GOLDEN_DATASET:
            continue
        df, matrix = loaded[corpus_key]
        scores = []
        gen_costs = []
        judge_costs = []

        for entry in GOLDEN_DATASET[corpus_key]:
            question = entry["question"]
            t0 = time.perf_counter()

            chunks = retrieve_for_config(args.config, question, corpus_key, df, matrix)
            answer, gen_data = generate_answer(question, chunks, corpus["label"])
            gen_cost = usage_cost(gen_data)

            context = "\n\n".join(
                f"[Source: {row.source_file} — {row.heading}]\n{row.text}" for row in chunks.itertuples()
            )
            score, reason, judge_data = judge_faithfulness(question, context, answer)
            judge_cost = usage_cost(judge_data)
            elapsed_ms = (time.perf_counter() - t0) * 1000

            scores.append(score)
            gen_costs.append(gen_cost)
            judge_costs.append(judge_cost)
            print(f"  [{corpus_key}] {question[:45]:45s} score={score} gen=${gen_cost:.5f} "
                  f"judge=${judge_cost:.5f} ({elapsed_ms:.0f}ms)")

            per_question.append({
                "corpus": corpus_key,
                "question": question,
                "answer": answer,
                "faithfulness_score": score,
                "judge_reason": reason,
                "generation_cost_usd": round(gen_cost, 6),
                "judge_cost_usd": round(judge_cost, 6),
                "generation_usage": gen_data.get("usage", {}),
                "judge_usage": judge_data.get("usage", {}),
                "elapsed_ms": round(elapsed_ms, 1),
            })

        valid_scores = [s for s in scores if s is not None]
        per_corpus_results[corpus_key] = {
            "mean_faithfulness": round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else None,
            "n": len(scores),
            "n_scored": len(valid_scores),
            "generation_cost_usd": round(sum(gen_costs), 6),
            "judge_cost_usd": round(sum(judge_costs), 6),
        }

    all_scores = [q["faithfulness_score"] for q in per_question if q["faithfulness_score"] is not None]
    all_gen_costs = [q["generation_cost_usd"] for q in per_question]
    all_judge_costs = [q["judge_cost_usd"] for q in per_question]
    overall = {
        "mean_faithfulness": round(sum(all_scores) / len(all_scores), 2) if all_scores else None,
        "n_scored": len(all_scores),
        "n_total": len(per_question),
        "total_generation_cost_usd": round(sum(all_gen_costs), 6),
        "total_judge_cost_usd": round(sum(all_judge_costs), 6),
        "total_cost_usd": round(sum(all_gen_costs) + sum(all_judge_costs), 6),
    }

    result = {
        "run_id": f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{args.config}_judge",
        "config": args.config,
        "judge_method": "hand-written Haiku judge (Path A) — RAGAS abandoned, see module docstring",
        "model": CLAUDE_MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "per_corpus": per_corpus_results,
        "overall": overall,
        "per_question": per_question,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{result['run_id']}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nOverall mean faithfulness: {overall['mean_faithfulness']}/5 ({overall['n_scored']}/{overall['n_total']} scored)")
    print(f"Generation cost (Anthropic): ${overall['total_generation_cost_usd']:.6f}")
    print(f"Judge cost (Anthropic): ${overall['total_judge_cost_usd']:.6f}")
    print(f"Total Anthropic cost: ${overall['total_cost_usd']:.6f}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
