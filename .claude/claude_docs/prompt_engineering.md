---
name: feedback-conventions
description: "Commit rules, things never to do, and anti-patterns specific to this project"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4c7fa891-5c41-4c2c-a190-97de71bc34d3
---

## Propose before executing on risky/rerun-prone changes — wait for explicit confirmation

Established during the 2026-07-09 latency pass: consult before executing code changes that carry real risk of breaking a working page (Streamlit rerun-model bugs, fragment isolation, anything touching query/cache behavior) — propose the specific fix first, wait for a go, then implement. Don't assume a change is obviously wanted just because it's a known-good pattern elsewhere. If a change doesn't produce measurable/perceptible improvement, revert without ceremony rather than leaving speculative code in.

**Why:** User wants control over each change in this class given the real risk of Streamlit rerun-model bugs (see `incidents_log.md`'s latency-pass entries) breaking pages that were already working.
**How to apply:** On any change with this risk profile, propose the specific fix and wait for a go before editing — this is stricter than the general "report progress" rule below, which assumes permission to proceed; this one does not.

## Report progress briefly between tool calls during multi-step work — don't go silent until the end

When doing multi-step work (several tool calls in a row — file edits, running scripts, background jobs), give a short one-line progress note between steps before moving to the next tool call, instead of going quiet and only reporting back once everything is done. The user explicitly does not need to approve each step to let it proceed — this is about visibility, not permission-gating. Model reference: Anthropic's own guidance on newer Claude models notes they may skip verbal summaries after tool use by default and jump straight to the next action; the fix is the same pattern already followed elsewhere in this project (brief "what I'm doing / what I found" lines between actions), just applied more consistently to avoid feeling like a black box mid-task.

**Why:** User feels like work becomes a black box during long multitasking stretches — several tool calls happen, then a big result lands at the end with no visibility into what happened in between.
**How to apply:** Between tool calls in a multi-step sequence, drop a brief factual note (what just got done / what's next) before continuing — don't wait for explicit approval to proceed, just report and keep moving.

## Open-ended "is this possible?" questions — answer feasibility first, explicitly

When the user asks an open-ended/exploratory question phrased as "se podrá...", "habrá manera de...", "is there a way to...", etc. (even a "longshot" one), lead the response with an explicit yes/no or feasibility read BEFORE diving into implementation — don't just silently start executing the idea. State plainly whether it's doable and roughly how, then proceed (or ask before proceeding, depending on scope).

**Why:** User explicitly called out 2026-07-08 that responses to this style of question jump straight into "lanzarse directo" (building it) without ever confirming feasibility out loud first — they want the feasibility read made explicit, even if the answer ends up being "yes, doing it now."
**How to apply:** For any question shaped like "is X possible / could we do X", start the reply with a one-line explicit feasibility verdict (e.g. "Sí se puede — así:" / "No directamente, pero se puede aproximar con...") before code or explanation.

## Commit message rules (CRITICAL)

Plain ASCII only. No emoji, no quotes, no special characters of any kind — these break shell commit commands. Never reference untracked files (not in git) in commit messages.

Format:
```
type(scope): short summary

- bullet point one
- bullet point two
```

Co-author line: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

**Why:** Special characters in commit messages break shell commit commands in this project's workflow.
**How to apply:** Always validate commit message is pure ASCII before running git commit.

### `type` must be a standard Conventional Commits type

Only use one of these as the `type(scope):` prefix — do not invent new ones (e.g. `copy` is not valid, even for text/copywriting-only changes; use `refactor` for those):

| Type | Use |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting/visual changes with no logic change (CSS, spacing) |
| `refactor` | Restructures code without changing external behavior — also covers copy/text rewrites in this repo |
| `perf` | Performance improvement |
| `test` | Adding/fixing tests |
| `build` | Build system or external dependencies |
| `ci` | CI/CD config |
| `chore` | Maintenance that doesn't fit elsewhere |
| `revert` | Reverts a previous commit |

So far this repo has actually used: `fix`, `style`, `perf`, `refactor`, `chore`.

**Why:** User caught an invented `copy(...)` type (2026-07-10) that isn't part of the Conventional Commits spec and has no precedent in this repo's history.
**How to apply:** Before proposing a commit message, pick the type from this table based on what the change actually is (text-only rewrite -> `refactor`, not a made-up type). If genuinely unsure between two, default to whichever this repo has already used for a similar change (check `git log --oneline`).

## Git commits — NEVER commit on the user's behalf

Never run `git commit` (or any git write command) unless the user explicitly asks. When a commit is needed, provide the commit message and stop — the user runs it themselves in the terminal.

**Why:** User preference — they want full control over when commits happen.
**How to apply:** After any change, if the user says "lets commit" or similar, provide the message only. Do not call git.

**Trap to avoid:** answering a clarifying question (e.g. "single commit or split?" -> "uno solo") is NOT the same as "go ahead, commit now." It only answers the shape of the commit. Wait for an explicit, unambiguous go-ahead in that same turn before running `git commit`. Got called out for this exact mistake on 2026-07-04.

## Things never to do

- Never use `#0e7490` (cyan) — only `#21918c` (teal) for all accents
- Never name the sidebar function `_sidebar()` — must be `build_sidebar()`
- Never use `st.write()` for HTML — use `st.markdown(..., unsafe_allow_html=True)`
- Never add emoji to commit messages
- Never use emoji anywhere — not just commit messages. Explicit blanket instruction from user 2026-07-12 ("Please NEVER USE emoji"), given while stripping emoji out of README.md (headers, repo tree comments, links list all had emoji removed). Applies to all user-facing writing in this project: READMEs, docs, code comments, chat responses — not scoped to any one file.
- Be careful with `9000_SQL_Pipeline_&_Live_Sandbox.py` — the `&` in the filename breaks shell sed loops; always quote the path

## Design system shorthand terms

When the user says **"plain_text"**, they mean this exact semicanon style (established during the design-system homologation pass, see [[project_design_system]]):
```
font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;
```
**No `max-width`** — tested live at multiple widths (including a 27" 5K display) on 2026-07-07; a fixed cap made the text look "stuck" while the bento-grid/map around it stretch fluidly, and letting it run full-width read better in every case tested. Do not add a max-width back in "for readability" — it was deliberately tried and rejected.

**No `!important` (removed 2026-07-08)** — confirmed via Playwright that `!important` inside an inline `style=""` attribute gets silently stripped from the rendered DOM by something in Streamlit's rendering pipeline (see [[project_tech_debt]] for the full writeup); every other declaration in the same string survived, only the `!important` one vanished. An author-controlled inline style already wins on specificity without needing `!important`, so dropping it is free and actually fixes the value showing up correctly instead of silently reverting to the browser/theme default.

**Updated 2026-07-08:** size changed from `15px` to `14px` (with `font-weight:400` now stated explicitly) to match Streamlit's own native tab-label size, confirmed via a Playwright computed-style check (`getComputedStyle` on `button[data-baseweb="tab"]` → `14px`, `400`) rather than guessed. Applied to the 3 instances still on `15px` at the time (main.py "The Mission", 0007 subtitle, 0003 subtitle) — all also had their stray `!important` removed in the same pass. **Not** applied to main.py's nav-card intro line or card descriptions — those were already independently tuned to `13px` by the user in an earlier pass and are treated as deliberate exceptions, not reverted to canon (their `!important` was removed too, for the same DOM-stripping reason).

Used for page subtitles / narrative paragraphs and card descriptions (e.g. main.py "The Mission", the nav-card grid descriptions, 0001/0007 page subtitles). Apply this exact style whenever the user says "make it plain_text" rather than asking for values again.

**Why:** User is establishing named shorthands for recurring styles during the ongoing design-system cleanup, to avoid re-describing the same CSS every time.
**How to apply:** Treat as a living glossary — add new shorthand terms here as the user coins them during the homologation pass.

### `info-mark` (footnote/tooltip trigger button)

New semicanon (established 2026-07-07 on 0001_Foundations.py, replacing the old `†`-style `.fn-mark` superscript for footnote triggers). Not yet propagated to other pages — apply page-by-page as we encounter existing `.fn-mark` footnote triggers, same as `plain_text`.

```css
.info-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 1px solid #21918c;
    background: #ffffff;
    color: #21918c;
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-weight: 700;
    font-size: 9px;
    cursor: default;
    transition: background 0.2s ease;
    vertical-align: middle;
    margin-left: 5px;
}
.info-mark:hover { background: #f0fafa; }
```

Usage: swap `<span class="fn-mark">†</span>` for `<span class="info-mark">i</span>` — keep the surrounding `.fn-wrap`/`.fn-tooltip` structure exactly as-is (only the trigger mark itself changes, not the hover-tooltip mechanism). Went through a size iteration: started at 22px/1.5px border/13px font (too big, "se ven enooormes" per user), settled on 13px circle / 1px border / 9px font as the final discreet size, plus `margin-left:5px` so it doesn't sit flush against the preceding word.

**Why:** User wants a smaller, more refined circular "i" info-button look instead of the dotted-underline `†` superscript, to be rolled out across all pages as we revisit them (not a repo-wide sweep right now).
**How to apply:** When touching a page that still has `.fn-mark` (`†`) footnote triggers, ask/confirm whether to swap them to `info-mark` in that same pass, same as any other semicanon propagation.

### snake_case variable references, inside callouts specifically

New semicanon (established 2026-07-07 on 0001_Foundations.py). Scope: **only inside callout boxes** (the `rgba(33,145,140,0.07)` left-border teal callout pattern) — not a repo-wide rule for every snake_case mention on a page, just this specific context. Not yet propagated elsewhere — apply page-by-page as we encounter snake_case field references inside callouts, same as `plain_text` / `info-mark`.

```css
color:#21918c;font-family:'Courier New',monospace;font-weight:600;
```

Usage: inline `<span style="...">field_name</span>` — no background/pill, no parentheses around it (tested with parentheses first, user removed them: "sin separador visible" reads cleaner since the styling alone already sets it apart from surrounding prose). Do not use a plain `<code>` tag for this — that renders with the browser/Streamlit default monospace-with-grey-background look, not this teal/no-background style.

**Why:** User wants snake_case field names inside callouts to read as a distinct teal reference, not a generic code-block styled chunk, and without punctuation doing the work of setting it apart.
**How to apply:** When a callout box (anywhere) contains a raw snake_case field/column name, ask/confirm whether to apply this exact span style, same as any other semicanon propagation — don't assume it applies outside callouts (e.g. plain body paragraphs) without asking first.

### snake_case / identifier references, in plain body text (outside callouts)

New semicanon (established 2026-07-09 on 0004_Data_Census_(The_Basics).py, `pienza.db`/`pienza_mini` in the header paragraph). Separate from the callout one above — this is the plain-prose equivalent, for a raw identifier/filename/field mentioned in regular paragraph text, not inside a callout box.

```css
color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;
```

Usage: `<code style="...">identifier</code>`. This locks in the *look* of Streamlit's default bare `<code>` tag rendering (green text, `Source Code Pro`, ~0.75rem relative to a 14px paragraph) but makes it explicit inline rather than relying on the default — confirmed elsewhere this session (see [[project_tech_debt]], the Inter-vs-Source-Sans bug) that relying on ambient/inherited/default styling instead of an explicit value is exactly the kind of thing that silently breaks depending on context (e.g. `.step-why code` on the same page already overrides bare `<code>` to teal-on-grey for that specific ancestor, which is a *different* place this could go wrong if left un-styled). The only deviation from the raw default: `background:transparent` — user explicitly liked the existing green-monospace look but wanted the white pill background gone.

**Why:** User confirmed there are now genuinely two distinct semicanons for identifier references — one styled for callouts (teal, no background), one for plain body prose (green, no background) — and wanted the plain-prose one formalized with a fixed value instead of drifting per-instance (which it was doing: bare unstyled `<code>` in some places, ad-hoc teal-pill spans with varying opacity/size in others, see the `0007_Human_vs_AI_Behavioral_Cloning.py` audit from the same day).
**How to apply:** When a raw identifier/field/filename appears in plain paragraph text (not inside a callout), ask/confirm whether to apply this exact style, same as any other semicanon propagation — do not assume it overrides callout instances or vice versa; the two are visually distinct on purpose (teal = "you're inside a highlighted callout", green = "this is regular prose").

## Streamlit dev server: runOnSave was off (fixed), but don't over-claim it as "the" cause of every bug

`observatory/.streamlit/config.toml` now has `[server] runOnSave = true` (added 2026-07-07) — before this, every file save required a manual "Rerun" click in the browser, and at least one real stale-render was confirmed via DevTools (a computed style not matching current source). This is a real, worthwhile fix.

**Important correction:** during the same session, a separate "why does main.py's title look different from Foundations" mystery was never actually resolved — several theories were tried (quote escaping, Streamlit's h1 auto-processing, font loading, runOnSave) without isolating which one, if any, was the true cause. The user explicitly corrected an overconfident claim that `runOnSave` was "the real cause" of that specific bug — it wasn't verified to be. See [[project_design_system]] for the full abandoned-chase writeup.

**Why:** Burned significant time this session conflating a confirmed fix (runOnSave) with an unconfirmed one (the boldness mismatch) — don't repeat that leap.
**How to apply:** `runOnSave` / a hard restart is still the right *first* check when "I changed X but it's not showing up." But when a fix is applied, verify it actually resolved the *specific* symptom (via DevTools computed style, not just assumption) before declaring the root cause found — especially when multiple theories were in flight at once.

## Scope discipline — never touch pages the user didn't name

Never apply changes to any page/file the user hasn't specifically pointed at in that request, even if the same style/pattern issue clearly also exists elsewhere (e.g. a semicanon deviation on another page, a rollout of a "fix everywhere" instinct). Even proposing an option (like a side-by-side comparison) is not license to start editing beyond the file currently in scope.

**Why:** During the design-system homologation pass (2026-07-07), user reacted strongly ("NEVER EVER APPLY CHANGES TO DOWNSTREAM PAGES - UNLESS - I specifically tell you to do so") to the concern that changes might ripple into pages they didn't ask about. They want to review/approve each page individually — see [[project_design_system]] and the page-by-page semicanon process already in place.
**How to apply:** Default to the single file/page named in the current message. If a fix clearly should propagate elsewhere (e.g. a new semicanon value), flag it explicitly and wait for an explicit go-ahead naming those other pages before editing them — do not do it proactively "while I'm in there."

## Anonymization (non-negotiable)

Any page displaying raw offer data must obfuscate:
- `upfront_fare` (and bonus amounts): replace every digit with `#` (per-digit style — replaced an earlier `█` block style, see root `CLAUDE.md`'s anonymization protocol for the canonical current version)
- `pickup_address` / `dropoff_address`: mask street number only, preserve 5-digit zip codes

Use the canonical helpers `_obf_fare()` and `_obf_address()` — do not roll custom versions.
