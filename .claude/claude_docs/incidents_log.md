# Incidents Log

Things that have already gone wrong once, with root cause and resolution, so they are not repeated or re-diagnosed from scratch. New entries go at the top.

---

## 2026-08-02 — RAG #2 (The Pienza Papers) retrieval misses a relevant passage on the first phrasing, finds it on a rephrase

Observed live (Manual Retrieval, C2 — The Pienza Papers): asking "How the the project managed the bias variance tradeoff?" retrieved passages about hierarchical classification and stratified K-fold, correctly declined to claim they were an explicit bias-variance strategy, and correctly suggested the answer might be in an unretrieved section. The actual bias-variance passage (the lightweight 6-feature model, 23.8% -> 10.6% generalization gap, EPH validation) exists in the corpus but wasn't in the top-k for that phrasing. A same-thread follow-up, "nothing on a lightweight model?", retrieved it correctly and answered in full with citations.

**Root cause not fixed, just diagnosed**: top-k=4 (`TOP_K` in `_0010_data.py`) plain cosine similarity over markdown/LaTeX-heading chunks means a query phrased at the wrong abstraction level ("bias variance tradeoff" as a general ML concept) can miss a chunk that discusses the same idea under different concrete terms ("lightweight model", "generalization gap") without those exact words. This is not a code bug — the model behaved correctly both times (honest "not found" first, grounded answer second) — it's a retrieval-recall gap inherent to single-vector top-k without query expansion/rewriting or hybrid keyword search.

**Not fixed now, deliberately** — logged here and cross-referenced in `tech_debt.md` under the RAG workflow section. Candidates already on record that would help: hybrid search (BM25 + vector, already flagged as a cross-corpus future item) and/or a higher `TOP_K` for corpora with fewer, denser chunks like The Pienza Papers specifically.

---

## 2026-07-09 — Recurring Streamlit rerun/fragment bug patterns found during the latency pass

Four distinct bug patterns surfaced while doing a page-by-page latency audit of the Observatory. Apply these checks to any page touched going forward, not just the ones already fixed.

1. **Per-interaction BQ queries.** A variable (e.g. `curr_filename`, `sid`) embedded directly in the SQL string means every distinct value is a new `@st.cache_data` key = a new live query. Fix: batch into one query with `WHERE x IN (...)`, filter in memory. Measured on this project: BQ cost is ~2-2.5s fixed overhead per query call, not per row — batching 500 rows costs the same as 50.
2. **`st.rerun()` reruns the whole page even inside `@st.fragment`** unless `scope="fragment"` is passed — but `scope="fragment"` raises `StreamlitAPIException` if that execution is still part of a full-app rerun (first load, or a branch triggered on initial mount). Fix, a small helper:
   ```python
   def _fragment_rerun():
       try:
           st.rerun(scope="fragment")
       except StreamlitAPIException:
           st.rerun()
   ```
3. **`components.html()` with JS that caches DOM refs via one-time `querySelectorAll`** (the "ci-stepper"/"phase-card" pattern replacing native Streamlit tabs) — if that script lives outside a `@st.fragment` but the tabs it references live inside, a fragment rerun recreates those DOM nodes and the JS refs go stale/orphaned. Real bug hit on page 0005 ("Phase 2/3/4 not clickable without reload"). Fix: move the `components.html()` call inside the fragment, right after the tabs are created, so it recaptures fresh refs every rerun.
4. **Don't assume `with tabX:` nesting from proximity in the file.** Streamlit only requires the `tabX` variable be in scope, not that the code be textually nested under it. This broke page 0006: wrapping `with top_tab1:` in a `def _render():` only captured the indented content — 5 sub-tabs existed as loose `with tab1:` blocks further down at module level, referencing variables that now only existed in the function's local scope, causing a `NameError`. The fragment-isolation attempt was reverted via `git checkout` and not retried. Before wrapping any tab region in a fragment, verify with a script that counts real column-0 Python statements in that tab's range — don't eyeball it, HTML inside triple-quoted f-strings fools the eye.

**Testing tool for this class of bug without a browser:** `streamlit.testing.v1.AppTest` (`AppTest.from_file("main.py")` → `at.switch_page(...)` → `.run()` → click buttons via `at.button` → assert `at.exception` is empty and `at.session_state[...]` updates) catches the exact `NameError`/scope-mismatch class of bug from the pattern-4 incident without needing a real browser.

---

## 2026-07-09 — Three cross-cutting latency findings, fixed across all pages

Found during a full call-site audit (every BQ query / GCS fetch / external HTML load across `main.py` + the active Observatory pages) done as prep for the page-by-page latency pass.

1. **PDF sidebar download ran on all 10 pages, eagerly.** Fixed everywhere with a two-step lazy pattern: a button triggers the `fetch_bytes_from_gcs` call only on click, then renders a second `st.download_button` to actually save. No fetch happens until the user clicks once.
2. **A page loaded the same parquet 3 times** — once per tab via 3 differently-named `@st.cache_data` functions, because Streamlit renders all tab panels' content every rerun regardless of which tab is visually active, so this was 3 real fetch+parse calls per rerun, not just 3 cache entries. Fixed: single shared loader function defined once above the `st.tabs(...)` call; per-tab views now just slice the shared dataframe instead of re-fetching.
3. **A query had `ttl=300`** set for a project where the underlying data never changes live — pointless. Fixed: removed, now matches the no-TTL pattern used everywhere else.

**Lesson:** map every network-touching call site before starting a latency pass, so effort goes to real hotspots instead of guessing — this audit is what made all 3 findings above visible in the first place, none were found by intuition.

---

## 2026-07-07 — main.py hero title bold exception: root cause never confirmed, abandoned

**What happened:** Tried to make main.py's hero title ("Project Pienza") a bold exception to the canonical `h1` (weight 300). It kept rendering less bold than intended despite identical declared CSS to Foundations' title. Several theories were tried without isolating which, if any, was the actual cause: font-weight value clamping, Inter font-file loading, quote-escaping in the inline style string, Streamlit auto-processing literal `<h1>` tags (confirmed real via DevTools — it does swallow inline styles on `<h1>` specifically), moving the page's CSS from the shared `components/styles.py` import to a page-local inline copy and back, and `runOnSave` being off in `.streamlit/config.toml`.

**Do not over-claim the fix:** `runOnSave` was a real gap and got fixed, but it was never verified to resolve the boldness mismatch specifically — treat the true root cause as unresolved, not solved, even though a real fix happened alongside the investigation.

**End state:** Reverted to plain `st.markdown("# Project Pienza")` — no custom `<div>`, no inline overrides, no exception. CSS moved back to the shared `components/styles.py` import (the page-local copy didn't fix anything either). Uses the exact same mechanism as every other page's title now. There is currently no hero-title exception.

**Lesson:** Several real and merely-plausible causes got tangled together and were never isolated one at a time, burning time without a confirmed fix. If a bold hero-title exception is wanted again, test *one* variable at a time and verify each with the browser DevTools "Computed" panel (not eyeballing) before moving to the next theory. Confirm `runOnSave` is on and do a real restart before assuming any CSS change "isn't working."

---

## 2026-07-19 — Devcontainer rebuild silently wiped Claude's persistent memory

**What happened:** A previous session added `docker-in-docker` + `node` devcontainer features (to enable local `docker build`/`docker run` testing of the Cloud Run image) without flagging that this forces a container rebuild. The rebuild wiped `/home/vscode/.claude/projects/-workspaces-pienza/memory/` because that directory lives outside the repo and isn't git-tracked. No project work was lost — only chat/memory context. Recovered by copying the repo-tracked mirror (now `.claude/claude_docs/`, formerly `assets_ignored/claude_docs/`) back over.

**Separate issue, same incident — rebuild also got stuck mid-way:** the `docker-in-docker`/`node` features run their own `apt-get update` before `postCreateCommand` gets a chance to remove a broken yarn apt repo, so the feature install failed on the stale yarn source. Fixed by adding `.devcontainer/Dockerfile` (`FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` + `RUN rm -f /etc/apt/sources.list.d/yarn.list`) and pointing `devcontainer.json`'s `build.dockerfile` at it, so the yarn repo is removed in the base image layer before any feature's `apt-get` runs. Docker confirmed installed afterward (29.6.2).

**Do not confuse:** `.devcontainer/Dockerfile` (fixes the devcontainer's own build) vs. `observatory/Dockerfile` (the Cloud Run app image) — unrelated problems, both exist in the repo.

**Lesson / how to apply going forward:** Before recommending any change to `.devcontainer/devcontainer.json` or `.devcontainer/Dockerfile` (new features, base image swap, `build` block), explicitly warn that applying it triggers a container rebuild, and that rebuild wipes Claude's persistent memory (the repo-tracked mirror survives, actual repo files survive — only chat/memory context resets). Let the user decide with that tradeoff stated up front, don't apply silently.
