# research_core Refactor Sprint — Guide

Persistent, human-readable companion doc for the `research_core/` refactor sprint. Not part of the memory-sync system (no frontmatter, not mirrored to `~/.claude/projects/.../memory/`) — same standalone treatment as `STAR_stories.md`. Purpose: if a new chat has to pick this sprint back up, read this file first for full context.

## Why this sprint, and why now

Pienza is shipping soon (feature-complete -> Streamlit tweaks -> **this refactor** -> public launch -> job search). `research_core/` (16 files) is the curated spine of research notebooks that hiring managers / technical recruiters will actually open and read. They will not be executed or extended after this — this is a one-time legibility pass, not a refactor for future scalability. That framing justifies choices that would be questionable in a living codebase (e.g. a static mermaid diagram in cell 0 that can't auto-update if a variable changes later — acceptable because there is no "later" here).

## Baseline survey (all 16 notebooks)

- Sizes range from 4 cells (`0604_ETL_cGAN_to_BigQuery.ipynb`) to 82 cells (`0212_ETL_Big_Bang_pienzadb.ipynb`).
- No shared script/module exists anywhere in `research_core/` — every notebook redefines its own DB path, GCS/BigQuery client setup, and (in the viz notebooks) color palette constants independently.
- Imports are scattered/re-imported cell-by-cell in most notebooks (worst offenders: 0211, 0509, 0608, 0601, 0407).
- Naming is inconsistent: snake_case dominates but is mixed with ALL_CAPS misused for one-off SQL blobs (`SQL_COPY_DATA`, `DDL_SQL_V3`), cryptic single/double-letter vars (`ap`, `mi`, `_c`, `k`, `x`, `y`), Spanish/English mixing (`df_arcos`, `df_comunidades`, `df_crater`), and AI/human in-joke naming (see Tech Debt below).
- Data sources vary by notebook family: local SQLite `pienza.db`, BigQuery, GCS, local `data/dumped_files/*.parquet`.
- **Data-routing canon** (already enforced repo-wide via an earlier Colab -> Codespaces sprint — not new): `pienza.db` is absolute SSoT for all data-eng/EDA/modeling phases; BigQuery is used strictly downstream of the `0603`/`0604` bridge notebooks; all intermediate writes go to `data/dumped_files/` (ephemeral, regenerable). Any notebook found deviating from this gets flagged as tech debt below, not silently changed as part of this sprint.

## Decisions locked in

1. **Mermaid diagram (cell 0)** — per-notebook judgment call. Simple/short notebooks: full variable-by-variable trace. Large notebooks (0211, 0509, 0608): high-level stage diagram (source -> key DataFrames -> transform stages -> output artifacts).
2. **Cell numbering — hierarchical by phase** — where a notebook naturally divides into phases, waypoints are renumbered `1.1, 1.2, 2.1, 2.2, 2.3...` instead of a flat `0..80` sequence, matching the phases in the cell-0 diagram. Not mandatory for small notebooks.
3. **Markdown "waypoint" cells** — instead of AI-style inline `# Cell N: does X` comments baked into code, a separate markdown cell goes before each code cell/group, narrating what's coming in a human, guided-journey tone, referencing the phase numbers.
4. **AI-authored comment stripping** — default is strip, replaced by waypoint markdown cells. **Exception: `0212_ETL_Big_Bang_pienzadb.ipynb`** already has hand-adapted comments — leave as-is. Every other notebook: explicit per-notebook keep/strip call from the user as we go. Overall goal: comments at a minimum by the end of the sprint.
5. **Shared setup module** — extract common boilerplate (DB path resolution, GCS/BigQuery client helpers, `dumped_files` path resolver, shared palette constants) into a module under `research_core/` once the pilot notebook shows what's actually reusable. Likely one module with focused helpers notebooks import selectively, not one monolithic setup cell — data sources differ by family.
6. **Outputs** — every refactored notebook is re-run end-to-end so committed `.ipynb` files show real executed output (what a recruiter sees on GitHub). All notebooks are confirmed runnable in this Codespace already (inputs/credentials present).
7. **Baseline rerun before refactor** — fresh top-to-bottom rerun of each notebook *before* any edits, to isolate "pre-existing bug" from "refactor regression."
8. **Naming language** — translate Spanish/English mixes and in-jokes to sober English (`df_arcos` -> `df_edges`, `df_comunidades` -> `df_communities`, salchichota map -> plain descriptive name); fix single-letter/cryptic vars; stop misusing ALL_CAPS for one-off SQL blobs (reserve for true constants: paths, config, palette hex values).
9. **No `.py` round-trip** — edit `.ipynb` JSON directly (`nbformat`/script), execute in-place (`jupyter nbconvert --execute` or equivalent). No jupytext conversion.
10. **Service accounts** — notebooks and Observatory keep separate credentials; out of scope for this sprint (tracked separately as deferred tech debt), consistent with the two possibly being split into separate repos someday.
11. **Pacing** — pilot notebook first (`0604_ETL_cGAN_to_BigQuery.ipynb`, 4 cells), user reviews the pattern, then the remaining 15 in ascending size order, refining the shared module and comment-stripping calls as they come up.
12. **Emojis and language — standing default, confirmed after the 0604 pilot (2026-07-13), no longer a per-notebook ask**: strip emoji from print statements/comments everywhere unless one is genuinely functional (rare in these notebooks); translate all Spanish print/comment text to plain English. Applies repo-wide across all 16 notebooks going forward.
16. **Tone — sober/professional, no dramatic flourish. Standing rule from 0407 (2026-07-15) onward.** Beyond the earlier "neutral wording" call on 0307 (mediocre/sufficient), 0407 surfaced a broader pattern: theatrical section titles and prints like "Invoking the beast: HDBSCAN", "Ockham's razor", "sovereign zones", "gravitational mass", "Forging the lean Golden Master" read as amateurish, not as a portfolio piece for hiring managers. Applies to `display(Markdown(...))` titles, print statements, plot titles, comments, and variable/function names alike — check every remaining notebook for this pattern, not just emoji/Spanish (which were already covered). When in doubt, prefer the flattest accurate description over anything that sounds like a video-game achievement.

   **Word blacklist (running list, check every remaining notebook for these):** `salchichota` (0509 id map — see Tech Debt #1), `genome` (0602, replaced with "feature set"), `sovereign` (0602, replaced with "mapped"/dropped), `refinery` (0602, replaced with "preprocessing pass"/"preprocessing pipeline"), `forensic` (0602's "forensic classifier"/"Forensic layers", replaced with "discriminating classifier"/"Discriminator layers"), `exilio`/`exile` (0608 — "el Exilio", "el monstruo", "Gran Exorcismo" for the unassigned/out-of-geofence zone filter; replace with neutral "out-of-geofence"/"unassigned zone" wording). Add to this list whenever a new dramatic/in-joke word surfaces.
15. **Anonymization protocol now applies to notebooks too — standing rule from 0601 (2026-07-15) onward, not just the Observatory.** The `assets_ignored/CLAUDE.md` anonymization canon (mask street numbers digit-by-digit with `#`, preserve 5-digit postal codes; see `_obf_address`) had only ever been applied to Observatory pages before 0601 — this notebook was the first time raw addresses showed up in a notebook's own output/display. Rule going forward: any notebook cell that **displays or prints** a raw address (or other PII covered by the canon, e.g. fares) must obfuscate it; any **file export/persistence** (parquet, JSON, etc.) written for downstream ML/data use stays raw/unmasked, since that's a data artifact, not a public-facing display. Concretely in 0601: added an `_obf_address` helper in Phase 1.1 (same masking logic as the Observatory's), applied to the `Address_Fed_To_Model` audit-table column (6.1) and to a display-only copy before the holdout-audit preview print (8.1) — the actual `df_audit.to_parquet(...)` export in 8.1 was deliberately left unmasked. Hardcoded/illustrative test strings (e.g., 3.2's regex test cases, author-written, not pulled from `pienza.db`) are out of scope — user confirmed those don't need masking. **Action per notebook**: check every remaining notebook for any place a raw address (or fare) gets displayed/printed, not just exported, and apply the same display-vs-export split.
14. **Mermaid diagram styling — teal outline + teal arrows, standing default from 0606 (2026-07-13) onward**: append both `classDef default stroke:#21918c,stroke-width:2px;` and `linkStyle default stroke:#21918c,stroke-width:2px;` as the last two lines inside every `mermaid` flowchart's code fence, so node borders AND arrows render in Pienza teal instead of mermaid's default blue. Applied to 0606; not yet retrofitted onto 0604/0607/0305's diagrams — ask before doing so, since that's their call.
13. **Hierarchical `N.M` cell numbering — apply whenever it's a good fit, no need to ask first**: user gave standing permission (after 0604) to use `1.1, 1.2, 2.1, 2.2...` numbering on any notebook where a phase naturally contains multiple sub-steps (e.g. 0607's Phase 2 "TRTR" has 5 sub-steps: extraction, product purge, train, final exam, purge class 7). Simple one-block-per-phase notebooks (like 0604) can stay flat (`Phase 1`, `Phase 2`...).

## Per-notebook refactor pattern

1. Baseline rerun (clean, no errors) — diff anchor. **Capture key output values at this point** (row counts, metrics like F1/accuracy, class counts, any printed numeric summary) before touching any code — hold these in-session so that after the post-refactor re-run, the comparison against them is automatic (mine to catch), not something the user has to eyeball and notice unprompted. This is how the emoji/LabelEncoder cache-mismatch bug in 0607 should have been caught — silent numeric drift is easy to miss on a manual read-through.
2. Imports consolidated to cell 1 (right after mermaid/context cell 0), deduplicated.
3. Shared boilerplate replaced with calls into the shared module.
4. Variables renamed: snake_case, English, no cryptic single letters (outside true local loop counters), ALL_CAPS reserved for real constants.
5. Cells modularized — one coherent step per cell, matching phase/mermaid structure.
6. Phase-based numbering applied where applicable.
7. Waypoint markdown cells inserted.
8. Comments stripped per the per-notebook call (0211 exempted).
9. Cell 0 gets the mermaid diagram + 1-2 sentences of plain-English context.
10. Re-run post-refactor, diff against the baseline rerun — row counts/metrics/plots should match (this is a reorganize/rename pass, not a logic change).
11. Canon check against the data-routing rule — flag deviations here, don't silently fix.
12. Log anything notable into the Tech Debt / README TODO sections below.

## Interaction workflow (panorama -> commit msg)

Here's the flow we follow in each notebook, end to end:

**1. Panorama inicial**
Leo la libreta completa (todas las celdas) y te doy un resumen: cuántas celdas tiene, qué hace cada fase/bloque, qué imports están dispersos, qué nombres de variables están en español/inglés mezclado o son crípticos, qué comentarios son dramáticos o de IA, y cualquier hallazgo raro (bugs, rutas hardcodeadas, deuda técnica). No toco nada todavía.

**2. Baseline (Run All)**
Te pido correr la libreta tal cual está, de arriba a abajo, para capturar los outputs/resultados originales — esta es la referencia contra la que voy a comparar después de refactorizar.

**3. Confirmar decisiones contigo**
Para cosas ambiguas o de alto impacto (ej. nivel de detalle del diagrama mermaid, si se borra o se conserva una celda superada, cómo nombrar algo con connotación rara) pregunto antes de ejecutar — no asumo.

**4. Refactor** (aplico el patrón estándar)
- Imports consolidados en una sola celda de setup al inicio
- Numeración jerárquica `N.M` por fases (`## Phase N`, `#### N.M`)
- Diagrama mermaid de fase (cell 0) + diagrama detallado de variables como Appendix al final (si aplica)
- Celdas markdown "waypoint" narrando cada paso
- Nombres de variables sobrios, en inglés, sin cripticismo ni in-jokes
- Cero emoji, cero español en prints/comentarios/títulos
- Tono sobrio — sin lenguaje dramático (ver word blacklist en la regla 16)
- Rutas/constantes repetidas consolidadas arriba
- Nunca cambio lógica/resultados — solo reorganizo, renombro, traduzco

**5. Validación estructural**
`nbformat.validate()` + `ast.parse()` por celda (tolerando el falso positivo de `!pip install`), confirmo que no quedaron imports duplicados fuera de la celda de setup.

**6. Verificación contigo**
Te pido correr Run All de nuevo sobre la versión refactorizada y confirmas que los resultados coinciden con el baseline (o discutimos cualquier diferencia intencional).

**7. Bugs reales encontrados**
Si aparece un bug de verdad fuera del alcance del sprint, lo documento en `project_tech_debt.md` (memoria + espejo en `assets_ignored/claude_docs/`) sin bloquear el sprint.

**8. Cierre**
Actualizo la tabla de progreso en `nb_refactor_guide.md` (memoria + espejo), y te doy el mensaje de commit — tú lo corres, yo nunca hago commit por mi cuenta.

## Execution order

1. **Pilot**: `0604_ETL_cGAN_to_BigQuery.ipynb` (4 cells) — full pattern, then stop for review.
2. Continue: `0607_cGAN_TSTR.ipynb` (10) -> `0305_EDA_Causal_Inference.ipynb` (11) -> `0606_cGAN_downscaling.ipynb` (11) -> `0307_EDA_Optimal_Stopping_Playbook.ipynb` (13) -> `0605_cGAN_denormalization.ipynb` (17) -> `0601_NLP_Transformer_miniBabel.ipynb` (17) -> `0407_Clustering_Paper_Streamlit.ipynb` (19) -> `0403_KMeans_Raw.ipynb` (20) -> `0602_cGAN_Training.ipynb` (27) -> `0608_Bridge_to_Markov_Network_Graph.ipynb` (63) -> `0212_ETL_Big_Bang_pienzadb.ipynb` (82) -> `0603_ETL_pienzadb_to_BigQuery.ipynb` (17, pairs with 0212) -> **`0509_WINNER_XGB_cascade_postablation.ipynb` (72) moved to very last (2026-07-15, user's call).**
3. **Reorder decision (2026-07-13)**: `0603` was originally slotted right after 0307 by ascending cell count, but the user moved it to dead last (after 0211, the Big Bang notebook) — 0603 creates/replaces the canonical BigQuery views (`v_mission_dossier`, `v_ML_Supervised`, `v_offers_human`, `v_lifecycle_audit_accepted`, etc.) the live Observatory depends on, and pairs narratively with 0211 (SQLite Big Bang) as the two ETL bridge notebooks — doing them back-to-back at the very end made more sense than fitting 0603 in by cell-count order alone.
4. Check in with the user periodically, especially before the three largest (0608, 0509, 0211) and before 0603 (view-DDL notebook — SQL view bodies must stay byte-identical, only Python wrapper code gets touched).

## Recurring gotcha — HDBSCAN non-determinism via approx_min_span_tree

Found in `0407_Clustering_Paper_Streamlit.ipynb` (2026-07-15): `hdbscan.HDBSCAN` has no `random_state` param in this environment's version, but defaults to `approx_min_span_tree=True`, which can produce slightly different point/hexagon counts between runs on the same data (observed: 2616/2621/2614 points, 525/528/522 hexagons across three runs — same zone coverage, same major totals, small numeric drift only). Fixed by adding `approx_min_span_tree=False` to the `HDBSCAN(...)` call, confirmed deterministic across two subsequent runs (2614/522 both times). Negligible performance cost at this dataset size (~4,760 points). Check for this in any other notebook using `hdbscan.HDBSCAN` for clustering.

## Recurring gotcha — emoji in class label strings (LabelEncoder sort order)

Found in `0607_cGAN_TSTR.ipynb`, Phase 3.2, on first post-refactor rerun (2026-07-13). Will likely recur in other notebooks — check for it every time a categorical target uses emoji-prefixed string labels (e.g. `"🔴 Non-Operational"`, `"💎 THE_NUANCED_REST"`).

**Root cause**: `sklearn.LabelEncoder.fit()` sorts unique label strings alphabetically (by Unicode code point) to assign integer codes. Stripping the emoji prefix as part of the sober-naming pass changes each label's leading character, which can completely reorder the alphabetical sort — e.g. `💎` (U+1F48E) sorts before `🔴` (U+1F534), so a gem-prefixed label used to sort first; with emoji removed, plain alphabetical order put it last instead. The result isn't a simple off-by-one, it's whatever permutation the new sort produces — but visually on a confusion matrix it can look like a shifted/rotated diagonal.

**Why it bites specifically on re-run, not on first glance**: if a notebook caches a trained model to disk (`model.save_model(...)` + a `FORCE_UPDATE` flag to skip re-training), the cached model was fit under the *old* label-to-int mapping. Re-running after the emoji edit re-fits `LabelEncoder` fresh (new mapping) but loads the *old* cached model — model output ints and label decoding are now out of sync. This is a cache-invalidation problem, not a logic bug in the pipeline.

**Fix pattern**: whenever emoji are stripped from strings that feed a `LabelEncoder` (or any place sort order determines an implicit encoding), force a retrain of any cached/persisted model downstream that depended on the old label order — flip `FORCE_UPDATE = True` for one run (or delete the cached model file, since `dumped_files/` is documented as ephemeral/regenerable), re-run, then set `FORCE_UPDATE` back to `False` and commit the regenerated cache artifact.

**Action per notebook**: before stripping emoji from any string, grep the notebook for whether that string feeds a `LabelEncoder`, `pd.factorize`, `.astype('category')`, or similar order-sensitive encoding — and whether a trained model/cache downstream depends on that encoding.

## Verification checklist (use to spot-check any refactored notebook)

**Estructura**
1. Cell 0 reservada exclusivamente para el diagrama mermaid + intro en inglés (nunca para código ni la primera fase).
2. Imports consolidados en una sola celda (Phase 1.1), deduplicados — ninguna otra celda debe tener `import`/`from` sueltos.
3. Notebook dividido por fases (`Phase 1`, `Phase 2`... o `1.1, 1.2, 2.1...` si la fase tiene varios sub-pasos) — cada fase es un par: celda markdown ("waypoint") + celda de código.
4. Cada celda de código hace una cosa coherente (no mezcla setup+conexión+query+plot en una sola).

**Idioma y tono**
5. Cero emojis — en prints, comentarios, y **en cualquier string que alimente un `LabelEncoder`/`factorize`/encoding** (ojo con el gotcha ya documentado).
6. Todo en inglés — prints, comentarios, docstrings, mensajes de error.
7. Comentarios AI-style (`# CELL N: TITLE...`) eliminados, reemplazados por el markdown waypoint de arriba.
8. Comentarios que sí quedan son mínimos, tipo section-divider (`# --- X ---`), solo donde ayudan a navegar una celda con varios sub-bloques.

**Naming**
9. Variables Spanglish/in-joke traducidas a inglés sobrio (`sacred_schedule` → `week_schedule`, etc.).
10. Constantes de marca (`OPUS_*` → `PIENZA_*`) y duplicados de una misma constante bajo dos nombres unificados (`PIENZA_BG` → `PIENZA_GREY`).
11. snake_case consistente, ALL_CAPS reservado solo para constantes reales.

**Integridad de lógica**
12. Cero cambios de lógica — mismos cálculos, mismo modelo, mismos parámetros. Solo reorganización/renombrado.
13. Verificación de que ningún cache/modelo persistido en disco quedó desalineado por un cambio de encoding (ver el gotcha de emoji+LabelEncoder).
14. Rutas GCS/BigQuery revisadas contra el canon de ruteo de datos existente (`pienza.db` pre-bridge, BigQuery post-bridge, `dumped_files/` para intermedios) — cualquier desviación se anota en tech debt, no se corrige en silencio.

**Verificación**
15. Baseline capturado antes de tocar código; outputs post-refactor comparados contra ese baseline (Claude revisa esto, no solo el usuario).
16. Notebook re-ejecutado de punta a punta tras el refactor, cero errores.

## Progress log

| Notebook | Status |
|---|---|
| 0604_ETL_cGAN_to_BigQuery.ipynb | Done |
| 0607_cGAN_TSTR.ipynb | Done |
| 0305_EDA_Causal_Inference.ipynb | Done |
| 0606_cGAN_downscaling.ipynb | Done |
| 0307_EDA_Optimal_Stopping_Playbook.ipynb | Done |
| 0605_cGAN_denormalization.ipynb | Done |
| 0601_NLP_Transformer_miniBabel.ipynb | Done |
| 0407_Clustering_Paper_Streamlit.ipynb | Done |
| 0403_KMeans_Raw.ipynb | Done |
| 0602_cGAN_Training.ipynb | Done |
| 0608_Bridge_to_Markov_Network_Graph.ipynb | Done |
| 0212_ETL_Big_Bang_pienzadb.ipynb | Done |
| 0603_ETL_pienzadb_to_BigQuery.ipynb | Done |
| 0509_WINNER_XGB_cascade_postablation.ipynb | Done (2026-07-16) — all 16/16 notebooks complete |

---

## Tech Debt (dumped here as noticed, some may apply retroactively to `research_full`)

1. **RESOLVED — "salchichota" id map naming.** `0509_WINNER_XGB_cascade_postablation.ipynb`'s cell titled "CELL 1.2: STRATEGIC GROUPING & THE 'SALCHICHOTA' NAMING CONVENTION" was sobered up during 0509's own refactor pass — now "#### 1.4 — Zone grouping and merged names", variable renamed to `id_map`. Confirmed 2026-07-17: no remaining occurrences of "salchichota" anywhere in the notebook.

2. **GCS subfolder writes in `0604_ETL_cGAN_to_BigQuery.ipynb`** — this notebook uploaded to `gs://pienza-streamlit/training/...` and `gs://pienza-streamlit/manifold/...` (subfolder prefixes), which contradicts the "flat bucket root, no subdirectories ever" rule in the `gcs_deploy.py` manifest workflow. Root cause: this notebook predates that rule — it wasn't a violation when written, the rule didn't exist yet. Fixed during the pilot refactor (2026-07-13) by changing `GCS_PATH`/`GCS_MANIFOLD_PATH` to root-level filenames (`df_gan_training_set_v8.parquet`, `260426_cGAN_manifold_v8.parquet`), matching the manifest convention. Confirmed via grep that `observatory/` does not read these two GCS parquet files directly anywhere (only a further-downstream BigQuery table, `synthetic_manifold_v8_downscaled`, is referenced, and only from an archived page) — so this was a safe rename with no live consumer to break.
   - **RESOLVED (2026-07-17) — decided against.** No staging-script/manifest convention will be introduced for notebooks. `gcs_deploy.py`'s manifest workflow is an Observatory-only concern (assets the live Streamlit app reads); notebooks writing directly to GCS inline via `blob.upload_from_filename` is fine and intentional, not a gap to close.

3. **RESOLVED (2026-07-17) — Italicize + teal-frame commentary/insight markdown cells, retrofitted repo-wide.** Established in `0608_Bridge_to_Markov_Network_Graph.ipynb` (2026-07-15): markdown cells that are explanatory commentary/insights (as opposed to structural `## Phase N` / `#### N.M` waypoint cells) get their heading demoted two levels (`##`->`####`, `###`->`#####`) and their body text italicized, then the whole cell is wrapped in `<div style="border-left: 4px solid #21918c; padding: 4px 20px; background: rgba(33,145,140,0.05); border-radius: 0 6px 6px 0;">...</div>` (blank line after the opening tag and before the closing tag, so the markdown inside still renders instead of being treated as raw HTML). Retrofitted onto 0407 (1 cell), 0403 (4 cells), 0602 (2 cells), plus 0603 (1 cell, caught separately after initial sweep). 0604, 0607, 0305, 0606, 0307, 0601 had no qualifying commentary cells — every markdown cell in those six was already structural.

4. **Real bug fixed in `0605_cGAN_denormalization.ipynb` — chunked BigQuery upload was silently uploading zero/wrong rows.** The original segmented-upload cell used `F.monotonically_increasing_id()` to assign a row index for chunking, but that function only guarantees *increasing*, not *consecutive*, IDs — each Spark partition's IDs start at `partition_index << 33` (~8.59 billion for partition 1+). Since the chunking loop only iterated `start < total_rows` (~1M), it could never reach any partition beyond partition 0, so most/all of the manifold silently never got uploaded despite every chunk printing "success" (loading an empty DataFrame to BigQuery is not an error). Confirmed via a clean Run All that the resulting `synthetic_manifold_v8_enriched` table had 0 rows.
   - **First attempted fix**: switch to native `df_final.write.format("bigquery")` via the Spark-BigQuery connector (using the GCS staging bucket already configured for this purpose). This hit two consecutive environment issues: (a) missing GCS-Hadoop filesystem support (`No FileSystem for scheme "gs"`) — fixed by adding `com.google.cloud.bigdataoss:gcs-connector:hadoop3-2.2.21` + `fs.gs.impl`/`fs.AbstractFileSystem.gs.impl` configs; (b) a Guava version conflict (`NoSuchMethodError` on `Preconditions.checkState`) between the BigQuery connector, the GCS connector, and Hadoop 3.3.4's own bundled Guava — classic multi-connector "Guava hell", not reliably fixable by version-guessing within reasonable effort.
   - **Final fix applied**: reverted to the original pandas-chunked-upload architecture (proven to work elsewhere in this repo, e.g. 0604/0606), but corrected the actual bug — replaced `F.monotonically_increasing_id()` with `df_final.rdd.zipWithIndex()`, which produces a true sequential `0..N-1` global index across all partitions. Removed the now-unneeded GCS-connector config from the Spark session. Verified via fresh Run All: 1,010,001 rows uploaded across 5 clean 250k-row segments, table confirmed non-empty in BigQuery, downstream audits (route control 58.12%, geospatial purity 18.35%) all produced sane non-zero numbers.
   - **Relevant to other notebooks**: any other notebook using `F.monotonically_increasing_id()` for row-based chunking (not yet seen elsewhere, but check if one comes up) has this same latent bug — prefer `zipWithIndex()` for that purpose.

5. **RESOLVED — "Appendix — variable journey" section, retrofitted onto every notebook.** Starting with `0407_Clustering_Paper_Streamlit.ipynb` (2026-07-15), each notebook gets a second, variable-level mermaid diagram (tracing actual DataFrame names/transformations cell-to-cell) placed as an `## Appendix — variable journey` markdown section at the very **end** of the notebook — not next to the phase-level diagram in cell 0, since having both up front before the imports was too much cognitive load on first read. Confirmed present across the full family, including 0602 and 0603 (both got a newly-authored appendix during the 2026-07-17 mermaid-consistency pass, since neither had one).
6. **RESOLVED — Mermaid teal styling retrofit, applied to all three pre-0606 notebooks.** The `classDef default` + `linkStyle default` teal styling (rule #14 above) was introduced starting with `0606_cGAN_downscaling.ipynb`. Confirmed 2026-07-17: `0604_ETL_cGAN_to_BigQuery.ipynb`, `0607_cGAN_TSTR.ipynb`, and `0305_EDA_Causal_Inference.ipynb` all now have both style lines in their cell-0 mermaid diagrams.

---

## Shared module — CONSIDERED AND DECIDED AGAINST (2026-07-17)

Decided 2026-07-13: the shared setup module(s) get built **last**, after all 16 notebooks are refactored — not incrementally. This log accumulates what's actually reusable (and what varies) as each notebook is done, so the final module design is based on real evidence across the whole family, not guessed upfront. Likely to end up as **multiple modules** split by data-source family (SQLite/`pienza.db` readers vs. BigQuery readers vs. GCS-only), not one universal setup file — confirm/revise once more notebooks are in.

**Final decision (2026-07-17), now that all 16/16 notebooks are refactored: do not build it.** The findings log below (stopped at 6/16) was never picked back up once the sprint reached 16/16 — deliberately, not by oversight. Reasoning:

- The sprint's own founding framing is that `research_core/` is now static — "will not be executed or extended after this... a one-time legibility pass, not a refactor for future scalability." A shared module is a maintainability investment that pays off when files keep changing together over time. There is no future change these notebooks will go through that a shared module would make cheaper.
- The actual reading medium matters: a recruiter/hiring manager opens one notebook on GitHub, in isolation, top-to-bottom, often without opening any of the other 15. Every notebook right now is fully self-contained — zero external files to go chase down to understand it. A shared `_pienza_setup.py` would trade that self-containment for DRY-ness that has no reader who benefits from it, since nobody is maintaining this repo's notebooks long-term.
- Modularizing here would have been driven by "this is what a senior engineer would do" rather than by an actual need in this context — correctly recognizing that a frozen, single-reader-at-a-time portfolio artifact does *not* call for it is the stronger signal, not the module itself. If asked why the palette constants are repeated across files, "static portfolio artifact, no future maintenance, prioritized single-file readability over DRY" is a better answer than a module built pre-emptively to avoid the question.

Not revisited unless `research_core/` stops being a frozen artifact (e.g. gets actively extended again) — if that ever happens, re-open this decision rather than assuming it still holds.

**Status as of 0604 + 0607 (2 of 16 done):**

- **Pienza palette** (`PIENZA_PURPLE/TEAL/GREY/TEXT` + the teal cmap) — 100% identical in both. Clear, safe extraction candidate already.
- **BigQuery connection** — not yet uniform: 0604 authenticates via `service_account.Credentials.from_service_account_file(SA_PATH)` passed explicitly to the client; 0607 uses `os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_PATH` and lets the client pick it up implicitly. Two different ways of doing the same thing — worth unifying, but no notebook reading from `pienza.db` (SQLite) has been refactored yet, which will show a third, likely very different connection pattern. Goal: homologize 0604 and 0607 (and everything else in the BigQuery family) to connect the same way.

**Status as of 0604 + 0607 + 0305 (3 of 16 done):**

- **SQLite connection** (`0305`, first `pienza.db` reader refactored): `from sqlalchemy import create_engine`, `DB_PATH = '/workspaces/pienza/data/pienza.db'`, `db_engine = create_engine(f'sqlite:///{DB_PATH}')`, then `pd.read_sql(query, db_engine)`. Third distinct connection pattern (vs. the two BigQuery auth styles in 0604/0607) — confirms this will need its own module/helper, separate from the BigQuery family.
- **Pienza palette** — still 100% consistent across all 3 notebooks so far (`PIENZA_PURPLE/TEAL/GREY` core three; `PIENZA_TEXT` value differs slightly — 0305 uses `#121212`, 0607 uses `#333333` — needs reconciling into one canonical value when the module is built).

**Status as of 0606 (4 of 16 done):**

- **BigQuery connection**: 0606 uses the same explicit `service_account.Credentials.from_service_account_file(SA_PATH)` + `bigquery.Client(credentials=..., project=...)` pattern as 0604 — now 2-of-2 on that style vs. 0607's implicit `os.environ["GOOGLE_APPLICATION_CREDENTIALS"]` approach. Leaning toward the explicit-credentials style as the canonical one when the module gets built.
- **GCS upload + storage client**: recurring pattern across 0604/0606: `storage.Client(credentials=credentials, project=PROJECT_ID)` + `bucket.blob(name).upload_from_filename(path)`, always uploaded flat to bucket root. Good candidate for a shared `upload_to_gcs(local_path, blob_name)` helper.
- **Geo dependency**: 0606 is the first (and so far only) notebook using `geopandas` + a local `poly.geojson` file (`/workspaces/pienza/assets/poly.geojson`) — this is notebook-specific, not a candidate for the shared module.

**Status as of 0307 (5 of 16 done):**

- **SQLite connection**: identical to 0305's pattern — `create_engine(f'sqlite:///{DB_PATH}')`, `DB_PATH = '/workspaces/pienza/data/pienza.db'`. Now 2-of-2 consistent for the `pienza.db`-reading family, confirming this as the canonical SQLite helper shape.
- **Pienza palette**: `PIENZA_PURPLE/TEAL/GREY/TEXT` fully consistent across all SQLite-reading notebooks so far. Still the `PIENZA_TEXT` value mismatch noted earlier (0305: `#121212`, 0607: `#333333`) to reconcile.

**Status as of 0605 (6 of 16 done):**

- **BigQuery connection, third variant**: 0605 uses `os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SA_PATH` (same as 0607) but then instantiates clients two different ways in the same notebook — `spark.read.format("bigquery")` (Spark connector, picks up the env var implicitly) and later `bigquery.Client(project=GCP_PROJECT_ID)` (plain client, no explicit credentials object, also relies on the env var). So env-var-based implicit auth now has 2-of-6 notebooks (0605, 0607) vs. explicit-credentials-object style 2-of-6 (0604, 0606) — still a genuine split, not yet resolved toward one canonical style.
- **Spark is notebook-specific** — not a candidate for the shared module (only 0605 uses PySpark so far).

*(Update this section after each subsequent notebook.)*

## README TODO — moved out of this sprint

Moved to `project_tech_debt.md` (2026-07-17) as core repo tech debt, not scoped to this sprint — this file is about `research_core/` internals, and README drift is a repo-wide concern independent of whether the notebook sprint itself is done.
