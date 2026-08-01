---
paths: ["research_core/**/*.ipynb", "research_full/**/*.ipynb"]
description: Mermaid diagram conventions for this project -- style, phase numbering, drift audit history
---

When creating or editing mermaid diagrams (flowcharts, architecture diagrams) anywhere in this repo, read `.claude/claude_docs/mermaid/mermaid_diagrams_for_design.md` in full before starting -- it is the canonical style guide (conventions, phase numbering, tone/word blacklist).

If auditing existing diagrams for drift from that canon, `.claude/claude_docs/mermaid/mermaid_drift_audit_v2.md` documents the last full audit pass -- read it first rather than re-deriving what was already found.

`.claude/claude_docs/mermaid/diagram_canon_generate.py` is the script used to generate canon-compliant diagrams programmatically -- prefer it over hand-writing mermaid syntax from scratch when it fits the task.

`.claude/claude_docs/mermaid/diagram_style_canon.md` documents additional project-specific style canon -- read alongside `mermaid_diagrams_for_design.md`.
