---
name: rag-eval-workflow
description: "Registro canonico de las 4 fases del harness de evaluacion de RAG #1 (Project Docs) -- numeros reales por fase y decision de adopcion con justificacion"
metadata:
  type: project
---

# RAG Eval Workflow — Fase 0-3, registro canonico

Documento de referencia sobre "por que cada mejora de retrieval fue o no adoptada"
para RAG #1. Complementa (no duplica) `assets_ignored/claude_docs/rag_eval.md`, que
es el log narrativo en vivo de la sesion de construccion -- este archivo es el
resumen final, tracked en git, por fase. Ver tambien la entrada de metodologia
generica en `agentic_knowledge.md` (2026-08-03).

Harness: `observatory/scripts/rag_eval.py` (retrieval-only) + `rag_eval_judge.py`
(faithfulness + costo real de generacion) + `rag_eval_compare.py` (agrega todo).
Golden dataset: `observatory/scripts/eval_data/rag_golden_dataset.py`, 24 preguntas
(6 por corpus x 4 corpus: Project Docs, The Pienza Papers, Trip Records, Codebase).

Todas las corridas usan las funciones REALES de `pages/_0010_data.py` -- nunca hay
drift entre lo que el harness mide y lo que la app en produccion ejecuta.

---

## Fase 0 — Baseline (top-k=4 cosine similarity)

Config de produccion actual, sin ninguna de las 3 mejoras.

- Hit-rate: 95.8% (23/24)
- Context precision: 0.931
- Context recall: 0.958
- Faithfulness: 4.67/5
- Latencia media: 5301ms
- Costo embed (GCP, query-time): $0.000032
- Costo generacion (Anthropic): $0.115488
- Costo juez (Anthropic): $0.065584

Miss conocido: "How does the sidebar build its navigation links?" (codebase) --
recupera el chunk equivocado, documentado desde Fase 0 original.

**Decision: referencia. No aplica adopcion/no-adopcion, es el punto de comparacion.**

---

## Fase 1 — Query rewriting (reescribir follow-ups ambiguos via Haiku)

`rewrite_query(question, history)` en `_0010_data.py` -- una llamada Haiku que
resuelve pronombres/referencias implicitas ("it", "that") usando el turno anterior,
antes de hacer retrieval. Medido con 4 pares golden follow-up construidos y
verificados a mano (uno por corpus).

- Preguntas standalone (24 originales): identico al baseline (95.8%, 5281ms) --
  esperado, sin historial no hay nada que reescribir.
- Follow-ups CON referencias ambiguas (el escenario real que ataca):
  - Hit-rate SIN rewrite (raw): **25%** (1/4)
  - Hit-rate CON rewrite: **75%** (3/4)
- Costo extra: una llamada Haiku corta (~100 tokens de salida) por turno con historial.

Detalle: 2 de 3 mejoras son claras (codebase: compact_if_needed, claude_docs: bug
del techo de 20K tokens). El unico caso sin mejora (trips, VIP fare efficiency) fallo
en ambos raw y rewritten -- indica un limite de Trip Records/ChromaDB, no una falla
del rewrite en si (consistente con el "RAG Limitation" tooltip ya documentado en
esa tab de la pagina).

**Decision: ADOPTAR.** Unica fase con mejora grande y clara, costo marginal minimo,
sin regresion en ningun otro metric.

---

## Fase 2 — Hybrid search (BM25 + cosine, alpha=0.5)

`retrieve_hybrid(question, df, matrix, alpha=0.5)` -- normaliza min-max los scores
de BM25 (`rank_bm25.BM25Okapi`, tokenizacion `.lower().split()`) y cosine por
separado, blend `alpha*cosine + (1-alpha)*bm25`. Alpha=0.5 es un punto de partida
sin tunear (documentado explicitamente como tal, no una recomendacion).

- Hit-rate: **91.7%** (peor que baseline 95.8%)
- Context precision: 0.826 (peor que baseline 0.931)
- Context recall: 0.917 (peor que baseline 0.958)
- Faithfulness: 4.83/5 (mejor que baseline, aislado)
- Latencia media: 7206ms (+36% vs baseline -- construye indice BM25 + ambas busquedas)
- Costo embed: identico ($0.000032, BM25 es computo local gratis)
- Costo generacion+juez (Anthropic): $0.239482 (mas caro que baseline $0.181072 --
  respuestas mas largas en algunos casos, ej. "How is address anonymization
  implemented?" gen=$0.02243 vs. equivalente baseline)

Detalle: el miss ya conocido de Cognitive Cascade/Gravitational Well (paper) SIGUE
fallando igual. Aparecio un miss NUEVO que baseline no tenia ("How is address
anonymization implemented?", codebase, antes hit rank=1).

**Decision: NO ADOPTAR.** Unica fase que regresiona hit-rate y sube costo. Causas
posibles sin investigar aun (fuera de alcance de esta build): alpha=0.5 puede estar
sobre-pesando BM25 para este corpus, o la tokenizacion naive `.lower().split()`
introduce ruido en vez de señal. Resultado real y honesto, no forzado ni ocultado --
el punto del harness es medir, no asumir que toda tecnica "conocida" ayuda.

---

## Fase 3 — Reranking (cross-encoder local, `cross-encoder/ms-marco-MiniLM-L-6-v2`)

`retrieve_with_rerank(question, df, matrix, wide_k=15)` -- recupera 15 candidatos
via `retrieve()` existente, el cross-encoder (PyTorch, `sentence-transformers`)
puntua cada par (pregunta, chunk) conjuntamente, ordena y trunca a k=4. Real
inferencia local, no una llamada API (arquitectonicamente distinto de un rerank
basado en LLM).

- Hit-rate: 95.8% (empata baseline, mejor que hybrid)
- Context precision: 0.917 (ligeramente menor que baseline 0.931)
- Context recall: 0.958 (empata baseline)
- Faithfulness: 4.71/5 (entre baseline 4.67 y hybrid 4.83)
- Latencia media: **7996ms (+51% vs baseline)** -- inferencia local sobre 15
  candidatos por pregunta
- Costo embed: identico ($0.000032 -- el rerank no llama a ningun API)
- Costo generacion+juez (Anthropic): $0.212889

Detalle: el miss bajo rerank es diferente al de baseline (mismo caso de
"address anonymization" que hybrid tambien fallo). El caso de Cognitive
Cascade/Gravitational Well SI mejoro respecto a hybrid: paso de rank=None a
rank=2 (hit=True) -- demuestra el valor conceptual esperado del rerank aunque
no en posicion ideal.

**Decision: NEUTRAL / NO ADOPTAR AUN.** Empata hit-rate y faithfulness similar al
baseline, pero suma ~51% de latencia y una dependencia nueva (PyTorch +
sentence-transformers, ~80MB de modelo) sin ganancia neta medible en este dataset
de 24 preguntas. Podria valer la pena en un corpus mas grande o con mas ambiguedad
semantica -- no evidenciado con este golden set.

**Matiz importante (desglose por corpus, agregado tras revision del usuario):** el
95.8% global de rerank esconde que INTERCAMBIA misses entre corpora, no los mismos.
Por corpus: **The Pienza Papers pasa de 83.3% (baseline) a 100% con rerank** -- el
cross-encoder SI resuelve el caso conocido de Cognitive-Cascade/Gravitational-Well
(sube de rank=None a rank=2, hit real). Pero introduce un miss NUEVO en Codebase
("How is address anonymization implemented?", hit=True en baseline, hit=False en
rerank) que compensa exactamente esa ganancia en el agregado global. Es decir,
rerank no es "neutral en todos lados" -- es una mejora real y localizada en Papers,
pagada con una regresion real y localizada en Codebase. Ver `_comparison.json` /
`per_corpus_comparison` para el desglose completo por config x corpus, expuesto en
la tab en vivo via un selector de corpus.

---

## Resumen final

| Fase | Adoptar? | Razon en una linea |
|---|---|---|
| Query rewriting | **Si** | 25%->75% en follow-ups ambiguos, costo marginal minimo |
| Hybrid search | No | Regresiona hit-rate (95.8%->91.7%) y sube costo |
| Reranking | Neutral | Empata metrics, +51% latencia, sin ganancia neta clara |

Costo de build por corpus (offline, ya pagado, calculado 2026-08-03):

| Corpus | Tokens | Costo build |
|---|---|---|
| Project Docs | 81,642 | $0.005991 |
| The Pienza Papers | 53,716 | $0.003942 |
| Trip Records | 339,722 | $0.024929 |
| Codebase | 250,150 | $0.018356 |
| **Total** | | **$0.053218** |
