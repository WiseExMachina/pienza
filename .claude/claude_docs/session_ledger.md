# Session Ledger

Bitácora de resúmenes de sesión, más reciente arriba. Cada entrada se agrega
automáticamente al invocar `/end`.

## 2026-07-30 (sesion 2)

- Se corrigio la definicion del candidato #4: es RAG real via serializacion de filas a lenguaje natural (Caso B, no NLG determinista sin retrieval), y se practico ChromaDB como vector DB embebido a proposito (no por necesidad del volumen), para tener experiencia real con la tecnica
- Se construyo el pipeline completo: 4,765 filas de v_ML_Supervised serializadas a oraciones (con ofuscacion de fare/marca Uber), embebidas via Vertex AI, y guardadas en un ChromaDB persistente subido a GCS (gcs_deploy.py extendido con modo de subida de directorio completo, unica excepcion documentada a la regla de sin-subcarpetas)
- Se encontraron y corrigieron varios bugs reales en el camino: valores nan como texto literal, BATCH_SIZE de Vertex AI subido de 5 a 200 tras confirmar empiricamente que el limite real de la API es 250 instancias por request (no 5), y la coleccion de Chroma creada sin especificar distancia coseno (heredaba L2 por defecto en silencio)
- Se integro el corpus nuevo a 0010_RAG_Assistant.py como tercera pestana del stepper (Trip Records), con su propia funcion de retrieval compatible con el resto del pipeline; queda pendiente depurar la lentitud reportada en vivo (logueado en tech_debt_claude.md)
- Sesion de tutoria conceptual extensa en Agentic_Knowledge.md: distincion rate limit vs payload limit, tipos de metrica de distancia en retrieval vectorial (L2 vs coseno vs dot product), y el porque de cuestionar un fix propio en vez de asumirlo correcto para siempre (STAR entrada #10)
- Se guardo una preferencia de colaboracion nueva: reportar avance breve entre llamadas a herramientas durante trabajo multi-paso, sin esperar aprobacion para continuar

## 2026-07-30

- Se definio la taxonomia de 5 candidatos RAG/NLG para el showcase de Neoris (RAG sobre MD, RAG sobre el paper, RAG sobre BQ texto libre, NLG tabular/reverse-RAG, text-to-SQL), documentada con el insight central de no usar RAG a huevo y saber diagnosticar RAG vs NLG segun el problema de negocio
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

- Se construyo el RAG MVP de punta a punta para el showcase de la entrevista de Neoris: script offline rag_build_corpus.py (chunking + embeddings via Vertex AI text-embedding-004 REST) y la nueva pagina 0010_RAG_Assistant.py (retrieval por coseno + generacion via Claude API REST)
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

- Arrancó la prep de entrevista Neoris (AI Engineering, sector siniestros); se creó el roadmap en assets_ignored/claude_docs/neoris_prep.md
- Se guardó contexto en memoria persistente: rol/entrevista, examen de agente de seguros (90, cedula pendiente), y la regla de ensenar-no-solo-ejecutar para esta prep
- Auditoria del ecosistema Claude Code de Pienza: confirmado que solo existian settings.local.json (proyecto) y settings.json (global, effortLevel low); no habia commands, hooks, skills ni subagents propios
- Se formalizaron 6 slash commands reales: hello (prueba de concepto), cloudflared (levanta Streamlit + tunel publico, antes vivia como skill autonomo y se movio a command por control explicito), commit-msg (reglas de commit de CLAUDE.md), start (lee CLAUDE.md), end y debrief (este mismo ledger)
- Se probo el flujo cloudflared end to end: tunel levantado, verificado, y cerrado a peticion
- Se definieron 6 ideas de hooks para implementar manana (sync de memoria, guardrail de gcs_deploy.py, bloqueo de git commit, SessionStart auto-/start, verificacion de anonimizacion, recordatorio de /end), documentadas en neoris_prep.md
