# claude_docs — Index

Pointer index for this directory — one line per file, no content duplicated here. Replaces the former `MEMORY.md`. Read the linked file for the real content; keep entries here to a single line each.

- [tech_debt.md](tech_debt.md) — canonical tech debt backlog, merged from Claude-originated and user-curated lists, Claude has write access
- [incidents_log.md](incidents_log.md) — bugs already diagnosed and fixed, so they're not repeated or re-diagnosed
- [prompt_engineering.md](prompt_engineering.md) — human-Claude interaction conventions (pending cleanup: still has some design-system content mixed in)
- [session_ledger.md](session_ledger.md) — running changelog of work sessions, appended via `/end`
- [files_dictionary.md](files_dictionary.md) — index of scripts/utils in the repo and what each does
- [cloud_run.md](cloud_run.md) — deployment canon: Cloud Run, Docker, domain, cron keep-alive
- [gcs_deploy.md](gcs_deploy.md) — full GCS asset pipeline mechanics: manifest, script usage, per-page status
- [agentic_knowledge.md](agentic_knowledge.md) — RAG/NLP/LLM concept study notes, technical reference
- [rag_workflow.md](rag_workflow.md) — RAG/NLG initiative build doc: architecture, pipeline, troubleshooting, roadmap
- [observatory_architecture.md](observatory_architecture.md) — findings from an architecture pass over `observatory/`'s shared infrastructure
- [nb_refactor_guide.md](nb_refactor_guide.md) — governing precedent for any future `research_core`/`research_full` notebook refactor
- [bigquery.md](bigquery.md) — BigQuery project/dataset/tables/views/join patterns/auth reference
- [cgan_limitation.md](cgan_limitation.md) — known architectural limitation of the cGAN model, root cause, deliberately deferred fix
- [paper_migration.md](paper_migration.md) — dormant reference: why/how The Pienza Papers moved to `paper-dev`, revival playbook if ever needed
- [pdf_export_canon.md](pdf_export_canon.md) — Playwright recipe for converting HTML resumes to 1-page PDFs
- [view_sql_locations.md](view_sql_locations.md) — archive of every "View SQL" expander's query text, for restoring after deprecation
- [mermaid/](mermaid/) — diagram style canon, drift audit history, canon-generation script (3 files)
