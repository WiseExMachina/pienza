# The Pienza Papers — Migration to `paper-dev`

**Status note (2026-07-31):** this doc is dormant reference, not an active plan. `paper-dev`'s own `README.md` reframes the paper as parked long-term ("not publication-ready, not abandoned... the tool it was compensating for got replaced") rather than something actively waiting for a resume sprint — the paper's original job (manual cross-session memory) is now handled by Claude Code's agentic workflows. The technical facts below (what was removed from `main`, exact files, `PDF_URL`, GitHub Pages behavior) remain accurate and untouched since 2026-07-18. If `The_Pienza_Papers/` is ever merged back into `main`, the revival steps here are the correct playbook — just don't read this doc as implying that's imminent or planned.

Standalone reference doc (not part of the memory-sync system). Documents why and how `The_Pienza_Papers/` was pulled out of `main` on 2026-07-18, and exactly how to bring it — and its two "Download PDF" buttons — back if it's ever revived.

## Why

The Pienza Papers grew past its original purpose. It started as a credibility/authority piece to accompany the portfolio, but has since grown to 100+ pages and isn't a one-sprint polish job. The user needs to prioritize job applications now, not keep expanding an unfinished paper. Rather than delete the work (real content, real git history), it's being moved to a dedicated branch — `paper-dev` — where it can be resumed later without living on the public-facing `main` branch or cluttering the live Streamlit app in the meantime.

## What "moving to a branch" actually means here, technically

`main` is the branch GitHub Pages publishes from (`Deploy from a branch → main → /(root)`), and the PDF's live hosted URL (`https://wiseexmachina.github.io/pienza/The_Pienza_Papers/Pienza_Papers_Scientific.pdf`, see `observatory_architecture.md`) mirrors the exact repo path under `main`. So this isn't a simple `mv` — it's:

1. A new branch, `paper-dev`, created from `main` at its current state (so it starts with the full repo, including `The_Pienza_Papers/`, and full git history is preserved on that branch).
2. On `main`, `The_Pienza_Papers/` is removed (`git rm -r`) — this is what actually stops GitHub Pages from serving the PDF (the file no longer exists on the branch Pages deploys from).
3. Because the PDF disappears from the live site, the two "Download PDF" buttons in the Streamlit app (which point at that now-dead URL) are removed from `main` too, so the live app never shows a broken/dead link.
4. `paper-dev` is pushed to `origin` so the work isn't only local — it's visible on GitHub (a recruiter looking at the repo sees an active `paper-dev` branch, which fairly represents "in progress, not abandoned").

**Important nuance, a real concern raised and addressed during this session**: a git branch is not a partial copy — it's a pointer to a full-repo snapshot, so `paper-dev` necessarily contains the *entire* repo, not just `The_Pienza_Papers/`. This is not a storage cost (branches share history/objects; nothing is duplicated on disk until the branches diverge), but it is a genuine workflow risk: if you `git checkout paper-dev` inside the same working directory, it's easy to lose track of which branch you're on and accidentally edit or commit something unrelated, or later merge more than intended.

**Fix chosen: a separate GitHub Codespace for `paper-dev`, not a checkout in this Codespace.** The user's day-to-day Codespace (this one) stays permanently on `main`. When it's time to resume the paper, spin up a *new*, separate Codespace pointed at the `paper-dev` branch. This is a stronger isolation guarantee than a local `git worktree` would have been — it's a fully separate VM/container/filesystem, not just a separate directory sharing the same `.git`. There's no `git checkout` step to fumble and no shared working directory to accidentally edit the wrong thing in.

To resume: from the GitHub repo page, open a Codespace on the `paper-dev` branch (not `main`). Work there exclusively while editing the paper. This Codespace (`main`) is never touched by that work.

**When reviving the paper later, don't blindly `git merge paper-dev` into `main`** — that would pull in the entire branch's divergent history, including anything unrelated that happened to land on `paper-dev` in the meantime. From this (the `main`) Codespace, pull back only the directory:
```bash
git fetch origin
git checkout paper-dev -- The_Pienza_Papers/
```
This restores just that path from `origin/paper-dev`'s tip into the current `main` working tree, ignoring everything else that branch may have accumulated. Review the diff before committing.

## Housekeeping done alongside this

Two old, stale branches (`origin/dev`, `origin/app-streamlit`) were deleted during this same session — confirmed via `git log`/`git diff` to be badly diverged from current `main` (missing ~146 files that exist in current `main`, containing notebooks long since restructured/renamed). They were not related to this paper-migration decision; they were cleaned up opportunistically because the user was already thinking about branch hygiene. `paper-dev` is a fresh branch off current `main`, unrelated to either of the deleted ones.

## Visual record of the two buttons before removal

Screenshots taken before removal, preserved at `assets_ignored/main_PDF.png`, `assets_ignored/sidebar_PDF.png`, and `assets_ignored/README_PDF.png` (not tracked in git, local-only reference):

- `main_PDF.png` — the "LLM Knowledge Base" / "Interact with the AI" ingestion-panel card on the home page (`main.py`), teal "📥 Download PDF" button.
- `sidebar_PDF.png` — the sidebar footer's `AI Knowledge Base: Download PDF` line, alongside Author/LinkedIn/GitHub/Domain/Stack.
- `README_PDF.png` — `README.md`'s original "Interacting with the Project" section (three-item list: Observatory, LLM-readable white paper with View/Download PDF placeholder links, and the repository) before it was reworked down to two items during this same session's README drift cleanup (TD0022). Useful if the paper's README promotion ever needs to look like this again, or just to see the original wording/structure.

Use these as the visual reference for exact placement/styling when the buttons are restored — don't rebuild them from a vague memory of "a download button somewhere."

## Exactly what changed on `main`

- **Deleted**: `The_Pienza_Papers/` (all contents: `Pienza_Papers_Scientific.pdf`, `Pienza_Papers_Scientific/`, `Pienza_Papers_Executive/`) — full directory, via `git rm -r`.
- **`observatory/components/sidebar.py`**: removed the "Download PDF" link (the `pdf_link` variable and its `<b>AI Knowledge Base:</b>` line inside the footer's `sb-meta-line` block). The `PDF_URL` import was removed from the `from config import ...` line.
- **`observatory/main.py`**: removed the entire "LLM Knowledge Base" / "Interact with the AI" ingestion-panel card (section 7, `<div class="ingestion-panel">...</div>`, the one with the "📥 Download PDF" button) from the home page. The `PDF_URL` import was removed from the `from config import ...` line.
- **`observatory/config.py`**: removed the `PDF_URL` constant entirely (its only two consumers were the two things just removed above).
- Verified live after the change: `main.py` and the sidebar render with no errors, no dead link, no orphaned CSS class references (`ingestion-panel`/`sb-pdf-link` CSS rules in `components/styles.py` were deliberately left in place — harmless unused CSS, cheap to keep for when the buttons come back, not worth a separate cleanup pass right now).
- The `ingestion-panel` card slot on `main.py` (previously the "LLM Knowledge Base" PDF button) was not left empty — it was replaced with a short disclaimer explaining the paper is in progress and not yet published. See the section below for what it says.

## The disclaimer that replaced the PDF card on `main.py`

Rather than leave a gap where the ingestion-panel card used to be, that space now shows a short, honest note that the full research paper is in active development and not yet published — reusing the same `ingestion-panel` CSS class so it still matches the page's visual rhythm. This avoids the page silently looking "unfinished" without explanation, and avoids a dead link. When the paper comes back (see revival steps below), this disclaimer block should be replaced by the restored "Download PDF" card, not left alongside it.

## How to bring it back (future session, when the paper is ready)

1. **Merge the content back**: from `main`, `git merge paper-dev` (or cherry-pick / manually copy `The_Pienza_Papers/` back, whichever is cleaner at that point — `paper-dev` will likely have diverged further with new paper content by then, so a clean merge may not be trivial; review conflicts carefully, this doc doesn't try to predict future drift).
2. **Confirm the file is really back on `main`** at the exact same path GitHub Pages expects: `The_Pienza_Papers/Pienza_Papers_Scientific.pdf` at repo root. If the filename or path changed while working on `paper-dev`, update the URL in step 4 accordingly.
3. **Verify GitHub Pages serves it**: after pushing `main`, curl or browser-check `https://wiseexmachina.github.io/pienza/The_Pienza_Papers/Pienza_Papers_Scientific.pdf` returns `200` with `content-type: application/pdf`. GitHub Pages rebuilds are not instant — allow a minute or two.
4. **Restore `config.py`**: re-add
   ```python
   PDF_URL = "https://wiseexmachina.github.io/pienza/The_Pienza_Papers/Pienza_Papers_Scientific.pdf"
   ```
   (adjust the path if it changed) — with the same "hosted on GitHub Pages, not GCS/local" comment context as before, see `observatory_architecture.md`'s PDF section for the full reasoning.
5. **Restore `components/sidebar.py`**: re-add the `PDF_URL` import and the `pdf_link`/`AI Knowledge Base` line in the footer block — see git history on `main` for the exact removed lines (`git log --all --oneline -- observatory/components/sidebar.py`, find this migration's commit, check the diff) rather than retyping from memory, to avoid re-introducing a since-fixed bug.
6. **Restore `main.py`**: re-add the `PDF_URL` import and the full "LLM Knowledge Base" ingestion-panel section — same approach, pull the exact removed block from this migration's commit diff.
7. **Verify live**: launch the app, click both "Download PDF" buttons, confirm they genuinely download (not just navigate) via the real hosted PDF — same Playwright `expect_download()` standard documented in `observatory_architecture.md`.
8. **Update this doc or delete it** once the paper is back and stable — at that point this migration doc has served its purpose and can either be archived or removed; don't let it linger as stale guidance.
9. **Restore `README.md`'s Top Level tree**: re-add a `├── The_Pienza_Papers/` line (with a one-line comment describing it, e.g. `# LaTeX white paper (Scientific + Executive)`) — it was removed entirely during this migration since it no longer exists on `main`. Also revisit `README.md`'s "Interacting with the Project" section (reworked the same day to drop paper-related links) and its "License & Access" section, whose closing line was simplified to only link The Observatory (`To interact with the project's live results, see [The Observatory](https://pienza.streamlit.app).`) after the old `[Pienza Papers](./The_Pienza_Papers/...)` link broke — restore a paper link there too once it's back.

## What NOT to do in the meantime

- Don't delete `paper-dev` — it's the only place the in-progress paper content lives once it's off `main`.
- Don't leave dead PDF links live on `main`/the Streamlit app — if a future session needs to reference the paper before it's ready to fully ship, link to the GitHub repo's `paper-dev` branch directly rather than resurrecting a broken PDF URL.
- Don't repeat the `origin/dev`/`origin/app-streamlit` mistake of letting a branch silently rot for months without being merged or deleted — if `paper-dev` sits untouched for a long time, that's a signal to revisit this decision, not to ignore it.
