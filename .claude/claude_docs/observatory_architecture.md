# Observatory Architecture — Standing Reference

Persistent, human-readable companion doc for `observatory/`'s shared/infra layer (`.streamlit/`, `components/`, `scripts/`, `utils/`, `config.py`). Not part of the memory-sync system (no frontmatter, not mirrored to `~/.claude/projects/.../memory/`) — same standalone treatment as `nb_refactor_guide.md` and `STAR_stories.md`. Reflects the current state only, not a session log — if a future session touches this layer, read this file first so it doesn't re-break or re-duplicate what's already been fixed.

## Verdict on the directory skeleton

**Spotless — do not reorganize.** `.streamlit/`, `components/`, `scripts/`, `utils/`, and `config.py`'s top-level placement are all correctly scoped and named. `scripts/gcs_deploy.py` in particular is exactly right: single-purpose, correctly named, not imported at runtime.

## `components/sidebar.py` — the one canonical sidebar

`build_sidebar()` + `load_favicon_b64()` live in exactly one place, `observatory/components/sidebar.py`. Every page + `main.py` (10 files total) imports `build_sidebar` from there — no per-page copies, no per-page `load_favicon_b64()`. Don't reintroduce a local copy in any page.

## `config.py` — fully wired, no orphaned constants

- `FAVICON` — a `PIL.Image` object, not a path string. Deliberate: passing a string page_icon has had unreliable classification behavior on Streamlit Community Cloud specifically.
- `ACCENT` — the single source of truth for the app's teal (`#21918c`). Consumed by `components/styles.py`'s `GLOBAL_CSS` (see pattern below) instead of that file hardcoding the literal 35 times.
- `GITHUB_URL` — `https://github.com/WiseExMachina/pienza`, consumed by `sidebar.py`.
- `AUTHOR` — `"Bernardo Lozano Wise"`, consumed by `sidebar.py`.
- `PDF_URL` — the real, working, hosted PDF link (see PDF section below), consumed by both `sidebar.py`'s "Download PDF" link and `main.py`'s "LLM Knowledge Base" ingestion card.
- `TITLE_PREFIX` + `build_page_title(name: str) -> str` — the browser-tab title convention (see below).

No dead constants remain in this file. If you find one, it's new debt, not something carried from before — flag it fresh.

## Browser-tab title convention: `"Pienza · Observatory · <page name>"`

Every page (`main.py` = `"Home"`, `0001` = `"Foundations"`, etc.) calls `config.build_page_title(name)` inside its `st.set_page_config(...)` — never hand-write a `page_title=` string.

**Scope note**: "page title" means *only* the browser tab `<title>`. It does NOT touch the sidebar nav label (`st.page_link(..., label=...)` inside `sidebar.py`) or the on-page `<h1>` heading (each page's own body content). Keep these three concepts separate.

`main.py` calls `st.set_page_config(layout="wide", page_title=build_page_title("Home"), page_icon=FAVICON)` as its very first Streamlit call, before `build_sidebar()` — required, since without it the tab falls back to an unbranded title.

## The PDF: hosting, links, and file inventory — DEPRECATED SECTION, DO NOT TRUST

**Everything below this line is stale as of 2026-07-18.** The Pienza Papers was pulled off
`main` entirely and deprecated (moved to a `paper-dev` branch, not merged back — see
[[paper_migration]] for the full story and revival steps). `PDF_URL` was deleted from
`config.py`, the "Download PDF" link was removed from `sidebar.py`, and the "LLM Knowledge
Base" ingestion card was removed from `main.py` (replaced with a short disclaimer). None
of the file paths, GitHub Pages URL, or consumer references below exist anymore. Kept here
only as historical record of the pre-deprecation setup — do not act on any instruction in
this subsection, and do not re-add `PDF_URL` without first reading [[paper_migration]]'s
revival steps.

<details>
<summary>Original content (pre-2026-07-18), for historical reference only</summary>

The PDF's actual, working, hosted location is **GitHub Pages**, published from the `main` branch root: `https://wiseexmachina.github.io/pienza/The_Pienza_Papers/Pienza_Papers_Scientific.pdf` (`HTTP 200`, `content-type: application/pdf`). This is the *only* copy that matters — `observatory/assets/Pienza_Papers.pdf` and `observatory/static/Pienza_Papers.pdf` (both stray duplicates) have been deleted; `config.py`'s `PDF_PATH` constant (a filesystem path pointing at the former) was deleted alongside them since it had zero consumers.

**How to trace a GitHub Pages URL for this repo**: Pages is set to `Deploy from a branch → main → /(root)`, so the published URL always mirrors the exact repo file path, appended after `https://wiseexmachina.github.io/pienza/`. The bare `.../pienza/` root 404s because there's no `index.html` at the repo root — expected, not a bug.

Both PDF links (`sidebar.py`'s "Download PDF", `main.py`'s "LLM Knowledge Base" ingestion card) use `config.PDF_URL` and are confirmed to trigger a genuine download (not just navigation) via the `download` HTML attribute — this does work cross-origin against GitHub Pages, since Pages doesn't force inline `Content-Disposition` on `.pdf` files.

`.streamlit/config.toml`'s `enableStaticServing` is `false` — there's no `static/` folder left to serve.

**Deferred, not implemented**: a "View PDF" option in addition to "Download PDF" on both buttons.

**3 archived pages still reference the old dead path** (`observatory/archive/pending_GM/9001_cGAN_Engine.py`, `9002_Network_Graph.py`, `9003_Markov_Fleet_Sim_Dashboard.py`, all `href='app/static/Pienza_Papers.pdf'`). Deliberately not fixed — don't fix archived/non-live pages preemptively, only if/when they're ever revived.

</details>

## `utils/gcp_auth.py`, `gcp_client.py`, `bq_client.py` — auth extracted, clients de-scoped

`utils/gcp_auth.py` holds the one shared piece both clients need: the `os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", ...)` fallback and a single public `get_gcp_credentials()` (returns `service_account.Credentials` from `st.secrets` when deployed, else `None` so the google-cloud clients fall back to the env var).

- `utils/gcp_client.py` — scoped to exactly what its name promises: `_storage_client()`, `fetch_parquet_from_gcp()`, `fetch_bytes_from_gcs()`, `download_from_gcs()`. No model code, no page-specific loaders.
- `utils/bq_client.py` — `_bigquery_client()`, `fetch_data_from_bq()`. Same shape, same pattern.
- Both call `get_gcp_credentials()` from `gcp_auth.py` rather than each reimplementing the check. Public function names are unchanged from before this consolidation — no call-site changes needed anywhere.

**Why a separate `gcp_auth.py` instead of one client importing from the other**: `gcp_client.py` and `bq_client.py` are two distinct clients (`storage.Client` vs `bigquery.Client`), each with its own logic for what to do *with* credentials once resolved. The resolution step itself isn't "client" logic, it's auth logic, and was identical in both. Having `bq_client.py` import from a file named `gcp_client.py` would read backwards. A neutral third file avoids that inversion.

**miniBabel's model code lives in `pages/_0008_data.py`, not `gcp_client.py`.** `PositionalEncoding`, `ZoneClassifierTransformer` (the PyTorch architecture), and `load_babel_assets()` are used exclusively by `0008_The_Quest_to_O1_NLP.py`, so they live in that page's existing "Layer 1 extraction" data file alongside its other heavy loaders (`load_holdout_audit`, `load_zone_map_template`, `load_latency_map_template`) — not in a generic client file. `load_manifold_dimensions()`, which had zero live callers, was deleted outright rather than moved.

**Standing concern for any future touch of `0008` or `_0008_data.py`**: 0008 is already carefully optimized for load speed — `load_babel_assets()` is preloaded via a background thread on page load specifically for this. Any change here must preserve that exact threading/caching shape; verify live (real server, real page load) that the preload still fires correctly and nothing became synchronous/blocking by accident.

## Comment tone: sober English only, no Spanish/dramatic phrasing

All comments in live code (`main.py`, every `pages/*.py`, `_NNNN_data.py`, `utils/*.py`, `components/*.py`, `scripts/*.py`) are in plain English — no Spanish, no "OPUS-era" naming, no dramatic phrasing ("the beast," "quantum," etc. used non-technically). This matches the convention already applied across the notebooks refactor sprint.

**`archive/` is exempt** — do not proactively translate or clean up comments in archived/non-live pages. Fix only if a specific archived file is ever revived.

## The abandoned per-page `#21918c` → `ACCENT` pass (context, don't redo blindly)

A past effort tried replacing every hardcoded `#21918c` literal across all 8 non-0007 Observatory pages (tech-debt item TD0025) with `ACCENT` references. It was **fully implemented and verified live, then hard-reset by the user** (`git checkout -- observatory/`) — not because it was wrong, but because the effort-to-value ratio was bad: purely cosmetic (zero functional/visual difference), for real risk across 8 files of dense, differently-shaped inline HTML.

**This does not mean "leave `#21918c` hardcoded everywhere forever."** The `components/styles.py` fix (`GLOBAL_CSS` sourcing `ACCENT` via `.replace()`, see pattern below) is the same idea applied to the *one* central shared CSS file instead of 8 scattered pages — much higher leverage, much lower risk. If asked to do the full per-page sweep again, treat it as a **separate, explicit ask** — don't assume it's still wanted, and don't be surprised if the answer is "no, we decided against that already."

## Still open / flagged but not touched

1. **`utils/mem_debug.py` self-flags as temporary** ("safe to remove once the memory picture is clear") but is wired into every page's top-level imports (`log_mem(...)` calls). **Deliberately kept as-is**: the likely path forward is migrating off Streamlit Community Cloud to Google Cloud Run (Streamlit Cloud's ~700MB actual ceiling vs. its nominal 1GB is a recurring constraint), and `mem_debug.py` is the active diagnostic tool for that migration decision. Don't remove without that migration question being resolved first.
2. **"View PDF" (not just "Download PDF") option** — wanted eventually on both PDF buttons, not yet implemented.

## Two reusable technical patterns

### Safe way to inject a config constant into a big string containing literal CSS braces

`GLOBAL_CSS` and similar multi-line `<style>`-containing strings have real CSS syntax (`{ color: ...; }`) inside them. **Do not** blindly prefix such a string with `f` to interpolate a variable — Python will try to evaluate every literal `{...}` block as an expression and crash (or worse, silently produce wrong output) unless every brace is manually escaped as `{{`/`}}`. The safe pattern:

```python
GLOBAL_CSS = """
<style>
... literal #21918c hardcoded throughout ...
</style>
""".replace("#21918c", ACCENT)
```

`.replace()` runs on the fully-formed string *after* any f-string interpolation would have happened anyway, so it composes fine with f-strings too if a block is a mix. Only convert a block directly to an f-string (`f"""..."""`, using `{ACCENT}` inline) when you've confirmed there are zero literal `{`/`}` characters in it.

### Verify Observatory changes live, not just via `ast.parse()`

Static syntax checks catch typos, not behavior. Several claims that looked obviously true from reading the code turned out to be wrong when actually tested (e.g. an assumed-broken favicon on `main.py` that Streamlit was silently handling correctly via a multipage-app fallback; an assumed cross-origin `download`-attribute limitation that Chromium actually handles fine for GitHub Pages). The standard: launch the actual Streamlit server, drive it (page loads, click-throughs, `expect_download()` for file links), and only then report something as fixed or broken.

**Critical operational rule**: never run `pkill -f "streamlit run main.py"` or any broad pattern-match kill — it matches *any* process with that command text regardless of who started it or which port, and has killed the user's own live tunneled server before. Always launch a test instance on an explicit, unlikely-to-collide port, capture its PID via `$!` immediately after backgrounding it, and kill *only* that exact PID when done (`kill $MY_PID`, with a `kill -9` fallback if it doesn't die within a couple seconds). Never assume you're the only Streamlit process running.
