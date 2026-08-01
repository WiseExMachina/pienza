# Agentic Knowledge — SSoT de estudio (RAG, NLP, despliegue de LLMs)

Documento personal de estudio, no atado a las decisiones especificas de Project Pienza.
Cada entrada es un concepto explicado en el momento en que surgio en conversacion, para
llevarselo de tarea. No es parte del sistema de memoria/mirror de Pienza (como
STAR_stories.md, vive solo aqui).

Formato por entrada: fecha, el concepto, una explicacion clara, y de donde salio
(que parte del proyecto la disparo), para que tenga contexto real y no sea un
glosario abstracto.

---

## 2026-07-30 — Managed embedding API vs. self-hosted embedding model

Cuando necesitas generar embeddings (vectores numericos que representan el
significado semantico de un texto, usados para busqueda por similitud en RAG),
hay dos caminos arquitectonicos:

1. **API gestionada** (ej. Vertex AI `text-embedding-004` via REST): el modelo
   corre en la infraestructura del proveedor. Tu app solo hace un POST y recibe
   el vector de vuelta. Cero pesos de modelo que descargar/versionar, cero
   dependencias pesadas (no necesitas `torch`, `transformers`, etc.), pero
   agrega latencia de red por cada llamada y depende de que el servicio externo
   este disponible.
2. **Modelo local/self-hosted** (ej. `sentence-transformers` corriendo dentro
   de tu propio contenedor): no depende de red externa en tiempo de inferencia,
   pero tienes que cargar un archivo de pesos real (comunmente `.pth`/`.safetensors`
   para PyTorch, o `.pkl`/`.joblib` para modelos sklearn clasicos) en cada cold
   start, aumentar el tamano de tu imagen Docker, e instalar las librerias del
   framework de ML.

No hay una respuesta universal correcta — es un trade-off real de latencia de
red vs. peso de imagen/dependencias vs. control total sobre el modelo. La
decision correcta depende del volumen de requests, si tu infra ya tiene auth
gestionada con el proveedor cloud, y si el tamano del contenedor importa (ej.
Cloud Run cobra por tiempo de cold start).

**Contexto:** Se disparo al justificar por que el RAG de Pienza usa Vertex AI
REST para embeddings en vez de un modelo local — comparando contra un caso real
del mismo repo (miniBabel, pagina 0008, que si carga un `.pth` de PyTorch desde
GCS en cada cold start). Ver STAR_stories.md entrada #9 para el caso completo.

---

## 2026-07-30 — Base de datos relacional vs. base de datos vectorial

**Relacional** (BigQuery, Postgres): filas/columnas, busqueda por coincidencia
exacta o rangos (`WHERE fare > 50`), via indices B-tree/hash. No entiende
significado — busca el string literal, no el concepto.

**Vectorial** (FAISS, ChromaDB, Pinecone, pgvector): almacena embeddings
(vectores de cientos de dimensiones que representan significado semantico) y
busca por **cercania geometrica** (similitud coseno / distancia euclidiana) en
vez de coincidencia exacta. Esto permite recuperar texto relevante aunque
ninguna palabra literal coincida con la pregunta — el motor entiende que hablan
del mismo tema.

**Por que un RAG con corpus chico no necesita un vector DB dedicado:** los
vector DBs existen para escalar busqueda aproximada (ANN — Approximate Nearest
Neighbor) sobre millones de vectores, evitando comparar contra todos uno por
uno. Con unos cientos de chunks, comparar "a fuerza bruta" (multiplicacion de
matrices + coseno en numpy, sin indice) es instantaneo — agregar FAISS/ChromaDB
ahi seria complejidad sin beneficio medible. La eleccion correcta depende de la
escala, no es "vector DB siempre mejor que numpy".

**Contexto:** Se disparo al pedir explicar la linea "No vector DB" en
rag_workflow.md (§2, decisiones de arquitectura) — el RAG de Pienza usa numpy
in-memory sobre ~380 chunks en vez de un vector DB dedicado.

---

## 2026-07-30 — Cuando usar RAG (vector search) vs. SQL directo, por primeros principios

El criterio no es "texto vs. numeros" en si mismo, sino **donde vive la
incertidumbre de la pregunta**:

- **RAG (busqueda vectorial) resuelve "no se exactamente que buscar."** Una
  pregunta como "como funciona el pipeline de GCS" no tiene un `WHERE` que la
  capture — no hay una llave exacta contra la cual filtrar. Hay que comparar el
  *significado* de la pregunta contra el *significado* de muchos fragmentos de
  texto candidatos, y quedarse con los mas parecidos (similitud vectorial). El
  costo de embeddings + busqueda solo se justifica cuando existe esa
  incertidumbre semantica real — mismo concepto, mil formas distintas de decirlo.

- **SQL resuelve "se exactamente que quiero, dime donde esta."** `WHERE fare >
  50 AND product = 'x'` es una condicion booleana exacta sobre datos
  estructurados — no hay significado que interpretar en un numero, coincide o
  no coincide. Ahi la busqueda por similitud no aporta nada: no existe una
  version util de "que tan parecido es 154 a caro", eso ya lo resuelve un
  operador `>`.

**Regla practica:** si la pregunta requiere *interpretar significado* para
saber que dato es relevante -> RAG. Si la pregunta ya se puede expresar como
condicion exacta/estructurada -> SQL directo. Texto libre (comentarios, notas)
cae en el primer caso porque el mismo concepto se puede decir de mil formas.
Datos numericos/categoricos puros caen en el segundo caso porque ya son
estructurados por definicion — el filtro exacto ES la busqueda. Meter un vector
DB en el segundo caso es pagar el costo de resolver una ambiguedad semantica
que nunca existio.

**Contexto:** Se disparo al distinguir por que el RAG #1 planeado (texto libre
de BigQuery, `special_note_raw` etc.) tiene sentido con vector DB, mientras que
el "reverse-RAG" descartado (tabular->NL, datos numericos puros como fares y
timestamps) nunca necesito uno — ese problema era de narracion/generacion
determinista sobre filas ya conocidas via SQL, no de busqueda semantica.

---

## 2026-07-30 — Text-to-SQL (NL2SQL): interactuar con una DB relacional en lenguaje natural

Ni RAG ni "no-RAG" — es un patron distinto con nombre propio. Aplica cuando el
usuario quiere hacer preguntas deterministas ("donde hubo mas viajes Black?")
sin saber SQL, sobre datos ya estructurados.

**Por que no es RAG:** la pregunta no requiere buscar entre candidatos por
significado — requiere **traducir la pregunta a una consulta exacta y
ejecutarla**. El LLM no recupera fragmentos parecidos ni responde desde su
propio conocimiento; genera codigo (SQL) que el motor de la base de datos
ejecuta de forma determinista. La respuesta sale de la base de datos real, el
LLM solo traduce NL -> SQL (y opcionalmente narra el resultado de vuelta a NL).

**Como funciona:**
1. Se le da al LLM el schema de las tablas (nombres, tipos, relaciones) como
   contexto en el prompt — nunca se le deja adivinar nombres de columna.
2. Usuario pregunta en NL: "donde hubo mas viajes Black?"
3. El LLM genera el SQL: `SELECT pickup_zone, COUNT(*) FROM ... WHERE
   product_category = 'Black' GROUP BY pickup_zone ORDER BY COUNT(*) DESC`
4. El codigo de la app **ejecuta** ese SQL de verdad contra la DB (el LLM no
   inventa el resultado).
5. Opcional: se le devuelve el resultado tabular al LLM para que lo narre en
   lenguaje natural.

**Riesgos reales a manejar:**
- Alucinacion de nombres de columna/tabla que no existen -> se mitiga dandole
  el schema exacto, nunca dejandolo adivinar.
- Si se conecta a una DB de escritura, un SQL mal generado podria ser
  destructivo -> en produccion se ejecuta en modo solo-lectura, con un usuario
  de DB con permisos restringidos.
- Preguntas ambiguas pueden generar SQL valido que responde algo distinto a lo
  que el usuario queria -> a veces conviene mostrarle el SQL generado al
  usuario antes de ejecutar, para que confirme.

**Contexto:** Se disparo al preguntar como interactuar con una DB relacional
via chat sin saber SQL. Se conecta con el SQL Sandbox ya existente en la pagina
0201/0004 del Observatory (donde hoy el usuario escribe el SQL a mano) — un
upgrade natural seria generar ese SQL con un LLM en vez de que el usuario lo
escriba.

---

## 2026-07-30 — Tabular -> NL: cuando SI es RAG y cuando NO (correccion sobre entrada previa)

El "reverse-RAG" (tabular -> texto natural) no es un solo patron — son DOS casos
que se ven parecidos pero resuelven problemas distintos:

**Caso A — narrar una fila ya conocida (NO es RAG):** ya sabes exactamente que
fila quieres (`WHERE offer_id = 123`, filtro exacto via SQL), y solo la
traduces a texto legible ("este viaje Black costo $X, duro Y minutos"). No hay
retrieval — vas de una fila conocida a una oracion. Generacion determinista
pura, sin ambiguedad que resolver, sin embeddings.

**Caso B — habilitar busqueda semantica sobre datos estructurados (SI es RAG):**
si conviertes CADA fila de una tabla a una oracion en NL ("viaje Black, tarifa
alta, zona Polanco, hora pico...") y luego embebes esas oraciones, construyes
un corpus de texto real — y ahi si aplica RAG genuino: "encuentrame viajes
parecidos a uno donde el conductor espero mucho cerca del aeropuerto" es una
busqueda semantica real sobre atributos que originalmente eran solo
numeros/categorias no comparables por `WHERE`, porque "parecido" no es una
condicion exacta. Esta tecnica tiene nombre: **serializacion de filas para
retrieval** (row-to-text serialization) — se usa quando quieres busqueda
"difusa" sobre datos que de otra forma solo admitirian filtros exactos.

**El criterio correcto no es "tabular vs. texto libre"**, es: la pregunta que
se quiere responder es "dame esta fila exacta" (Caso A, generacion sin
retrieval) o "encuentrame filas parecidas a una descripcion" (Caso B, RAG real
sobre texto serializado)? Ambos convierten tabular a NL, pero solo el Caso B
tiene una etapa de busqueda por significado que justifique el nombre RAG.

**Contexto:** El usuario señalo correctamente que la entrada anterior
("reverse-RAG no es RAG") solo cubria el Caso A, colapsando dos casos
distintos en uno. Ejemplo de por que "no usar RAG a huevo" y saber discernir
esto es, en palabras del usuario, "la ultima frontera de seniority" — la
distincion no es sobre la tecnologia, es sobre que problema de negocio se
esta resolviendo.

---

## 2026-07-30 — Roadmap: lo que falta mas alla del retrieval basico (reranking, context window, hallucinations, evaluacion)

Lo ya cubierto (base solida): embeddings, similitud vectorial vs. busqueda
exacta, chunking, criterio de cuando RAG es la herramienta correcta vs.
sobre-ingenieria (SQL directo, generacion determinista). Lo que sigue es
"produccion real" encima de esa base — cuatro areas:

**1. Reranking.** El retrieval por coseno (embeddings precomputados) es rapido
pero impreciso — un vector comprime todo el significado en un solo punto,
perdiendo matices. Patron de dos etapas: recuperas de mas (ej. top-20 por
coseno, barato) y luego pasas esos candidatos por un **reranker** — modelo mas
pesado que compara la pregunta contra cada candidato directamente (no via
vectores precomputados) y reordena por relevancia real. Reduces a top-k despues
del rerank, no antes.

**2. Context window control.** Cuanto y como ordenas el contexto en el prompt
final importa tanto como cual recuperas. Problemas reales: (a) "lost in the
middle" — los LLMs prestan menos atencion a informacion en medio de un
contexto largo que al principio/final, el orden de los chunks importa; (b)
presupuesto de tokens — mas contexto no es gratis (costo + latencia), y a veces
empeora la respuesta si mete chunks irrelevantes que distraen al modelo; (c)
compresion/resumen de chunks largos antes de meterlos al prompt.

**3. Hallucinations (se mitigan, no se eliminan).** Capas de mitigacion: (a)
prompt explicito de "responde SOLO con la informacion dada, di no se si no
esta"; (b) citar la fuente exacta de cada afirmacion; (c) grounding score —
medir que tan respaldada esta cada oracion de la respuesta por el contexto
recuperado; (d) el caso mas dificil: el modelo alucina DENTRO del contexto
correcto (mezcla mal dos chunks reales) — eso ya no lo resuelve el retrieval,
es un problema del generador.

**4. Evaluacion de RAG.** No basta "probe unas preguntas y se veia bien" — hay
metricas especificas, tipicamente via un framework como RAGAS: **faithfulness**
(la respuesta se sostiene en el contexto recuperado, o invento algo?),
**answer relevancy** (la respuesta contesta lo que se pregunto?), **context
precision/recall** (los chunks recuperados eran los correctos, y no falto
ninguno relevante?). Se evalua retrieval y generacion por separado porque
pueden fallar independientemente — retrieval perfecto + generacion que
alucina, o retrieval malo que ni con el mejor generador se salva.

**Contexto:** Se disparo al pedir un mapa honesto de que falta por aprender de
RAG mas alla de lo ya construido en Pienza (retrieval basico via coseno,
citacion de fuentes, prompt de grounding), pensando en preguntas de un curso o
entrevista tecnica sobre RAG.

---

## 2026-07-30 — Correccion: el reverse-RAG (#4) SI se va a construir, y no es sobre-ingenieria [SUPERADA, ver nota]

Entrada previa dejaba #4 (tabular -> NL narrado) como diseno verbal-only por
"sobre-ingenieria a este volumen". El usuario corrigio el marco: el motivo real
de construirlo no es el volumen de datos de Pienza, es un **insight de
posicionamiento para la entrevista** — muchas empresas (incluida la que aplica
a Neoris) asumen que su problema es "RAG" cuando en realidad necesitan **NLG
sobre datos estructurados** (ver entrada de reportes de siniestros mas arriba),
o ambos combinados. Saber diagnosticar eso — que la empresa pide la herramienta
equivocada — es justo el insight de seniority que se quiere demostrar, y
requiere tener el modulo construido para poder hablar de el con evidencia, no
solo describirlo.

**Contexto:** Se disparo al planear construir los 5 candidatos de RAG/NLG del
proyecto (corpus MD, corpus paper, BQ texto libre via RAG, NLG tabular, y
text-to-SQL) en un sprint de 2 dias, con evaluacion (hallucinations, etc.) el
fin de semana.

**Nota de superacion (2026-07-30, mas tarde el mismo dia):** esta entrada
describia el "#4" bajo la definicion equivocada (narracion determinista de UNA
fila, "Caso A", sin retrieval). El usuario aclaro que #4 siempre significo
"Caso B" — RAG real sobre N filas serializadas a lenguaje natural y embebidas
(ver la entrada "Tabular -> NL: cuando SI es RAG" mas arriba). El Caso A
determinista se enterro explicitamente, no se construye — ver rag_workflow.md
§0, nota de "graveyard" bajo la tabla de candidatos, para el registro completo
de esta correccion.

---

## 2026-07-30 — La similitud coseno no se fine-tunea, pero es el paso donde mas falla el RAG

La similitud coseno (`(A . B) / (|A| x |B|)`) es una formula fija, sin
parametros que entrenar — no tiene pesos, no aprende, siempre hace lo mismo
dado el mismo par de vectores. Eso NO es lo que se ajusta cuando se dice
"mejorar el retrieval". Lo que si se puede ajustar es lo que entra a la
formula y como se usa el resultado:

1. **El modelo de embeddings** (esto si se puede fine-tunear, con pares de
   contraste especificos del dominio). Si los vectores no capturan bien la
   jerga de un dominio (ej. terminos de seguros), la similitud coseno entre
   ellos es matematicamente correcta pero semanticamente inutil.
2. **k** (cuantos chunks recuperar) — muy chico deja fuera contexto real, muy
   grande diluye la respuesta con ruido irrelevante.
3. **Reranking** — existe justo porque este paso es aproximado. Retrieval
   barato por coseno trae candidatos gruesos; el reranker corrige despues con
   mas precision (ver entrada de reranking mas arriba).
4. **Tamano/overlap del chunking** — si una respuesta queda partida entre dos
   chunks, ninguno solo tiene similitud suficiente para ganar el top-k, aunque
   juntos si contendrian la respuesta.

**El fallo clasico de este paso especifico:** similitud alta no es lo mismo
que relevancia real. Dos textos pueden compartir vocabulario (coseno alto) sin
ser relevantes entre si — o una pregunta y su negacion exacta pueden salir con
similitud alta porque usan casi las mismas palabras. El embedding captura "de
que tema hablan las palabras", no necesariamente "responde esto a aquello".
Por eso, cuando una respuesta de RAG sale mal, el primer sospechoso casi
siempre es retrieval, no generacion — si se le dio al LLM el chunk
equivocado, no importa que tan bueno sea el modelo generador, va a alucinar o
responder generico con ese contexto malo.

**Contexto:** Se disparo al preguntar si la operacion de similitud coseno
usada en el RAG de Pienza (ver rag_workflow.md §1, paso 2 del flujo de
inferencia) se podia fine-tunear, y si es ahi donde estan las fallas del
sistema.

---

## 2026-07-30 — La formula real de similitud coseno (no es determinante, es norma)

```
cos(theta) = (A . B) / (||A|| x ||B||)
```

- **A . B** (producto punto): se multiplica cada componente de A por el
  componente correspondiente de B, y se suma todo. Con vectores de 768
  dimensiones (como los de `text-embedding-004`), son 768 multiplicaciones
  sumadas.
- **||A||** (norma o magnitud de A, NO determinante — el determinante es un
  concepto distinto, aplica a matrices cuadradas, no a vectores): la
  "longitud" del vector — raiz cuadrada de la suma de cada componente al
  cuadrado. Lo mismo para ||B||.

**Por que se divide entre las normas:** el producto punto solo, sin
normalizar, seria mas grande simplemente si los vectores son mas "largos"
(mas magnitud), no necesariamente mas parecidos en direccion. Dividir entre
las normas cancela el efecto de tamano y deja solo el angulo entre los
vectores — literalmente el coseno de ese angulo. Resultado entre -1 y 1: 1 =
misma direccion (maxima similitud semantica), 0 = perpendiculares (sin
relacion), -1 = direcciones opuestas.

En codigo (numpy, vectorizado contra todo el corpus a la vez):
```python
sims = matrix @ query_vec / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(query_vec) + 1e-10)
```
`matrix @ query_vec` es el producto punto del vector de la pregunta contra
TODOS los vectores del corpus en una sola operacion matriz-vector (no un loop
por chunk). El `+ 1e-10` evita division entre cero si algun vector fuera todo
ceros.

**Contexto:** Refresco de la formula real tras confundir "norma" con
"determinante" al repasar el paso de retrieval del RAG (rag_workflow.md §1,
paso 2). Complementa la entrada anterior sobre por que este paso, aunque es
matematica fija sin nada que entrenar, es el sospechoso mas comun cuando una
respuesta de RAG sale mal.

---

## 2026-07-30 — El pipeline RAG completo: que se ajusta en cada etapa (mapa de 4 etapas)

Un pipeline RAG "generico" tiene 4 etapas reales, no solo "corpus + retrieval +
generacion". Cada tecnica popular (reranking, hybrid search, query rewriting)
tiene un lugar especifico en este mapa, no son sinonimos entre si:

**Etapa 0 — Preparacion del corpus.** Chunking (tamano, overlap, por donde se
corta), que modelo de embeddings se usa, que metadata se guarda junto al
vector. Determina la calidad de lo que existe para ser encontrado.

**Etapa 1 — Entendimiento de la pregunta (query rewriting).** Antes de embeber
la pregunta del usuario tal cual la escribio, un LLM la puede reescribir o
expandir primero: corregir ambiguedad, generar varias formulaciones
alternativas de la misma pregunta, inferir contexto implicito. Por que
importa: si el usuario pregunta mal o vago, el vector de su pregunta va a
estar mal apuntado sin importar que tan bueno sea el corpus — el problema no
siempre esta en el corpus, a veces esta en la pregunta misma.

**Etapa 2 — Retrieval (la matematica: similitud coseno).** La formula en si
nunca falla (ver entrada anterior), pero aqui tambien vive **hybrid search**:
combinar busqueda semantica (embeddings) con busqueda por keyword tradicional
(BM25/TF-IDF), y fusionar los dos rankings. Por que: los embeddings son
buenos para "significado" pero malos para cosas exactas — un codigo de
poliza, un ID, un termino tecnico exacto — la busqueda semantica los difumina
como "mas o menos parecidos" cuando deberian ser coincidencia exacta o nada.
Hybrid search cubre ese punto ciego combinando ambos mecanismos.

**Etapa 3 — Reranking.** Despues de tener candidatos (de retrieval puro o
hibrido), un modelo mas pesado los reordena por relevancia real, no por
aproximacion vectorial (ver entrada de reranking mas arriba en este doc).

**Etapa 4 — Generacion.** Fine-tuning del generador (offline, caro, poco
comun en la practica) — pero mucho mas barato y frecuente: prompt engineering
(instrucciones del system prompt, formato pedido), eleccion de modelo (Haiku
vs Sonnet), temperature.

**El mapa clave:** query rewriting mejora lo que ENTRA a retrieval desde el
lado de la pregunta. Hybrid search mejora el MECANISMO de retrieval en si.
Reranking corrige DESPUES de retrieval. Los tres existen porque la Etapa 2
sola, aunque matematicamente perfecta, tiene puntos ciegos reales (ver
entrada anterior sobre similitud alta != relevancia real).

## 2026-07-30 — Agentes multipaso (agentic RAG) y MCP — primer vistazo conceptual

**Agentes multipaso (agentic RAG):** en vez de "una pregunta -> un retrieval
-> una respuesta" (patron actual del RAG de Pienza), el LLM entra en un LOOP
de decision: observa la pregunta, decide que accion tomar (retrieval de que
corpus? reformular la pregunta? necesita otra fuente?), ejecuta esa accion,
mira el resultado, y decide si ya tiene suficiente o necesita otro paso.
Ejemplo directo con el roadmap de Pienza: un agente podria decidir solo "esta
pregunta es sobre numeros -> usa Text-to-SQL" vs "esta pregunta es sobre
documentacion -> usa RAG sobre claude_docs" — en vez de que un humano elija
el corpus manualmente (como hoy, con el stepper de 0010_RAG_Assistant.py), el
agente elige la herramienta.

**MCP (Model Context Protocol):** protocolo abierto (creado por Anthropic)
para que una aplicacion con LLM se conecte a fuentes de datos/herramientas
externas de forma ESTANDARIZADA, en vez de que cada app escriba su propio
codigo custom para cada integracion. Arquitectura cliente-servidor: un
"servidor MCP" expone herramientas/datos (ej. BigQuery, sistema de
archivos), y cualquier "cliente MCP" compatible (Claude Desktop, una app
propia) se conecta y las usa sin codigo de integracion especifico. Relevante
para Pienza: hoy existen funciones Python hechas a mano
(`fetch_parquet_from_gcp`, `embed_text`) — una version MCP de esto expondria
esas mismas capacidades como servidores estandar, reusables por cualquier
cliente compatible, no solo la app de Streamlit.

**Contexto:** Se disparo al pedir validar/organizar el modelo mental de "que
se puede ajustar en un pipeline RAG generico" (corpus, retrieval, generacion)
y ubicar correctamente donde caen reranking/hybrid search/query rewriting —
mas una peticion explicita de al menos conocer conceptualmente que son los
agentes multipaso y MCP, sin construirlos todavia.

---

## 2026-07-30 — Parent Document Retriever (Small-to-Big)

El problema de partir un documento largo en chunks: si los chunks son muy
chicos pierden el sentido/contexto; si son muy grandes, saturan la memoria
del prompt y diluyen la precision de la busqueda vectorial.

La logica: se hacen chunks pequenos para que la busqueda vectorial sea
matematicamente precisa (Etapa 2 del pipeline, ver entrada de "el pipeline
RAG completo"). Pero cuando la busqueda encuentra el chunk ganador, en vez de
mandarle ESE pedacito al LLM, se recupera el "documento padre" (la seccion o
pagina entera de donde salio ese chunk) para que el generador tenga el
contexto completo y no alucine por falta de contexto.

Esto separa la unidad de busqueda (el chunk chico, optimo para matching) de
la unidad de contexto (el documento padre, optimo para generar). Aplica
directamente al RAG de Pienza: hoy ambos son la misma unidad (`text` del
chunk chunkeado por heading), asi que si un chunk queda "cortado" a media
idea, el LLM solo ve ese pedazo, no la seccion completa.

## 2026-07-30 — Filtrado por metadatos antes de la busqueda vectorial

Antes de siquiera hacer la busqueda matematica (similitud coseno), se puede
usar conocimiento de bases relacionales para acotar el universo de busqueda
primero.

La logica: los vectores se guardan con metadata etiquetada (ej. `tipo_poliza:
auto_comercial`). Cuando llega una pregunta, el sistema primero filtra de
forma estricta (equivalente a un `WHERE` de SQL) solo los documentos que
cumplen esa etiqueta, y DESPUES hace la busqueda vectorial dentro de ese
subconjunto ya reducido. Asi se evita que la busqueda semantica traiga
resultados de una categoria equivocada (ej. coberturas de polizas de vida
cuando la pregunta era sobre auto comercial) solo porque el texto sonaba
parecido.

Esto es un filtro exacto (Etapa 0/estructura del dato) combinado con busqueda
semantica (Etapa 2) — el mismo principio de "SQL para lo exacto, vectores
para lo ambiguo" ya visto en la entrada de "cuando usar RAG vs SQL", aplicado
aqui como un paso previo dentro del mismo pipeline en vez de una eleccion
binaria entre uno u otro.

**Contexto de ambas entradas:** tecnicas de RAG mas avanzadas mencionadas por
el usuario en el contexto de aplicaciones de seguros/siniestros (relevante
para la entrevista de Neoris), complementando el mapa de 4 etapas ya
documentado.

---

## 2026-07-30 — LangChain no es una alternativa a Haiku (error de categoria comun)

LangChain y Haiku son cosas de tipos distintos, no comparables directamente:

- **Haiku** es un modelo — el que realmente genera texto.
- **LangChain** es una libreria de ORQUESTACION — codigo que ayuda a
  encadenar pasos (cargar datos, hacer retrieval, construir el prompt, llamar
  al LLM, parsear la respuesta) sin escribir cada pieza a mano. No genera
  texto por si misma, necesita un modelo real por debajo, elegido por quien
  la usa.

Por eso "usar LangChain en vez de Haiku" no es una decision valida — es como
preguntar "uso una llave de tuercas en vez de un tornillo". LangChain podria
usarse JUNTO con Haiku, no en su lugar. Tiene integraciones directas para
Anthropic (`langchain-anthropic`), Google, Cohere, modelos locales, etc. —
**no requiere cuenta de OpenAI**, esa asociacion viene de que LangChain se
hizo popular con ejemplos que usaban GPT al inicio, pero el framework en si
es agnostico de proveedor.

La decision real y valida seria: seguir con `requests` crudo llamando directo
a la API de Claude (lo que ya se hizo en el RAG de Pienza, cero dependencias
extra, control total) vs. migrar a LangChain como capa de orquestacion por
encima (abstracciones ya hechas — cadenas de retrieval, memoria de
conversacion, agentes — a costo de una dependencia pesada y una capa extra
que a veces oculta lo que realmente esta pasando).

**Contexto:** Se disparo al preguntar si se podia usar LangChain en vez de
Haiku, asumiendo que requeriria cuenta de OpenAI — ambas partes de la premisa
estaban equivocadas.

---

## 2026-07-30 — MCP (protocolo de conexion) vs. Text-to-SQL (capacidad de traduccion)

Son capas distintas que se complementan, no lo mismo:

- **MCP es la capa de conexion/protocolo.** Resuelve "como el chatbot llega a
  la base de datos" de forma estandarizada, en vez de que cada app escriba su
  propio codigo custom de integracion (ver entrada anterior de MCP y agentes
  multipaso).
- **Text-to-SQL es la capacidad/tecnica.** Resuelve "como el LLM convierte
  una pregunta en lenguaje natural en una consulta SQL ejecutable". Esa
  traduccion NL->SQL no viene gratis solo por conectarse via MCP — sigue
  siendo trabajo del LLM razonar y generar la consulta correcta, tenga o no
  MCP de por medio.

Un caso de uso tipico de MCP ("chatbots empresariales conectados a multiples
bases de datos, permitiendo analizar datos por chat") describe el CASO DE USO,
no el mecanismo — y en la practica casi siempre se implementa CON Text-to-SQL
por debajo. MCP es el "como te conectas" (el enchufe estandarizado),
Text-to-SQL es el "que haces una vez conectado" (la traduccion real). Se
puede tener MCP sin Text-to-SQL (un servidor MCP que solo expone consultas
predefinidas, sin generacion libre de SQL), y se puede tener Text-to-SQL sin
MCP (conexion directa a la base con codigo Python propio, como estaba
planeado el candidato #5 de Pienza).

**Contexto:** Se disparo al preguntar si un ejemplo de la documentacion de
MCP ("enterprise chatbots can connect to multiple databases... analyze data
using chat") era lo mismo que el candidato #5 (Text-to-SQL) del roadmap RAG
de Pienza.

---

## 2026-07-30 — Dos limites distintos de una API, y por que no hay que confundirlos

Cuando una API de embeddings (o cualquier API en batch) falla, casi siempre
es por uno de DOS limites completamente distintos, y la solucion correcta
depende de cual es:

**1. Rate limit (limite de velocidad) — "cuantas veces por minuto puedes
llamar".** Se manifiesta como `429 RESOURCE_EXHAUSTED` o similar. Es un limite
de TIEMPO, no de tamano — no importa que tan chica sea cada llamada, si
llamas demasiado seguido, truena. La solucion real es reducir el NUMERO de
llamadas (batching: meter mas texto por request) y/o espaciarlas (sleep,
retry con backoff).

**2. Payload limit (limite de tamano) — "cuanto puedes meter en UNA sola
llamada".** Se manifiesta como `400 Bad Request`. Es un limite de TAMANO, no
de frecuencia — no importa que tan espaciadas esten tus llamadas, si una sola
llamada trae demasiadas instancias, truena. No lo arregla ni el sleep ni el
retry, porque el request en si es invalido.

**El error real que se cometio en Pienza:** el rate limit (#1) se diagnostico
y arreglo bien originalmente (`429`, resuelto con `BATCH_SIZE=5`). Pero nunca
se volvio a preguntar cual era el payload limit real (#2) — se asumio que 5
era "el numero correcto" solo porque hizo desaparecer el error de rate limit,
sin verificar si la API permitia mucho mas por request. Al probarlo
empiricamente contra la API real de `text-embedding-004` (`:predict` online),
el limite real de payload resulto ser **250 instancias por request** — 50
veces mas grande que el valor que se venia usando. Subir el batch a 200 (con
margen de seguridad) redujo un trabajo de 4,765 filas de 953 requests a ~24.

**La leccion general:** cuando arreglas un error subiendo o bajando un
numero, ese numero apaga el sintoma — no es automaticamente el numero
correcto. Vale la pena, despues, probar el limite real por separado (en este
caso: escalar el batch hasta que el error cambie de tipo — de `429` a
`400` — eso marca la frontera entre "estoy pidiendo muy seguido" y "estoy
pidiendo demasiado de una vez").

**Contexto:** Se disparo al preguntar por que `BATCH_SIZE` era 5 al arrancar
el candidato de ChromaDB (~4,765 filas de BigQuery a embeber). Se probo el
limite real contra la API en vivo (5, 10, 20, 50, 100, 250 OK; 251, 300, 500
fallan con 400) y se corrigio el valor de produccion con evidencia, no
suposicion. Ver STAR_stories.md entrada #10 para el caso completo.

---

## 2026-07-30 — Tipos de metrica de distancia en retrieval vectorial (y por que el default de ChromaDB casi causa un bug)

Cuando un vector DB busca "los vectores mas parecidos", tiene que elegir COMO
mide "parecido". Hay tres metricas comunes, y no son intercambiables:

**1. Distancia L2 (euclidiana).** `sqrt(sum((a_i - b_i)^2))` — la distancia en
linea recta entre dos puntos en el espacio vectorial. Menor valor = mas
cercano. Es sensible a la MAGNITUD del vector, no solo a su direccion: dos
vectores pueden apuntar casi al mismo lugar (misma "idea") pero si uno es mas
"largo" que el otro, la distancia L2 los ve como mas lejanos de lo que su
significado semantico sugeriria.

**2. Similitud coseno.** `(A . B) / (||A|| x ||B||)` (ver entrada anterior de
la formula) — mide el ANGULO entre vectores, ignorando la magnitud
completamente. Es la metrica que ya se uso en el retrieval de `#1`/`#2` de
Pienza (`numpy`, coseno explicito).

**3. Producto punto (dot product / inner product, IP).** `A . B` sin dividir
entre las normas — la version SIN normalizar de coseno. Sensible a magnitud,
igual que L2, pero mide "alineacion" no "distancia".

**Por que la eleccion importa de verdad, no es solo teoria:** si los vectores
NO estan normalizados a longitud 1, L2 y coseno pueden dar rankings DISTINTOS
para la misma busqueda — un vector "mas largo" (mayor magnitud) puede
aparecer mas cercano en L2 aunque su direccion (su significado) este menos
alineada con la pregunta. No hay garantia de que `text-embedding-004`
devuelva vectores normalizados a longitud 1.

**El bug real evitado en Pienza:** al crear una coleccion en ChromaDB
(`client.create_collection(nombre)`), su indice HNSW usa **L2 por defecto**
si no se especifica lo contrario — no coseno. Esto se paso por alto al
construir el corpus de viajes serializados (candidato #4): la coleccion se
creo sin metadata, heredando L2 en silencio, mientras el resto del pipeline
(#1/#2) usa coseno explicito. El fix es pasar
`metadata={"hnsw:space": "cosine"}` al crear la coleccion. Sin este fix, el
retrieval del corpus #4 habria rankeado resultados con una metrica distinta
a la de los otros dos corpus, sin ningun error visible — solo resultados
sutilmente peores o inconsistentes.

**Contexto:** Se disparo al corregir la creacion de la coleccion ChromaDB del
candidato #4 (trip rows serializados) antes de escribir el codigo de
retrieval, evitando construir sobre un default silencioso equivocado.

---

## 2026-07-30 — Parallel tool calls vs. subagents en paralelo (no son el mismo nivel de paralelismo)

Dos mecanismos distintos, ambos "en paralelo", pero de naturaleza diferente:

**Parallel tool calls** — un solo agente, un solo contexto. El mismo agente
dispara varias herramientas simples (`Read`, `Grep`, etc.) al mismo tiempo
dentro de un mismo turno, en vez de esperar secuencialmente cuando no hace
falta. No hay razonamiento independiente de por medio — es concurrencia
mecanica de I/O (leer 3 archivos a la vez en vez de uno por uno), y todos los
resultados vuelven al mismo hilo de razonamiento que los pidio.

**Subagents en paralelo** — multiples agentes independientes, cada uno con su
propio contexto AISLADO, cada uno corriendo su propio loop completo (pensar
-> usar herramientas -> pensar de nuevo) por su cuenta. No comparten
razonamiento entre si ni con el usuario en tiempo real; cada uno devuelve solo
un RESUMEN al agente principal cuando termina, no datos crudos.

**El criterio para distinguir cual aplica:** si la tarea es solo traer
informacion sin necesidad de juicio/interpretacion (leer N archivos, buscar un
string) -> parallel tool calls alcanza. Si cada tarea requiere razonar/evaluar
por su cuenta antes de poder resumir una conclusion (ej. "juzga si cada pagina
sigue el patron de anonimizacion correcto") -> ahi se justifica un subagent
por tarea, porque hace falta un ciclo de pensamiento propio, no solo I/O.

**Contexto:** Se disparo al leer la seccion de tool use de la doc de
prompting best practices de Claude, que incluye literalmente el bloque
`<use_parallel_tool_calls>` — el mismo texto que ya vive, verbatim, en el
system prompt del propio Claude Code usado en este proyecto. Distincion
util para la entrevista de Neoris dado el requisito de "automatizacion de
flujos de desarrollo" y conocimiento de subagents.

---

## 2026-07-30 — Compactacion de contexto: quien es responsable, harness vs API cruda

La doc de prompting best practices sugiere un prompt de ejemplo para avisarle
al modelo que su contexto se comprime automaticamente al acercarse al limite
(para que no intente cerrar tareas antes de tiempo por miedo a quedarse sin
espacio). Ese prompt es necesario SOLO si uno mismo esta construyendo una app
directo sobre la API cruda de Anthropic (`client.messages.create`) — ahi la
compactacion no viene gratis, hay que implementarla uno mismo y avisarle al
modelo explicitamente que existe.

En un harness ya armado como Claude Code, esta garantia ya viene incluida en
el system prompt del propio harness (seccion "Context management"): la
conversacion se resume automaticamente al acercarse al limite, y el modelo ya
sabe que no necesita cortar tareas a medias por eso. Agregar el mismo prompt
de ejemplo a un CLAUDE.md de un proyecto que corre sobre Claude Code seria
instruccion redundante — el harness ya lo garantiza, no depende de que el
usuario lo pida.

**El patron general (mismo que con parallel tool calls, ver entrada
anterior):** varias tecnicas de la doc de prompt engineering son necesarias
"desde cero" si uno construye directo sobre la API, pero ya vienen resueltas
por el harness si se usa una herramienta como Claude Code — hay que revisar
el propio system prompt de la herramienta antes de asumir que hace falta
agregar una instruccion que "suena util" segun la doc general.

**Contexto:** Se disparo al leer el prompt de ejemplo de "managing context
limits" en la seccion de agentic systems, y preguntar si convenia agregarlo
al CLAUDE.md de Pienza — mismo patron de confusion (y misma correccion) que
con `<use_parallel_tool_calls>` antes en la misma sesion.

---

## 2026-07-30 — Prompt chaining: separate, inspectable API calls, not just shorter prompts

Prompt chaining means breaking a complex task into multiple sequential,
separate API calls, where the output of one call becomes part of the input
to the next -- not simply writing smaller/shorter prompts inside one
conversation. The distinction that matters: in a single big prompt, every
intermediate step happens invisibly inside the model in one response. In a
chained pipeline, each intermediate result exists as a real variable in the
calling code between steps, so it can be logged, evaluated, or used to
branch logic before the next call even runs.

Common patterns beyond the canonical self-correction chain (draft -> review
-> refine): extraction -> transformation pipelines (one call extracts
structured data, a second validates/normalizes it); map -> reduce over large
inputs (call the model separately per chunk, then a final call synthesizes);
classify -> route -> specialize (a cheap first call classifies the request
type and routes to a different chained prompt or model tier); generate ->
verify against ground truth (a second call checks factual claims against
retrieved documents, distinct from self-correction which checks style/quality);
plan -> execute per step (one call plans, each subsequent call executes one
step with prior results as context -- a manual-checkpoint alternative to full
subagent autonomy).

Applied concretely to Pienza's RAG Assistant (0010_RAG_Assistant.py): the
current pipeline is retrieve -> one generation call, with the human manually
picking the corpus tab. A chained version would add (1) a classify/route step
that picks the corpus automatically instead of the human doing it via the
stepper UI, and (2) a grounding-check step after generation that verifies
every claim in the draft answer is supported by the retrieved chunks before
returning it -- turning the hallucination-mitigation technique already
documented (respond only with given info) into its own inspectable pipeline
stage instead of hoping one generation call gets it right.

**Contexto:** Se disparo al leer la seccion "Chain complex prompts" de la
doc de prompting best practices de Claude, seguido de una confusion real del
usuario (pensar que chaining es solo dividir un prompt largo en mensajes mas
chicos dentro del mismo chat) que se corrigio con ejemplos de codigo
concretos, y finalmente aterrizado en el pipeline real del RAG Assistant de
Pienza.

---

## 2026-07-30 — A harness system prompt does not carry over to a custom API-based agent

Claude Code's own system prompt (the guardrails about parallel tool calls,
confirming before destructive/irreversible actions, and avoiding
overengineering) is specific to the Claude Code product itself, injected by
its application layer before every request. It is not a property of the
underlying model (e.g. Claude Sonnet 5) and is not stored anywhere in this
repo's claude_docs -- it lives entirely inside the Claude Code tool, separate
from project-level CLAUDE.md content.

This matters concretely for building any custom agent directly on the raw
Anthropic API (e.g. a RAG agent): none of that harness behavior carries over
for free. `client.messages.create(system=...)` starts empty/generic unless
you write it yourself -- no automatic parallel tool-calling discipline, no
ask-before-destructive-action guardrail, no anti-overengineering scoping.
Every one of those behaviors has to be deliberately authored into the
custom agent's own system prompt, informed by the same prompting-best-practices
patterns documented in Claude's official docs, because the model itself has
no inherent memory of "being Claude Code" -- that identity and its guardrails
belong to the specific harness wrapped around the model, not the model itself.

**Contexto:** Se disparo al notar que varias secciones seguidas de la doc de
prompting best practices (parallel tool calls, balancing autonomy and safety,
avoid overengineering) ya estaban presentes casi verbatim en el propio system
prompt de Claude Code usado en este proyecto, y preguntar si ese mismo system
prompt aplicaria tambien a un agente de RAG propio construido sobre la API
cruda de Anthropic.

---

## 2026-08-01 — Prompt chaining is RAG-adjacent, not RAG-specific

Prompt chaining is a general agentic-design pattern -- breaking a task into
multiple separate, sequential LLM calls where each call's output becomes a
real inspectable variable feeding the next call -- not a technique unique to
RAG. RAG pipelines are simply a common place to apply it, because a RAG
pipeline already has multiple natural stages that map cleanly onto separate
calls: query rewriting before retrieval (rephrase a vague question into a
better search query), reranking after retrieval (a cheap call re-scores
retrieved chunks before the final generation call), and grounding
verification after generation (a call that checks every claim in the answer
against the retrieved chunks). But chaining applies equally to tasks with no
retrieval at all -- classify-route-specialize for a support ticket triager,
or plan-execute for a multi-step coding agent. The correct framing: RAG is a
common home for chaining, chaining is not a RAG-only concept.

**Contexto:** Se disparo despues de una explicacion concreta de chaining
aplicada al RAG Assistant de Pienza (0010_RAG_Assistant.py: classify corpus
-> generate -> verify grounding como 3 llamadas separadas en vez de un solo
prompt gigante), seguido de la pregunta directa del usuario de si chaining es
canon especificamente para RAGs.

---

## 2026-08-01 — Reranking (retrieve wide, rerank narrow)

Retrieval por embeddings (cosine similarity) es rapido pero aproximado: compara
vectores de query y chunk calculados por separado, cada uno sin ver al otro, asi
que no evalua relevancia real para ese par especifico, solo cercania vectorial.

Reranking corrige eso agregando una segunda etapa con un modelo distinto,
tipicamente un cross-encoder: toma la query y cada chunk candidato juntos, en un
solo forward pass (no vectores precomputados por separado), y produce un score de
relevancia directo para ese par. Al ver query+chunk simultaneamente captura
matices que el embedding puro no puede, pero es mucho mas caro (un forward pass
completo por candidato) -- por eso solo se aplica sobre el top-k que ya filtro
retrieval, nunca sobre el corpus completo.

De ahi el patron "retrieve wide, rerank narrow": retrieval trae un top-k grande
(ej. 50) para maximizar recall (no perder el chunk correcto por una diferencia
minima de coseno), y rerank lo reordena y recorta a un top-k final chico (ej. 4)
que es el que realmente llega a generacion. Si retrieval ya trajera solo top-4,
el reranker no tendria margen de corregir un error de retrieval -- el chunk
correcto ya se habria quedado fuera antes de que el reranker lo viera. Retrieval
optimiza recall (barato, amplio); rerank optimiza precision (caro, angosto);
son objetivos distintos y por eso usan tamanos de k distintos en cada etapa.

**Contexto:** Se disparo revisando el diagrama de "Traditional RAG" que el
usuario pego (con un paso explicito de Rerank entre Vector Database y
Augmentation), y la pregunta directa de como funciona mecanicamente el rerank
y por que conviene correrlo sobre un top-k grande en vez de sobre el top-k
final chico. Ninguno de los 3 corpus del RAG Assistant de Pienza (0010) tiene
reranking implementado — es un hueco identificado, no una feature existente.

---

## 2026-08-01 — Chunk size vs. top-k (trade-off, no variable libre)

El tamano de chunk y el valor de k en retrieval estan inversamente relacionados:
chunks mas grandes cubren mas contenido cada uno, asi que se necesitan menos
(k mas bajo) para cubrir la misma cantidad de informacion; chunks mas chicos
cubren menos cada uno, asi que se necesita un k mas alto para la misma cobertura.

Pero esa relacion no significa que se pueda optimizar libremente hacia un
extremo (chunks gigantes + k=1). Cada extremo tiene su propio costo:

- Chunks grandes + k bajo: menos ruido de piezas irrelevantes, pero cada chunk
  mezcla varios temas adentro, asi que su embedding es menos preciso (un
  promedio de varias ideas, no una sola) -- retrieval puede fallar en
  encontrarlo aunque solo una parte sea relevante. Ademas cada chunk pesa mas
  tokens, asi que "menos chunks" no siempre significa menos tokens totales.
- Chunks chicos + k alto: cada chunk es semanticamente mas preciso (una sola
  idea), pero la respuesta puede quedar partida entre dos chunks separados y
  ninguno solo tener el contexto completo -- el mismo problema que motiva el
  Parent Document Retriever (recuperar el chunk chico y preciso, pero
  adjuntarle el documento padre completo para no perder contexto).

El tamano de chunk optimo no se elige solo para minimizar k -- se elige por
donde vive el mejor balance entre precision semantica del chunk y no
fragmentar respuestas que necesitan contexto contiguo.

**Contexto:** Se disparo tras la pregunta directa del usuario de si chunks
mas grandes permiten un top-k menor que chunks mas chicos, en la misma
conversacion donde se explico el trade-off de reranking (retrieve wide,
rerank narrow) para el RAG Assistant de Pienza (0010).

---
