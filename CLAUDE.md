# Project Pienza — Claude Context File (root)

## What is this?

Read `README.md` for what this project is, its structure, and its architecture — that is the canonical source, not this file. Do not duplicate repo description or file-tree content here; if `README.md` and this file ever disagree, `README.md` wins and this file is stale.

## How Claude should navigate this project

This file sits on top of your own built-in system prompt — it does not repeat what that already covers (tool use, safety, general behavior). It only adds what's specific to Pienza.

- `README.md` — project overview, architecture, repo structure. Read first for orientation.
- `observatory/CLAUDE.md` — nested, loads automatically when working inside `observatory/`. Observatory-specific conventions live there, not here.
- `.claude/commands/` — user-invocable skills (`/deploy`, `/commit-msg`, etc.)
- `.claude/skills/` — reusable knowledge/workflows Claude can load on demand
- `.claude/rules/` — path-scoped conventions, load automatically only when touching matching files
- `.claude/hooks/` (via `settings.json`) — enforced guardrails that fire on specific events, not just suggestions
- `.claude/agents/` — custom subagent definitions for this project (none yet — see tech debt)
- `.claude/claude_docs/` — deeper reference material, not loaded by default, read on demand or via memory. `README.md` is the index — read that first, not this list, if it ever drifts.
  - `tech_debt.md` — formal tracked backlog with progress (canonical, merged from the former Claude-only and human-only backlogs)
  - `incidents_log.md` — things already tried and failed, don't repeat them
  - `prompt_engineering.md` — human-Claude interaction rules specific to this project
  - `session_ledger.md` — running changelog of work sessions
  - `mermaid/` — diagram style canon, drift audit history, generation script
  - `cloud_run.md` — deployment canon
  - `agentic_knowledge.md` — agentic workflows / RAG reference
  - misc reference docs (architecture notes, migration history, design canon, etc.)

## Deployment

For all things deployment (Cloud Run, Docker, domain, cron keep-alive), refer to the canon documentation: `.claude/claude_docs/cloud_run.md`. Do not improvise deployment steps from memory — that file is the single source of truth.

## Agentic workflows & RAG

For all things agentic workflows and RAG implementation, read `.claude/claude_docs/agentic_knowledge.md` — the canonical study/reference doc for these topics on this project.

## Requirements files — two, different purposes

- **`/workspaces/pienza/requirements.txt`** (repo root) — full dependency set for local dev, Codespaces, Streamlit Community Cloud, and the `research_core`/`research_full` notebooks.
- **`observatory/requirements.txt`** — trimmed runtime-only subset, exists only to keep the Cloud Run Docker image small. Only the Dockerfile references it — do not `pip install -r` it into the main dev environment. Not auto-derived; re-audit manually if `observatory/`'s imports change.

## research_full refactor — standing alert

If `research_full/` (or any notebook directory beyond the already-completed `research_core/`) is ever refactored for legibility/portfolio purposes, `.claude/claude_docs/nb_refactor_guide.md` is the governing precedent — read it in full before starting.

## BigQuery

For all things BigQuery (project ID, dataset, key tables/views, canonical join patterns, auth), read `.claude/claude_docs/bigquery.md` — the canonical reference, shared by both `research_core`/`research_full` notebooks and the observatory app. Do not query from memory without checking the schema reference it points to.

## GCS-only asset policy — REGLA ABSOLUTA, repo-wide

Any file consumed at runtime by a deployed app (observatory or otherwise) must live in GCS — never read from a local `/workspaces/...` path or from the repo in application code. Notebooks/Codespaces may read `pienza.db` local or BigQuery directly; this restriction is about deployed runtime code, not research environments. Bucket: `pienza-streamlit`, root-level blobs only, no subfolders. **Never run `gcs_deploy.py` or any command that writes to GCS without explicit user permission first** (free tier).

Full operational reference — manifest pattern, how to add a file, how to run the script, current per-page GCS status — read `.claude/claude_docs/gcs_deploy.md` in full before touching this pipeline. This is some of the most load-bearing documentation in the project; do not improvise from memory.

## Placeholder / pending callout pattern

When asked for a "shiny yellow" placeholder, render a deliberately ugly bright-yellow callout signaling a pending/unresolved item:

```html
<div style='border-left:6px solid #ffe600;background:#ffff00;border-radius:0 8px 8px 0;
     padding:12px 16px;margin-top:10px;font-size:0.80rem;color:#1a1a1a;line-height:1.65;'>
  <span style='font-size:0.7rem;font-weight:900;text-transform:uppercase;letter-spacing:0.8px;
        color:#cc6600;'>⚠ PENDING FIX — [title]</span><br><br>
  [explanation]
</div>
```
Pure Excel yellow (`#ffff00`) — never a soft tint. Deliberately impossible to miss.

## Brand convention

Never display "Uber" in product/category labels shown to the user, in any chart, table, or UI element. Strip programmatically: `re.sub(r'(?i)uber_?', '', label).strip('_').strip()`

## Anonymization protocol — repo-wide

Any surface displaying raw offer data (observatory pages, notebook audit cells) must obfuscate:

| Field | Rule |
|-------|------|
| `upfront_fare` / bonus amounts | Replace every digit with `#` |
| `pickup_address` / `dropoff_address` | Mask street number digit-by-digit with `#`; preserve 5-digit zip codes |

EPH computed values (derived ratios) do not need obfuscation.

```python
import re

def _obf_fare(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    return re.sub(r'\d', '#', f"{float(v):.0f}")

def _obf_address(v):
    if v is None or str(v) in ("None", "nan", ""):
        return "—"
    _mask_digits = lambda m: re.sub(r'\d', '#', m.group(0))
    return re.sub(r'\b(?!\d{5}\b)\d+[\w-]*\b', _mask_digits, str(v), count=1)

# additional helpers used in observatory pages:
# _obf_hash(v)    — truncates to 12 chars + ...
# _obf_latlon(v)  — masks decimal precision
```

`#`-per-digit is the canonical style (replaced an earlier `█` block style — see `.claude/claude_docs/` history if the reasoning is needed). Confirmed applied beyond observatory, e.g. `research_core/0212_ETL_Big_Bang_pienzadb.ipynb`'s financial-lineage audit cells.

## Claude Code environment mechanics (this VSCode extension, this Codespace)

- A new chat session does NOT reload `.claude/settings.local.json` — requires VSCode "Reload Window," not just a fresh chat.
- `systemMessage` in a hook's output does not render visibly in this extension — use `hookSpecificOutput.additionalContext` instead.
- `/hooks` with "Continue in Terminal" does not work here — the `claude` binary is not on PATH in this extension.
- To verify a hook fired without trusting the UI: add a sentinel file write to the hook command, trigger the real event, check the sentinel.

## Key conventions

- `__pycache__` directories are auto-generated — gitignored, never delete manually.
- **NEVER run `git commit` on the user's behalf.** Provide the message and stop.
- Commit co-author line: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
- **Commit messages: ZERO quotes of any kind**, no emoji, plain ASCII only. Format: `type(scope): short summary`, blank line, `-` bullets. Never include untracked files. **Hard limit: 500 characters total.**
- **`.claude/claude_docs/tech_debt.md` is the single canonical tech debt doc** (merged from the former Claude-only and human-only backlogs) — both you and Claude write to it directly; see that file's own header for the current format.
- **Whenever a new file is created** (scripts, utils, one-off tools — not per-page observatory `.py` files, those are tracked by page status docs), add an entry to `.claude/claude_docs/files_dictionary.md`.
- **Do not overengineer.** No helper scripts/workarounds in place of standard tools, no hardcoded values that only work for the current case, no unrequested abstractions. If a task is infeasible or based on a wrong premise, say so instead of working around it.

## Images
Once an image has been read and acted on, do not re-process or reference it again in subsequent turns.

## Session memory

Extended context lives in Claude's persistent memory at `/home/vscode/.claude/projects/-workspaces-pienza/memory/` (not exposed in the repo/frontend), mirrored to `.claude/claude_docs/` (public docs) and `assets_ignored/` (private/personal — interview prep, job tracking). Index: `.claude/claude_docs/README.md` (formerly `MEMORY.md`).

**Sync rule (explicit):** whenever any file is edited in the memory directory, copy the same change into its tracked mirror (`.claude/claude_docs/` or `assets_ignored/`, same filename) — and vice versa, whenever a mirrored file is edited in the repo, copy the change back into the memory directory. Keep both copies byte-identical after any edit to either side.

Never create a new memory file without proposing the destination first — see `/canonize`.
