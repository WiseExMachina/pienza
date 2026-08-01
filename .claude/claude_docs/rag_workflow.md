---
name: rag-workflow
description: "RAG/NLG initiative for Neoris interview showcase, restructured for learning-first reading: shared inference mechanism first (Vertex AI embeds, Claude generates, GCS touched once), then per-candidate Inputs/Scripts/Outputs/Deploy/Inference for #1 (markdown), #2 (paper LaTeX), and #4 (Trip Records, ChromaDB), shared architecture decisions, troubleshooting, roadmap"
metadata: 
  node_type: memory
  type: project
  originSessionId: ce8f32de-f63b-487a-88b9-e131c495bdae
  modified: 2026-08-01T20:00:00.000Z
---

# RAG / NLG Workflow — Neoris interview showcase

Read this file to understand **what happens and why**, not just what was built. Structure:
§0 the 5-candidate roadmap, §1 the shared inference mechanism (read this first — it's the
same for every RAG candidate, only the corpus changes), §2-§4 one section per built candidate
with a fixed 5-part shape (Inputs / Scripts / Outputs / Deploy to GCS / Inference notes),
§5 shared architecture decisions, §6 UI notes, §7 troubleshooting log, §8 what's next.

## 0. The 5 candidates

Interviewing companies in this space are posting AI Engineer / Data Scientist roles
without a clean, orthogonal definition of the job — the tech is new enough that job specs
are fuzzy. The strongest way to show seniority isn't to build "RAG" reflexively wherever
text shows up — it's to correctly diagnose **which** pattern a given business problem
actually needs, including cases where a company thinks it needs RAG but actually needs
NLG (or both). Five concrete candidates were scoped against Pienza's own data, each
demonstrating a different pattern:

| # | Candidate | Pattern | Why this pattern (not another) |
|---|-----------|---------|-------------------------------|
| 1 | RAG over `claude_docs/*.md` corpus | Classic RAG (embed → retrieve → generate) | Free-text docs where the right document isn't known in advance — needs semantic search |
| 2 | RAG over The Pienza Papers (`.tex` source) | Classic RAG, same mechanism as #1 | Same reasoning as #1 — just a different free-text source |
| ~~3~~ | ~~RAG over BigQuery free-text columns (`special_note_raw`, addresses, etc.)~~ | ~~Classic RAG~~ | **Retired 2026-07-30 (correction — an earlier pass on this doc had the wrong reason).** Not retired because the field was already structured — retired because there's no genuine query pattern for it: these are address strings and free-text note blobs, and no realistic question against them was identified beyond "prove the technique works." Without a real information-need behind it, building RAG here would only demonstrate technical capability, not solve an actual problem — the opposite of the "don't use RAG a huevo" principle this whole roadmap is built on (§0 intro). |
| 4 | RAG over serialized trip rows (row-to-text) | Classic RAG via row-to-text serialization ("Caso B" in `Agentic_Knowledge.md`) | N structured trip rows are serialized into one descriptive NL sentence each (product, fare bracket, decision, outcome, zone), then embedded — enabling genuine semantic search over otherwise-numeric/categorical data ("find trips similar to X"), the kind of ambiguity a plain `WHERE` can't resolve. Same mechanism as #1/#2 (§1), just a BigQuery-derived corpus instead of documents. |
| 5 | Text-to-SQL (NL2SQL) | LLM translates a natural-language question into an executable SQL query — **not RAG** | Lets a non-technical user query a relational DB in plain language; the LLM never answers from its own knowledge, the DB does |

**Status:** #1, #2, and #4 built, deployed, verified. #3 retired (see above). #5 is the only remaining active-sprint candidate.

**Graveyard note — deterministic tabular→NL narration (no retrieval, "Caso A"), explicitly not being built:**
`#4` briefly carried a different definition earlier in this doc — narrating ONE already-known row via exact SQL (`WHERE offer_id = 123`) into prose, with zero retrieval involved (the insurance-claim-summary analogy: the business knows exactly which record it wants, the problem is only presentation). That's a real, named technique (NLG over structured data, distinct from RAG — see `Agentic_Knowledge.md`), and a legitimate insight (companies conflating "we need RAG" with "we actually need NLG"). But it was never what the user meant by `#4`, and at Pienza's scope has no genuine use case behind it beyond demonstrating the technique — same reasoning that retired `#3`. Deliberately not built, kept only as a verbal talking point if the RAG-vs-NLG distinction comes up in the interview.

## 1. How inference actually works, end to end (read this first)

This is the single mechanism shared by candidates #1, #2, and (later) #3 — only the
corpus differs between them. There are **two separate cloud AI providers** involved, each
doing exactly one job. Confusing them is the single easiest way to misexplain this system:

- **Vertex AI (Google Cloud)** — embeddings only. Never generates text.
- **Claude API (Anthropic, not GCP)** — generation only. Never does retrieval.

```
OFFLINE — runs once per corpus, manually, in Codespaces (never in the live app)
─────────────────────────────────────────────────────────────────────────────
  raw source files  →  chunk into pieces  →  embed each chunk (Vertex AI)  →
  write one parquet (chunk text + its vector)  →  upload that parquet to GCS

ONLINE — runs every time the Streamlit page is used
─────────────────────────────────────────────────────────────────────────────
  page loads (once, cached):
      GCS parquet  →  loaded into memory  →  stays cached for the session

  every question typed into the chat:
      1. your question text        →  Vertex AI (embed)      →  one 768-dim vector
      2. that vector                →  compared, IN MEMORY, via numpy cosine
                                        similarity, against the corpus vectors
                                        already loaded in step "page loads"
                                        (no network call — this step is instant)
      3. top-4 matching chunks      →  their PLAIN TEXT (not vectors) is put into
                                        a prompt together with your question
      4. that prompt                →  Claude API (Anthropic)  →  generated answer
      5. answer + which chunks were used → rendered on screen
```

**The two calls that happen per question, and only these two, hit the network:**
one to Vertex AI (embed the question), one to Anthropic (generate the answer). GCS is
touched once per page load, never per question. The retrieval step (comparing vectors) is
pure local computation — no API, no cost, no latency worth mentioning at this corpus size.

**One-line answer for the interview, if asked "walk me through what happens when someone
asks a question":** *"Two API calls per question — Vertex AI embeds the question into a
vector, then an in-memory cosine-similarity search over the precomputed corpus finds the
closest chunks, and those chunks get handed to Claude as context to generate the answer.
Nothing is retrained or fine-tuned at query time — retrieval and generation are two
separate, stateless steps."*

## 2. RAG #1 — markdown corpus

### 2.1 Inputs

`assets_ignored/claude_docs/*.md` — the project's own internal documentation (architecture
notes, decision logs, memory mirrors). Local-only, gitignored, never public. 30 files
existed at build time; 3 excluded as personal/career content (`STAR_stories.md`,
`neoris_prep.md`, `job_tracker.md`). **27 files** made the final corpus.

Privacy note: the output parquet's `text` column holds plain readable chunk text, not just
an opaque vector — if it ever lands in a public GCS location, that text is effectively
public too. Bucket `pienza-streamlit` is not public — flag this again before it ever is.

### 2.2 Scripts

| File | Role |
|---|---|
| `observatory/scripts/rag_build_corpus.py` | Offline precompute — the only thing that runs §1's "OFFLINE" stage for this corpus |
| `observatory/utils/vertex_embed.py` | Shared Vertex AI REST wrapper (`embed_batch`, `embed_text`) — used by this script AND by the live page, so offline and online embeddings always come from the identical endpoint/model |
| `observatory/pages/0010_RAG_Assistant.py` | The live page — runs §1's "ONLINE" stage |

What `rag_build_corpus.py` does, in order: reads the 27 `.md` files → splits each on
`##`/`###` headings, then hard-caps any oversized section at ~1500 chars with ~150 char
overlap (`chunk_markdown()`) → batches chunks 5-at-a-time through `embed_batch()` → writes
the output parquet.

### 2.3 Outputs

`data/dumped_files/rag_corpus_claude_docs.parquet` — verified with pandas:

```
(380, 5)          # 380 rows (chunks), 5 columns
embedding dim: 768
```

Columns: `chunk_id`, `source_file`, `heading`, `text` (plain readable chunk), `embedding`
(768-float vector — that width is fixed by `text-embedding-004`, not a project choice).
380 = sum of chunks across all 28 files counted (27 corpus files + this doc itself, which
auto-qualified as a non-excluded `.md` the moment it was created).

### 2.4 Deploy to GCS

MANIFEST entry in `gcs_deploy.py` (page `"0010"`) → dry-run shown → user approved →
uploaded to `gs://pienza-streamlit/rag_corpus_claude_docs.parquet`. This is the exact
artifact §1's "ONLINE" stage loads at page-open time.

### 2.5 Inference

Identical to §1 — no corpus-specific deviation. Verified end to end twice: locally
(`streamlit run` + `cloudflared`) and in production on Cloud Run, both with real questions
answered correctly with cited sources.

**Status: DONE.** `ANTHROPIC_API_KEY` is wired in both `.streamlit/secrets.toml` (local)
and Cloud Run's container env vars (via `patch_cloud_run.py`, production).

## 3. RAG #2 — The Pienza Papers (LaTeX source)

### 3.1 Inputs

The paper (`The_Pienza_Papers/`) was deprecated off `main` on 2026-07-18 and lives only on
the `paper-dev` branch (see [[paper_migration]]) — not merged back, not re-hosted publicly.
Its 10 chapter `.tex` files were read directly with
`git show origin/paper-dev:The_Pienza_Papers/<file>.tex` (no branch checkout, no merge —
avoids the exact risk [[paper_migration]] warns about: losing track of which branch is
active in this working directory) and staged locally at `data/dumped_files/paper_tex/`.
`main.tex` (preamble + `\input{}` list only, no prose) is excluded.

**Why `.tex` source, not the compiled PDF:** LaTeX source already carries explicit section
markup (`\section`/`\subsection`/`\subsubsection`) — the same kind of heading signal the
markdown chunker needs. Extracting from a compiled PDF instead would mean fighting layout
noise a parser can't cleanly undo (page breaks that don't align with topic breaks, repeated
headers/footers) for no benefit, since the clean source was available.

### 3.2 Scripts

| File | Role |
|---|---|
| `observatory/utils/latex_strip.py` | New — `strip_latex()` / `chunk_latex()`, converts raw `.tex` into the same plain, heading-chunked text shape `chunk_markdown()` produces from `.md` |
| `observatory/scripts/rag_build_corpus_paper.py` | Offline precompute — sibling of `rag_build_corpus.py`, same shape, pointed at the staged `.tex` files |
| `observatory/utils/vertex_embed.py` | Same shared wrapper as #1 — reused, not duplicated |

What `latex_strip.py` does to a `.tex` file before chunking (regex-based — an "adequate
MVP proxy" like the markdown chunker, not a real LaTeX parser): drops comments; for
figures/tables keeps only the `\caption{}` text and discards the raw markup; drops
equation/table-grid/code-listing environments entirely (low retrieval value as literal
LaTeX); inlines `\footnote{}` text; converts `\section`/`\subsection`/`\subsubsection` into
`##`/`###`/`####` markers so the same heading-based chunker from #1 can be reused as-is;
unwraps `\textbf{}`/`\textit{}`/`\texttt{}`/`\emph{}` to plain text; strips
`\label{}`/layout commands. Known minor artifact: a top-level `\section{}` whose content
lives entirely under its first `\subsection{}` produces one near-empty heading-only chunk —
judged negligible, not fixed.

### 3.3 Outputs

`data/dumped_files/rag_corpus_paper.parquet`:

```
(232, 6)          # 232 chunks from 10 files
```

Same 5 columns as #1's parquet, **plus** `source_type: "paper"` — this extra column is
what lets the live page label which corpus a citation came from.

### 3.4 Deploy to GCS

MANIFEST entry added (page `"0010"`) → uploaded to
`gs://pienza-streamlit/rag_corpus_paper.parquet`.

**Side effect of this step — `gcs_deploy.py` itself changed:** it now compares the local
file's MD5 against the already-uploaded GCS blob's MD5 (stored as blob metadata, no
download needed) and skips re-uploading files that haven't changed (logged as "SIN
CAMBIOS"). This is now the default for every future deploy, not just this corpus —
`--force` restores the old always-upload-everything behavior if ever needed.

### 3.5 Inference

Identical mechanism to §1/§2.4 — the only difference is which parquet gets loaded, driven
by which corpus tab is selected on the page (see §6 for the selector UI, a cosmetic detail
that doesn't change how retrieval/generation work). Verified locally via `cloudflared`
tunnel with a real question answered correctly against this corpus.

**Status: DONE locally/Codespaces. Not yet re-verified on Cloud Run production** after
this change (#1 was re-verified in production; #2 wasn't yet).

## 4. RAG #4 — Trip Records (row-to-text serialization over BigQuery, ChromaDB)

### 4.1 Inputs

No local/gitignored source files this time — the corpus comes directly from BigQuery.
`QUERY` in `rag_build_vectordb_trips.py` joins `v_ML_Supervised` with dimension tables
(`offer_action`, `product_category`, `reason_primary`, `driver_state_at_request`) to pull
one row per trip offer. Each row is serialized into one natural-language sentence via
`row_to_sentence()` — no chunking step at all, since a row is already the right-sized
atomic unit (see `Agentic_Knowledge.md`'s "1 chunk = 1 row" entry). Uber branding stripped
(`_strip_uber()`) and fare/address fields obfuscated per the repo-wide anonymization
protocol before the sentence is ever embedded.

### 4.2 Scripts

| File | Role |
|---|---|
| `observatory/scripts/rag_build_vectordb_trips.py` | Offline precompute — BQ query → `row_to_sentence()` → embed via `embed_batch()` → write to a persistent ChromaDB collection instead of a parquet |
| `observatory/utils/vertex_embed.py` | Same shared wrapper as #1/#2 — `BATCH_SIZE` raised from 5 to 200 while building this candidate, after empirically confirming the real Vertex AI ceiling is 250 instances/request; benefits all 3 candidates since the module is shared |
| `observatory/scripts/gcs_deploy.py` | Extended with `upload_dir()` — directory-mode uploads (`kind: "dir"` in `MANIFEST`), the one documented exception to the repo's no-subfolders-in-bucket rule, needed because a ChromaDB store is a directory of files, not a single artifact |
| `observatory/pages/_0010_data.py` | `load_trip_collection()` (`@st.cache_resource`, downloads the ChromaDB directory from GCS to `/tmp` once per session) and `retrieve_trips()` (embeds the query, then queries the live ChromaDB collection) |

Collection created with `metadata={"hnsw:space": "cosine"}` explicitly — Chroma defaults to
L2/Euclidean distance otherwise, which would have been silently inconsistent with #1/#2's
numpy cosine retrieval (a real bug caught and fixed during the build, required a full
rebuild + re-upload).

### 4.3 Outputs

A persistent ChromaDB store, not a parquet: `chroma.sqlite3` (metadata + document text) plus
HNSW index binaries in UUID-named subdirectories (`data_level0.bin`, `link_lists.bin`,
`header.bin`, `length.bin`, `index_metadata.pickle`). **4,765 rows** embedded from
`v_ML_Supervised` (build time: ~4 minutes locally).

### 4.4 Deploy to GCS

Uploaded as a directory to `gs://pienza-streamlit/chroma_trips/` via `gcs_deploy.py`'s new
`upload_dir()` path (`--page 0010`, dry-run shown and approved before the real upload, as
with every GCS write in this project).

### 4.5 Inference

Diverges from §1's default mechanism in the retrieval step only — generation (Claude) is
identical. Instead of loading a parquet into memory and running numpy cosine similarity,
`load_trip_collection()` downloads the ChromaDB directory once per session (cached), and
`retrieve_trips()` queries the live collection via Chroma's own HNSW-indexed cosine search
(`similarity = 1 - distance`, since Chroma returns distance, not similarity, in its cosine
space). ChromaDB was chosen deliberately for hands-on practice with a real embedded vector
DB, not because 4,765 rows required one — at this scale, in-memory numpy (§1's default)
would have worked just as well; the point was demonstrating the technique, same reasoning
already logged in `Agentic_Knowledge.md`.

**Status: DONE.** Built, deployed, and verified live — including, as of this session,
correctly selected by name under the page's new Agentic RAG tool-use routing tab (Claude
picks this corpus for Trip-Records-shaped questions without being told to). **Known open
item, not yet root-caused:** first load of this tab feels slow — suspects are the
multi-file sequential GCS download, ChromaDB's own index warm-up, or the usual two-call
embed+generate latency stacking on a cold session; needs actual profiling before proposing
a fix (see tech debt).

## 5. Shared architecture decisions (apply to every RAG candidate, #1 through #4+)

- **No LLM/embedding integration existed in the repo before this** (confirmed via
  `grep -rln "anthropic\|import openai\|Claude("` — zero hits repo-wide, before #1).
- **Embeddings: Vertex AI REST (`text-embedding-004`)**, not a local
  `sentence-transformers` model. Reuses the GCP service account credentials already wired
  up in `observatory/utils/gcp_auth.py`; adds zero new Python dependencies to
  `observatory/requirements.txt` (Cloud Run image stays small); concrete contrast case in
  this same repo: miniBabel (page 0008) ships a real `.pth` PyTorch weights file loaded
  from GCS on every cold start (see STAR_stories.md #9) — that's the cost avoided.
- **Generation: raw REST call to the Claude Messages API via `requests`**, no `anthropic`
  SDK — mirrors the only existing external-API pattern already in this repo
  (`get_google_maps_latency()` in `pages/0008_The_Quest_to_O1_NLP.py:105`). Model:
  `claude-haiku-4-5` for cost/latency in an interactive demo. (Corrected 2026-07-30 — code
  and this doc previously had a stale, incorrectly date-suffixed model ID,
  `claude-haiku-4-5-20251001`; the real current ID has no date suffix.)
- **GCS-only rule compliance**: Streamlit page code never reads local files at runtime.
  Raw source corpora are read only by the offline precompute scripts, run manually in
  Codespaces; only the derived parquet gets uploaded to GCS.
- **No vector DB**: each corpus is small (low hundreds of chunks). Retrieval is in-memory
  `numpy` cosine similarity — no `faiss`/`chromadb` needed at this scale. See
  `Agentic_Knowledge.md`'s "relational vs. vector DB" and "when RAG vs. SQL" entries for
  the general principle behind this call.

## 6. UI notes (cosmetic — doesn't affect how RAG works, kept separate on purpose)

The page's corpus picker is a horizontal stepper (numbered dots, active one highlighted
teal) matching the visual pattern already used on page 0008, driven under the hood by
hidden `st.tabs()`. This is presentation only — switching corpora just changes which
parquet gets loaded in §1's "page loads" step; the retrieval/generation mechanism itself
never changes. `st.components.v1.html` (used for the stepper's tab-sync script) is
deprecated by Streamlit (removal after 2026-06-01) — migrate to `st.iframe` eventually, not
urgent.

## 7. Troubleshooting log (real incidents, also literal interview material)

1. **403 `Lightning dunning decision is deny`** — a pending payment on GCP billing for
   project `drivers-dilemma`. Vertex AI requires active billing, unlike the BigQuery/GCS
   free-tier usage the rest of the project relied on. Resolved in GCP Billing directly.
2. **403 `IAM_PERMISSION_DENIED` on `aiplatform.endpoints.predict`** — service account
   missing the IAM role, complicated by Google's Vertex AI → "Agent Platform" rebrand (the
   expected role name no longer appears verbatim in the IAM picker). Resolved by granting
   the broader "Agent Platform Administrator" role — an accepted, flagged tradeoff for a
   personal, non-production, short-sprint project.
3. **429 `RESOURCE_EXHAUSTED`** — low requests-per-minute quota on a new/free-tier
   project, hit embedding one chunk per request. Fixed structurally: `embed_batch()` sends
   up to 5 chunks per request (cuts request count directly) plus retry-with-backoff and
   partial-progress saving.
4. **Background process reliability** — launching Streamlit via a bare `(streamlit run
   main.py &)` subshell in the agent's shell tool silently died mid-demo more than once
   (symptom: a transient 502 in the browser, backend actually dead not just disconnected).
   Fixed by always using the Bash tool's native `run_in_background: true` instead of a
   manual subshell — this held reliably every time it was used.

## 8. What's next

Candidate #4 is now DONE (§4 — see §0, #3 retired). **Candidate #5 (Text-to-SQL) is the
only remaining candidate**, not yet started — it gets its own section following the same
5-part shape (Inputs / Scripts / Outputs / Deploy to GCS / Inference notes), pointing back
to §1 for the shared mechanism where applicable (note: #5 is NL2SQL, not classic RAG, so §1
won't apply verbatim — expect a different mechanism section). Also not yet documented here:
conversational memory (sliding window + compaction), the system-prompt rewrite, and the
Agentic RAG tool-use routing tab added to `0010_RAG_Assistant.py` — these are page-level
features that apply across all 3 corpora rather than being specific to one candidate, and
still need a write-up (a natural home would be a new §1.x subsection, since they extend the
shared inference mechanism itself rather than any one candidate's §2-§4 section). A weekend
pass is planned to evaluate the completed RAG set (#1/#2/#4): hallucination behavior,
retrieval quality, and (where relevant) reranking — see `Agentic_Knowledge.md`'s RAG
evaluation roadmap entry for the metrics framework (RAGAS: faithfulness, answer relevancy,
context precision/recall).
