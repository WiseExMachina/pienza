# Session Ledger

Bitácora de resúmenes de sesión, más reciente arriba. Cada entrada se agrega
automáticamente al invocar `/end`.

## 2026-08-03

- Se completo el harness de evaluacion incremental de RAG #1: Fase 1 (query rewriting, ADOPTAR — follow-up hit-rate 25%->75%), Fase 2 (hybrid search BM25+cosine, NO adoptar — regresiono el hit-rate global 95.8%->91.7%, resultado negativo real y documentado sin ocultarlo), Fase 3 (reranking con cross-encoder local via PyTorch, neutral en el agregado pero con ganancia real y localizada en The Pienza Papers, compensada por una regresion real y localizada en Codebase)
- Se encontro y arreglo un bug real: rag_eval_judge.py no pasaba corpus_file a retrieve_hybrid(), causando un AttributeError en la primera corrida de --config hybrid; se replico el fix ya presente en rag_eval.py
- Se construyo rag_eval_compare.py (agrega todos los runs JSON en una comparacion por config) y se agrego un desglose per_corpus_comparison tras notar el usuario que la tabla global escondia que The Pienza Papers era el unico corpus con gap real (83.3% vs 95.8% global) — la tab en vivo ahora tiene un selector de corpus, no solo el agregado
- Se agrego la 3ra tab "RAG Eval" a 0010_RAG_Assistant.py (read-only, lee rag_eval_comparison.json desde GCS), subida con permiso explicito del usuario, y verificada en vivo con Playwright (las 3 tabs renderizan sin errores, el stepper y Agentic RAG no se rompieron)
- Se documento la metodologia de evaluacion incremental como concepto reusable en agentic_knowledge.md, mas un rag_eval_workflow.md canonico con la decision de adopcion por fase y su razon
- Se confirmo explicitamente al usuario que Manual Retrieval en produccion sigue en baseline puro (sin las 3 mejoras ni judge call) — el harness completo vive solo en los scripts offline, nunca se conecto a la app en vivo

## 2026-08-01 (sesion 4)

- Se repointeo el corpus de RAG #1 de assets_ignored/claude_docs/ (viejo, untracked) a .claude/claude_docs/ (canonico), y se scrubbeo framing de certificado/entrevista de 6 archivos que alimentan ese corpus, tras detectar que una respuesta del RAG citaba un certificado educativo y framing de busqueda de empleo
- Se encontro y arreglo un bug real de Vertex AI en el camino: limite de 20,000 tokens por request (distinto al limite de 250 instancias ya conocido) — embed_batch() en vertex_embed.py ahora sub-divide internamente respetando ambos limites, beneficia a los 3 scripts que la usan
- Se construyo un GitHub Action nocturno (rebuild-rag-corpus.yml) que rebuildea y sube el corpus de RAG #1 automaticamente, con una excepcion acotada y documentada en CLAUDE.md a la regla de nunca escribir a GCS sin permiso explicito; costo verificado antes de construirlo (~$0.23/mes, despreciable); verificado en vivo end-to-end tras un primer intento fallido por un secret de GitHub guardado vacio
- Se agrego el tab Agentic RAG a 0010: Claude elige el corpus via tool use real (no cosmetico) en vez de que el usuario pique el stepper; se encontraron y arreglaron 2 bugs de CSS/JS al anidar tabs, y un system prompt enganoso que sonaba agentico sin serlo
- Se agrego token count real por corpus en el stepper de Manual Retrieval (calculado del artefacto real, no inventado) y un ttl=86400 a load_corpus() para que una instancia de Cloud Run que lleve dias corriendo recoja el rebuild nocturno sin necesitar cold start
- Se diagnostico una pregunta real de costo de Cloud Run citando el incidente ya documentado (conexiones websocket de pestanas propias dejadas abiertas, no bots) en vez de reinvestigar desde cero

## 2026-08-01 (sesion 3)

- Sesion de tutoria conceptual pura (sin cambios de codigo) tras un ejercicio de repaso que revelo huecos de teoria RAG: temperature vs top-k de sampling (distinto del top-k de retrieval), hybrid search (dense + sparse/BM25), reranking con cross-encoder (por que es caro -- forward pass por candidato -- y el patron retrieve wide/rerank narrow), trade-off chunk size vs k, one-shot vs Agentic RAG, y MCP como capa de plomeria estandarizada para exponer fuentes de datos a un agente
- Se reviso el codigo real de 0010_RAG_Assistant.py y _0010_data.py en vivo para confirmar (no asumir): no hay memoria conversacional (cada pregunta es una llamada aislada a ask_claude()), y el payload de la API no manda temperature (usa el default 1.0, desalineado con el system prompt)
- Se agregaron 4 items nuevos a tech_debt.md: memoria conversacional con gestion de context window/costos (prioridad top del usuario), query rewriting (ligado al anterior), fix de temperature (trivial, un-liner), y se corrigio el skill /knowledge para apuntar a la ruta canonica nueva (.claude/claude_docs/agentic_knowledge.md en vez de la vieja assets_ignored/)
- Se agregaron 2 entradas nuevas a agentic_knowledge.md: reranking (mecanica de cross-encoder y por que retrieve-wide/rerank-narrow) y chunk size vs top-k como trade-off, no variable libre
- Se armo una lista tentativa de todo el trabajo de RAG pendiente para manana (fixes a 0010, documentar #4 en rag_workflow.md, construir candidato #5 Text-to-SQL) mas fin de semana (evaluacion de RAG -- confirmado por el usuario como mandatory, no opcional -- y exploracion de LangChain)
- Charla breve de perspectiva de aprendizaje: validacion de que el conocimiento de primeros principios (no memorizar terminologia) es la barra correcta a la hora de defender tecnicamente el diseno del RAG

## 2026-08-01 (sesion 2)

- Se corrigio la ubicacion del batch size de embeddings (BATCH_SIZE 5 -> 200) tras confirmar empiricamente que el limite real de la API de Vertex AI es 250 instancias por request, no el valor conservador heredado del primer fix de rate limit
- Se realizo una auditoria de concept drift entre el CLAUDE.md/claude_docs viejo y el canon nuevo (post-reorg CLAUDE2): se encontro que dos arboles de documentacion (assets_ignored/claude_docs/ y .claude/claude_docs/) quedaron divergiendo en vivo porque se seguia escribiendo en la ruta vieja sin saber que el canon se habia movido
- Se reconciliaron entradas de tech debt huerfanas hacia el nuevo tech_debt.md canonico, y se decidio dejar assets_ignored/claude_docs/ intacto solo para trazabilidad (gitignoreado, sin mantenimiento activo de aqui en adelante)
- Se encontro y recupero via git history un snippet CSS perdido (fn-below del patron de tooltip) que el reorg dejo como referencia rota a un archivo inexistente; se reinserto directo en observatory/CLAUDE.md
- Se confirmo que la regla de STAR stories proactivas no se perdio en el reorg, se formalizo como comando /star con el mismo disparo proactivo explicito
- Se guardo una preferencia de colaboracion: reportar avance breve entre llamadas a herramientas durante trabajo multi-paso, sin esperar aprobacion para continuar

## 2026-08-01

- Sesión de estudio tecnico: lectura guiada de la documentación oficial de Claude Code (features-overview, tools-reference, prompting best practices) con quiz de multiple choice intercalado (20/20 en la ronda final sobre prompt engineering)
- Refactor completo de CLAUDE.md: split en CLAUDE.md raíz (131 líneas, navegacional) + observatory/CLAUDE.md nuevo (67 líneas) + .claude/claude_docs/ (21 archivos) + .claude/rules/mermaid-diagrams.md, todo construido primero en un sandbox (CLAUDE2/) y promovido solo tras un diff-check exhaustivo contra el original
- Reorganización completa de claude_docs: 25 archivos originales clasificados uno por uno (movidos, fusionados, o occam'd con razón documentada), incluyendo dos misses reales atrapados en la verificación final (project_roadmap.md y placeholder.md nunca procesados)
- tech_debt.md unificado: se fusionaron tech_debt_claude.md (Claude) y project_tech_debt.md (usuario, TD0001+) en un solo doc canónico con Claude teniendo ahora permiso de escritura, historias completas preservadas
- Separación de contenido personal: nuevo assets_ignored/interview_prep/ para STAR_stories.md y material de busqueda de empleo, manteniéndolo fuera de .claude/claude_docs/ que ahora es público/tracked
- README.md actualizado con una sección técnica real sobre el uso de Claude Code en el proyecto, reemplazando el placeholder puesto antes del sprint
- Nuevos comandos creados: /acknowledge, /plain, /brainstorming, /star

## 2026-07-30 (sesion 2)

- Se corrigio la definicion del candidato #4: es RAG real via serializacion de filas a lenguaje natural (Caso B, no NLG determinista sin retrieval), y se practico ChromaDB como vector DB embebido a proposito (no por necesidad del volumen), para tener experiencia real con la tecnica
- Se construyo el pipeline completo: 4,765 filas de v_ML_Supervised serializadas a oraciones (con ofuscacion de fare/marca Uber), embebidas via Vertex AI, y guardadas en un ChromaDB persistente subido a GCS (gcs_deploy.py extendido con modo de subida de directorio completo, unica excepcion documentada a la regla de sin-subcarpetas)
- Se encontraron y corrigieron varios bugs reales en el camino: valores nan como texto literal, BATCH_SIZE de Vertex AI subido de 5 a 200 tras confirmar empiricamente que el limite real de la API es 250 instancias por request (no 5), y la coleccion de Chroma creada sin especificar distancia coseno (heredaba L2 por defecto en silencio)
- Se integro el corpus nuevo a 0010_RAG_Assistant.py como tercera pestana del stepper (Trip Records), con su propia funcion de retrieval compatible con el resto del pipeline; queda pendiente depurar la lentitud reportada en vivo (logueado en tech_debt_claude.md)
- Sesion de tutoria conceptual extensa en Agentic_Knowledge.md: distincion rate limit vs payload limit, tipos de metrica de distancia en retrieval vectorial (L2 vs coseno vs dot product), y el porque de cuestionar un fix propio en vez de asumirlo correcto para siempre (STAR entrada #10)
- Se guardo una preferencia de colaboracion nueva: reportar avance breve entre llamadas a herramientas durante trabajo multi-paso, sin esperar aprobacion para continuar

## 2026-07-30

- Se definio la taxonomia de 5 candidatos RAG/NLG para el proyecto (RAG sobre MD, RAG sobre el paper, RAG sobre BQ texto libre, NLG tabular/reverse-RAG, text-to-SQL), documentada con el insight central de no usar RAG a huevo y saber diagnosticar RAG vs NLG segun el problema de negocio
- Se construyo el candidato #2: extraccion de los .tex del paper desde la rama paper-dev via git show (sin checkout), stripper de LaTeX nuevo (latex_strip.py), embeddings via Vertex AI, subida a GCS con gcs_deploy.py mejorado para saltar archivos sin cambios (comparacion MD5)
- Se agrego un selector de corpus tipo stepper horizontal en 0010_RAG_Assistant.py (mismo patron visual que 0008), y luego se refactorizo la pagina para cumplir la regla de separacion View/Model del Observatory, creando _0010_data.py
- Se reescribio rag_workflow.md dos veces por feedback directo: primero para dejar clara la mecanica de inferencia en vivo (Vertex AI solo embebe, Claude solo genera, GCS se toca una vez por sesion no por pregunta), luego con estructura fija Inputs/Scripts/Outputs/Deploy a GCS/Inferencia por cada candidato
- Se corrigio un ID de modelo mal formado (claude-haiku-4-5-20251001 -> claude-haiku-4-5) en codigo y documentacion
- Sesion larga de tutoria conceptual documentada en Agentic_Knowledge.md: vector DB vs relacional, cuando usar RAG vs SQL, el mapa de 4 etapas de un pipeline RAG (chunking, query rewriting, retrieval/hybrid search, reranking, generacion), formula real de similitud coseno, Parent Document Retriever, filtrado por metadatos, LangChain como orquestacion (no alternativa a un modelo), y primer vistazo a agentes multipaso y MCP

## 2026-07-29 (sesion 2)

- Se reparo el toolchain de LaTeX local para The Pienza Papers (TeX Live, biber, latexmk desde cero) y se diagnosticaron varios bugs reales: lmodern pisando las fuentes CrimsonPro/Inter/Inconsolata por orden de carga, opcion defaultmono no soportada por la version local de inconsolata, conflicto underscore+hyperref en labels con guion bajo, y underscores sin escapar en texttt que rompian la compilacion
- Se limpio el contenido: se elimino el apendice duplicado de Fase 5, se renombro una label duplicada, se borro el paper companero Executive (sin mantener), se quitaron placeholders/links muertos/una seccion vacia, y se convirtieron las 75 figuras a escala de grises
- El usuario decidio deprecar el paper (no terminarlo) pero conservarlo como registro tecnico del proyecto; se escribio un README explicando el origen (workaround de memoria para AI Studio/Gemini que crecio a 90+ paginas) y el estado actual, movido a la raiz del repo en la rama paper-dev
- Se reestructuro el directorio: todos los .tex/.bib subieron a The_Pienza_Papers/ raiz, las imagenes a figures/, se configuro .latexmkrc para que el build salga a build/ sin ensuciar el source; se reemplazo el PDF canonico viejo por uno nuevo (The_Pienza_Papers.pdf) compilado con todos los fixes
- Se instalo la extension LaTeX Workshop en VSCode y se resolvio confusion recurrente sobre por que The_Pienza_Papers/ aparece como untracked al volver a main (son artefactos de build gitignored en paper-dev pero invisibles para el gitignore de main, no perdida de datos)
- Se borro .CV.MD (desordenado, nunca trackeado) tras revisar el resume real ya pulido; charla breve sobre estrategia de busqueda de empleo

## 2026-07-29

- Se construyo el RAG MVP de punta a punta: script offline rag_build_corpus.py (chunking + embeddings via Vertex AI text-embedding-004 REST) y la nueva pagina 0010_RAG_Assistant.py (retrieval por coseno + generacion via Claude API REST)
- Se resolvieron tres bugs de infraestructura en cadena: billing pendiente (403 dunning), rol IAM no encontrable tras el rebrand de Vertex AI a Agent Platform, y rate limit 429 arreglado con batching + retry/backoff
- Se subio el parquet del corpus a GCS (pienza-streamlit) y se inyecto ANTHROPIC_API_KEY a Cloud Run via patch_cloud_run.py sin tocar la imagen desplegada
- Se documento todo el flujo en rag_workflow.md (arquitectura, troubleshooting, seccion de como leer el parquet) y se agrego una historia STAR nueva
- Se agrego un panel "A Look Ahead: AI Engineering" en main.py, deliberadamente separado del grid secuencial de 9 modulos, con icono nuevo y CSS para que el boton Explore Module se vea contenido y centrado
- Cambios pendientes de commit al cierre de la sesion (mensaje ya redactado, no ejecutado): main.py, styles.py, _main_data.py

## 2026-07-28 (sesion 2)

- Se pregunto si existia otro command de arranque ademas de /start; se aclaro que /start solo lee CLAUDE.md y /debrief muestra el ledger, son dos pasos separados
- Se creo el septimo command: /catchup, resume en que quedamos usando solo el contexto vivo de la conversacion actual, sin leer archivos
- Se probo /catchup (invocado de forma jocosa, sin slash nativo) y respondio correctamente el resumen en vivo
- Pidieron un hook para que el loop de keep-alive (.keep_alive_dummy.txt cada 180s) corra solo al abrir el Codespace; se identifico que la ruta correcta seria devcontainer.json postStartCommand, pero eso fuerza un rebuild que borra la memoria persistente de Claude
- Se opto por la alternativa sin rebuild: se agrego el loop a ~/.bashrc con guard anti-duplicados (pgrep) y cd explicito a /workspaces/pienza; se aclaro que esto es un hook de shell, no un hook de Claude Code ni de devcontainer
- Quedan pendientes para manana los 6 hooks reales de Claude Code definidos ayer (sync de memoria, guardrail de gcs_deploy.py, bloqueo de git commit, SessionStart auto-/start, verificacion de anonimizacion, recordatorio de /end)

## 2026-07-28

- Arrancó la prep tecnica del proyecto (AI Engineering, sector siniestros); se creó el roadmap en assets_ignored/claude_docs/neoris_prep.md
- Se guardó contexto en memoria persistente: examen de agente de seguros (90, cedula pendiente), y la regla de ensenar-no-solo-ejecutar para esta prep
- Auditoria del ecosistema Claude Code de Pienza: confirmado que solo existian settings.local.json (proyecto) y settings.json (global, effortLevel low); no habia commands, hooks, skills ni subagents propios
- Se formalizaron 6 slash commands reales: hello (prueba de concepto), cloudflared (levanta Streamlit + tunel publico, antes vivia como skill autonomo y se movio a command por control explicito), commit-msg (reglas de commit de CLAUDE.md), start (lee CLAUDE.md), end y debrief (este mismo ledger)
- Se probo el flujo cloudflared end to end: tunel levantado, verificado, y cerrado a peticion
- Se definieron 6 ideas de hooks para implementar manana (sync de memoria, guardrail de gcs_deploy.py, bloqueo de git commit, SessionStart auto-/start, verificacion de anonimizacion, recordatorio de /end), documentadas en neoris_prep.md
