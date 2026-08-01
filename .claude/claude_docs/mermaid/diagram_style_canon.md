---
name: project-diagram-style-canon
description: "Canonical Graphviz recipe/script for research_core flowchart PNGs (A/B diagrams), reverse-engineered to match the external \"Claude Design\" render style"
metadata: 
  node_type: memory
  type: project
  originSessionId: 449bef80-1524-41e7-a936-b2a50cb70eec
  modified: 2026-07-19T01:48:14.832Z
---

Canonical style for research_core notebook flowchart diagrams (the `<notebook>_A.png` /
`_B.png` pipeline images) is now generated locally with Graphviz, not the external "Claude
Design" tool — recipe and reusable script live at
`assets_ignored/claude_docs/diagram_canon_generate.py`.

**Recipe (reverse-engineered from `0407_Clustering_Paper_Streamlit_B.png` pixel sampling):**
- Fill `#d9efed`, stroke `#21918c` (project's canonical teal), text `#123f3c`
- `shape=box, style="rounded,filled"`, `penwidth=2`, `fontname=Helvetica`, `fontsize=19`
- `splines=ortho` for elbow connectors, `arrowhead=vee, arrowsize=0.7`
- Render at `dpi=96` (natural size) — **do not upscale/downscale the whole render**
- Center the natural-size PNG on a transparent 3600px-wide canvas (pad ~20px top/bottom)

**Why the "don't scale" rule matters:** the existing B-style images keep node/font size
CONSTANT in absolute pixels regardless of a diagram's complexity — a simple diagram just
has more empty margin on the same big canvas. My first attempt rendered big then resized
to fill 3600px width, which made everything look oversized compared to B. Confirmed fixed
by the user after re-rendering at natural dpi=96 size and centering instead of scaling.

**How to apply:** [0407 pilot](project_nb_refactor_sprint.md) A-diagram was the first one
converted (2026-07-19), replacing `assets/0407_Clustering_Paper_Streamlit_A.png`. The user
now wants more of the 25 research_core diagram PNGs (see `mermaid_diagrams_for_design.md`
source list — 13 notebooks, 12 with both A+B) migrated to this same locally-generated
canon style. Preserve each diagram's own logic (node/edge structure) — do not blindly copy
another diagram's structure, only the visual style parameters above.
