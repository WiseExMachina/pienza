---
name: files-dict
description: "Índice de scripts/utils/herramientas creadas en el repo (no cubre paginas de observatory/pages/) — que hace cada archivo, para no perder contexto"
metadata: 
  node_type: memory
  type: project
  originSessionId: e1616b04-98d3-4e90-a4e2-fd2a853bf60e
  modified: 2026-07-28T16:49:22.928Z
---

# Files Dict

Índice corriente de scripts/utils/herramientas creadas en el repo, para no perder contexto de qué existe y qué hace. No cubre páginas de `observatory/pages/` (esas ya se trackean en `project_page_status.md`).

| Archivo | Qué hace |
|---|---|
| `observatory/scripts/gcs_deploy.py` | Sube artefactos (`data/dumped_files/`, `observatory/assets/`) al bucket GCS `pienza-streamlit` según el MANIFEST interno. |
| `observatory/scripts/patch_cloud_run.py` | Aplica patches puntuales (env vars, `cpuIdle`, scaling) al servicio Cloud Run `pienza-observatory` sin pisar la imagen desplegada por el trigger de CI/CD — siempre lee el servicio actual antes de escribir. |
| `observatory/scripts/rag_build_corpus.py` | Script offline (corre en Codespaces, nunca en runtime) del RAG MVP: lee `assets_ignored/claude_docs/*.md` (excluye `STAR_stories.md`, `neoris_prep.md`, `job_tracker.md`), chunkea por encabezado markdown, embebe cada chunk via Vertex AI y escribe `data/dumped_files/rag_corpus_claude_docs.parquet`. |
| `observatory/utils/vertex_embed.py` | Wrapper REST de Vertex AI `text-embedding-004` (`embed_text(text, project_id, credentials)`), sin SDK de `google-cloud-aiplatform`. Compartido entre `rag_build_corpus.py` (precompute) y la pagina `0010_RAG_Assistant.py` (query-time), para que ambos usen el mismo endpoint/modelo. |
| `observatory/utils/latex_strip.py` | Stripper regex de LaTeX -> texto plano (`strip_latex`, `chunk_latex`), no es un parser real, mismo espiritu MVP que el chunker de markdown. Mapea `\section`/`\subsection`/`\subsubsection` a marcadores `##`/`###`/`####` para reusar la logica de chunking por encabezado, conserva solo los `\caption{}` de figuras/tablas, e inlinea `\footnote{}`. |
| `observatory/scripts/rag_build_corpus_paper.py` | Script offline gemelo de `rag_build_corpus.py` pero para el corpus de The Pienza Papers: lee los `.tex` staged en `data/dumped_files/paper_tex/` (extraidos de la rama `paper-dev` via `git show`, sin checkout), los limpia con `latex_strip.py`, embebe via Vertex AI, y escribe `data/dumped_files/rag_corpus_paper.parquet` (mismo schema de 5 columnas mas `source_type`). |
| `observatory/scripts/rag_build_vectordb_trips.py` | Candidato #4 del roadmap RAG/NLG: serializa cada fila de `v_ML_Supervised` (joined con tablas de dimension) a una oracion NL descriptiva (row-to-text, "Caso B" en Agentic_Knowledge.md), la embebe via Vertex AI, y puebla un `chromadb.PersistentClient` local en `data/dumped_files/chroma_trips/` (no parquet+numpy como los otros dos). Aplica ofuscacion canonica de fare/direcciones antes de serializar. |
