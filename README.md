# The Pienza Papers

## What this actually is

This started as a memory workaround. Early in Project Pienza, work happened across Google's AI interfaces — AI Studio, Gemini — none of which carry context between sessions. Every new chat meant re-explaining the schema, the phase history, the decisions already made. So this document began as exactly that: a single, growing file to paste in at the start of a session so the model (and the human) could pick up where things left off.

It did not stay small. By the time the habit ran its course, it had become a 90+ page LaTeX document — half research log, half white paper — tracking the project's technical evolution phase by phase: data acquisition, feature engineering, exploratory analysis, unsupervised clustering, the supervised classification tournament, and the generative (cGAN) synthesis phase that closed it out.

## Status: not publication-ready, not abandoned

This is not a finished academic paper, which is exactly why it lives here on `paper-dev` and not on `main` — it was never meant to sit in the middle of the project's public-facing portfolio surface. But it isn't being thrown away either. It stays because it's the most complete technical record of *how* Project Pienza actually got built, decision by decision, including the dead ends.

The intent is for this to eventually be revisited — cleaned up, tightened, possibly adapted for an academic audience (a scholarship application, a research portfolio piece, that kind of use case). Until then, it's parked, not polished.

## Who it's for

Anyone. Read it directly, or point your LLM of choice at it and use it as ingestible context to interact with the project's reasoning and history — that was quite literally its original job.

## Why it stopped mattering as much

The paper's whole reason for existing was to solve a memory problem. That problem doesn't really exist anymore. Once the project's day-to-day work moved into Claude Code running in a terminal, agentic workflows took over the job this document used to do by hand — documentation and cross-session memory now persist automatically, without a human manually copy-pasting a growing LaTeX file into a chat window. The paper didn't fail; the tool it was compensating for got replaced.

## What's in here

- **`The_Pienza_Papers/The_Pienza_Papers.pdf`** — the compiled, canonical version. This is the one to actually read.
- **`The_Pienza_Papers/`** — the LaTeX source, flat: `main.tex` as the root document, chapters `00_introduction` through `07_conclusion` plus a glossary and appendix (all pulled in via `\input`), `references.bib`, and a `figures/` subdirectory holding every image.

Rough shape of the narrative, if you want to jump to a phase:

| Phase | Content |
|---|---|
| 1 | Acquisition & ground truth (the two data-collection engines) |
| 2 | Feature engineering (the Bronze/Silver/Gold medallion pipeline) |
| 3 | Exploratory analysis (EPH, market volatility, optimal stopping) |
| 4 | Unsupervised clustering (HDBSCAN vs. hand-drawn geofence polygons) |
| 5 | Supervised classification (the XGBoost tournament, hierarchical cascade) |
| 6 | Generative synthesis (cGAN-based manifold expansion, cloud migration) |
| 7 | Conclusion, glossary, references |

An earlier companion document — a shorter "Executive" summary version — existed briefly alongside this one but was dropped rather than maintained in parallel; this Scientific paper is the single source of truth going forward.

## Building it locally

It compiles clean with a standard TeX Live install (`pdflatex` + `biber`, orchestrated via `latexmk`). From `The_Pienza_Papers/`:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

## The obvious disclaimer

Same as the one printed on page 1: this is an independent academic/portfolio research project, not a commercial or operational product. Source data has been anonymized. Nothing here should be read as an audit of, or claim about, any ride-hailing platform's actual pricing or dispatch logic — the platform is just the environment; the driver is the agent under study.
