# Project Pienza — Claude Context File (observatory/)

Loads additively on top of root `CLAUDE.md` whenever Claude works inside `observatory/`. Only observatory-specific content lives here — repo-wide conventions (BigQuery, GCS policy, anonymization, brand convention, commit rules) are in root `CLAUDE.md`, not duplicated here.

## How to run

```bash
cd /workspaces/pienza/observatory
streamlit run main.py
```

Public tunnel:
```bash
streamlit run main.py & ./cloudflared tunnel --url http://localhost:8501
```

## Before touching shared infrastructure

Before touching `observatory/config.py`, `components/`, `utils/`, or `.streamlit/`, read `.claude/claude_docs/observatory_architecture.md` in full — documents a prior architecture pass, what's deliberately left alone and why (e.g. a hardcoded-color sweep the user explicitly decided against), and two reusable technical patterns (safely injecting a config constant into a CSS-bearing string; verifying Streamlit changes live via Playwright).

## Design system

- **Font:** Inter · **Primary color:** `#21918c` (teal)
- **CSS classes from GLOBAL_CSS:** `.bento-card`/`.bento-grid`/`.bento-title`/`.bento-value`/`.bento-desc`, `.story-section`, `.story-pill`, `.phase-badge`, `.ingestion-panel`
- **Stepper UI:** `.step-row`, `.step-spine`, `.step-circle`, `.step-line`, `.step-body`
- **Column split for stepper indent:** `[1, 11]` · **Nav buttons:** `[3, 1, 1, 3]`, teal-outlined
- **Custom-styled containers:** use `st.container(border=True, key="some-name")` + target `div[class*="st-key-some-name"]` in CSS. Do not use `div[data-testid="stVerticalBlockBorderWrapper"]:has(.hidden-marker-span)` — confirmed unreliable in Streamlit 1.58.0 (silently failed to apply height/background/hover/button-color rules).
- **Callout block canon:** `border-radius:0 8px 8px 0` (square on the left where the border-left sits, rounded only on the right) — not full rounding, not square all around.
- **Header vertical rhythm:** the `# Page Title` H1 must sit at the same height across all pages. The deciding factor is the count of separate `st.markdown()` calls between `build_sidebar()` and the title — canon is exactly 2 (`GLOBAL_CSS` injection + one page-specific `<style>` block, real or an empty spacer). Count actual calls before adding/removing a spacer; don't add one blindly.

## Color notes

- `#f8fffe` / `#d0f0ed` — fine for pills/small accents, **avoid for text box / info card backgrounds** (use `#f5f5f5` / `#e5e5e5` instead).
- **Canonical callout/pill background:** `rgba(33,145,140,0.07)` — use everywhere a teal-tinted callout is needed.
- **BLACKLISTED:** `#f0faf9` (reads phosphorescent) and `#0e7490` (cyan, banned everywhere) — only `#21918c` teal is the accent color.

## Tooltip rules

- All tooltips bounded to 2 decimal places — `format=".2f"` on every `alt.Tooltip(...:Q)`, `:.2f` in HTML/f-strings.
- Known Altair 6.2.1 bug: `format=".2f"` silently ignored inside `alt.layer()` + `configure_*()`. Workaround: pre-format as a string column, use `:N` instead of `:Q`.

## Canonical sidebar

`build_sidebar()` lives in `observatory/components/sidebar.py` — single source of truth for the nav, called by every page and `main.py`. Current real order (verified against source, not memory):

Home → Foundations (0001) → Acquisition Pipelines (0002) → Feature Store (0003) → Data Census: The Basics (0004) → The Cost of Patience: Optimal Stopping (0005) → Payout Physics: Causal Inference (0006) → Human vs AI: Behavioral Cloning (0007) → The Quest to (O)1: NLP Transformer (0008) → Generative Moonshots: pienza_big (0009) → RAG Assistant (0010)

If this list and the actual `sidebar.py` ever disagree, `sidebar.py` wins — re-verify from source rather than trusting this doc, page order/labels have drifted before.

## Canonical hover footnote pattern

CSS lives in `components/styles.py` (`GLOBAL_CSS`), already injected. Never write custom tooltip CSS:

```html
<span class="fn-wrap"><span class="fn-mark">†</span><span class="fn-tooltip">Footnote text.</span></span>
```
Place immediately after the annotated word/phrase, no space before the `<span>`. For a below-mark variant near a page header, add the `fn-below` modifier — see `.claude/claude_docs/project_design_system.md` for the CSS override snippet.

## Feature store schema (0003_Feature_Store.py)

Three medallion layers as `{domain: [features]}` dicts: `bronze_schema` (F01-F37, 7 domains, raw OCR), `silver_schema` (S01-S31, 7 domains, stateful engineered features), `gold_schema` (G01-G09, 2 domains, spatial + volatility). Categorical features carry a `categories` list; others carry `desc`. `_bento_card()`/`_render_table()` check `categories` first and render chips if present.

## Key conventions (Streamlit-specific)

- `@st.cache_data` on all BQ queries — one network call per unique SQL string.
- `st.set_page_config(layout="wide")` on every page.
- Page numbering: sequential `0001`–`0010` (verified against `observatory/pages/`, 2026-08-01). If a new page is added, confirm the next real number from the directory rather than assuming a scheme — this project has renumbered before.
