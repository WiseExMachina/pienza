# Mermaid → PNG drift audit v2 — ground truth is the notebook, not the mermaid source

Method: for each notebook, read the actual notebook (code + markdown cells) to derive the
real data lineage — which variable/step feeds which, in what order — independent of any
previously-written mermaid text (that mermaid may carry its own drift from earlier AI passes,
so it is NOT used as reference here). Then compare that ground truth against the current
`assets/<notebook>_A.png` / `_B.png` diagram image, node by node, edge by edge.

Findings are appended below by notebook as each batch completes. Nothing has been fixed yet —
this is audit-only. Review with the user before regenerating any PNG.

---

## 0601_NLP_Transformer_miniBabel

### Diagrama A

**Exactitud lógica:**
Derivé el lineage real leyendo Phases 1-8 del notebook. Casi todo coincide: pienza.db → Phase 1
(setup: imports, DB, HF auth) → Phase 2 (zone labeling) → Phase 3 (address standardization +
TF-IDF) → {Phase 4 Word2Vec, Phase 5 neural+Transformer, Phase 7 BETO} → Phase 5 → {Phase 6
audit, Phase 8 export}.

Hay un drift real en el nodo de Phase 7 (BETO): el PNG lo dibuja colgando directo de Phase 3
("Address standardization + TF-IDF"), en paralelo con Phase 4 y Phase 5. Pero el código real de
Phase 7 (celda 7.1) consume `X_train`, `X_val`, `y_train`, `y_val`, `zone_to_idx` y
`unique_zones` — todas variables creadas en **Phase 5.1** (el split estratificado + vocabularios),
no en Phase 3. Phase 3 solo produce `clean_address`; Phase 7 nunca toca esa columna directamente
para nada que no pase primero por el split de Phase 5. El padre real de Phase 7 es Phase 5, no
Phase 3 — la flecha está mal dirigida (salto que se salta un nodo intermedio real).

**Legibilidad gestáltica:**
Buena. Árbol vertical limpio, una sola dirección dominante (arriba→abajo), fila de fase 4/5/7
bien alineada, fila de fase 6/8 alineada debajo de fase 5. Sin cruces. El único problema es
lógico (el hijo mal ubicado), no visual — la disposición en sí es clara.

### Diagrama B

**Exactitud lógica:**
Comparé contra el código real de las celdas 2.1-2.2 (df_input→df_nav), 3.2 (standardize_...),
3.4 (tfidf_final), 4.1 (w2v_model), 5.1 (loaders), 5.3-5.4 (model), 6.1 (audit), 7.1 (BETO),
8.1-8.2 (exports). Dos discrepancias reales:

1. **Arista inventada `tfidf_final → w2v_model`.** El PNG dibuja el Word2Vec model como hijo de
   `tfidf_final`, implicando que Word2Vec consume el objeto TF-IDF. Pero la celda 4.1 construye
   `sentences` directamente desde `df_nav['clean_address'].tolist()` — no usa `tfidf_final` para
   nada. El padre real de `w2v_model` es "Standardized addresses" (la misma columna
   `clean_address`), en paralelo con `tfidf_final`, no encadenado después de él.

2. **Arista inventada `df_nav → BETO` (salta Phase 5).** Igual que en el Diagrama A: el código de
   BETO (celda 7.1) usa `X_train`/`X_val`/`y_train`/`y_val`/`zone_to_idx` — variables creadas en
   "Neural DataLoaders" (Phase 5.1), no en `df_nav` directamente. El PNG debería mostrar
   `Neural DataLoaders → BETO`, no `df_nav → BETO`.

3. **Posible arista inventada `BETO → Holdout audit parquet`.** El código de Phase 8 (celdas
   8.1/8.2) usa exclusivamente `model` (el Transformer custom), `token_to_idx`, `idx_to_zone` y
   `df_nav` — nunca `model_bert` ni ningún artefacto de BETO. Si el PNG efectivamente dibuja una
   línea de BETO hacia el nodo de exportación final (aparenta hacerlo, una curva larga baja desde
   BETO hasta el nodo inferior), esa conexión no tiene respaldo en el código: los pesos/resultados
   de BETO nunca se usan en la exportación.

**Legibilidad gestáltica:**
Aceptable pero con fricción. El flujo es mayormente top-down, pero la fila intermedia
(Standardized addresses / Neural DataLoaders / BETO) y sus hijos (tfidf_final / model) generan
líneas que se cruzan visualmente cerca del centro, y la línea larga que baja desde BETO hasta el
nodo de exportación final cruza por encima de la columna de "Randomized contrast audit",
obligando al ojo a rebotar en vez de seguir una columna limpia.

---

## 0602_cGAN_Training

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Leí las 6 fases completas (Setup/ingestion → Data
preprocessing → GAN architecture → Adversarial training → Manifold synthesis → Statistical
audit). El PNG es una cadena lineal de 6 nodos top-to-bottom que coincide exactamente con el
orden real y los encabezados markdown (`## Phase N — ...`).

**Legibilidad gestáltica:**
Correcto. Flujo vertical único, sin ramificaciones, sin cruces, alineación perfecta.

### Diagrama B

**Exactitud lógica:**
Derivé el lineage real: `BigQuery: v_ML_Supervised → df_raw` (celda 1.2); desde `df_raw` salen
tres ramas independientes y paralelas (confirmado en 2.1 "v2.17 physics", 2.4/2.5 "v3.1/v3.2
pickup filter", y 2.8 `execute_final_preprocessing(df_raw)` que produce `df_gan_ready` — las tres
funciones se llaman directamente sobre `df_raw`, no encadenadas entre sí, así que la nota del
docstring de 2.8 ("consolida v2.17 + v3.2") describe el *contenido* de la lógica reescrita, no una
dependencia real de datos entre esas celdas). Esto coincide con el PNG: tres flechas paralelas
desde `df_raw` hacia "v2.17 physics pass", "v3.1/v3.2 pickup filter" y `df_gan_ready`, con las dos
primeras terminando en nodos sin salida (correctamente "exploratory, superseded", sin hijos).

`df_gan_ready → build_generator_pienza_v4` y `df_gan_ready → build_discriminator_pienza_v5`:
correcto (celda 3.3 confirma que `SWITCH_COLS`/`PHYSICS_COLS`/`dataset` se construyen desde
`df_gan_ready`, alimentando ambas arquitecturas). `generator/discriminator → training loop →
df_synthetic → audits`, y `df_raw → audits` (ground truth para el battery de KS/JS/TVD):
correcto, confirmado en Phase 6.

Posible discrepancia: el PNG muestra una línea vertical continua que baja del nodo `df_raw`
central atravesando toda la columna intermedia (pasando cerca/por encima de la fila de
generator/discriminator) hasta llegar a "Adversarial training loop", como si hubiera una arista
directa `df_raw → training loop`. El código real (celda 3.3 + 4.1) muestra que el training loop
solo consume el `dataset` de TensorFlow ya construido desde `df_gan_ready`, y los objetos
`generator`/`discriminator` — nunca `df_raw` directamente. Si esa línea es una arista real (no
solo una coincidencia de trazado vertical), es una conexión de "salto largo" inventada que no
tiene respaldo en el código.

**Legibilidad gestáltica:**
Mayormente clara — filas bien agrupadas por fase, alineación limpia. El único problema es
justamente esa posible línea vertical larga de `df_raw` hasta el training loop: aunque sea
intencional o accidental, visualmente atraviesa dos filas de nodos intermedios y rompe la lectura
de "una fila = una fase", forzando al ojo a rastrear una línea larga en lugar de seguir el flujo
por bloques.

---

## 0603_ETL_pienzadb_to_BigQuery

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Las 6 fases (Setup/BigQuery client → Table migration →
Relational audit → View reconstruction → Parity audit → GCS backup) están en el mismo orden que
los encabezados reales del notebook. Cadena lineal de 7 nodos (incluyendo el nodo fuente
`pienza.db (SQLite)`), top-to-bottom, sin ramificaciones.

**Legibilidad gestáltica:**
Correcto. Igual de limpio que los demás diagramas A: una sola columna vertical, sin cruces.

### Diagrama B

**Exactitud lógica:**
Este es el diagrama más denso de los tres notebooks (17 nodos), y lo revisé con atención especial
en la convergencia final hacia `perform_parity_audit()`, como pidió el encargo.

Confirmé, celda por celda: `pienza.db` alimenta 5 ramas paralelas (`db_engine`, `client`,
`complete_migration()`, `extract_view_logic()`, `investigate_and_seal()`) — las 5 coinciden con
el código de las celdas 1.1/1.2/2.1/4.1/6.1, cada una usando `DB_PATH`/`sqlite3.connect` de forma
independiente. `complete_migration()` alimenta 7 hijos: `execute_relational_audit()`,
`v_trip_funnel_metrics`, `v_trip_funnel_wide`, `v_broche_fks`, `v_offers_human`,
`v_lifecycle_audit`, `v_ML_Supervised` — los 7 son vistas/funciones de BigQuery construidas
después de que la migración deja las tablas nativas en BQ (cada `CREATE OR REPLACE VIEW` en las
celdas 4.2-4.10 lee de tablas ya migradas). Correcto.

`v_trip_funnel_wide → v_trip_final_kpis → v_mission_dossier`: correcto, confirmado en celdas
4.3/4.4/4.5 (cada vista hace `SELECT ... FROM` la vista anterior). `v_lifecycle_audit →
v_lifecycle_audit_accepted`: correcto (celda 4.8/4.9, el accepted es un filtro sobre la vista
madre).

**Convergencia final en `perform_parity_audit()`:** el PNG muestra 5 flechas entrando a este
nodo, desde `v_mission_dossier`, `v_broche_fks`, `v_offers_human`, `v_lifecycle_audit_accepted` y
`v_ML_Supervised`. Verifiqué la celda 5.1 (`perform_parity_audit`): la función en sí no referencia
ninguna de esas 5 vistas por nombre en su cuerpo — hace un audit genérico iterando
`INFORMATION_SCHEMA.TABLES`/`sqlite_master` sobre **todas** las tablas y vistas del dataset (el
`df_audit` de salida en la celda 35 incluye las 18 tablas + las 9 vistas, no solo esas 5). Así que
la elección específica de esas 5 vistas (y no las otras 4: `v_trip_funnel_metrics`,
`v_trip_funnel_wide`, `v_trip_final_kpis`, `v_lifecycle_audit` sin filtrar) como "padres" de la
auditoría de paridad es arbitraria — conceptualmente son los 5 "productos finales" de negocio
(vistas terminales de la cadena, no vistas intermedias), lo cual es una simplificación razonable
para un diagrama de "variable journey", pero no es una dependencia de código real: la función de
paridad en verdad depende de *todas* las 27 tablas/vistas del dataset por igual, no
preferencialmente de esas 5. No lo marco como drift duro (es una decisión de diseño defendible
para mantener el diagrama legible), pero vale la pena que quede documentado como simplificación,
no como lineage literal.

Fuera de esa simplificación documentada, no encontré aristas inventadas ni nodos con padres/hijos
faltantes: los conteos de hijos de `complete_migration()` (7) y de padres de `perform_parity_audit()`
(5) coinciden con lo que el PNG dibuja.

**Legibilidad gestáltica:**
Con 17 nodos es, con diferencia, el diagrama más denso de los tres notebooks, pero se mantiene
razonablemente legible: fases agrupadas por fila (fila de fuentes, fila de vistas de primer nivel,
fila de vistas derivadas, fila de convergencia), alineación columna por columna consistente con el
orden de fases. El punto de fricción real es exactamente la convergencia final: 5 líneas curvas
llegando a `perform_parity_audit()` desde distintas columnas se cruzan entre sí y con las líneas
verticales de las columnas vecinas (`v_lifecycle_audit → v_lifecycle_audit_accepted`,
`v_ML_Supervised`), generando un nudo visual en la banda inferior del diagrama que rompe el
patrón de "una fila, una fase" que domina el resto. Un lector tiene que rastrear cuidadosamente
cuál curva viene de cuál nodo en esa zona.

## 0407_Clustering_Paper_Streamlit

### Diagrama A

**Exactitud lógica:**
Discrepancia real: el nodo `pienza.db: offers` dibuja su línea de salida hacia **Phase 1**
("Polygon geometry: ID injection, centroids"). Pero por código, Phase 1 (celdas 1.1-1.6) solo
toca `assets/poly.geojson` — el `db_engine` se crea en 1.1 (conexión), sí, pero la tabla
`offers` en sí no se consulta hasta **Phase 2** (celda 2.1, HDBSCAN clustering, `query_geo =
"SELECT offer_id, dropoff_lat, dropoff_lon FROM offers ..."`). El nodo `offers` está apuntando
un salto de fase antes de donde realmente entra al pipeline; debería apuntar a Phase 2, no a
Phase 1.

**Legibilidad gestáltica:**
La cadena vertical Phase 1→5 es limpia, alineada, sin cruces. Pero el nodo `offers` entra a
Phase 1 por el costado derecho (la línea baja y dobla en ángulo recto hacia la cara lateral de
la caja) en vez de por arriba como `poly.geojson` — rompe la convención top-down del resto del
diagrama para esa única flecha, aunque el problema real es de destino (ver arriba), no solo de
estilo de entrada.

### Diagrama B

**Exactitud lógica:**
1. Confirmado correcto: `poly.geojson → gdf (72 polygons) → gdf + map_id (Tecamachalco fix) →
   df_labels (centroids)` coincide con 1.1→1.4→1.6. `offers (pienza.db) → df_hdbscan_analysis
   (+hdbscan_cluster_id) → df_hdbscan_analysis (+zone_name, naming fix)` coincide con 2.1→2.2.
   Los tres hijos de `df_hdbscan_analysis` final (`df_kepler_clean`, `df_viz`) están
   correctamente parentados solo ahí, sin arrastrar `gdf` — verificado por crop de pixeles, no
   hay línea cruzada de `gdf+map_id` hacia `df_kepler_clean`. `df_kepler_clean → df_h3_final →
   labels_final → Folium audit map` coincide con 3.1→4.4→5.1.
2. Discrepancia real (arista faltante): `gold_master_df` se dibuja con un solo padre, `df_viz`.
   Pero la celda 5.2 (`gold_master_df`) en realidad tiene **dos fuentes independientes**: (a)
   `df_viz` para los datos espaciales, y (b) una query SQL nueva y directa (`df_sql =
   pd.read_sql(query, db_engine)`) que vuelve a golpear la tabla `offers` (más
   `engineered_features`, `product_category`, `reason_primary`) para los datos operacionales
   (fare, rejection reason, EPH). El nodo `offers (pienza.db)` ya existe en el diagrama (arriba,
   alimentando a `df_hdbscan_analysis`) — sería trivial agregarle una segunda flecha hacia
   `gold_master_df`, pero esa arista no está. Es un padre faltante, no un padre inventado.

**Legibilidad gestáltica:**
Buen árbol top-down, dos columnas de raíces (`poly.geojson`, `offers`) claramente separadas,
fan-out limpio de 2→3 nodos y luego merge a 2 nodos sin cruces. Routing ortogonal consistente
en todo el diagrama. Sin problemas de legibilidad más allá de la arista faltante ya señalada en
exactitud lógica.

---

## 0509_WINNER_XGB_cascade_postablation

### Diagrama A

**Exactitud lógica:**
Los tres subgraphs con título de fase (`Phase 1 - Data Foundry`, `Phase 2 - Layer 1 (Triage)`,
`Phase 3 - Layer 2 (Nuance)`) están presentes, visibles y correctamente nombrados/ordenados
contra los encabezados markdown reales (`## Phase 1 — Data Foundry`, etc.). Contenido interno:
"Ingest v_ML_Supervised, purge rare class" (1.2) → "Zone grouping + merged zone names" (1.4-1.6)
→ "Wide (41-feat) and Focused (20-feat) universes" → "Geo + temporal feature-selection arenas"
(1.7, 1.10) → "Scale, one-hot fuse, walk-forward folds" (1.12-1.15): todos los pasos existen y
en el orden final correcto de fase, aunque el diagrama colapsa el orden real de construcción
(el markdown de 1.2 dice que Wide/Focused ya se construyen ahí mismo, en paralelo al ingest,
antes de que exista el zone grouping — no estrictamente "después" como sugiere la cadena lineal
del diagrama). Es una simplificación de una fase con ~14 sub-pasos entrelazados a una cadena de
4 cajas; razonable para una vista de alto nivel, no un error de invención de nodos/aristas.
Phase 2 y Phase 3 sí siguen el orden real: target → tune/fit → threshold/SHAP/ROC/PR (Phase 2,
celdas 2.1→2.4→2.7-2.14); isolate → tune/fit (champion + lightweight) → Week 6 eval → 3.11 SHAP
atlas (Phase 3, celdas 3.1→3.4/3.10→3.5-3.9→3.11). Correcto.

**Legibilidad gestáltica:**
Correcto y es el mejor caso de los diagramas A auditados: subgraphs con encabezado propio
visibles y legibles, una sola columna vertical, sin cruces, alineación perfecta, jerarquía
clara (fuente arriba, resultado abajo). Cumple explícitamente el criterio adicional pedido
(títulos de fase visibles y correctos en el PNG).

### Diagrama B

**Exactitud lógica:**
1. Confirmado correcto en la raíz: `df_input (v_ML_Supervised, rare class purged) →
   final_zone_id/final_zone_name` (celdas 1.4-1.6) y `df_input → Wide+Focused raw universes` en
   paralelo, con `final_zone_id` retroalimentando a `Wide+Focused raw universes (scaled,
   one-hot fused)` — coincide con la fusión OHE de 1.13, que sí incorpora `final_zone_id` junto
   con las columnas numéricas escaladas.
2. Discrepancia real (aristas inventadas): el diagrama dibuja `Wide + Focused raw universes
   (scaled, one-hot fused) → X_L1, y_L1` y también `→ X_L2, y_L2`, como si ambos fueran
   construidos a partir de ese universo fusionado. Pero por código, **ninguno de los dos lo
   usa**: `X_L1` (celda 2.1) se construye leyendo columnas crudas directamente de `df_input`
   (`numeric_L1`, `categorical_L1` incluyendo `final_zone_id`, `hour_of_day` ya como columnas de
   `df_input`), con su propio `fillna`/`get_dummies` independiente. Igual `X_L2` (celda 3.2,
   función `build_l2_raw_features`) toma columnas de `df_L2` (subconjunto de `df_input`), con su
   propio log-transform y `StandardScaler` (`scaler_L2`) independiente del universo Wide/Focused
   fusionado. El objeto `ligas_finales`/`X_final` (el universo escalado+fusionado que sí dibuja
   el diagrama) solo se usa en la celda 2.3 (`Purge, split, chronological isolation`,
   `X_final = ligas_finales['LIGA_B_Focused_Raw_Hybrid']`), que no alimenta a `X_L1` ni `X_L2`
   en ningún punto visible del notebook. Es decir: el diagrama muestra el universo Wide/Focused
   fusionado como el padre común de ambas cascadas, cuando en realidad ambas cascadas bypasean
   ese universo por completo y reconstruyen sus features directamente desde `df_input`. Esto es
   una cadena de aristas fantasma — el parentesco real correcto sería `df_input → X_L1, y_L1` y
   `df_input → X_L2, y_L2` directamente (posiblemente con `final_zone_id` como padre adicional,
   dado que ambas listas de columnas incluyen `final_zone_id`).
3. Discrepancia real (dirección de flecha invertida): en ambas ramas, el diagrama dibuja
   `model_champion_L1 → X_L1_test, y_pred_L1` y `model_champion_L2 → X_test_l2`. Pero el
   test-split (`X_L1_test` recuperado en 2.7 vía máscara `week_id==6` sobre `X_L1`; `X_test_l2`
   construido en 3.5 vía `test_mask_l2` sobre `X_L2`) es un split cronológico de los datos que
   **no depende del modelo entrenado** — el modelo solo consume ese split para generar
   predicciones (`y_pred_L1`, o las probabilidades usadas después). La flecha real debería salir
   de `X_L1, y_L1`/`X_L2, y_L2` hacia el nodo de test, con `model_champion_L1`/`model_champion_L2`
   como una entrada adicional (converger, no encadenar linealmente) hacia esos mismos nodos de
   evaluación. Tal como está dibujado, sugiere que el test set es un producto del modelo, lo
   cual invierte la dependencia real.

**Legibilidad gestáltica:**
Estructura de árbol razonable (raíz arriba, dos ramas L1/L2 abajo, converge a evaluación), pero
usa líneas curvas/diagonales en vez de las líneas ortogonales en ángulo recto usadas en el
diagrama B de 0407 — estilo distinto dentro del mismo proyecto, no necesariamente un error, pero
rompe la consistencia visual entre notebooks. La curva doble desde `df_input` (una directa a
Wide+Focused, otra vía `final_zone_id` que se curva de regreso) es visualmente algo más difícil
de seguir de un vistazo que el patrón recto de bifurcación/fusión usado en 0407_B. La rama L1 es
visualmente muy delgada (una sola cadena lineal) comparada con la rama L2 (bifurca en
`model_champion_L2` + `xgb_spartan`), lo cual es fiel al contenido real (L2 sí tiene una
variante lightweight, L1 no) pero produce una asimetría notable en el diagrama que un lector
podría interpretar erróneamente como una omisión en la rama L1.

## 0212_ETL_Big_Bang_pienzadb

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Derivé el lineage real desde la celda 117 (Appendix —
table journey, la tabla de linaje real, no un mermaid) y desde el recorrido de las 118 celdas
del notebook (Phases 1-6, secciones 1.1 a 6.5): GCS raw offers+OCR → Phase 1 (offers ETL) →
Phase 2 (trip_events ETL, GTS-4, linking cascade) → Phase 3 (lifetime_trips + activity_earnings)
→ Phase 4 (manual data corrections) → Phase 5 (engineered_features + consolidated analytical
views) → Phase 6 (silver_palette + final ML views) → Closing checkpoint. El PNG es una cadena
lineal de 8 nodos top-to-bottom que coincide exactamente con este orden y con los encabezados
markdown reales de cada fase (`## Phase N — ...`).

**Legibilidad gestáltica:**
Correcto. Flujo vertical único, sin ramificaciones, sin cruces, alineación perfecta, jerarquía
clara de arriba (fuente) a abajo (resultado). Es el caso más simple y más limpio de los tres
notebooks auditados.

### Diagrama B

No aplica — confirmado. La celda final del notebook (celda 117, markdown) es un
"## Appendix — table journey" que consiste en una tabla Markdown (columnas: Table/view | Built
from | Waypoint), no un diagrama. No existe imagen `_B.png` para este notebook y no debería
existir; no hay drift que reportar aquí porque no hay diagrama que comparar.

---

## 0305_EDA_Causal_Inference

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Derivé el lineage desde las celdas de código: fuente
única `v_mission_dossier + offers` (queries en las celdas 6, 8, 15, 17, 19, 22, todas hacen JOIN
`v_mission_dossier`/`offers`). Se ramifica en tres fases independientes, cada una consumiendo la
fuente directamente (no unas de otras): Phase 2 (celdas 5-12: policy-intervention audit, OLS
baseline, cono de heteroscedasticidad) → produce "yield lift % / spread coefficient"; Phase 3
(celdas 13-19: matriz de correlación reality-check, auditoría de integridad de telemetría) →
produce "fare vs time correlation"; Phase 4 (celdas 20-26: extracción double-spread, curva de
respuesta fraud-prevention, modelo cuadrático) → produce "inelasticity threshold (tipping
point)", calculado explícitamente en la celda 26 (`tipping_point = -b1 / (2*b2)`). El PNG
muestra exactamente esta estructura: un nodo fuente que se abre en tres ramas paralelas
(Phase 2/3/4), cada una con su propio nodo de salida. Coincide.

**Legibilidad gestáltica:**
Correcto. Fuente arriba, tres fases en fila alineada, tres salidas alineadas debajo de cada una.
Sin cruces, sin saltos largos, jerarquía clara arriba→abajo con ramificación simétrica.

### Diagrama B

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Rastreé cada variable: `dossier` alimenta a seis
dataframes de primer nivel — `df_dated` (celda 6, session-level, policy audit), `df_risk`
(celda 8, spread extraction; celda 10 hace el cast numérico), `df_reality_matrix` (celda 15),
`df_leak_check` (celda 17), `df_core_reality` (celda 19), `df_double_spread` (celda 22) — los
seis se construyen directamente desde queries que hacen JOIN `v_mission_dossier`/`offers`, sin
depender unos de otros. De estos, tres son hojas terminales sin más pasos derivados
(`df_reality_matrix`, `df_leak_check`, `df_core_reality` — cada uno solo alimenta un heatmap o
un print, no genera una variable nueva), lo cual el PNG respeta correctamente (no dibuja hijos
para esos tres). `df_risk` → "OLS baseline + heteroscedasticity cone" (celdas 10 y 12, ambas
parten de `df_risk`/`df_clean`, derivado de `df_risk`) — correcto. `df_double_spread` → `df_final`
(celda 24: `df_final = df_double_spread.copy()`) → `model_poly` (celda 26: `smf.ols(...,
data=df_final)`) → "inelasticity tipping point (vertex of the curve)" — correcto, cadena de 4
pasos bien representada.

**Legibilidad gestáltica:**
Problema menor de lectura: la fila superior tiene 6 nodos, y la flecha que conecta
`df_double_spread` (el nodo más a la derecha) con `df_final` (ubicado en el centro-derecha,
debajo de `df_leak_check`/`df_core_reality`) viaja horizontalmente por encima de dos nodos
intermedios antes de bajar — un salto largo que obliga al ojo a rastrear una ruta no directa.
Alternativa más legible: reordenar la fila superior para que `df_double_spread` quede
inmediatamente arriba de `df_final`, evitando el cruce visual sobre los otros nodos. Aparte de
esto, el resto del diagrama es limpio: alineación por niveles correcta, sin cruces de líneas,
jerarquía arriba→abajo consistente.

---

## 0307_EDA_Optimal_Stopping_Playbook

### Diagrama A

**Exactitud lógica — DRIFT DETECTADO.**
Rastreé el lineage real celda por celda. La celda 5 (1.2) construye `df_campaign` desde
`pienza.db: offers + engineered_features` (join con `product_category`, `engineered_features`,
`offer_action`) — el nodo fuente del PNG es correcto. La celda 7 (1.3) calcula el inter-offer
delta y, al final, ejecuta `global df_opportunity_cost; df_opportunity_cost = df_campaign` —
es decir, el "Phase 1" (foundation: quality index, inter-offer delta, sanitized search rhythm,
completado en 1.4-1.6) efectivamente produce `df_opportunity_cost` como el dataframe central.
Hasta ahí, el PNG es correcto: fuente → Phase 1.

El drift está en Phase 4 ("Efficient frontier"). El PNG dibuja dos flechas convergiendo en
Phase 4: una desde Phase 2 (Baseline escape clock) y otra desde Phase 3 (Opportunity oracle).
Pero leí la celda 28 completa (4.1, la que genera la frontera eficiente) y su única
dependencia declarada es `if 'df_opportunity_cost' in locals()` — lee directamente
`df_opportunity_cost` (el output de Phase 1), no ninguna variable producida por Phase 2
(`escape_points`, celda 16) ni por Phase 3 (`df_prob`, `oracle_results`, celda 19; o
`quadrant_cvs`, celda 21; o el simulador interactivo, celda 23). De hecho, la celda 28
re-implementa desde cero su propia lógica de archetypes y su propio oráculo de ventanas
móviles (rolling window), duplicando el patrón conceptual de Phase 2/3 pero sin consumir sus
variables. La única conexión entre fases es un comentario humano en la celda 19
("windows discovered in Phase 2" — una nota de insight, no una dependencia de código).
Conclusión: Phase 4 debería dibujarse como una cuarta rama independiente de Phase 1 (al igual
que Phase 2, 3 y 5), no como un nodo que converge desde Phase 2 y Phase 3. El PNG hereda esta
estructura incorrecta directamente del mermaid embebido en la celda 0 del notebook (que
también muestra `B --> E` y `D --> E`), pero mi derivación desde el código real (ignorando ese
mermaid, como indica la metodología) confirma que esa estructura no corresponde al código.

**Legibilidad gestáltica:**
Aparte del problema lógico anterior, el diagrama es limpio: fuente arriba, Phase 1 debajo,
tres/cuatro ramas en fila alineada, sin cruces de líneas, jerarquía arriba→abajo clara. Si se
corrige la lógica (Phase 4 como cuarta rama directa de Phase 1), el layout de "fila de 4 cajas
paralelas bajo Phase 1" seguiría siendo igual de legible que el actual.

### Diagrama B

**Exactitud lógica — mismo drift que en Diagrama A, más una imprecisión adicional.**
Confirmé el mismo problema a nivel de variables: `df_prob` (celda 19, definido dentro de
"3.1 — Global oracle") y "Baseline escape clock" (celda 16, Phase 2) aparecen en el PNG
convergiendo hacia "Efficient frontier". Pero la celda 28 no usa el `df_prob` de la celda 19 ni
ninguna variable de la celda 16 — reconstruye `df_sim = df_opportunity_cost.sort_values(...)`
internamente. El nodo "Efficient frontier" debería colgar directamente de
`df_opportunity_cost` (el nodo central), como una rama más, igual que "df_el" o "Continuation
value simulator". (Nota aparte: el nombre "df_prob" en el diagrama es ambiguo — la celda 21,
"Strategic probability matrix", también crea su propia variable local llamada `df_prob`,
independiente de la de la celda 19; ambas se derivan de `df_opportunity_cost` de forma
redundante, pero el diagrama las trata como si fueran un único objeto compartido, lo cual
funciona por casualidad para la conexión hacia "Strategic probability matrix" pero no para la
conexión hacia "Efficient frontier").

Imprecisión adicional en el texto del nodo fuente: el PNG de este Diagrama B dice
`"pienza.db: offers + sessions"`, mientras que el Diagrama A del mismo notebook dice
`"pienza.db: offers + engineered_features"`. La query real (celda 5) hace JOIN de `offers` con
`product_category`, `engineered_features` y `offer_action` — no existe una tabla `sessions`
separada, `session_fk` es solo una columna de `offers`. El texto del Diagrama A es el correcto;
el del Diagrama B es una imprecisión heredada (probablemente de una iteración anterior del
mermaid) que no corresponde al código.

**Legibilidad gestáltica:**
Problema menor: `df_deltas_valid` queda como nodo huérfano muy aislado en el extremo izquierdo,
con un espacio notablemente mayor respecto a los demás nodos de su fila, lo que rompe un poco
la sensación de agrupación por fase. Aparte de eso, el resto es legible: alineación por niveles
correcta, sin cruces de líneas, jerarquía arriba→abajo clara. Una vez corregida la lógica de
"Efficient frontier" (colgándola directamente de `df_opportunity_cost`), el layout de 6 ramas
paralelas bajo el nodo central seguiría siendo legible, aunque con 6 columnas en la fila superior
el diagrama ya empieza a sentirse ancho — vale la pena considerar agrupar visualmente las que
son hojas terminales (`df_deltas_valid`, y potencialmente `df_el` si se confirma que no alimenta
nada más) separadas de las que sí continúan la cadena.

## 0403_KMeans_Raw

Note: this notebook's two PNGs were generated today, in this same session, via a Graphviz
script (`assets_ignored/claude_docs/diagram_canon_generate.py`) derived from git-history mermaid,
not by the "Claude Design" lineage under audit. Audited with the same rigor regardless, purely
from the notebook's code/markdown (git-history mermaid was not consulted).

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Derivación real: `pienza.db (offers + engineered_features)`
alimenta, de forma independiente, tanto Phase 2 (`2.1` — k-tournament k=2/k=6 sobre los 3
features físicos crudos, cell 6) como Phase 4 (`4.1` — clustering purificado sobre `base_fare`,
cell 13, que corre su propia query SQL independiente `query_subsidy` y su propio KMeans). Phase 2
alimenta Phase 3 (rate analysis usa `profiles_k6`, cell 10), Phase 5 (incentive analysis usa
`archetype_name` adjuntado a `df_master` en Phase 2, cell 19) y Phase 6 (EPH panel, también usa
`archetype_name`, cell 23). Phase 4 es un callejón sin salida — no alimenta a Phase 3/5/6 (correcto,
es un análisis paralelo autocontenido, confirmado porque `profiles_purified` y `df_incentives` no
reaparecen fuera de las cells 13/15/16). El PNG refleja exactamente esta topología: dos padres
independientes desde la fuente, Phase 2 con tres hijos (3, 5, 6), Phase 4 sin hijos.

**Legibilidad gestáltica:**
Correcto. Flujo top-down consistente, un solo salto de "codo" (Phase 2 → Phase 3, giro a la
izquierda) pero es corto y no cruza otros nodos. Los 3 hijos de Phase 2 (3, 5, 6) están agrupados
en la misma fila, alineados limpiamente. Jerarquía visual clara: fuente arriba, hojas abajo.

### Diagrama B

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Sigue el lineage variable por variable: `pienza.db`
→ `df_master` (query maestro, cell 3) y → `4.1: df_incentives` (query separado, cell 13) como dos
ramas independientes, igual que en A. `df_master` → `2.1: k=2/k=6 tournament (features_core)` →
`profiles_k6` → `df_master (+cluster_fisico, +archetype_name)` (correcto: cell 6 asigna
`cluster_fisico` y `archetype_name` de vuelta a `df_master`) → tres hojas: `3.1: rate analysis`,
`5.1: incentive frequency`, `6.1/6.2: eph_profile`. La rama derecha: `df_incentives` →
`profiles_purified` (purified archetypes, cell 13) → `4.2: dual-economic plot` (cell 15). Cada
nodo y cada flecha corresponde a una variable/paso real verificado en el código.

**Legibilidad gestáltica:**
Correcto. Árbol limpio top-down, dos ramas bien separadas espacialmente (izquierda = flujo
principal df_master, derecha = flujo purificado), sin cruces de líneas, nodos del mismo nivel
lógico alineados en la misma fila.

---

## 0604_ETL_cGAN_to_BigQuery

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Phase 1 (setup, auth de BigQuery/GCS, cell 2) alimenta
tanto Phase 2 (training set → GCS staging + external table, cell 4) como Phase 3 (synthetic
manifold → GCS staging + external table, cell 6), ambas ramas independientes entre sí que solo
comparten el cliente autenticado en Phase 1. Ambas convergen en Phase 4 (verificación de conteo de
filas por tabla, cell 8, que efectivamente itera sobre `['gan_training_set_v8_reference',
'synthetic_manifold_v8']`, las dos tablas creadas en Phase 2 y Phase 3). El PNG coincide
exactamente: un padre (Phase 1) con dos hijos (Phase 2, Phase 3), ambos convergiendo en un nodo
final (Phase 4).

**Legibilidad gestáltica:**
Correcto. Flujo top-down impecable, las dos ramas paralelas (Phase 2/Phase 3) están alineadas en
la misma fila, sin cruces, jerarquía clara de arriba hacia abajo.

### Diagrama B

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Dos cadenas idénticas y paralelas confirmadas en el
código: `local parquet df_gan_training_set_v8.parquet` → `GCS: pienza-streamlit (uploaded if
missing)` → `BQ external table gan_training_set_v8_reference` (cell 4, función `sync_to_staging` +
`create_external_table`), y en paralelo `local parquet 260426_cGAN_manifold_v8.parquet` → `GCS:
pienza-streamlit (uploaded if missing)` → `BQ external table synthetic_manifold_v8` (cell 6,
función `deploy_synthetic_manifold_v8`). Ambas tablas BQ convergen en `row-count verification
(client.query per table)` (cell 8, correcto — el loop de verificación consulta exactamente esas
dos tablas).

**Legibilidad gestáltica:**
Correcto. Dos columnas paralelas perfectamente simétricas y alineadas por fila, convergencia
limpia al final, sin cruces de líneas, fácil de seguir de un vistazo.

---

## 0605_cGAN_denormalization

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado — incluyendo un detalle no trivial que el diagrama
capturó bien: el nodo `local parquet: 260426_cGAN_manifold_v8.parquet` tiene dos hijos, uno hacia
Phase 1 (carga inicial en Spark, cell 5, `df_manifold`) y otro directo (salto largo) hacia Phase 5
(cell 30, donde `df_facts = spark.read.parquet(PATH_MANIFOLD)` vuelve a leer el mismo parquet
local desde cero, como variable separada de `df_manifold`, no reutilizándolo). Esto es real en el
código, no un artefacto inventado. Cadena principal confirmada: Phase 1 → Phase 2 (BigQuery
destination config + GCS staging, cell 8) → Phase 3 (master zone dictionary, 89→67 zonas, cells
11-21) → Phase 4 (persistencia de diccionarios, cells 25-27) → Phase 5 (triple join, recibe tanto
el parquet local fresco como los diccionarios de Phase 4, cell 30) → Phase 6 (escritura a
BigQuery + validación, cells 33-37) → nodo final "validated by 0606/0607".

**Legibilidad gestáltica:**
Mayormente correcto, con una observación menor: el salto largo desde el nodo raíz hasta Phase 5
(curva por la izquierda, saltándose 4 fases) es exactamente el tipo de conexión que suele generar
drift en otras pasadas, pero aquí está bien resuelto — la curva es suave, no cruza ningún otro
nodo, y es visualmente distinguible de la cadena principal. Aun así, un lector rápido podría
tardar un segundo en notar que ese nodo raíz tiene dos flechas de salida en direcciones muy
distintas (una recta abajo a Phase 1, otra curva larga a la izquierda hasta Phase 5); se podría
mejorar separando más los orígenes de ambas flechas en el nodo fuente. Por lo demás: flujo top-down
consistente, nodos alineados, jerarquía clara.

### Diagrama B

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Confirmé cada nodo contra el código: `local parquet` →
`df_manifold (Spark DataFrame, Phase 1)` (cell 5); `BigQuery: real zone geography` → `Master zone
lookup table (P_/C_ axis reconciliation)` (cell 11, lectura de `silver_palette`); `df_manifold` y
`lookup` ambos alimentan `Geographic purge + ghost recovery (67 survivors of 89 zones)` (cells
15-19, join contra `df_active_keys` derivado de `df_manifold`); esto alimenta `df_full_dict`
(cell 25, reconstrucción P_+C_+Unassigned filtrada); `df_full_dict` alimenta tanto `Pickup
dictionary (mirror of dropoff)` (cell 27) como directamente `Dictionaries persisted to local
parquet` (cell 25 guarda el diccionario de dropoff/producto; cell 27 guarda el de pickup) — el
diagrama muestra correctamente que ambas ramas (dropoff dict y pickup dict) confluyen en el nodo
de persistencia. `local_pq` también alimenta `df_facts (manifold re-read fresh, Phase 5.1)`
(cell 30, la misma relectura fresca ya notada en el diagrama A) y `dict_parquets` alimenta
`df_dim_prods/df_dim_drop/df_dim_pick (re-read fresh, Phase 5.1)` (cell 30, los tres `spark.read.
parquet` de los diccionarios). Ambos confluyen en `Triple broadcast join` → `df_final` (cell 30) →
`Segmented BigQuery upload (zipWithIndex, sequential chunking)` (cell 33, confirmado el uso de
`rdd.zipWithIndex()` en vez de `monotonically_increasing_id()`) → `synthetic_manifold_v8_enriched`
→ `Route-control + geospatial native BigQuery audits` (cells 35 y 37, las dos validaciones en la
nube). Ningún nodo ni flecha inventados; ningún padre/hijo faltante.

**Legibilidad gestáltica:**
Aceptable pero con más fricción visual que el resto de los diagramas auditados. El diagrama usa
dos columnas (izquierda: parquet local → df_facts; centro-derecha: lógica de zonas) que convergen
recién en "Triple broadcast join", lo cual está bien conceptualmente, pero en el tramo central
(`df_full_dict` → `Pickup dictionary` → `Dictionaries persisted...`) hay una curva que se dobla
hacia la izquierda por debajo de "Pickup dictionary", generando un cruce visual leve con la línea
recta `df_full_dict → Dictionaries persisted`. También el punto de convergencia principal
("Triple broadcast join") recibe una flecha larga desde la columna izquierda y otra desde la
columna derecha, obligando al ojo a rebotar horizontalmente en ese punto. No es un error de lógica
— es puramente una fricción de lectura en un diagrama con más nodos (14) que los demás notebooks
auditados.

---

## 0606_cGAN_downscaling

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Confirmé el lineage leyendo las celdas de código de
cada fase: BigQuery ingest (`df_synthetic`, `df_real`, cell 3) → Phase 2 (`id_map`, disambiguación
reforma_social/tecamachalco, spatial join, cell 6) → Phase 3 (motor de downscaling con outer join
+ rounding guard, cell 11) → Phase 4 (inyección de nombres micro + guardado parquet, cell 18) →
{Phase 5 (upload a GCS + external table, cell 21), Phase 6 (re-forja de diccionarios pickup/dropoff,
cells 24/26)} → Phase 6 → `observatory/utils/gcp_client.py` (lee `dim_pickup_micro`/`dim_dropoff_
micro`, según el propio comentario del código). El split Phase 4 → {Phase 5, Phase 6} en paralelo
(sin Phase 5 → Phase 6) es correcto: son dos ramas independientes que consumen el mismo
`df_synthetic` final, no una cadena secuencial.

**Legibilidad gestáltica:**
Correcto. Flujo vertical limpio de arriba a abajo, único punto de bifurcación (Phase 4 → Phase 5 /
Phase 6) bien alineado en la misma fila, sin cruces de líneas. Fácil de seguir de un vistazo.

### Diagrama B

**Exactitud lógica:**
Hay drift real, dos discrepancias concretas:

1. **`gdf_polygons` no nace de `df_real`.** El PNG dibuja una cadena lineal única
   `df_real → gdf_polygons → joined`, pero el código (cell 6) muestra que `gdf_polygons` se carga
   de forma independiente desde un archivo externo (`gpd.read_file(".../poly.geojson")`), y que el
   verdadero encadenamiento es: `df_real` → (limpieza de nulos + construcción de puntos) →
   `gdf_pickups`; por separado, `poly.geojson` → `gdf_polygons`; ambos se combinan en
   `gpd.sjoin(gdf_pickups, gdf_polygons, ...)` → `joined`. El diagrama omite tanto el nodo
   intermedio `gdf_pickups` como la fuente externa real de `gdf_polygons`, y en su lugar inventa
   una dependencia directa `df_real → gdf_polygons` que no existe en el código.

2. **`mini_agg` (`df_mini_dropoffs`/`df_mini_pickups`) tiene un padre faltante.** El PNG muestra
   `joined → mini_agg` como única entrada, pero cell 11 confirma que `df_mini_dropoffs` se
   construye directo desde `df_real.groupby(...)` (no pasa por `gdf_polygons`/`joined` en
   absoluto — esa ruta es exclusiva de los pickups). El dropoff path bypasea completamente el
   spatial join. Falta la flecha `df_real → mini_agg` en paralelo a `joined → mini_agg`.

3. **El "downscaling engine" tiene un segundo padre faltante.** Cell 11 muestra que
   `gan_p = df_synthetic.groupby('pickup_zone_id')...` — es decir, el motor de downscaling
   consume tanto `mini_agg` (proporciones reales) como `df_synthetic` (volúmenes GAN a
   redistribuir) directamente. El diagrama solo dibuja `mini_agg → downscale`, sin ninguna flecha
   de salto largo desde `df_synthetic`/el ingest original hacia el motor de downscaling — es
   exactamente el tipo de "arista de salto largo perdida" mencionado en la metodología.

4. **`audit` está mal insertado como paso serial, cuando en realidad es una rama lateral de
   diagnóstico.** El PNG dibuja `downscale → audit → df_synthetic_final`, implicando que el
   resultado de la auditoría de fidelidad alimenta la inyección de nombres. Pero el código (cells
   13/15 auditoría vs. cell 18 inyección) muestra que `audit_p_df`/`audit_d_df`/`mae_p`/`mae_d`
   son solo de impresión/diagnóstico y nunca se usan en cell 18 — la inyección usa directamente
   `downscale_p`/`downscale_d` (la salida del motor de downscaling), no la salida de la auditoría.
   `audit` debería ser una hoja lateral (`downscale → audit` como rama muerta), no un eslabón
   intermedio antes de `df_synthetic_final`.

**Legibilidad gestáltica:**
Buena en general: columna vertical única, sin cruces de líneas, bifurcación final (GCS upload /
diccionarios) bien alineada en la misma fila. El problema es puramente de exactitud lógica (arriba),
no de legibilidad — el diagrama es fácil de leer, solo que lo que muestra no es lo que el código
realmente hace en varios tramos.

---

## 0607_cGAN_TSTR

### Diagrama A

**Exactitud lógica:**
Verificado correcto, sin drift detectado. Coincide exactamente con las fases del notebook:
BigQuery (`v_ML_Supervised` + `synthetic_manifold_v8_enriched`) → Phase 1 (blueprint de
features/target, cell 7) → Phase 2 (TRTR: extracción, unificación de tiers, entrenamiento en real
W1-5, evaluación en real W6, cells 10-18) → {`trtr_f1`, Phase 3 (TSTR: entrena en manifold
sintético, evalúa en el mismo holdout W6, cells 20-23)} → `tstr_f1` → veredicto de paridad
predictiva (`tstr_f1 / trtr_f1`). Ambos F1 confluyen correctamente en el nodo final.

**Legibilidad gestáltica:**
Correcto. Árbol limpio de arriba a abajo, bifurcación Phase 2 → {trtr_f1, Phase 3} bien alineada,
convergencia final de `trtr_f1`/`tstr_f1` en el veredicto sin cruces. Fácil de seguir.

### Diagrama B

**Exactitud lógica:**
Este es el diagrama con más drift del lote — encontré tres discrepancias concretas, confirmadas
recortando la imagen en zonas específicas para verificar el trazo exacto de cada flecha:

1. **`df_holdout_real` queda huérfano (sin flecha de salida), y su hijo real aparece colgado del
   nodo equivocado.** El PNG dibuja `real → holdout` como una hoja muerta (sin salida), y separado,
   `model_trtr → holdout_eval` (el nodo etiquetado "X_test_L1_TRTR, y_test_L1_TRTR (from
   df_holdout_real)"). Pero el código (cell 16) construye `X_test_L1_TRTR`/`y_test_L1_TRTR`
   directamente desde `df_holdout_real` (features + target del holdout) — `model_bouncer_TRTR` no
   participa en absoluto en construir esas variables, solo las consume después
   (`model_bouncer_TRTR.predict(X_test_L1_TRTR)`). La flecha real debería ser
   `df_holdout_real → holdout_eval`, no `model_trtr → holdout_eval`.

2. **Cableado cruzado entre las ramas TRTR y TSTR.** Recortando la zona donde
   `y_synth_encoded` y `holdout_eval` convergen en un bus horizontal compartido antes de
   bifurcarse hacia `trtr_f1` y `model_bouncer_TSTR`: el trazo muestra `y_synth_encoded` uniéndose
   a esa barra y bajando hacia `trtr_f1`, mientras `holdout_eval` baja hacia
   `model_bouncer_TSTR`. Es exactamente al revés de la lógica real: `y_synth_encoded` (el target
   codificado del manifold sintético) alimenta el **entrenamiento** de `model_bouncer_TSTR` (cell
   21), y `holdout_eval` (`X_test_L1_TRTR`/`y_test_L1_TRTR`, el holdout real W6) alimenta el
   **cálculo de `trtr_f1`** junto con `model_bouncer_TRTR`. El diagrama tiene las dos ramas
   intercambiadas.

3. **`trtr_f1` tiene una flecha inventada hacia `tstr_f1`.** Confirmado con un recorte de esa zona
   exacta: hay una línea que sale de `trtr_f1 (baseline)` y baja directamente para alimentar
   `tstr_f1 (challenger)`, cuando en realidad `trtr_f1` y `tstr_f1` son dos métricas hermanas
   e independientes que solo deberían converger en el nodo final "Predictive parity verdict"
   (igual que en el propio Diagrama A de este mismo notebook, que sí lo dibuja bien). En el
   código no existe ninguna dependencia de `tstr_f1` sobre `trtr_f1` — el classification_report de
   TSTR (cell 23) no toca `trtr_f1` para nada. Es una conexión completamente inventada, y de paso
   dejó a "Predictive parity verdict" sin su flecha directa de `trtr_f1` (solo le llega desde
   `tstr_f1`).

4. **Falta la arista de reutilización de `X_test_L1_TRTR` entre TRTR y TSTR.** El código confirma
   que `model_bouncer_TSTR.predict(X_test_L1_TRTR)` (cell 23) reutiliza la misma matriz de holdout
   que ya se construyó para TRTR — es la pieza central del diseño experimental (ambos modelos se
   evalúan sobre exactamente el mismo holdout). El diagrama no dibuja ningún vínculo entre
   `holdout_eval` y `tstr_eval`, perdiendo justo ese salto largo que sería el hallazgo más
   importante de la trazabilidad de variables en este notebook.

**Legibilidad gestáltica:**
Con problemas, independientes de la lógica. La zona de la bifurcación cruzada (hallazgo 2) usa un
bus horizontal compartido entre dos pares fuente/destino — un patrón que ya es ambiguo de leer aun
si las conexiones fueran correctas, porque un humano no puede saber a simple vista cuál línea
entra a cuál nodo cuando comparten el mismo tronco. Sumado al hallazgo 3 (la flecha larga de
`trtr_f1` bajando en paralelo, cruzando visualmente cerca del nodo "predict on same X_test_L1_TRTR
holdout" antes de llegar a `tstr_f1`), esta sección central del diagrama es genuinamente difícil de
seguir de un vistazo, más allá de que además esté mal.

---

## 0608_Bridge_to_Markov_Network_Graph

### Diagrama A

**Exactitud lógica:**
Hay un drift real, aunque menor: el PNG dibuja dos columnas paralelas totalmente independientes —
Phase 1 → Phase 2 (grafo físico) por un lado, y Phase 3 → Phase 4 (tensor de movilidad → grafo
funcional) por otro — que solo convergen en Phase 5. Pero el código (cell 31) muestra que Phase 3
(el filtro de sistema cerrado) depende directamente de `G_manual` — la salida de Phase 2 —, no solo
del manifold sintético: `pienza_polygons = list(G_manual.nodes())` se usa como la lista oficial de
72 polígonos para colapsar cualquier zona externa a `unassigned_area`. Falta una flecha de Phase 2
hacia Phase 3 (un salto cruzado entre las dos columnas antes de la convergencia final en Phase 5),
que el diagrama omite al tratarlas como dos ramas completamente paralelas.

**Legibilidad gestáltica:**
Correcto. Dos columnas paralelas bien alineadas por fila, convergiendo limpiamente en Phase 5 →
Phase 6, sin cruces. Fácil de seguir (el problema es solo de exactitud, no de lectura).

### Diagrama B

**Exactitud lógica:**
Este es el diagrama más grande del lote (~19 nodos) y tiene el hallazgo más grave de todo el
audit — una conexión inventada en la zona de convergencia física/funcional que el prompt pedía
revisar con cuidado especial:

1. **Conexión inventada: `G_functional → Q_ij`.** Confirmado recortando esa zona exacta: hay una
   flecha curva que sale de `G_functional (directed functional graph)` y se fusiona visualmente
   con la flecha de `V(s) → Q_ij` justo en la punta de flecha de `Q_ij`. Pero el código (cell 77)
   es inequívoco: `Q_ij = np.where(P_ij > 0, R_ij + (gamma * V), 0)` — `Q_ij` depende únicamente
   de `P_ij`, `R_ij` y `V`. `G_functional` (el grafo dirigido usado para PageRank/betweenness/line-
   graph en la sección 4.8) no participa en absoluto en el cálculo de `Q_ij`; son dos ramas
   analíticas completamente distintas (una es centralidad de grafos, la otra es value iteration de
   un MDP) que el diagrama fusiona indebidamente.

2. **Arista faltante en su lugar: `P_ij / R_ij → Q_ij`.** La misma línea de código anterior confirma
   que `Q_ij` reutiliza `P_ij` y `R_ij` directamente (no solo indirectamente vía `V(s)`, que ya
   colapsó esos dos términos en un valor escalar por estado). El nodo `P_ij / R_ij` en el diagrama
   solo tiene una salida dibujada (hacia `V(s)`); le falta la segunda flecha de salto largo hacia
   `Q_ij` que el código sí ejecuta. Es probable que la conexión inventada del hallazgo 1 haya
   reemplazado a esta arista perdida durante alguna pasada previa.

3. **Arista faltante: `gdf_f → mobility_tensor`.** Cell 43 construye
   `ordered_zones = sorted(list(gdf_f['name'].unique()))`, que define las 72 dimensiones
   origen/destino del tensor — es decir, `gdf_f` alimenta directamente la construcción del tensor,
   no solo `G_manual`/`df_synth`. El diagrama no dibuja esa arista de salto largo desde `gdf_f`
   (definido varias filas más arriba) hasta `mobility_tensor`.

4. **Ciclo real simplificado a cadena lineal en `gdf_f`/`G_manual`.** Cell 10 muestra que el orden
   real es: `36 manual routes → G_manual` (solo nodos/aristas, sin atributos) → `mentioned_nodes =
   G_manual.nodes()` → `gdf_f = gdf_nodes[gdf_nodes['name'].isin(mentioned_nodes)]` (filtro) →
   de vuelta a `G_manual` (esta vez para inyectarle atributos geográficos desde `gdf_f`). Es un
   ciclo de dos pasadas sobre `G_manual`, no una cadena acíclica. El diagrama dibuja
   `gdf_nodes → gdf_f → G_manual` como si `gdf_f` naciera de un filtro independiente de las rutas,
   omitiendo que el propio `G_manual` (ya construido desde las rutas) es el que determina qué
   filtra `gdf_f` en primer lugar.

**Legibilidad gestáltica:**
Con problemas, concentrados exactamente en la zona de convergencia que el prompt señalaba. La
curva de `G_functional → Q_ij` (hallazgo 1) cruza por encima de la flecha recta `V(s) → Q_ij` y se
fusiona con ella justo en la punta, haciendo prácticamente imposible distinguir a simple vista que
son dos líneas distintas — un humano leería eso como una sola flecha con un origen ambiguo. Aparte
de ese punto, el resto del diagrama (~19 nodos) se mantiene sorprendentemente ordenado para su
densidad: dos columnas temáticas claras (física/topológica a la izquierda, tensor/económica a la
derecha) que fluyen de arriba a abajo sin más cruces graves, y la fila final de exports CSV está
bien alineada. La única otra fricción notable es la línea diagonal larga `mobility_tensor →
df_arcos`, que cruza visualmente por delante de la columna izquierda (`G_manual`) en su camino
hacia abajo — no es un error, pero obliga al ojo a rebotar de la columna derecha a la izquierda en
un punto donde el resto del diagrama es limpiamente vertical.
