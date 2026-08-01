# Tech Debt — Canonical

This is the single canonical tech debt doc, merged 2026-08-01 from two prior sources:
1. `tech_debt_claude.md` — Claude-originated items, previously kept separate from the user's own list.
2. `project_tech_debt.md` — the user's own manually-curated backlog (numbered `TD0001`+).

Nothing was deleted in the merge — both files' full histories are concatenated below, Claude's section first. Both original files are kept in `claude_docs/` for traceability, but this file is now the one to read/update going forward. The previous rule ("Claude never edits `project_tech_debt.md`") is lifted for this unified doc — Claude has write access here. The exact format/process for how entries should be added going forward still needs to be formalized (see the Claude-open item about this below); until then, follow the existing conventions visible in each concatenated section.

---

# Part 1 — Claude-originated (formerly tech_debt_claude.md)


Tech debt items discovered or logged by Claude during sessions go here, not in `project_tech_debt.md` (that file is human-only, per [[feedback_conventions]] / `assets_ignored/CLAUDE.md`).

## Open

- **2026-08-01 — Add conversational memory to the RAG Assistant (0010), with explicit context-window and cost management.** Confirmed by reading `pages/0010_RAG_Assistant.py`: each question is sent to `ask_claude()` in isolation (only that question + its retrieved chunks) — no `st.session_state` history, no multi-turn memory across questions in the same browser session. Adding conversational memory means accumulating a message list and resending it each call, which directly trades off against context window size and per-request cost (more history + more retrieved chunks = more input tokens every turn). Needs a deliberate design, not just "add session_state": decide how much history to keep verbatim vs. summarize/compact, and how growing history interacts with retrieval's own top-k chunk budget. Cost is explicitly the top priority per the user — tie this to reading Anthropic's prompt-caching, context-windows, token-counting, pricing, and compaction docs (in progress, assigned by a mock interview) before implementing, so the design uses real numbers instead of guesses. Planned for tomorrow.

- **2026-08-01 — `ask_claude()` (`_0010_data.py:121-137`) doesn't set `temperature` in the API payload, silently using the API default of 1.0.** Confirmed by reading the code: the request body has `model`, `max_tokens`, `system`, `messages` but no `temperature` key. This is misaligned with the system prompt's own instruction ("Answer using ONLY the provided context... don't guess") — high default temperature favors creative/varied token choices over fidelity to retrieved context. Fix: add `"temperature": 0.2` (or similar low value) to the payload dict. Trivial one-line fix, left for tomorrow alongside the other RAG work rather than done ad hoc mid-conversation.

- **2026-08-01 — Add query rewriting to the RAG Assistant (0010).** Currently `retrieve()`/`retrieve_trips()` embed the raw `st.text_input` question as-is for similarity search. Once conversational memory (item above) exists, a follow-up question like "what about the second one?" has no standalone meaning for retrieval without rewriting it against prior turns first (e.g. "what about the second retrieved trip in the Comfort ride example?"). Tied to the same memory item — query rewriting is the piece that makes multi-turn RAG actually retrieve correctly, not just remember the chat text. Planned for tomorrow, same session as the memory work.

- **2026-08-01 — RAG #1's corpus is stale: it reads from `assets_ignored/claude_docs/` (untracked), needs to read the git-tracked docs instead.** `observatory/scripts/rag_build_corpus.py` still points `DOCS_DIR` at `assets_ignored/claude_docs/`, which predates the CLAUDE2 reorg. Per the new root `README.md` ("On the Use of Claude Code" section), the real, git-tracked documentation now lives at `.claude/claude_docs/` — `assets_ignored/` is untracked/local-only and no longer where the canonical docs live. `#1`'s corpus (`rag_corpus_claude_docs.parquet`) was built from the old, now-stale location and needs a full rebuild pointed at the new path once the reorg settles. Planned for tomorrow, per the user.

- **RESOLVED (2026-08-01) — Two parallel claude_docs trees diverging live, found during a concept-drift audit.** `assets_ignored/claude_docs/` (old) still exists in full alongside the new canonical `.claude/claude_docs/`, byte-identical at reorg time (2026-08-01 00:51) but Claude kept writing to the OLD path afterward without realizing the canon had moved — this very tech-debt entry and its neighbor above were symptoms of that (added to `assets_ignored/claude_docs/tech_debt_claude.md` first, only reconciled into this file after the user asked explicitly). **Decision (user, same day): leave `assets_ignored/claude_docs/` in place as-is, gitignored, kept for traceability — not deleted, not actively maintained going forward.** `.claude/claude_docs/` is the sole write target from here on.
  - Also fixed same day — `observatory/CLAUDE.md` referenced `.claude/claude_docs/project_design_system.md` for the `fn-below` tooltip CSS override, a file that never existed in the new tree. Recovered the exact original snippet from git history (`git show 6d0c788:CLAUDE.md`, present before the reorg commit `25a341f` dropped it) and inlined it directly into `observatory/CLAUDE.md`'s existing "Canonical hover footnote pattern" section instead of creating a new file for one small snippet.

- **2026-07-31 — MEMORY.md rewrite deferred to end of the claude_docs pass, explicitly do not forget.** MEMORY.md is the pointer/index file for claude_docs (README-of-claude_docs equivalent, per user's own framing) -- every file touched during the current CLAUDE2 reorg (renames, deletes, new files like incidents_log.md/prompt_engineering//mermaid/) makes it stale, so updating it live mid-pass would be pure churn. Deliberately left stale until the file layout under CLAUDE2/claude_docs/ is fully settled, then do one clean rewrite reflecting the final structure. Fold into step 4 (iterar sobre los dos ClaudeMD) of the reorg agenda, not a separate step.

- **2026-07-31 — Cleanup pending: prompt_engineering.md (renamed from feedback_conventions.md, moved out of a now-deleted prompt_engineering/ subdirectory into a flat file).** Two issues to fix once the first full claude_docs pass is done: (1) redundancy check against root CLAUDE2.md -- overlaps with conventions already stated there (commit message rules, never-commit-on-users-behalf, anonymization). (2) Scope cleanup -- the file currently mixes genuine prompt-engineering/human-Claude interaction content with design-system/CSS semicanon content (plain_text, info-mark, snake_case styling shorthand terms) that belongs in observatory/CLAUDE2.MD's design system section instead, not in a doc meant to be prompt-engineering-only. Deferred: user explicit instruction, track it, do not fix mid-pass.

- **2026-07-30 — ChromaDB corpus (candidate #4, Trip Records tab in 0010) feels slow, needs profiling.** First load of that tab downloads the full ChromaDB persistent store (~30MB, several files) from GCS to `/tmp` via `download_prefix_from_gcs()` before any query can run — flagged by the user as suboptimal while testing live. Not root-caused yet. Suspects to check: (a) the multi-file sequential download itself (6+ separate GCS blob fetches, no parallelism); (b) ChromaDB's own load/index-warm time once the local files exist; (c) the usual two-call latency (Vertex AI embed + Claude generate) stacking on top of (a)/(b) on a cold session. Needs actual profiling (time each stage) before proposing a fix — don't guess.
- **2026-07-30 — RAG system prompt (`ask_claude()` in `_0010_data.py`) needs a prompt-engineering pass.** It's a single generic prompt shared across all 3 corpus tabs (also mislabeled "documentation assistant" for the Trip Records/ChromaDB tab, see below). Apply Anthropic's documented best practices before rewriting: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices — and while there, decide whether to keep one shared prompt (parametrized per corpus) or split into per-corpus prompts.
- **2026-07-30 — Create hooks and agents for this project.** Raised during EPAM interview-prep reading of Claude Code docs (features-overview, tools-reference). This repo has no custom `.claude/agents/*.md` subagent definitions and no project hooks in `settings.json` yet — both are documented capabilities the user hasn't set up locally. Not scoped/prioritized yet; revisit once there's a concrete recurring task that fits either pattern (per the "build your setup over time" trigger table — don't add either speculatively).
- **2026-07-30 — Refactor/reorganize `CLAUDE.md` and `assets_ignored/claude_docs/`.** Also surfaced during EPAM interview-prep reading of the Claude Code docs, which recommend keeping CLAUDE.md under ~200 lines and moving reference material out into skills/rules — this project's CLAUDE.md is currently 461 lines covering many unrelated topics (GCS deployment workflow, anonymization protocol, BQ reference, environment mechanics, STAR stories pointer, etc.) that could arguably live in `.claude/rules/` (path-scoped) or dedicated skills instead. Not scoped yet — needs a deliberate pass, not a drive-by edit.
  - **2026-07-30 update:** user moved the file from `assets_ignored/CLAUDE.md` to repo root `/CLAUDE.md` ("as it should have always been"). Confirmed via `ls`: old path gone, new path exists. But `git status` shows it as **untracked** — since `assets_ignored/` was gitignored, git sees this as a brand-new file, not a tracked rename. Needs `git add`/commit to actually bring it under version control (user's call when). Also still has stale internal path references (e.g. line ~47 repo-layout diagram says `assets/CLAUDE.md`) and other memory files (this one included) still say `assets_ignored/CLAUDE.md` — needs a full path-reference sweep across memory + the file itself once the move is final and no more moves are planned.
  - **2026-07-30 update 2:** blanket `/.claude/` rule removed from `.gitignore` (with `worktrees/` and `scheduled_tasks.lock` re-ignored specifically instead), so `.claude/rules/` and any custom `.claude/agents/*.md` will now be tracked once created — no longer blocked by the gitignore issue noted above.
  - **2026-07-30 update 3 — actual reorg workflow agreed with user:** when the real pass happens, go section by section through CLAUDE.md (currently 461 lines) and sort each into one of four buckets instead of defaulting everything into rules: (1) stays in CLAUDE.md — always-on, short, core; (2) moves to a skill — reference/workflow consulted on demand (e.g. GCS deploy pipeline, feature store schema); (3) moves to `.claude/rules/` with `paths:` frontmatter — scoped to specific files/dirs (e.g. anonymization protocol only relevant to `pages/*.py`, BQ join patterns only relevant near `bq_client.py`); (4) becomes a hook — anything phrased as a hard guarantee rather than a suggestion (candidates already identified: the zero-quotes-in-commit-messages rule as a PreToolUse block on `git commit`, the GCS-upload permission requirement as a PreToolUse block on `gcs_deploy.py`, and the never-run-git-commit-on-the-users-behalf rule as a PreToolUse block on `git commit` itself, currently only enforced via the permissions system, not a hook). Goal: CLAUDE.md under ~200 lines when done.
  - **2026-07-30 update 4 — fifth bucket, nested CLAUDE.md:** discussed with user whether observatory/-specific content (sidebar, stepper CSS, page_link pattern) should live in a separate observatory/CLAUDE.md instead of the root one, since nested CLAUDE.md files are natively supported (load additively when Claude works inside that subdirectory, per the layering rules). Verbatim distinction agreed with user: Nested CLAUDE.md = scope by folder/directory, simple, one file per area. .claude/rules/ with paths: = scope by file pattern (glob), more granular. For teams/multi-project, nested CLAUDE.md is more readable (whats in observatory/? look at observatory/CLAUDE.md), while rules is better for cross-cutting rules by file type. Not decided yet which sections would move here vs to rules/skills/hooks -- fold into the section-by-section sort when the real pass happens.
  - **2026-07-30 update 5 — /start skill likely deprecated by the CLAUDE.md move.** The start skill exists to manually force-read the project context file because it used to live at assets_ignored/CLAUDE.md, a non-standard path Claude Code does not auto-load. Now that the file lives at the repo root (/CLAUDE.md), Claude Code loads it automatically, full content, every session start -- per the official features-overview context-loading diagram (CLAUDE.md = Session start, Always in context). So /start is now (a) redundant, since the load already happens without invoking it, and (b) pointing at a stale path (assets_ignored/CLAUDE.md, which no longer exists) in its own instructions. Needs a decision: retire the skill entirely, or repurpose it toward something else (e.g. re-reading memory files and giving a status summary, not re-reading CLAUDE.md).
  - **2026-07-30 update 6 — approved scope for the reorg, target: ready to showcase/explain by Monday (2026-08-03).** User confirmed the following as the actual plan (not just candidate ideas):
    1. Split into root CLAUDE.md + a separate observatory/CLAUDE.md (nested, nested-CLAUDE.md bucket from update 4).
    2. Root CLAUDE.md hard cap at ~200 lines.
    3. Beyond the four formal mechanisms (Skills, Commands, Rules, Hooks), user wants a deliberate set of persistent-state/memory documents, distinct from those four, covering:
       3.1 A formal Tech Debt doc with progress tracking. RESOLVED 2026-07-31: this WILL unify with the user's project_tech_debt.md into one canonical, continuously-updating doc -- one-time merge preserving both files full histories (this Claude-originated file's content plus the user's own numbered TD backlog), not a fresh start. Confirmed: the standing never-edit-project_tech_debt.md rule is lifted going forward once merged -- Claude will have write access to the unified doc. NOT YET EXECUTED -- the exact format/handling process for the unified doc still needs to be formalized before Claude actually writes to it, and the physical merge itself is deferred to the end of the current CLAUDE.md/CLAUDE2 reorg pass (per user: no se mueve nada hasta el final).
       3.2 An error/testing log -- what has already been tried and failed, so it is not repeated.
       3.3 Prompt engineering / human-Claude interaction rules -- specific instructions for how the user and Claude should interact (distinct from project conventions).
       3.4 Other miscellaneous docs for preserving context, uncategorized bucket.
    User explicitly deferred deep design of this to a dedicated session (same day, later), this entry is just to not lose the agreed scope in the meantime.

**Why:** User wants a hard separation between their own manually-curated tech debt backlog (`project_tech_debt.md`, numbered TD0001+) and anything Claude notices/logs — so the two don't get mixed or accidentally overwritten.
**How to apply:** When a new piece of tech debt comes up during a session, add it here with a short description and date, not to `project_tech_debt.md`. If the user wants something promoted into their own numbered list, that's their call to make manually.

---

# Part 2 — User-curated backlog (formerly project_tech_debt.md, numbered TD0001+)


> [!WARNING]
> TD0001. Status: Pending ; Priority: Low
## NOT FIXED — network_notes.md should inform the undirected-graph/geodesic-distance dashboard rebuild

`assets_ignored/network_notes.md` (renamed 2026-07-11 from `assets/network_notes.md` as part of
splitting the private/untracked context folder — see [[project_overview]] for the rename) contains
notes the user wants applied when rebuilding the undirected network graph dashboard (zone
connectivity / geodesic distance analysis, `grafo_topologico` in the project's asset list —
currently surfaced in `0603_Network_Graph.py` / `research_full/Phase_6_Generative_Moonshots/`).

**Why:** User flagged this file specifically as relevant input for that future rebuild, not just
background reading.
**How to apply:** Before rebuilding or significantly revising the undirected-graph/geodesic-distance
dashboard, read `assets_ignored/network_notes.md` first and incorporate its notes into the design.

> [!WARNING]
> TD0002. Status: Pending ; Priority: Medium

## NOT FIXED — research_core / research_full will drift until final sync pass

Confirmed 2026-07-10: `research_core/` (flat, curated ~15-notebook spine) and
`research_full/Phase_N_*/` (full phase-organized history) currently hold duplicate
copies of the same notebooks, kept in sync manually. The user expects to keep editing the
`research_core` copies (e.g. `0407_Clustering_Paper_Streamlit.ipynb`, flagged separately for
its 50MB size) before they're truly final — so the two directories are allowed to diverge
during that editing period, by design, not by accident.

**Naming note (2026-07-18):** these directories went `research_archive`/`research_core` ->
`research_full`/`research_core` -> back to `research_full`/`research_core` — "notebooks_"
was dropped because both directories hold non-`.ipynb` files (webapp scripts, AppsScript),
not just notebooks. Current names are `research_full`/`research_core`.

**Why:** User's stated intent — edit `research_core` notebooks toward their final polished
form first, without needing to touch `research_full`'s copies on every edit.
**How to apply:** Once every `research_core` notebook is at its 100% final version (no more
planned edits), copy each one back over its counterpart in `research_full/Phase_N_*/` so
the two directories become byte-identical again for the notebooks that exist in both. Don't
do this copy-back prematurely — only after the user confirms a given `research_core` notebook
is truly done. Re-check file size on `0407_Clustering_Paper_Streamlit.ipynb` specifically when
this happens (see separate note on its 50MB size / GitHub push warning) — if it's still huge,
consider trimming embedded cell outputs before copying it back into the archive too.


> [!WARNING]
> TD0003. Status: RESOLVED ; Priority: NA

## RESOLVED (2026-07-18) — Phase 1 acquisition scripts missing from repo entirely

Originally confirmed 2026-07-10: Phase 1 (Ground Truth acquisition) was represented only by
the GTS field-logging webapp, with two real artifacts (the initial geocoding AppsScript, the
OCR pipeline script) missing from the repo entirely — recovered from Drive and triaged
2026-07-18, file by file, to weed out deprecated/duplicate copies rather than dumping
everything in wholesale.

**Resolution:** `research_full/Phase_1_Acquisition_and_Ground_Truth/` is now flat (no more
`GTS_WebApp/` subfolder) and holds:
- `0101_Engine1_WebApp_index.html` (renamed from `GTS_index.html`)
- `0102_Engine1_WebApp_back.js` (renamed from `GTS_AppsScript.js`)
- `0104_Engine2_Geocoding_API.py` — the previously-missing geocoding script, recovered from
  Drive (`Geocoding_API.py`, misleadingly `.py`-extensioned but actual content is Google Apps
  Script — batch-geocodes pickup/dropoff addresses in a Google Sheet)

`research_core/` (curated spine) picked up the two most narrative-worthy pieces:
`0101_Engine1_WebApp_index.html` and `0103_Engine2_Gemini_OCR.py` (the OCR pipeline script,
`gemini_ocr_pipeline.py` from the Drive recovery). The backend AppsScript (`0102`) and the
geocoding script (`0104`) stayed `research_full`-only — not spine material.

**Deprecated/duplicate files found during the same Drive recovery, deliberately left out:**
- `geotimestamps/` (an earlier `Code.gs` + `index.html` pair) — confirmed near-identical to
  the already-archived GTS webapp, just an older deployment (different `webAppUrl` endpoint).
  No new information, not archived.
- `chrono_forge_pre_processing.py` and `colab_keystone_generator_v6_2_definitive.py` — both
  confirmed byte-for-byte Colab auto-exports of notebooks already in `research_full/Phase_2`
  (each file's own header says "Automatically generated by Colab"). Not archived.
- `ledger_join.py` — a genuinely distinct local-edition variant of
  `0203_Temporal_Ledger_join.ipynb`'s "Cloud Edition" (reads local CSVs instead of live Google
  Sheets), but user decided to leave it out since the cloud edition already covers that
  pipeline step in the kept artifact.
- `chrono_forge_poc.py` — kept (see below), the one true gap: a local-filesystem-only script
  (scans a local Drive-synced screenshots folder, extracts EXIF/PNG timestamps) that could
  never have run in Colab, which is why it went missing in the first place. Added as
  `0201_Temporal_Ledger_POC.py`, with `Phase_2_Data_Engineering/`'s existing files renumbered
  `+1` to make room at the front of the sequence.

**Why this matters:** these are load-bearing parts of the acquisition story (Engine 1 GTS +
Engine 2 OCR/geocoding, per `0002_Acquisition_Pipelines.py`'s "dual-engine" narrative) — now
fully backed by source-of-truth in git instead of only existing as the Observatory's own
description of them.



> [!WARNING]
> TD0004. Status: RESOLVED ; Priority: Keep for traceabilty, future problems. 


## RESOLVED (2026-07-10) — 0006 fragment isolation revisited and closed out

User confirmed this is done as of 2026-07-10. See the abandonment writeup directly below for the root-cause pattern (non-contiguous `with` blocks) — still worth checking before attempting fragment isolation on any other page with the same module-level-`with`-block structure.

## ABANDONED — 0006 fragment isolation attempt, reverted (structural indentation mismatch)

Attempted 2026-07-10: wrap `top_tab1` ("Analysis") and `top_tab2` ("Interactive Inference Tool") in `0006_Payout_Physics_Causal_Inference.py` each in their own `@st.fragment`, same pattern used successfully on 0002/0003, to stop the Interactive Inference Tool's slider/selectbox (pure local math, no BQ) from triggering a full-page rerun that re-renders all 5 "Analysis" sub-tabs' Plotly charts on every drag.

**Why it broke:** unlike 0002/0003, this page's `with top_tab1:` block is NOT contiguously indented — only the intro text + `ci-stepper` HTML/JS + the `tab1, tab3, tab4, tab5, tab6 = st.tabs([...])` call are actually nested under `with top_tab1:`. The 5 sub-tabs' actual content (`with tab1:`, `with tab3:`, etc.) is written as separate **module-level** (0-indent) `with` blocks further down the file, which only worked because `tab1`/`tab3`/etc. are plain Python variables visible module-wide once assigned — Streamlit doesn't require a tab's content to be textually nested under the variable's creation point. Converting `with top_tab1:` into `def _render_analysis(): ...` only pulled the truly-indented portion into the function; the module-level `with tab1:` blocks after it stayed outside, and since `tab1` is now a local variable inside the function (only bound when the function actually runs), referencing it at module level raised `NameError: name 'tab1' is not defined`.

**Fix reverted via `git checkout` before commit** — 0006 is back to its last committed state, no fragment isolation, working as before. Never got to confirm whether the fix would have provided meaningful perceived improvement, since it broke before that could be tested.

**Why:** Third time this project has learned that Streamlit's `with <container>:` blocks don't need to be textually contiguous — the same "assumed structure without checking indentation/nesting for real" mistake class as the nav-card `:has()` bug and the 0003 stepper-connector bug, but this time on *my own* refactor rather than pre-existing code.
**How to apply:** If fragment isolation on 0006 is revisited, first map out (via `grep -n "^with \|^    with "` or similar, checking actual leading-whitespace column, not just visual proximity in the file) exactly which lines are genuinely inside `with top_tab1:` vs. which are module-level `with tabN:` blocks that merely reference a variable assigned inside it. Either move all the sub-tab bodies to be textually nested inside the fragment function too (large mechanical edit, re-indent ~600 lines), or leave 0006 as-is — the actual performance case for fixing it was never strong to begin with (only client-side re-render cost, no network calls involved, since all 4 BQ queries are already `@st.cache_data`-cached).


> [!WARNING]
> TD0005. Status: Resolved ; Priority: Monitor; Keep for traceabilty, future problems. 

## SUPPOSEDLY FIXED (watch for recurrence) — 0005 "Phase 1-4" cards go unclickable after any fragment rerun, until page reload

**Fix applied 2026-07-10:** moved the `components.html()` click-forwarding script (see full root cause below) from module-level — outside `render_observatory()` — to just after `tab1, tab2, tab3, tab4 = st.tabs([...])` *inside* `render_observatory()` (which is `@st.fragment`-decorated). It now re-injects and re-captures fresh tab element references on every fragment rerun instead of once at page load, so the stale-reference bug described below should no longer be reproducible. **Not yet confirmed fixed by the user in the running app** — if the "Phase 2/3/4 not clickable without reload" symptom recurs, this entry should be reopened (move back to "NOT FIXED") rather than assumed already covered. If confirmed permanently resolved during a future tech-debt sweep, delete this entry entirely instead of leaving it as a stale "fixed" note.

Original bug, confirmed 2026-07-10 (user-reported recurring bug, root-caused via code read): in `0005_The_Cost_of_Patience.py`, the custom "Phase 1/2/3/4" clickable cards (`.phase-card` divs, ~line 166-187) are a JS-driven visual replacement for the native (CSS-hidden) `st.tabs()` bar — same pattern as the `ci-stepper` in 0007/0008. The `components.html()` script that wires `.phase-card` clicks to `tabs[i].click()` (line 191) runs **once**, outside any fragment, and captures `document.querySelectorAll('[data-baseweb="tab"]')` at that moment via closure.

The actual `st.tabs()` call (`tab1, tab2, tab3, tab4 = st.tabs([...])`, line 439) lives **inside** `render_observatory()`, which is decorated `@st.fragment` (line 325). Any interaction that triggers a fragment-scoped rerun of `render_observatory()` (any widget inside the 4 tabs) causes Streamlit to recreate the tab-bar DOM nodes. The JS's captured `tabs` array still points at the old, now-detached nodes — clicking a `.phase-card` after that calls `.click()` on an element that's no longer wired to the live UI, so nothing happens. A full page reload re-runs the whole script fresh, re-capturing correct references, which is why reload "fixes" it until the next fragment rerun.

**Why:** Same root-cause class as three earlier-documented bugs this project has hit (nav-card `:has()` selector unreliability, 0003's old stepper connector line, the h1-swallows-inline-styles issue) — code assumed a DOM reference captured once stays valid across a mechanism (here, `@st.fragment` reruns) that actually replaces the underlying nodes. Worth recognizing this pattern immediately in any future page that mixes a `components.html()`-injected click-forwarding script with `@st.fragment`-wrapped tabs.
**How to apply:** Two possible fixes, not yet chosen/implemented (ask user before proceeding, per their standing instruction to consult before executing):
1. Move the `components.html()` script call to run *inside* `render_observatory()` itself (so it re-injects and re-captures fresh tab references on every fragment rerun, same as the tabs it's targeting) — simplest, but re-injects the script on every fragment rerun, which is wasteful but likely harmless given it's cheap JS.
2. Rewrite the click-forwarding to not rely on captured element references at all — e.g. use event delegation on a stable ancestor (`document.body` or `window.parent.document`) with a `MutationObserver` or re-query `tabs` live inside the click handler instead of at closure-creation time (`document.querySelectorAll(...)` called fresh on each click, not cached once at setup).
Also worth checking whether 0007/0008's `ci-stepper` pattern has the same latent bug — those pages don't currently wrap their stepper's tabs in `@st.fragment` (confirmed during the 2026-07-09 perf pass), so they're not affected *today*, but would become vulnerable to this exact same failure mode if fragment-wrapping is ever added there later.



> [!WARNING]
> TD0006. Status: RESOLVED ; Priority: NA

## RESOLVED (2026-07-10) — loading-spinner text homologated

User confirmed this is done as of 2026-07-10. See the original findings below for the specific inconsistent instances found and the tone/ellipsis decision that had to be made — useful if a new spinner call site is added and needs to match the now-unified convention (check current code for which tone/character was chosen, since that decision isn't recorded here).

## FORMERLY NOT FIXED — homologate loading-spinner text across the app

Found 2026-07-09 during the page-by-page perf pass (see [[project_live_calls_audit]]): `st.spinner(...)`/`show_spinner="..."` label text is inconsistent in tone and style across the repo — no shared copy convention. Current instances found:

- `pages/0005_The_Cost_of_Patience.py:327` — `"Loading data…"` (generic)
- `pages/0005_The_Cost_of_Patience.py:928` — `"Simulating the Efficient Frontier…"` (specific/contextual — fine as-is)
- `pages/0004_Data_Census_(The_Basics).py:247` — `"Warming up SQL sandbox…"` (added 2026-07-09 with the parallel-prefetch fix)
- `pages/0004_Data_Census_(The_Basics).py:260` — `"Querying pienza_mini…"` (generic, names the dataset)
- `utils/bq_client.py:23` — `@st.cache_data(show_spinner="Querying the Pienza Data Warehouse...")` — this is the shared `fetch_data_from_bq()` wrapper, so this exact string is what shows on every page that uses it and doesn't override with its own spinner
- `utils/gcp_client.py:43` — `show_spinner="Decrypting GCP Telemetry..."` (stylized/thematic)
- `utils/gcp_client.py:128` — `show_spinner="Initializing O(1) miniBabel Engine..."` (stylized/thematic, page-specific)
- `utils/gcp_client.py:164` — `show_spinner="Accessing Sovereign Dimensions (Fast-Load)..."` (stylized/thematic, odd phrasing)

Also inconsistent: `...` (three periods) vs `…` (ellipsis character) used interchangeably.

**Why:** No functional impact — purely a copy/tone consistency issue, visible to anyone waiting on a query. Some are plain/technical ("Querying pienza_mini…"), others are flavorful/thematic ("Decrypting GCP Telemetry...", "Accessing Sovereign Dimensions") — reads as unintentional drift rather than a deliberate voice choice.
**How to apply:** Before homologating, decide (ask user) whether the target voice is plain/technical or the flavorful/thematic style already used in a few spots — then apply one consistent tone and one consistent ellipsis character across all `st.spinner()`/`show_spinner=` call sites repo-wide. Not urgent, cosmetic-only, safe to batch into a future styling pass.


> [!WARNING]
> TD0007. Status: RESOLVED ; Priority: NA
## NOT FIXED — modularization candidate: 0002's hardcoded Engine 2 data literals (550 lines) -> FIXED

During the 2026-07-09 page-by-page perf pass (see [[project_live_calls_audit]]), the 4 BigQuery queries backing Engine 2's OCR carousel in `0002_Acquisition_Pipelines.py` were replaced with hardcoded Python literals (`_DF_OCR_RECORDS`, `_DF_OFFERS_RECORDS`, `_DF_SILVER_RECORDS`, `_DF_DTYPES_RECORDS`, lines ~487-1034) — frozen ground truth for the 10 fixed carousel offers, sensitive fields pre-masked with the page's own `_obf_*` functions before being written to source. This eliminated ~4 live BQ round trips on every cold-cache first load with zero perf downside (Python doesn't get slower to import/run from more lines in a file — that concern only applies to runtime I/O, not file length).

**Why this is here:** User flagged that once the current perf sprint is done, the next phase is a modularization pass across the Observatory pages (some of which run 1000-2000+ lines), and wants this specific block considered as a candidate then, not now.
**How to apply:** When modularization work starts, consider splitting these 4 literals out of `0002_Acquisition_Pipelines.py` into a sibling module (e.g. `pages/_engine2_offers_data.py` or similar naming convention decided at that time) and importing them (`from pages._engine2_offers_data import _DF_OCR_RECORDS, ...`). This is a pure code-organization move — plain Python import, zero added I/O, zero perf cost, same as today. Do **not** move this data to an external file loaded at runtime (JSON/parquet/GCS) — that would reintroduce the exact live-fetch cost this hardcoding pass just eliminated, and would also violate the GCS-only-for-runtime-assets architecture rule in `assets/CLAUDE.md` if done as a local file read via `open()`.



> [!WARNING]
> TD0008. Status: RESOLVED ; Priority: Monitor (SUPPOSEDLY FIXED MULTIPLE TIMES, STILL FAILS EVERY NOW AND THEN)

Confirmed 2026-07-09: `kepler_3D.html`'s (GCS bucket `pienza-streamlit`) actual `mapState` config is correct — `latitude:19.394486029613017, longitude:-99.19233180996436` (Mexico City), not San Francisco. The only San-Francisco coordinates in the file (`-122.3391,37.7922`) are hardcoded Mapbox static-image thumbnail URLs used by Kepler.gl's built-in map-style picker UI (preset style preview icons) — completely unrelated to the actual displayed viewport.

**Suspected cause (not confirmed by reading Kepler.gl's internals):** Kepler.gl's exported HTML likely renders its factory-default initial state (San Francisco) for a brief moment before its JS bundle finishes parsing and dispatching the saved `mapState`/`config` JSON to the redux store — a known class of behavior in Kepler.gl's async `addDataToMap`/`loadKeplerGlData` boot sequence, not something wrong with our exported config.

**Why:** User has hit this "map briefly shows SF before snapping to CDMX" symptom before and wanted it in memory since they'd lost track of any workaround previously considered — surfaced again during a 2026-07-09 page-by-page perf pass on main.py (see [[project_live_calls_audit]]) while looking at the Kepler hero map, which was also wrapped in `@st.fragment` that same session to stop full-page reruns from reinitializing it (that fix does not address this flash, which happens on first mount / page navigation regardless).
**ATTEMPTED AND REVERTED 2026-07-09:** tried option (b) in `main.py`'s `_render_kepler_hero()` — injected `body { opacity: 0; transition: opacity 0.3s ease; }` plus `setTimeout(() => document.body.style.opacity = 1, 700)` into the `force_white_css` string prepended to the Kepler HTML. Worked locally, but on the deployed Streamlit Cloud app this caused a regression worse than the original bug: the map rendered as a **permanently blank white box**, not fixed by waiting, only fixed by a manual browser reload — user reported this on the live public app. Reverted back to the plain `force_white_css = "<style>body { background-color: white !important; }</style>"` (just the white background override, no opacity/timeout trick) in the same session.

**Root cause of the regression not diagnosed** — suspects: (a) Streamlit Cloud may render `components.html()` output through a different mechanism than local dev (static asset serving vs. direct srcdoc) where inline `<script>` execution or `setTimeout` timing behaves differently; (b) Cloud's cold-start load time is unpredictable and likely just longer than the fixed 700ms, and the fixed timer had no recovery path if it fired before the map was ready. Do not reintroduce a bare fixed-delay setTimeout hack without testing directly against the deployed Cloud app — local testing alone did not catch this failure mode.

**CONFIRMED FIXED 2026-07-09 (verified live on deployed Streamlit Cloud app):** replaced the fixed-delay approach with an event-driven one — `setInterval` every 100ms polling for `document.querySelector('canvas')` (the actual WebGL canvas Kepler/Mapbox creates once the map paints, a real readiness signal instead of a guessed delay), calling `reveal()` the moment it's found. Also added a hard 4-second `setTimeout` safety net that force-reveals regardless of whether the canvas was ever found, so the map can never get stuck permanently invisible again. User confirmed on the live public app that the SF flash no longer appears and the map loads cleanly straight to CDMX. This is the current, working implementation in `main.py`'s `_render_kepler_hero()` — don't revert to the fixed-delay version.
**How to apply:** If this second attempt still misbehaves on Cloud, the next debugging step should be checking whether Streamlit Cloud's `components.html()` iframe even allows script execution the same way local does (e.g. by having the user check browser devtools console on the live app for JS errors) rather than guessing at another timing-based fix blind.


> [!WARNING]
> TD0009. Status: RESOLVED ; Priority: NA

## NOT FIXED — df_master (load_tournament_ledger) in 0007 is likely dead code from the deprecated Model Playoffs tab

The "Model Playoffs" tab was removed from `0007_Human_vs_AI_Behavioral_Cloning.py` on 2026-07-09 (its content now lives standalone in `observatory/archive/9005_Model_Playoffs.py`, moved by the user out of the active frontend nav). What was left behind in 0007: `df_master = load_tournament_ledger()` (a `@st.cache_data` function that downloads `260420_resultados_torneo_iter2v3.parquet` from GCS bucket `pienza-streamlit` and loads it into a DataFrame) — this was `df_master`'s original consumer. A grep across the current 0007 file found no other reference to `df_master` — it appears to be a fully unused load running on every page visit.

**Why:** This was flagged during a 2026-07-09 profiling pass (see [[project_perf_tricks]]) where 0007 was instrumented with `_prof()` timing checkpoints to find its bottleneck — `load_tournament_ledger` was one of the checkpoints added specifically because it looked like dead weight, not confirmed dead yet (profiling results from the user were still pending when this was written).
**How to apply:** Before removing `df_master`/`load_tournament_ledger` from 0007, re-confirm with a fresh `grep -n "df_master" observatory/pages/0007_Human_vs_AI_Behavioral_Cloning.py` that it's still unused (in case someone re-adds a consumer), and check the `_prof` timing output logged by the user to see how much load time it was actually costing. If confirmed dead, `260420_resultados_torneo_iter2v3.parquet` may also be worth checking for other consumers before considering the whole file orphaned. The temp `_prof()` instrumentation itself (5 checkpoints, red inline `⏱` labels) should be stripped from 0007 once the bottleneck is found — it's not meant to stay in the shipped page.


> [!WARNING]
> TD0010. Status: OPEN ; Priority: Low

## NOT FIXED — layout experiment idea removed from 0007, Threshold Calibrator tab

Removed 2026-07-08: a yellow "PENDING — Layout experiment" banner in
`0007_Human_vs_AI_Behavioral_Cloning.py`, tab 1 "The Science" → sub-tab
"Threshold Calibrator" (`sci4`, right after the Simulator scope caveat box).
It read: "Jugar con el orden de matrices: idea: mover la matriz de FP hacia
abajo y colocar la tabla de Accepted en el espacio vacío que quedaría a la
derecha de L1 (actualmente ocupado por el layout de L2+FP). Esto pondría la
narrativa de earnings directamente al lado de la acción de L1, sin hacer
scroll." The banner was removed as part of the same stale-dev-note cleanup
pass as the 0005 MQI banner above, but the underlying layout idea was never
implemented.

**Why:** user is clearing pending-fix callouts across pages as a style pass;
this is a design/layout improvement idea, not a bug, so it's safe to defer
but shouldn't be lost.
**How to apply:** if revisiting the Threshold Calibrator layout in 0007,
consider moving the FP matrix down and placing the Accepted table in the
space that opens up to the right of L1 (currently occupied by the L2+FP
layout), to put the earnings narrative directly next to the L1 action
without scrolling. Not yet actioned — purely an idea, no urgency.

> [!WARNING]
> TD0011. Status: ABANDONED (out of tech_debt scope) ; Priority: NA

## ABANDONED — Session MQI mean→median change not backpropagated to paper/notebooks

Removed 2026-07-09: a yellow "PENDING FIX" banner in `0005_The_Cost_of_Patience.py` (Session Quality Timeline chart, tab 1 "Market Quality Index") that read: "Session MQI was updated from mean → median in this chart. This change must be backpropagated to: the LaTeX paper (PNG figures) and the source Jupyter notebooks (.ipynb)." The banner was removed from the page (user is clearing stale dev-note callouts across pages), but the underlying work it tracked was never done.

**Why:** the Observatory app's Session MQI aggregation now uses `median` instead of `mean`, but the LaTeX paper's figures (PNGs) and the Jupyter notebooks that produced the original `mean`-based numbers still reflect the old aggregation — the app and the paper/notebooks are now inconsistent on this specific metric.
**Decision (2026-07-18): abandoned from this tech-debt list, not fixed.** User will address this when polishing the LaTeX paper directly — out of scope for repo-wide tech debt tracking. Not tracked as blocking; no action expected here.





> [!WARNING]
> TD0012. Status: RESOLVED ; Priority: NA 

## RESOLVED — plain_text canon `<div>`s silently rendering in Source Sans instead of Inter (2026-07-09)

Confirmed via Playwright `getComputedStyle`: a `plain_text`-styled block wrapped in `<div style='font-size:14px;...'>` computed `font-family: "Source Sans", sans-serif` (Streamlit's own default), while the identical style wrapped in `<p style='...'>` computed `font-family: Inter, sans-serif` correctly. Both had the exact same computed `font-size: 14px` — so two blocks that looked like they shared the same canon still read as visibly different sizes, because `styles.py`'s `GLOBAL_CSS` only forces Inter onto `html, body, [class*="css"], h1-h6, p` — **not `div`**. An explicit (even unrelated) font-family rule anywhere always beats an inherited one, so any plain_text block written as a `<div>` instead of a `<p>` silently falls back to Streamlit's default font while looking identical in the raw style string. Same underlying bug class as the active-tab-color issue (explicit rule beats inheritance) and the nav-card `:has()` issue (assumption about how Streamlit/browser applies styles turned out false) — worth checking for this pattern by default now.

**Fixed instances:** `main.py` (Mission paragraph + Observatory Architecture nav intro, both `<div>`s), `0007_Human_vs_AI_Behavioral_Cloning.py` (page subtitle, also a `<div>`). Fix: add `font-family:'Inter',sans-serif;` directly into the div's own inline style (switch the attribute's outer quotes to double quotes so `'Inter'` can use single quotes inside, e.g. `style="font-family:'Inter',sans-serif;font-size:14px;..."`).

**How to apply:** Any time you write a new `plain_text` (or other canon) block, prefer `<p>` over `<div>` where possible (it gets Inter for free from `GLOBAL_CSS`). If a `<div>` is required (e.g. because it needs to contain other block-level children), always add `font-family:'Inter',sans-serif;` explicitly into its inline style — don't assume it inherits from `body`. If a future "this text looks smaller/different than that other text" report comes in despite identical font-size in the code, check `getComputedStyle(...).fontFamily` on both before looking anywhere else — this exact false alarm already happened once.


> [!WARNING]
> TD0013. Status: RESOLVED ; Priority: NA 

## RESOLVED (2026-07-10) — deployed site theme fixed

User confirmed this is done as of 2026-07-10. Original diagnosis below (`.streamlit/config.toml` swept up by blanket `.streamlit/` gitignore entry, never deployed) — the fix was presumably un-ignoring `config.toml` specifically while keeping `secrets.toml` excluded, per the original recommendation. Worth a quick `git check-ignore -v observatory/.streamlit/config.toml` if the red-theme symptom ever reappears on a fresh deploy.


## FORMERLY NOT FIXED — deployed site shows default Streamlit red theme, `.streamlit/` is gitignored

Confirmed 2026-07-08: repo's root `.gitignore` has a blanket `.streamlit/`
entry, which also excludes `observatory/.streamlit/config.toml` — the file
that sets `primaryColor = "#21918c"` (teal) and the rest of the app's theme.
It's never committed/pushed, so it's never present in the deployed
environment (which clones from git), and the deploy falls back to
Streamlit's default red primary color — e.g. active `st.tabs()` underlines/
text render red instead of teal on the live deploy. Locally everything looks
correct because the file exists on disk even though git doesn't track it.

**Why:** the `.gitignore` blanket-excludes the whole `.streamlit/` directory,
almost certainly to keep `secrets.toml` (BigQuery/GCP credentials) out of
git — but it swept up `config.toml` (pure theme config, no secrets) too.

**How to apply:** un-ignore `config.toml` specifically while keeping
`secrets.toml` (and any other credential file under `.streamlit/`) excluded
— e.g. `.gitignore` entries like `.streamlit/*` plus `!.streamlit/config.toml`,
or just `.streamlit/secrets.toml` instead of the whole directory. Verify with
`git check-ignore -v observatory/.streamlit/config.toml` before/after. Not
yet actioned — user wants to handle this later, deliberately deferred.


> [!WARNING]
> TD0014A. Status: RESOLVED ; Priority: NA 

## RESOLVED — active st.tabs() label showing grey/black instead of teal (0001, 0002)

Root cause (2026-07-08): Streamlit's active tab label inherits `primaryColor`
(teal, `#21918c`) natively from its parent button onto the internal `<p>` —
no explicit CSS needed for that to work. But several pages define a page-wide
`p, li { color: #555; ... }` rule for normal body text, and that explicit
rule always wins over the inherited color regardless of specificity — so the
underline showed teal but the tab text stayed grey. `0003_Feature_Store.py`
has no such `p, li` rule, which is why its tabs looked correct and served as
the reference to diagnose this.

**Fix applied** (identical in `0001_Foundations.py` and
`0002_Acquisition_Pipelines.py`, right after their `p, li {...}` rule):
```css
[data-baseweb="tab"][aria-selected="true"] p { color: #21918c !important; }
```
This targets only the active tab's text, without touching the `p, li` rule
itself (which still correctly controls normal body text everywhere else on
the page).

**How to apply:** If a page's tabs show a teal underline but grey/black
label text, check for a `p, li { color: ... }` rule near the top of that
page's `<style>` block and add the same one-line override right after it —
do not rewrite the `p, li` rule itself. Pages confirmed to have this pattern
as of 2026-07-08: only 0001 and 0002 (both now fixed) — 0003-0009 don't have
a generic `p, li` rule, so they're not affected, but check if a future page
adds one.



> [!WARNING]
> TD0014B. Status: Abandoned ; Priority: NA  (era un bug del tamaño de letra que ya no aplica, se deja aqui por si vuelve a suceder)

## CRITICAL — `!important` inside a raw inline `style=""` attribute gets silently stripped

Confirmed 2026-07-08 via Playwright `getComputedStyle`/`getAttribute('style')` on
`0003_Feature_Store.py`'s subtitle `<p>`: with
`style='font-size:14px !important;font-weight:400;color:#475569;...'`, the
**rendered DOM's actual `style` attribute was missing `font-size` entirely**
— every other declaration in the same string (no `!important`) survived
intact. Removing `!important` from just that one declaration made
`font-size:14px` show up correctly. Reproduced cleanly: this is not a fluke
of one page, one property, or one screenshot — it's a real, verifiable
browser-rendered DOM difference for an inline `style=""` string passed
through `st.markdown(..., unsafe_allow_html=True)`.

**This likely explains a chunk of the session-long "the value I set isn't
showing up" confusion** (main.py hero title chase, various font-size fights)
that got attributed to other causes (`runOnSave`, Streamlit's `<h1>`
auto-processing, quote escaping) — some of those may have been real, but
this `!important`-stripping behavior was very likely *also* silently in play
across many of the `plain_text` / semicanon instances that used
`!important` inside inline `style=""` strings, without ever being isolated
as its own variable.

**Root cause not yet identified** — suspect either Streamlit's own HTML
handling or a sanitization step somewhere in its markdown rendering pipeline
selectively drops `!important` from inline `style` attributes specifically,
but this hasn't been confirmed by reading Streamlit's source, only observed
empirically from the rendered DOM.

**Why this matters:** `!important` was used **extensively** throughout this
session's design-system work (`plain_text`, nav-card CSS, sidebar CSS, etc.)
— but critically, almost all of that usage was inside real `<style>` blocks
(via `st.markdown("<style>...</style>", unsafe_allow_html=True)`), which is a
**different mechanism** than a bare `style=""` attribute on a single element
— `<style>` block content is not an inline attribute and does not appear to
be affected the same way (those `!important` usages, e.g. in `styles.py`'s
`GLOBAL_CSS` and the various `div[class*="st-key-..."]` rules, were
confirmed working correctly all session via other verification). **The bug
is specifically about `!important` written inside a `style="..."` HTML
attribute on an element**, not inside a `<style>...</style>` CSS block.

**How to apply:** Going forward, avoid `!important` inside inline
`style=""` attributes on individual elements — an author-controlled inline
style already has the highest specificity and doesn't need `!important` to
win against page CSS in the first place, so dropping it is usually free. If
a future style value silently "isn't applying" and it's set via inline
`style=""` with `!important`, check this first — try removing the
`!important` and re-measuring via a Playwright computed-style check (see
[[project_page_status]] for the pattern) before chasing other theories.




> [!WARNING]
> TD0015. Status: OPEN ; Priority: Medium/High

## NOT FIXED — HDBSCAN cluster 14/15 naming swap (vialidad_de_la_barranca / interlomas_magnocentro) never actually corrected

Confirmed 2026-07-15 while refactoring `research_core/0407_Clustering_Paper_Streamlit.ipynb` (the
research_core refactor sprint, see [[project_nb_refactor_sprint]]): this notebook's own history
contains a markdown note (originally right after the first HDBSCAN naming pass) flagging that
"san jeronimo vs pedregal" and "magnocentro vs barranca" were swapped. A later cell ("final naming
commit") did fix the san_jeronimo/pedregal swap — but checking both naming dictionaries side by
side, cluster ID 14 maps to `vialidad_de_la_barranca` and cluster ID 15 maps to
`interlomas_magnocentro` in **both** the buggy first pass and the supposedly-fixed later pass.
The barranca/magnocentro half of the originally-flagged bug was never actually corrected, despite
the note implying both would be fixed together. User confirmed this same swap is still visibly
wrong on the live Streamlit map (`observatory/main.py`'s Kepler/zone map), meaning it propagated
downstream and is currently shipping incorrect zone labels for these two clusters.

**Why:** the notebook's own bug-tracking note created an expectation that both halves of the swap
were resolved together; only one half was. This is a real labeling defect visible to end users on
the live app, not just an internal notebook inconsistency.
**How to apply:** in `research_core/0407_Clustering_Paper_Streamlit.ipynb`, swap clusters 14 and
15's names back (`vialidad_de_la_barranca` <-> `interlomas_magnocentro`) in whichever naming
dictionary is canonical (check both the "final naming" cell and the "canonical + Kepler dummy ID"
cell, keep them consistent with each other), re-derive any exported CSV/GeoJSON that embeds these
names, and then propagate the corrected names downstream into whatever `observatory/main.py` (or
its data-loading sibling) reads to render the map — confirm the fix by visually checking the two
zones on the live map afterward. Explicitly out of scope for the current research_core refactor
sprint itself (per the user: don't let this derail the sprint) — track and fix separately.

**Also evaluate while fixing this:** whether to apply the Pienza visual canon (`PIENZA_TEAL`/
`PIENZA_PURPLE`) to this notebook's Folium audit markers (currently plain `'blue'`/`'red'`) and the
`background_gradient(cmap='Greens')` styled table (could become a teal-based cmap, same pattern as
0305/0606's `sns.light_palette(PIENZA_TEAL, as_cmap=True)`). Not applied during the refactor sprint
pass itself — the notebook's wide 44-category qualitative palettes (`Vivid`/`Alphabet`) don't fit
the 2-color brand palette and were deliberately left alone, but the binary/sequential color spots
above are a separate, smaller judgment call worth revisiting whenever this notebook is touched again.




> [!WARNING]
> TD0016. Status: RESOLVED ; Priority: NA 

##  — rename VEN to CV (Continuation Value) in observatory/pages/0005_The_Cost_of_Patience.py

Confirmed 2026-07-13 while refactoring `research_core/0307_EDA_Optimal_Stopping_Playbook.ipynb`
(the research_core refactor sprint, see [[project_nb_refactor_sprint]]): "VEN" is a deprecated
name. `0005_The_Cost_of_Patience.py` already display-labels the concept correctly as
"Continuation Value (CV)" (e.g. `"CV(τ) — Continuation Value by Regime & Search Window"`)
but internally still uses `ven`/`VEN` as the actual variable/column name throughout
`0005_The_Cost_of_Patience.py` and `_0005_data.py` (e.g. `ven = ev_wait - eph_base_immediate`,
`df_res['VEN']`, `ven_matrix`). The notebook's variables were renamed to `cv`/`CV`/`cv_matrix`
during the refactor sprint to match the canonical display name — the live Streamlit page is now
the one that's out of sync with its own displayed terminology.

**Why:** "VEN" has no meaning on its own to a reader of the code (it's a legacy internal
abbreviation), while "CV"/"Continuation Value" is both the correct optimal-stopping-theory term
and what the page already shows the user. Code and UI should use the same vocabulary.
**How to apply:** Rename `ven`/`VEN` variables, DataFrame columns, and any other internal
references in `observatory/pages/0005_The_Cost_of_Patience.py` and
`observatory/pages/_0005_data.py` to `cv`/`CV` (e.g. `ven_matrix` -> `cv_matrix`,
`df_res['VEN']` -> `df_res['CV']`). This is a page-level rename, separate from and not part of
the `research_core` refactor sprint — do not action without the user's go-ahead, since it
touches live production Observatory code.




> [!WARNING]
> TD0017. Status: RESOLVED ; Priority: NA  (DECIDED AGAINST)

## Unificar service accounts (observatory vs resto del repo)

Hay dos service-account JSON distintos haciendo lo mismo (auth a BigQuery/GCP):
uno usado por `observatory/` (via `GOOGLE_APPLICATION_CREDENTIALS` /
`.streamlit/service-account.json`, ver [[project_bigquery]]) y otro usado por
el resto del repo (notebooks en `Phase_6_Generative_Moonshots/`, scripts de
`data/`, etc). Deberia unificarse a una sola service account para todo el repo.

**Why:** Redundancia sin justificacion — mismo proposito (autenticar contra
el mismo proyecto/dataset BigQuery), doble superficie de credenciales que
mantener y rotar.

**How to apply:** Antes de tocar auth en cualquier notebook o pagina nueva,
verificar cual de las dos service accounts sigue usandose y consolidar a esa.
No ejecutar la consolidacion sin permiso explicito del usuario (toca
credenciales). Revisar tambien si `GOOGLE_APPLICATION_CREDENTIALS` apunta a
rutas distintas entre notebooks y `observatory/` antes de asumir cual matar.





> [!WARNING]
> TD0018. Status: RESOLVED ; Priority: Leave her for traceability, if anything similar happens again
## RESOLVED — nav-card `:has()` selector unreliability (root cause found + fixed, 2026-07-07)

Previously logged here as an unsolved mystery: nav-card height, background, hover
border, and the "Explore Module" button background were all inconsistently
applying (e.g. button grey background only showing on the currently-hovered
card). Root cause confirmed: `div[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-card)`
— relying on a hidden `<span class="nav-card">` marker plus `:has()` to select
the ancestor container — does not reliably apply in the installed Streamlit
version (1.58.0). Plain descendant selectors (no `:has()`) worked fine
throughout, isolating `:has()` itself as the broken mechanism.

**Fix applied:** switched to `st.container(border=True, key=f"nav-card-{i}")`,
which makes Streamlit attach a stable `st-key-nav-card-{i}` class directly to
the container's DOM wrapper. All nav-card CSS in `main.py` now targets
`div[class*="st-key-nav-card-"]` instead of the old `:has()` selector. The
hidden marker span and its `.nav-card { display: none; }` rule were removed
(no longer needed). Verified visually via headless browser screenshot that
cards render correctly (rounded corners, consistent height, subtle
"Explore Module" button).

**Why this matters going forward:** `st.container(key=...)` (Streamlit >= ~1.32)
is the reliable way to target a specific container's wrapper via CSS in this
codebase — prefer it over `:has()` + hidden-marker-span tricks for any future
custom-styled container, on this page or others.
**How to apply:** If a future container needs custom CSS on its own wrapper
(not just its children), use `st.container(key="some-name")` and target
`div[class*="st-key-some-name"]` — do not reintroduce the `:has(.marker-span)`
pattern for this purpose.




> [!WARNING]
> TD0019. Status: RESOLVED ; Priority: NA 

## RESOLVED (repo-wide as of 2026-07-10) — vertical stepper connector line, same root cause as nav-card bug

`.step-row`/`.step-spine`/`.step-line`/`.step-connector` (the vertical numbered
stepper pattern, e.g. Bronze -> Silver -> Gold in 0003_Feature_Store.py) assumed
the opening `<div class='step-row'>` from one `st.markdown()` call stayed open
around later `st.pills()` and table-markdown calls, with `.step-line` using
`flex:1` to stretch and fill the visual height. **False assumption** — same bug
class as the nav-card `:has()` issue: Streamlit renders each `st.markdown()`/
`st.pills()` as independent sibling DOM nodes, not nested inside an unclosed tag
from a prior call. The line only ever covered the "why" text's height, leaving
the rest of the card with no line, and the separate `.step-connector` arrow
piece didn't reliably meet up with it (a visible gap, sometimes an overlap
depending on other margin tweaks tried first).

**Fix applied (0003 only so far):** wrap the entire step's content (circle,
label, why-text, pills, table) in `st.container(key=f"step-{radio_key}")`,
giving it one real nested DOM node with a stable `st-key-step-*` class. The
vertical line is now a `::before` pseudo-element on `div[class*="st-key-step-"]`
that grows with the container's actual rendered height automatically (no flex
assumptions), with `top`/`bottom` offsets tuned to bridge Streamlit's ~16px
default gap between sibling blocks. `_render_connector()` and the separate
`.step-connector`/`.step-conn-arrow` arrow piece were deleted entirely — no
longer needed.

**Other pages using the same OLD buggy pattern — RESOLVED (2026-07-10):**
User confirmed the stepper connector fix has now been ported to
`0001_Foundations.py`, `0002_Acquisition_Pipelines.py`,
`0004_Data_Census_(The_Basics).py`, `0007_Human_vs_AI_Behavioral_Cloning.py`,
and `0008_The_Quest_to_O1_NLP.py` as well (previously only `0003` had it).
All stepper instances repo-wide should now use the `st.container(key=...)` +
`::before` pattern described above rather than the old flex-based
`.step-line`/`.step-connector` mechanism.

**Why:** Third confirmed instance of "assumed nested/open HTML across separate
Streamlit calls" causing a real visual bug (h1 auto-processing swallowing
inline styles, nav-card `:has()`, now this) — worth recognizing the pattern
immediately next time rather than re-diagnosing from scratch.
**How to apply:** When touching the stepper on any of the pages listed above,
check whether the same line/connector-gap bug is present, and if fixing it,
port the `st.container(key=...)` + `::before` approach from 0003 rather than
patching the old flex-based `.step-line`/`.step-connector` — that mechanism is
the root cause, not a case-by-case styling issue.



> [!WARNING]
> TD0020. Status: RESOLVED ; Priority: NA 
## NOT FIXED — 0002_Acquisition_Pipelines.py still uses old block-style PII masking

`assets_ignored/CLAUDE.md`'s anonymization protocol moved fare/earnings masking from a
solid `█` block to per-digit `#` masking (originally an 0003_Feature_Store.py-only
exception as of 2026-07-08, promoted to the general default as of 2026-07-15 after also
being applied to `research_core/0212_ETL_Big_Bang_pienzadb.ipynb`'s financial-lineage
audit cells). `0002_Acquisition_Pipelines.py`'s offer cards still use the older `█` block
style for fares — this was already flagged inline in `CLAUDE.md` since the address-masking
change on 2026-07-03 but never promoted to this tracked list until now.

**Why:** The solid `█` block reads as heavy-handed document redaction (the "Epstein files"
look) for both addresses and fares — the user's stated reason for switching to `#`
per-digit everywhere else. Leaving 0002 on the old style makes it visually inconsistent
with every other page/notebook now using `#`.
**How to apply:** Update `0002_Acquisition_Pipelines.py`'s `_obf_fare` (and any other
`█`-based masking helper on that page) to per-digit `#` masking, matching the pattern in
`assets_ignored/CLAUDE.md`'s anonymization protocol section.


> [!WARNING]
> TD0021. Status: Resolved ; Priority: NA
## RESOLVED (2026-07-18) — "Exilio" dehumanizing wording in Pienza_Papers.pdf and Observatory pages

Found while surveying `0608_Bridge_to_Markov_Network_Graph.ipynb` (2026-07-15): that notebook's
language for out-of-geofence/unassigned zones ("el Exilio", "el monstruo", "Gran Exorcismo",
"zonas foraneas", "agujero negro") read as dehumanizing/classist when describing real geographic
areas outside the wealthy zones Pienza models (user's own words: "que horror es clasismo de la
IA" — flagged half-jokingly but seriously). The notebook itself was fixed as part of the
research_core sober-tone pass.

**Observatory pages, traced 2026-07-18:** the "0602_cGAN_Engine.py"/"0603_Network_Graph.py"
page numbers in the original note were stale — those pages are now archived as
`observatory/archive/pending_GM/9001_cGAN_Engine.py` and `9002_Network_Graph.py` (both clean,
zero hits). The actual carrier is `observatory/archive/0701_Bridge_to_Markov.py` — one direct
"Exilio" hit (line 591) plus 4 more uses of "sovereign"/"sovereignty" (lines 79, 83, 126, 603),
same classist-framing pattern as the word already blacklisted in the `0602` notebook. **Decision:
not fixing now** — this page is archived/deprecated, not live; if it's ever revived, fix the
wording then, not preemptively.

**Pienza_Papers.pdf:** never checked, in this pass or before — deliberately left open, user is
already aware and will clean it up separately when it comes up, not tracked as blocking debt.





> [!WARNING]
> TD0022. Status: RESOLVED ; Priority: NA

## NOT FIXED — README.md drift after research_core refactor sprint

Moved here from `nb_refactor_guide.md` (2026-07-17) — repo-wide README concern, not scoped to the
`research_core/` sprint itself, so it doesn't belong in that sprint's own guide file anymore now
that the sprint (all 16/16 notebooks) is done.

- Review the per-notebook one-line descriptions in the Core Notebooks tree (`README.md`, lines
  ~90-106) — update any that went stale once notebook internals/naming changed during the sprint.
- Tone-check in-joke comments in that same tree against the sober-naming standard applied inside
  the notebooks during the sprint (e.g. `0606_cGAN_downscaling.ipynb # Apache Spark, obviously`
  is still present as of 2026-07-17) — decide whether it stays (README is a different register
  than the notebooks themselves) or gets toned down for consistency.

**Why:** the research_core sprint renamed variables, retitled sections, and changed tone
throughout all 16 notebooks — the README's descriptions of them were never revisited afterward.
**How to apply:** read `README.md`'s Core Notebooks tree section against the current state of
each notebook (post-sprint), update stale one-liners, and make an explicit tone call on the
in-joke comments rather than leaving them by default.



> [!WARNING]
> TD0023. Status: Abandoned ; Priority: NA (se refactorizó de todos modos, pero es perdida de tiempo hacerlo 1:1 a streamlit, I have to ship now...)

## NOT FIXED — 0509 preprocessing pipeline should mirror Streamlit exactly

Flagged 2026-07-17. `research_core/0509_WINNER_XGB_cascade_postablation.ipynb`'s preprocessing
pipeline needs to be refactored so it mirrors exactly what's on Streamlit. No further detail
recorded — user will know what to do when picking this up.

> [!WARNING]
> TD0024. Status: RESOLVED ; Priority: NA

## NOT FIXED — build_sidebar() copy-pasted across 15 Observatory files

Confirmed 2026-07-17 while triaging the now-deleted `refactor_sprint.md`: `build_sidebar()` is
independently defined in 9 active pages (`0001`-`0009`, minus whichever don't have it) plus 6
archive pages under `observatory/archive/`, instead of living in one shared module. Adding or
removing a page from the sidebar currently means editing every file that defines it.

**Why:** single source of truth for the canonical sidebar (see `assets_ignored/CLAUDE.md`'s
"Canonical sidebar" section for the exact link list) would mean a page addition/removal is a
one-file change instead of a 15-file grep-and-edit.
**How to apply:** extract `build_sidebar()` into `observatory/components/sidebar.py` (sibling to
the existing `components/styles.py`), have every page do
`from components.sidebar import build_sidebar` instead of defining it locally, and delete the
local definitions. Verify the archive pages still render correctly after the change (they're not
in the active nav but still get visited directly).


> [!WARNING]
> TD0025. Status: Abandoned ; Priority: NA (no need for it to be perfect)

## NOT FIXED — #21918c (teal) hardcoded outside config.py in 12 Observatory pages

Confirmed 2026-07-17: `observatory/config.py` already defines `ACCENT = "#21918c"` (and
`ACCENT_DARK`), but 12 page files still hardcode the literal `#21918c` directly in inline
`<style>` blocks (e.g. `color: #21918c !important;` for active-tab text) instead of referencing
`ACCENT` from `config.py`. This is drift from `config.py`'s own purpose as the single source of
truth for the brand color.
**Why:** if the teal accent ever needs to change, `config.py`'s `ACCENT` alone won't be enough —
someone would also have to grep and update 12 separate hardcoded occurrences.
**How to apply:** in each of the 12 pages, import `ACCENT` from `observatory/config.py` and
f-string it into the inline `<style>` blocks instead of the literal hex value. Re-grep
`grep -rn "#21918c" observatory/pages/*.py` afterward to confirm only page-specific,
non-brand-color hex values remain (if any).







========
Notes to self:
> [!WARNING]
MAPBOX token -> ocultar ----> DONE
Analizar si agregar 0403 Clustering a NBViewer (link del readme) -> DONE
Acquistion.py loads painfully slow again; same for cost of patience -> al parecer ya no / verificar -> DONE
Did You Know Collapsible que resalte mas (teal o amarillo) -> DONE
Ultima pasada a las pages -> DONE
> polish STORY.md
> GEMINI CLI
CRON / Github Actions Failling everynow and then... ---> DONE
fondo transparenete para las png's del readme -> DONE

> Update claude_docs + Claude.MD
Update LinkedIn links a mi repo -> nuevo USERNAME: bernardowise -> superseded 

========
NUEVOS;

footers pending yellow banners... quitar todos.  -> DONE
> polish STORY.md
> GEMINI CLI
Update READMEmd para incluir containerization/docker -> DONE
cron-job para new app -> DONE (cron-job.org job pinging the Cloud Run *.run.app URL every 10 min, 2026-07-20)
buy domain for new app -> DONE (projectpienza.com on Namecheap, Cloud Run domain mappings live for apex + www, 2026-07-20)
test speed in new app
deprecate streamlit app (de readme, de linkedin, etc) -> DONE 
> CREATE PRIVATE REPO FOR ALL GITIGNORED FILES (if something is large like data files csvs, db, move em to a new bucket in GCS)



One nitpick: "read-only record" / "not designed to be forked" language is correct and good boundary-setting, but make sure it doesn't read as "don't bother looking at my code" to someone evaluating you for a coding-heavy role — you might want a one-line addendum like "happy to walk through any part of the codebase live" to signal openness despite the read-only framing. -> DONE










===========
Low / deferred by design:
TD0001, TD0010 (idea, no urgency)
==========







===========
OUT OF SCOPE OF CLAUDE
TD0021 — "Exilio" wording in PDF
TD0011 — Session MQI mean→median backprop to paper/notebooks
voy a cambiar el pienza_papers scientific a solo pienza papers, y borrar el executive. -> DONE
=============




