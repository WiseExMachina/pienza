# Project Pienza — Claude Context File

## What is this?

A Streamlit Observatory (multi-page app) documenting **Project Pienza**: a full-stack AI research project building a generative digital twin of a human Uber driver in Mexico City. The dataset (~4,700 ride offers) was collected via two custom acquisition engines, then enriched through a medallion feature store, and consumed by multiple ML/generative models.

## How to run

```bash
cd /workspaces/pienza/observatory
streamlit run main.py
```

Public tunnel (when needed):
```bash
streamlit run main.py & ./cloudflared tunnel --url http://localhost:8501
```

## Repository layout

```
/workspaces/pienza/
  observatory/
    main.py                          # Home page + canonical sidebar
    pages/
      0001_Foundations.py            # Strategy, pivot narrative, timeline
      0002_Acquisition_Pipelines.py  # Engine 1 (GTS sim) + Engine 2 (Gemini OCR)
      0003_Feature_Store.py          # Bronze/Silver/Gold feature pipeline + simulator
      0201_SQL_Pipeline_&_Live_Sandbox.py
      0301_Optimal_Stopping_&_The_Efficient_Frontier.py
      0302_Causal_Inference.py
      0501_XGB_Coliseum.py
      0601_O1_NLP1.py
      0602_cGAN_Engine.py
      0603_Network_Graph.py
      0604_Markov_Fleet_Sim_Dashboard.py
      9000_*.py                      # Archive pages (legacy, not actively developed)
    components/
      styles.py                      # GLOBAL_CSS — Inter font, bento cards, story-section, phase-badge
    utils/
      bq_client.py                   # fetch_data_from_bq() — cached BigQuery helper
    assets/
      offer_cards/                   # Real OCR screenshot PNGs (IMG_XXXX.PNG)
      kepler_3D.html                 # Kepler.gl 3D manifold map
      Pienza_Papers.pdf
  assets/
    CLAUDE.md                        # This file
```

## Requirements files — two, different purposes

- **`/workspaces/pienza/requirements.txt`** (repo root) — the full dependency set, shared by local dev, Codespaces, Streamlit Community Cloud, and the `research_core`/`research_full` notebooks (torch, tensorflow-cpu, geopandas, hdbscan, transformers, pyspark, etc.). This is what's installed in this Codespace and what Streamlit Cloud builds from.
- **`observatory/requirements.txt`** — a trimmed subset containing only what `observatory/` (`pages/`, `main.py`, `components/`, `utils/`) actually imports at runtime, created 2026-07-19 for the Cloud Run migration. It exists **only** to keep the Docker image small/fast — it is not meant to be installed into the main dev environment (`pip install -r` doesn't scope by folder; running it here would just redundantly layer a subset on top of what's already installed from the root file, doing no harm but adding no value either). Only the Dockerfile should reference this file. If `observatory/`'s active-page imports change, re-audit and update this file — it's not auto-derived, it's a manually maintained snapshot.

## research_full refactor — standing alert

**If `research_full/` (or any notebook directory beyond the already-completed `research_core/`) is ever refactored for legibility/portfolio purposes, `assets_ignored/claude_docs/nb_refactor_guide.md` is the absolute governing guideline — read it in full before starting, and follow its decisions (mermaid diagram conventions, phase numbering, waypoint cells, tone/word blacklist, anonymization protocol, the shared-module decision, etc.) rather than improvising a new pattern.** That file documents the complete, closed-out `research_core/` sprint (16/16 notebooks done, all decisions and tech debt logged) — it is the precedent, not just historical notes. Do not start a fresh refactor pass on any other notebook directory without first reading it end to end.

**Naming history:** these directories were originally `research_archive`/`research_core`, briefly renamed to `notebooks_full`/`notebooks_core`, then renamed back to `research_full`/`research_core` (2026-07-18) — "notebooks_" was misleading since both directories hold non-`.ipynb` files (webapp scripts, AppsScript, etc.), not just notebooks. If any older doc/memory reference still says `notebooks_core`/`notebooks_full` or the original `research_archive`, it's stale — the current names are `research_core`/`research_full`.

## observatory/ shared infrastructure — standing reference

**Before touching `observatory/config.py`, `components/`, `utils/`, or `.streamlit/`, read `assets_ignored/claude_docs/observatory_architecture.md` in full.** It documents a 2026-07-18 architecture pass over this exact layer: what was found broken/duplicated/dead, what got fixed (sidebar dedup, `config.py` constants actually wired up, the real PDF host on GitHub Pages, the missing `main.py` page title), what was deliberately left alone and why (a per-page hardcoded-color sweep the user explicitly decided against — don't redo it without asking), what's still flagged-but-unfixed, and two reusable technical patterns (safely injecting a config constant into a CSS-bearing string; verifying Streamlit changes live via Playwright instead of trusting static reads). Skipping this file risks re-introducing exactly the duplication/contradiction this pass just removed.

## BigQuery

- **Project ID:** `645009831643`
- **Dataset:** `pienza_mini`
- **Full schema reference:** `assets/drivers-dilemma_pienza-mini_schema_2026-06-18.json` — INFORMATION_SCHEMA.COLUMNS export. **Always consult this file before writing any BQ query** to confirm exact table/column names.
- **Key tables:**
  - `raw_offers_ocr` — OCR output, keyed by `ocr_id`, has `image_filename`
  - `offers` — canonical offer record, `offer_id` PK; FK lookups via `offer_action_fk`, `reason_primary_fk`, `outcome_fk`, `product_category_fk`, etc.
  - `engineered_features` — all Silver stateful features, FK `offer_id_fk`
  - `silver_palette` — Gold geo + volatility features, FK `offer_id`
  - `trip_events` — has `realized_fare`, `upfront_fare` per event; FK `offer_id_fk`
- **Key views (pre-joined, prefer over raw joins):**
  - `v_ML_Supervised` — **canonical view**: offers + engineered_features + silver_palette. Has `consecutive_rejects` and all ML features. Does NOT have `str_*` — join dimension tables instead (see pattern below).
  - `v_offers_human` — human-readable: same as above but with `str_action`/`str_product`/`str_reason`/`str_driver_state` already resolved. Lacks `consecutive_rejects`. Use only if you specifically need a single-table str_* source.
  - `v_lifecycle_audit_accepted` — accepted offers with GTS event timestamps and earnings
  - `v_mission_dossier` — per-trip KPIs: `spread_percentage`, `eph_on_ride`, `eph_total_time`
- **Canonical join pattern for v_ML_Supervised + str_* fields:**
  ```sql
  FROM `645009831643.pienza_mini.v_ML_Supervised` ml
  LEFT JOIN `645009831643.pienza_mini.offer_action` oa       ON oa.offer_action_id = ml.offer_action_fk
  LEFT JOIN `645009831643.pienza_mini.product_category` pc   ON pc.product_category_id = ml.product_category_fk
  LEFT JOIN `645009831643.pienza_mini.reason_primary` rp     ON rp.reason_primary_id = ml.reason_primary_fk
  LEFT JOIN `645009831643.pienza_mini.driver_state_at_request` ds ON ds.driver_state_at_request_id = ml.driver_state_at_request_fk
  -- oa.offer_action_description → str_action ('accepted' / 'reject')
  -- pc.category_name            → str_product
  -- rp.reason_primary_description → str_reason
  -- ds.driver_state_at_request_description → str_driver_state
  ```
- **Auth:** `.streamlit/service-account.json` (set via `GOOGLE_APPLICATION_CREDENTIALS`)
- **Join pattern for OCR filename -> silver_palette:**
  ```sql
  FROM silver_palette sp
  JOIN offers o ON sp.offer_id = o.offer_id
  JOIN raw_offers_ocr r ON o.ocr_fk = r.ocr_id
  WHERE r.image_filename = '...'
  ```

## Design system

- **Font:** Inter (Google Fonts)
- **Primary color:** `#21918c` (teal)
- **CSS classes from GLOBAL_CSS:** `.bento-card`, `.story-section`, `.story-pill`, `.phase-badge`, `.ingestion-panel`
- **Stepper UI:** `.step-row`, `.step-spine`, `.step-circle`, `.step-line`, `.step-body` — used in Engine 2 (OCR) and Feature Store pipeline tab
- **Column split for stepper indent:** `[1, 11]`
- **Nav buttons:** `[3, 1, 1, 3]` column layout, teal-outlined

## Color notes

- `#f8fffe` / `#d0f0ed` (teal-tinted white) — fine for pills and small accents, **avoid for text box / info card backgrounds**. Use neutral `#f5f5f5` / `#e5e5e5` there instead.
- **Canonical callout / pill background:** `rgba(33,145,140,0.07)` — use this everywhere a teal-tinted background is needed for callout boxes, info cards, or pill containers.
- **BLACKLISTED:** `#f0faf9` — do not use. It reads as phosphorescent / overexposed. Replace with `rgba(33,145,140,0.07)` whenever encountered.

## Placeholder / pending callout pattern

When the user asks for a "shiny yellow" or "phospho yellow" placeholder, render a deliberately ugly bright-yellow callout — this is their signal for pending/unresolved items that must not be missed:

```html
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — [title]</span><br><br>
  [explanation]
</div>
```

Use `background:#ffff00` (pure Excel yellow) — never a soft tint. The point is that it's ugly enough to be impossible to miss.

## Tooltip rules

- **All tooltips everywhere must be bounded to 2 decimal places** — use `format=".2f"` on every `alt.Tooltip(...:Q)` field, and `:.2f` when formatting values in HTML/f-strings.
- Known Altair 6.2.1 limitation: `format=".2f"` on `alt.Tooltip` is silently ignored inside `alt.layer()` charts that also call `configure_*()`. Workaround to try: pre-format the value as a string column and use `:N` type instead of `:Q`.

## Canonical sidebar

Every page must call `build_sidebar()` which renders these links in order:

```python
st.page_link("main.py", label="Home")
st.page_link("pages/0001_Foundations.py", label="Foundations")
st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
st.page_link("pages/0201_SQL_Pipeline_&_Live_Sandbox.py", label="SQL Pipeline & Live Sandbox")
st.page_link("pages/0301_Optimal_Stopping_&_The_Efficient_Frontier.py", label="Optimal Stopping & The Efficient Frontier")
st.page_link("pages/0302_Causal_Inference.py", label="Causal Inference")
st.page_link("pages/0501_XGB_Coliseum.py", label="XGBoost Tournament: Human vs AI")
st.page_link("pages/0601_O1_NLP1.py", label="The Quest to (O)1: NLP")
st.page_link("pages/0602_cGAN_Engine.py", label="cGAN Keras Engine")
st.page_link("pages/0603_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
st.page_link("pages/0604_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
# Archive section below
```

## Brand convention

Never display the word "Uber" in product/category labels shown to the user. Strip it programmatically before rendering:
- `uberx` → `x`
- `envíos_uber` → `envíos`
- `uber_planet` → `planet`
- Pattern: `re.sub(r'(?i)uber_?', '', label).strip('_').strip()`

This applies to any chart label, table cell, or UI element derived from `category_name` or similar fields.

## Anonymization protocol

Any page that displays raw offer data from BigQuery (Session Playback, Acquisition Pipelines, etc.) **must** obfuscate:

| Field | Rule |
|-------|------|
| `upfront_fare` (and bonus amounts) | Replace every digit with `█` — e.g. `$154` → `$███` |
| `pickup_address` / `dropoff_address` | Mask street number only, digit-by-digit with `#`; preserve 5-digit zip codes — e.g. `Calle 5 de Mayo 123, CDMX 06600` → `Calle 5 de Mayo ###, CDMX 06600` |

EPH computed values (eph_direct, eph_operational, etc.) are derived ratios and do **not** need obfuscation.

**Note (as of 2026-07-03):** the address rule changed from a fixed-width block (`████`) to per-digit `#` masking — the block style read as heavy-handed document redaction ("Epstein files" look). Updated first in `0008_The_Quest_to_O1_NLP.py`; other pages (`0002_Acquisition_Pipelines.py`) still use the old `████` block and are due for the same swap in a future pass — don't assume they already match this canon.

**Update (2026-07-15):** the `#`-per-digit style for fare/earnings masking (originally an 0003-only exception, 2026-07-08) is now the general preference going forward — confirmed again when applied to `research_core/0212_ETL_Big_Bang_pienzadb.ipynb`'s financial-lineage audit cells. `█` still reads as heavy-handed ("Epstein files") for money the same way it did for addresses. New `_obf_fare` implementations (Observatory pages or notebooks) should default to `#` per digit; `0002_Acquisition_Pipelines.py`'s offer cards still use the old `█` block and are due for the same swap in a future pass — don't assume they already match this canon.

```python
import re

def _obf_fare(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    return re.sub(r'\d', '█', f"{float(v):.0f}")

def _obf_address(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    _mask_digits = lambda m: re.sub(r'\d', '#', m.group(0))
    return re.sub(r'\b(?!\d{5}\b)\d+[\w-]*\b', _mask_digits, str(v), count=1)
```

## Data obfuscation helpers (0002_Acquisition_Pipelines.py)

Sensitive fields are masked before display:

```python
_obf_fare(v)      # replaces digits with█
_obf_address(v)   # masks house number
_obf_hash(v)      # truncates to 12 chars + ...
_obf_latlon(v)    # masks decimal precision
```

## Feature store schema (0003_Feature_Store.py)

Three medallion layers, each as a Python dict `{domain: [features]}`:

- `bronze_schema` — F01-F37, 7 domains: raw OCR output
- `silver_schema` — S01-S31, 7 domains: stateful engineered features (state machine)
- `gold_schema`   — G01-G09, 2 domains: spatial index + volatility suite

Categorical features carry a `categories` list; others carry `desc`. The `_bento_card()` and `_render_table()` helpers check for `categories` first and render chips if present.

TBD categories (need user input): `reason_primary`, `heuristic_flag`, `driver_state_at_request`, `outcome`, `day_type/time_block`, `product_category` (partial: UberX, Comfort, Black, Envios, Flash).

## Canonical hover footnote pattern

CSS lives in `components/styles.py` (`GLOBAL_CSS`) — already injected on every page. Use this HTML, never custom tooltip CSS:

```html
<span class="fn-wrap">
  <span class="fn-mark">†</span>
  <span class="fn-tooltip">Your footnote text here.</span>
</span>
```

- `fn-wrap` — inline-block container, triggers hover
- `fn-mark` — the visible † superscript (teal, styled)
- `fn-tooltip` — dark card that appears on hover (visibility + opacity transition)

Place immediately after the word/phrase it annotates, no space before the `<span>`.

To drop the tooltip **below** the mark instead of above (e.g. when near the page header), add the `fn-below` modifier and inject the override once on the page:

```html
<style>
.fn-wrap.fn-below .fn-tooltip { bottom: auto; top: 130%; }
.fn-wrap.fn-below .fn-tooltip::after { top: auto; bottom: 100%; border-top-color: transparent; border-bottom-color: #21918c; }
</style>
<span class="fn-wrap fn-below"><span class="fn-mark">†</span><span class="fn-tooltip">...</span></span>
```

## Session memory

Extended context (page status, design system details, BQ reference, feedback conventions) is stored in Claude's persistent memory at:

```
/home/vscode/.claude/projects/-workspaces-pienza/memory/
```

Files: `MEMORY.md` (index), `project_overview.md`, `project_page_status.md`, `project_design_system.md`, `project_bigquery.md`, `feedback_conventions.md`, `project_perf_tricks.md` (backlog of loading/latency optimization ideas — deferred until the app is feature-complete, don't act on these mid-feature-work unless explicitly asked).

At the start of any new session, after reading this file, read those memory files for full project state.

**Never create a new persistent memory file without consulting the user first.** Before writing any new file under `/home/vscode/.claude/projects/-workspaces-pienza/memory/` (or its mirror in `assets_ignored/claude_docs/`), check `MEMORY.md` for an existing file the content could live in instead, and propose the destination (new file vs. existing file + section) for approval before writing. This does NOT apply to ephemeral scratchpad files Claude uses mid-task — only to durable memory files meant to persist across sessions. The `/canonize` command is the standing tool for this: propose where an event/decision should be archived as project canon, wait for approval, then write.

A mirror of these same files (for the user's own direct access, since `.claude/` is hard to browse) lives at `assets_ignored/claude_docs/` in the repo. **Sync rule:** whenever any file is edited in `/home/vscode/.claude/projects/-workspaces-pienza/memory/`, copy the same change into `assets_ignored/claude_docs/` (same filename), and vice versa — whenever a file in `assets_ignored/claude_docs/` is edited, mirror the change back into the memory directory. Keep both copies byte-identical after any edit to either.

**Recovery note (2026-07-19):** this Codespace's `/home/vscode/.claude/projects/-workspaces-pienza/memory/` was found empty at the start of a session — a container rebuild wipes it, since it lives outside the repo and isn't git-tracked. The `assets_ignored/claude_docs/` mirror survived (it's in the repo) and was copied back over to restore memory. **Lesson: a devcontainer/container rebuild resets Claude's persistent memory — the repo-tracked mirror is the only thing that survives one.** Anyone advising a container rebuild mid-project should flag this first.

## STAR interview stories

`assets_ignored/claude_docs/STAR_stories.md` is the user's personal interview-prep file — NOT part of the memory-sync system above (no frontmatter, no mirror in `/home/vscode/.claude/projects/-workspaces-pienza/memory/`, lives only in this one file). The user is preparing for job interviews and struggles to recall/narrate technical anecdotes on the spot, so this file exists as a pre-built arsenal of STAR-format (Situation/Task/Action/Result) stories drawn from real work done on this project.

**Whenever a piece of work in this session has real interview-story value** — a bug that took genuine diagnostic work to track down, a tradeoff decision with a defensible "why," a mistake caught before it shipped, a moment of technical judgment (including knowing when *not* to keep optimizing) — proactively add a new STAR entry to `assets_ignored/claude_docs/STAR_stories.md` once that piece of work is done. Don't ask permission first; just add it and mention briefly that you did. Skip routine/mechanical changes (styling tweaks, semicanon propagation, simple renames) that don't have a real story behind them.

**Format:** match the existing entries — Situation/Task/Action/Result in first-person, spoken-language-ready prose (not corporate jargon), plus a short "Why this story matters" line naming the trait/skill it demonstrates. Keep the running "Quick reference — one-liners" section at the bottom updated too when a strong one-liner emerges.

## GCS Deployment Workflow

### Principio arquitectural — REGLA ABSOLUTA
Todo archivo consumido por el Observatory (Streamlit Cloud) debe vivir en GCS.
NUNCA leer desde rutas locales `/workspaces/...` ni desde el repo en una pagina `.py`.
Las libretas (Codespaces) pueden leer pienza.db local o BigQuery — no aplica la restriccion.
Bucket: `pienza-streamlit`. Compute/storage decoupling: Streamlit Cloud es efimero y stateless.

Esta regla aplica tambien a assets de frontend (HTML/JS/CSS embebidos, no solo datos).
`assets/` (raiz del repo) es contexto/documentacion privada, correctamente sin trackear.
`observatory/assets/` NO deberia tener el mismo tratamiento de "nunca publico" que la raiz
solo por estar gitignored -- ese gitignore es deuda tecnica, no una decision de arquitectura.
La logica correcta (confirmada 2026-07-04): un solo criterio para todo el repo, "assets = no
trackeado/no publico", y todo lo que la app necesita en runtime (incluyendo HTML/JS de frontend,
no solo parquets/JSON/pesos de modelo) migra a GCS igual que los datos, en vez de vivir como
archivo local leido con `open()`.

### DEUDA TECNICA — asegurar que TODAS las paginas lean assets desde GCS, nunca local
**Reencuadre 2026-07-09:** el criterio correcto NO es "esta gitignored, por lo tanto en riesgo
de no desplegar" — varios archivos en `observatory/assets/` resultan estar trackeados en git
desde antes de que existiera la regla `/observatory/assets/` en `.gitignore` (que solo bloquea
archivos NUEVOS de trackearse, no destrackea los que ya estaban), asi que SI se despliegan bien
aunque tecnicamente esten en una carpeta gitignored. Eso fue una confusion de diagnostico, no el
punto real.

El punto real (regla arquitectonica original, ver REGLA ABSOLUTA arriba): la decision de mover
todo a GCS ya se tomo deliberadamente en este proyecto. Cualquier `.py` de pagina que siga
leyendo un archivo local via `Path(__file__)...` / `open()` en vez de `fetch_bytes_from_gcs` /
`fetch_parquet_from_gcp` es una excepcion que nunca se migro cuando se adopto la politica
GCS-only — sin importar si el archivo local "funciona" hoy por estar trackeado.

**ACLARACION DE REGLA 2026-07-10:** la regla GCS-only aplica a datos
sensibles/PII (parquets, JSON de features, etc.) — no a assets estáticos y
compartibles como PNGs/favicons, que pueden seguir leyéndose local vía
`Path(__file__)` siempre que el archivo esté trackeado en git. Bajo este
criterio, `0004_Data_Census_(The_Basics).py`'s `Pienza_ERD.png` (leído local,
confirmado por lectura directa del código durante el pase de modularización
2026-07-10) **no es deuda técnica** — es un diagrama estático, no dato
sensible. `9003_Markov_Fleet_Sim_Dashboard.py:63` (`poly.geojson`) no fue
reverificado en esta pasada, pero probablemente cae en la misma categoría
(revisar su contenido real antes de asumir cuál regla aplica).

**Ya confirmados correctos (leen via GCS, no locales):**
- `kepler_3D.html` en `main.py` — via `fetch_bytes_from_gcs("pienza-streamlit", "kepler_3D.html")`.
  La copia local en `observatory/assets/kepler_3D.html` es un sobrante sin uso, no el loader real.
- `0008_The_Quest_to_O1_NLP.py` ya no referencia `poly.geojson` en absoluto (debio removerse o
  renombrarse en un refactor posterior a la nota original de esta seccion).
- `logo.png` — sin referencias `Path(__file__)` encontradas; uso aun sin confirmar, pero no es
  un caso activo de lectura local conocido.

**Como aplicar:** antes de dar por resuelta esta deuda, correr
`grep -rn 'Path(__file__).*assets\|open(.*assets' observatory/pages/*.py observatory/main.py`
para re-confirmar que la lista sigue completa (puede haber nuevos casos si se agrega una pagina).
Para cada archivo pendiente: subir a GCS bucket `pienza-streamlit` (raiz, sin subcarpetas, ver
regla abajo) y cambiar el loader Python para leer desde GCS. No ejecutar la subida sin permiso
explicito del usuario (ver regla de permiso abajo).

### IMPORTANTE — Permiso obligatorio antes de subir a GCS
El usuario esta en el free tier de GCS. NUNCA ejecutar `gcs_deploy.py` ni ningun comando
que escriba a GCS sin pedir permiso explicito primero. Mostrar que se va a subir y esperar
confirmacion antes de proceder.

### ESTRICTO — Nunca crear subdirectorios/carpetas en el bucket
Todo archivo se sube DIRECTO a la raiz del bucket `pienza-streamlit`, sin prefijos de carpeta
(nada de `gs://pienza-streamlit/algun_directorio/archivo.ext`). El nombre del blob en GCS debe
ser un nombre de archivo plano, igual al patron ya usado en el MANIFEST de `gcs_deploy.py`
(ej. `260702_minibabel_holdout_audit.parquet`, no `holdout/260702_minibabel_holdout_audit.parquet`).
Si una IA sube un archivo y sin querer crea una carpeta nueva por poner una ruta con `/` en el
nombre del blob, es un error — hay que corregirlo y volver a subir el archivo a la raiz.

### Pipeline canonico — TODO archivo nuevo debe seguir este flujo
```
Notebook escribe → data/dumped_files/   (staging, siempre aqui primero)
                         ↓
           scripts/gcs_deploy.py        (agregar al manifiesto y correr con permiso del usuario)
                         ↓
              GCS pienza-streamlit      (unica fuente de verdad para Streamlit)
                         ↓
           observatory/pages/*.py       (solo lee desde GCS via gcp_client.py)
```

### Regla para cualquier IA que escriba codigo para una pagina de Observatory
1. Si la pagina necesita leer un archivo: ese archivo DEBE estar en GCS.
2. Usar `fetch_parquet_from_gcp` o `download_from_gcs` de `utils/gcp_client.py`.
3. Nunca usar `open(...)`, `pd.read_parquet("ruta/local")`, ni `json.load(open(...))` con rutas locales.
4. Si el archivo no existe en GCS todavia: agregar al manifiesto de `gcs_deploy.py`, informar al usuario, y pedir permiso para subirlo.

### Como agregar un archivo nuevo al manifiesto
Abrir `observatory/scripts/gcs_deploy.py` y agregar una entrada al array `MANIFEST`:
```python
{
    "page": "NNNN",                # numero de pagina que lo consume, ej. "0007"
    "local": "nombre_archivo.ext", # nombre exacto en data/dumped_files/ (SIEMPRE desde ahi)
    "gcs":   "nombre_archivo.ext", # nombre con el que quedara en el bucket (puede ser igual)
},
```
Nota: `local` SIEMPRE apunta a `data/dumped_files/`. Si un notebook escribe a otro lugar,
corregir el notebook para que escriba a `dumped_files/` antes de agregarlo al manifiesto.

### Como correr el script (pedir permiso antes)
```bash
python observatory/scripts/gcs_deploy.py --page 0007 --dry-run  # verificar primero
python observatory/scripts/gcs_deploy.py --page 0007             # subir con permiso del usuario
python observatory/scripts/gcs_deploy.py                         # subir todo el manifiesto
```

### Estado actual por pagina

**0007_Human_vs_AI_Behavioral_Cloning.py**
- `260420_resultados_torneo_iter2v3.parquet` — GCS OK
- `0508_monolith_metrics.json` — GCS OK
- `0509_cascade_metrics.json` — GCS OK
- `lasso_liga_a.json` — GCS OK (movido de `observatory/assets/` a `dumped_files/`)
- BigQuery queries al vuelo — OK

**Resto de paginas — PENDIENTE AUDITAR**
```bash
grep -n "open\|read_parquet\|read_csv\|read_json\|dumped_files\|/workspaces" observatory/pages/*.py
```

### Script de deploy
`observatory/scripts/gcs_deploy.py` — sube artefactos de `data/dumped_files/` a GCS.
Correr desde Codespaces despues de cada Run All de notebook que genere artefactos nuevos.

**Como agregar un archivo nuevo al manifiesto:**
Abrir `observatory/scripts/gcs_deploy.py` y agregar una entrada al array `MANIFEST`:
```python
{
    "page": "NNNN",               # numero de pagina que lo consume, ej. "0007"
    "local": "nombre_archivo.ext", # nombre exacto en data/dumped_files/
    "gcs":   "nombre_archivo.ext", # nombre con el que quedara en el bucket (puede ser igual)
},
```

**Como correr el script:**
```bash
# subir solo los archivos de una pagina
python observatory/scripts/gcs_deploy.py --page 0007

# dry-run primero para verificar que encuentra los archivos
python observatory/scripts/gcs_deploy.py --page 0007 --dry-run

# subir todo el manifiesto
python observatory/scripts/gcs_deploy.py
```

### Patron de lectura en Streamlit (ya implementado en gcp_client.py)
```python
from utils.gcp_client import fetch_parquet_from_gcp, download_from_gcs
# parquet: fetch_parquet_from_gcp("pienza-streamlit", "archivo.parquet")
# JSON/joblib: download_from_gcs("pienza-streamlit", "archivo.json", "/tmp/archivo.json")
```

---

## Claude Code environment mechanics (this VSCode extension, this Codespace)

Observed, not documented behavior — found while building the first project hook.

- **A new chat session does NOT reload `.claude/settings.local.json`.** Editing hooks
  mid-session has no effect until **Reload Window** in VSCode (`Ctrl+Shift+P` ->
  "Reload Window"). Starting a fresh chat is not enough.
- **`systemMessage` in a hook's output does not render visibly in this extension**
  (unlike the standalone CLI). Use `hookSpecificOutput.additionalContext` instead —
  that does get injected into the model's context, so Claude can relay it to the user.
- **`/hooks` with "Continue in Terminal" does not work here** — the `claude` binary is
  not on the system PATH in this environment (this is the extension, not the standalone
  CLI).
- **To verify a hook actually fired, without trusting the UI:** temporarily add a
  sentinel write to the hook's command (e.g. `echo ... >> /tmp/some_file.txt`), trigger
  the real tool call, and check the sentinel file — more reliable than waiting to see a
  message on screen.

## Key conventions

- `@st.cache_data` on all BQ queries — one network call per unique SQL string
- `st.set_page_config(layout="wide")` on every page
- `__pycache__` directories are auto-generated by Python — add to `.gitignore`, do not delete manually
- **NEVER run `git commit` on the user's behalf.** When a commit is needed, provide the message and stop — the user runs it in the terminal.
- Commit co-author line: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- **MEGA ALERTA — commit messages: ZERO quotes of any kind.** No `"`, no `'`, no smart quotes, no backticks around identifiers, no emoji, no special characters — these break shell commit commands. This applies even when referencing code that itself contains quotes (e.g. `st.secrets[gcp_service_account]`, not `st.secrets["gcp_service_account"]`) — paraphrase or drop the brackets/quotes entirely rather than quoting the literal code. Plain ASCII only. Format: `type(scope): short summary` on the first line, then a blank line, then bullet points starting with `-`. Never include untracked files (files not in git) in commit messages.
- **HARD LIMIT — commit messages must be 500 characters or fewer, total.** Count the full message (subject + body). If it doesn't fit, cut bullet points or tighten wording rather than exceeding the limit.
- Page numbering: `0001`, `0002`, `0003`, `0201`, `0301`, `0302`, `0501`, `0601–0604`; `9000_*` = archive
- **`assets_ignored/claude_docs/project_tech_debt.md` (and its memory mirror) is human-only — never edit it.** That file (numbered `TD0001`–`TD0025`+, plus an unnumbered "NUEVOS" notes section) is the user's own tracked backlog. If a piece of tech debt is discovered or logged during a session, write it to `assets_ignored/claude_docs/tech_debt_claude.md` instead (mirrored to memory same as the other docs) — never append to or edit `project_tech_debt.md` itself, even to mark something DONE.
- **Whenever a new file is created (scripts, utils, one-off tools — not per-page Streamlit `.py` files under `observatory/pages/`, those are already tracked by page status docs), add an entry to `assets_ignored/claude_docs/files_dict.md`** with the file's path and a one-line description of what it does. This is a running index so files don't get scattered/forgotten across the repo — check it before assuming a helper script doesn't already exist.
- **Do not overengineer.** No helper scripts or workarounds in place of using standard tools directly, no hardcoded values or logic that only work for the current data/test case, no abstractions or extra configurability for one-off tasks. Implement the general, principled solution, not the one that happens to make the current case pass. If a task or request seems infeasible or based on a wrong premise, say so instead of quietly working around it.

## Images
Once an image has been read and acted on, do not re-process or reference it again in subsequent turns.
