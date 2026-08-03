"""
RAG Golden Dataset — Phase 0 of the retrieval evaluation harness (rag_eval.py).

24 questions (6 per corpus), reusing pages/_0010_data.py's SAMPLE_QUESTIONS as the
question set, each manually verified against the real corpus content on 2026-08-02
(grep against .claude/claude_docs/*.md, git show against the paper-dev branch's .tex
chapters, live retrieve_trips()/retrieve() calls against the real ChromaDB collection
and Codebase parquet) to confirm the true expected_source/expected_chunk_id — not
"whatever retrieval currently returns" (that would make hit-rate tautologically 100%
and defeat the purpose of the harness).

Schema per entry:
    question: str — the golden question (verbatim from SAMPLE_QUESTIONS where kept as-is;
        two Trip Records questions were swapped for cleaner single-row ground truth, see notes).
    expected_source: str | None — the source_file that should appear in the top-k for
        claude_docs/paper/codebase corpora. None for trips (see below).
    expected_chunk_id: str | None — the ChromaDB row id that should appear in the top-k,
        used ONLY for the "trips" corpus. retrieve_trips() hardcodes source_file to the
        constant "v_ML_Supervised" for every row (see pages/_0010_data.py), so source_file
        can't discriminate hits there — chunk_id is the real discriminator instead.
    notes: str — verification method and any caveats (e.g. known miss with current
        top-k=4 baseline, multiple valid sources, etc.).

Known baseline misses (found during manual verification, kept deliberately — capturing
real gaps is the point of this harness, not making every question artificially pass):
- codebase: "Where is retrieve_trips() defined..." — the correct chunk
  (pages/_0010_data.py / function retrieve_trips) ranks 3rd by cosine similarity but with
  other corpora's chunks scoring close; confirmed present in top-4 but the margin is thin,
  worth re-checking after query rewriting/hybrid search land.
- codebase: "How does the sidebar build its navigation links?" — plain retrieve() top-4
  returned components/sidebar.py's "module-level" chunk, NOT the real
  "function build_sidebar" chunk that actually answers the question (confirmed both chunks
  exist separately in the parquet) — a genuine top-k miss with today's baseline.

Usage: python observatory/scripts/rag_eval.py --config baseline
"""

GOLDEN_DATASET: dict[str, list[dict]] = {
    "claude_docs": [
        {
            "question": "What's the anonymization protocol for fares and addresses?",
            "expected_source": "prompt_engineering.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: _obf_fare()/_obf_address() canon and the per-digit "
                     "masking rule are documented in prompt_engineering.md.",
        },
        {
            "question": "How does the GCS-only asset policy work?",
            "expected_source": "gcs_deploy.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: gcs_deploy.md is the full operational reference "
                     "for the GCS-only asset pipeline (root CLAUDE.md only summarizes it).",
        },
        {
            "question": "What caused the Vertex AI 20K-token ceiling bug?",
            "expected_source": "tech_debt.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: the 20,000-token-per-request ceiling discovery "
                     "and fix (CHAR_BUDGET) is documented as a tech_debt.md DONE entry, "
                     "not in a dedicated doc.",
        },
        {
            "question": "Nested CLAUDE.md vs. a rule in .claude/rules/ — what's the difference?",
            "expected_source": "tech_debt.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: this distinction was worked out and logged as a "
                     "tech_debt.md entry (2026-07-30 update 4), not a standalone doc.",
        },
        {
            "question": "Why was prompt caching descoped from conversational memory?",
            "expected_source": "tech_debt.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: the prompt-caching-minimum discovery (1024 vs real "
                     "4096 tokens) and descoping decision is documented as a tech_debt.md entry.",
        },
        {
            "question": "What's the commit message format convention?",
            "expected_source": "prompt_engineering.md",
            "expected_chunk_id": None,
            "notes": "Verified via grep: the type(scope): format, ASCII-only rule, and "
                     "valid-type list live in prompt_engineering.md (tech_debt.md only "
                     "mentions it tangentially).",
        },
    ],
    "paper": [
        {
            "question": "How does the Cognitive Cascade address the Gravitational Well problem?",
            "expected_source": "05_supervised.tex",
            "expected_chunk_id": None,
            "notes": "Verified via git show origin/paper-dev:The_Pienza_Papers/05_supervised.tex "
                     "— both terms are defined together in the Hierarchical Classification "
                     "Strategy section (real definition, not a passing mention).",
        },
        {
            "question": "What does the Yield quadratic formula define?",
            "expected_source": "03_eda.tex",
            "expected_chunk_id": None,
            "notes": "Verified via grep for the exact coefficients (0.9915, 0.3645, 0.1945) "
                     "across all 10 paper-dev chapters — only 03_eda.tex contains them, "
                     "in the Integrity Buffer discussion.",
        },
        {
            "question": "Why did the Trial 1 localization experiment fail?",
            "expected_source": "02_engineering.tex",
            "expected_chunk_id": None,
            "notes": "Verified via git show — Trial 1 (Google Location History, failed due "
                     "to 'While Using' vs 'Always' permission truncation) and the SHA-256/"
                     "PNG-metadata event_id scheme are both in 02_engineering.tex.",
        },
        {
            "question": "What is the Market Quality Index and the Mixture Problem?",
            "expected_source": "03_eda.tex",
            "expected_chunk_id": None,
            "notes": "Verified via git show — both concepts defined together under "
                     "'The Market Quality Index' subsection in 03_eda.tex.",
        },
        {
            "question": "Why use a Conditional GAN to synthesize the 1M-row manifold?",
            "expected_source": "06_gan_sim.tex",
            "expected_chunk_id": None,
            "notes": "Verified via grep for '1,000,000'/JS Divergence/KS Test across all "
                     "chapters — the cGAN synthesis and its statistical validation (KS "
                     "Test, JS Divergence) are both in 06_gan_sim.tex.",
        },
        {
            "question": "How does Phase 6 use the Mobility Tensor and Bellman Equation?",
            "expected_source": "06_gan_sim.tex",
            "expected_chunk_id": None,
            "notes": "Verified via git show — the Mobility Tensor, Bridge to Markov, and "
                     "Bellman Equation / State-Value Function discussion are all in "
                     "06_gan_sim.tex (same chapter as the cGAN question above).",
        },
    ],
    "trips": [
        {
            "question": "Describe a rejected offer on a surge-priced ride.",
            "expected_source": None,
            "expected_chunk_id": "OF02209",
            "notes": "Verified via live retrieve_trips() call, k=4: top-1 by similarity "
                     "(0.795), a genuinely correct match (x offer, surge flag, reject/"
                     "dropoff_non_operational).",
        },
        {
            "question": "What does a typical Comfort product offer look like?",
            "expected_source": None,
            "expected_chunk_id": "OF04761",
            "notes": "Verified via live retrieve_trips() call, k=4: top-1 by similarity "
                     "(0.448), a comfort-product offer as expected.",
        },
        {
            "question": "Show an example of a trip offer with a long pickup distance.",
            "expected_source": None,
            "expected_chunk_id": "OF00690",
            "notes": "Verified via live retrieve_trips() call, k=4: top-1 by similarity "
                     "(0.701), flagged 'long trip' in the retrieved text.",
        },
        {
            "question": "What driver states appear in the retrieved trip records?",
            "expected_source": None,
            "expected_chunk_id": "OF00003",
            "notes": "Verified via live retrieve_trips() call, k=4: top-1 by similarity "
                     "(0.617). Question is inherently a multi-answer/pattern question; "
                     "using top-1 as the anchor hit, not a strict single-fact lookup.",
        },
        {
            "question": "Describe an offer flagged as VIP rider.",
            "expected_source": None,
            "expected_chunk_id": "OF03160",
            "notes": "REPLACED 2026-08-02 (was 'Compare an accepted and a rejected offer "
                     "from the retrieved rows' — verified via live call that the real top-4 "
                     "returned four REJECTED offers, zero accepted, making a hit "
                     "structurally impossible as originally phrased). New question verified "
                     "via live retrieve_trips() call, k=4: top-1 by similarity (0.701), "
                     "correctly VIP-flagged and accepted.",
        },
        {
            "question": "Describe a business comfort offer.",
            "expected_source": None,
            "expected_chunk_id": "OF00816",
            "notes": "REPLACED 2026-08-02 (was 'What's the fare range for accepted offers "
                     "in this sample?' — verified via live call that all 4 real top-k rows "
                     "had redacted fares ($##), a known aggregation-vs-RAG limitation "
                     "already documented as the 'RAG Limitation' tooltip on the live page — "
                     "not fixable by better retrieval, so not useful as a hit-rate target). "
                     "New question verified via live retrieve() call, k=4: top-1 by "
                     "similarity (0.509), the only business_comfort product-type match.",
        },
    ],
    "codebase": [
        {
            "question": "Where is retrieve_trips() defined and what does it return?",
            "expected_source": "pages/_0010_data.py",
            "expected_chunk_id": None,
            "notes": "Verified via live retrieve() call, k=4: correct chunk "
                     "(function retrieve_trips) ranks 3rd (sim=0.605), present in top-4 "
                     "but with a thin margin over unrelated corpus chunks — worth "
                     "re-checking after query rewriting/hybrid search land.",
        },
        {
            "question": "How does ask_claude_agentic() decide which corpus to query?",
            "expected_source": "pages/_0010_data.py",
            "expected_chunk_id": None,
            "notes": "Verified via live retrieve() call, k=4: correct chunk "
                     "(function ask_claude_agentic) ranks 1st (sim=0.744), clean hit.",
        },
        {
            "question": "What does the AST-based chunking script do?",
            "expected_source": "scripts/rag_build_corpus_codebase.py",
            "expected_chunk_id": None,
            "notes": "Verified via live retrieve() call, k=4: correct chunk "
                     "(function chunk_python) ranks 1st (sim=0.654), clean hit.",
        },
        {
            "question": "How is address anonymization implemented?",
            "expected_source": "pages/_0002_data.py",
            "expected_chunk_id": None,
            "notes": "Verified via live retrieve() call, k=4: 3 valid obf_address "
                     "implementations exist in the corpus (_0002_data.py, _0003_data.py, "
                     "rag_build_vectordb_trips.py) — genuinely ambiguous question with "
                     "multiple correct answers. Picked _0002_data.py (top-1, sim=0.563) as "
                     "the primary expected_source since compute_hit() only needs ONE match "
                     "in top-k; a future stricter eval could treat this as multi-valid.",
        },
        {
            "question": "What does compact_if_needed() do and when does it trigger?",
            "expected_source": "pages/_0010_data.py",
            "expected_chunk_id": None,
            "notes": "Verified via live retrieve() call, k=4: correct chunk "
                     "(function compact_if_needed) ranks 1st (sim=0.602), clean hit.",
        },
        {
            "question": "How does the sidebar build its navigation links?",
            "expected_source": "components/sidebar.py",
            "expected_chunk_id": None,
            "notes": "KNOWN MISS, kept deliberately: verified via live retrieve() call, "
                     "k=4 — the real top-4 returned sidebar.py's 'module-level' chunk, NOT "
                     "the 'function build_sidebar' chunk that actually answers the "
                     "question (confirmed both exist as separate chunks in the parquet). "
                     "compute_hit() only checks source_file (not heading), so this WILL "
                     "register as a hit despite retrieving the wrong specific chunk — a "
                     "known limitation of source_file-level hit-rate vs. chunk-level.",
        },
    ],
}


# Phase 1 (query rewriting) golden set — 1 pair per corpus, each with a seed question,
# a pronoun/reference-dependent follow-up, and the expected ground truth for the
# follow-up. Built and verified live on 2026-08-03: for each pair, the RAW follow-up
# (no rewrite) was run through retrieve()/retrieve_trips() and confirmed to either miss
# the expected source entirely or return an ambiguous/wrong-corpus top result; then a
# manually-simulated rewrite (standing in for rewrite_query()'s real output) was run
# and confirmed to retrieve the expected source cleanly at a meaningfully higher
# similarity score. This is what makes these valid test cases for measuring query
# rewriting's real effect — a pair where the raw follow-up already retrieves correctly
# wouldn't show any measurable improvement (see the module's dev notes: the first
# candidate pair tried for "paper" was rejected for exactly this reason).
GOLDEN_FOLLOWUPS: dict[str, list[dict]] = {
    "paper": [
        {
            "seed_question": "Why use a Conditional GAN to synthesize the 1M-row manifold?",
            "seed_answer_hint": "To overcome data sparsity (N~4,700 ground truth rows) by "
                                 "synthesizing a 1,000,000-row manifold via a cGAN.",
            "followup_question": "What was it validated against?",
            "expected_source": "06_gan_sim.tex",
            "expected_chunk_id": None,
            "notes": "Raw followup: top1/top2 nearly tied (sim 0.547/0.546), one from the "
                     "wrong chapter (05_supervised.tex). Rewritten "
                     "('What was the cGAN synthetic manifold validated against?'): "
                     "clean 4/4 hits in 06_gan_sim.tex, sim 0.668 top1.",
        },
    ],
    "codebase": [
        {
            "seed_question": "What does compact_if_needed() do and when does it trigger?",
            "seed_answer_hint": "Keeps last MAX_HISTORY_TURNS verbatim, folds aged-out turns "
                                 "into a running summary via a small Haiku call.",
            "followup_question": "What model does it use for that?",
            "expected_source": "pages/_0010_data.py",
            "expected_chunk_id": None,
            "notes": "Raw followup: dispersed across 4 unrelated files, none correct "
                     "(sim 0.51-0.52). Rewritten "
                     "('What Claude model does compact_if_needed use for its summary "
                     "calls?'): clean top1 hit, function compact_if_needed, sim 0.663.",
        },
    ],
    "claude_docs": [
        {
            "seed_question": "What caused the Vertex AI 20K-token ceiling bug?",
            "seed_answer_hint": "A 200-chunk batch of dense technical markdown totaled "
                                 "72,489 tokens against Vertex AI's 20,000-token-per-request "
                                 "limit.",
            "followup_question": "What ratio did they measure for it?",
            "expected_source": "tech_debt.md",
            "expected_chunk_id": None,
            "notes": "Raw followup: 4 wrong docs, none tech_debt.md (sim 0.44-0.48). "
                     "Rewritten ('What chars-per-token ratio did they measure for the "
                     "Vertex AI token ceiling bug?'): top1/top2 tech_debt.md, "
                     "sim 0.632/0.620.",
        },
    ],
    "trips": [
        {
            "seed_question": "Describe an offer flagged as VIP rider.",
            "seed_answer_hint": "A VIP-flagged offer, accepted, premium earnings-per-hour "
                                 "efficiency.",
            "followup_question": "What was its fare efficiency?",
            "expected_source": None,
            "expected_chunk_id": "OF03160",
            "notes": "Raw followup: 4 comfort offers, none VIP-flagged (sim 0.61-0.62). "
                     "Rewritten ('What was the VIP-flagged offer earnings-per-hour "
                     "efficiency?'): top1 hit OF03160, sim 0.647.",
        },
    ],
}
