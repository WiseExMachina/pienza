 

 Project Pienza es un proyecto personal de Data Science anclado a la realidad de las calles de la Ciudad de México. El proyecto inició en Julio 2025 en paralelo al certificado de 1 año de Data Scientist del Tecnológico de Monterrey. En ese entonces había cumplido ya 2 años como conductor de plataformas de Ride-Hailing. 

 Siendo exatec (LAF '19), lo que empezó como un trabajo temporal post-pandemia como transición de Monterrey a CDMX, se terminó conviertiendo en un trabajo de tiempo completo. El certificado lo inicié con el propósito de emplearme formalmente al terminarlo en 2026... el problema: sin experiencia corporativa reciente, aún con el certificado, me encontraría en desventaja.

 Así que, desde sus inicios, planié este proyecto desde cero. En vez de practicar con datasets públicos, preferí ensuciarme las manos un poco y armar mi propio dataset anclado a mi realidad como conductor. 
 
 Casi todos los estudios de Ride-Hailing que encontraba eran sobre datos agregados y en ciudades como San Francisco y Nueva York. Y la bella y caótica CDMX? Al no encontrar ningún estudio público, me dije, qué mejor razón que yo proponer el mío. 
 
 Con 1 año como fecha limite y con RL como la absoluta frontera, decidí irme profundo y aprovechar mis conocimientos de pregrado de economía y finanzas para aplicarlos a la realidad de la micro-economía gig de la Ciudad de México. 

 El objetivo: que un algortimo de ML aprenda lo que yo, y replique mi política de decisiones como conductor. Al ser bastante repetitivo y cuasi-determinista, me pregunté, podría enseñarle a una IA, mi estrategia de aceptación/rechazo de viajes?  Que aprenda que no todos lo rechazos son iguales? Que es mejor rechazar un viaje de Santa Fe a Polanco un viernes en la tarde, pero si ya voy a terminar la sesión entonces los viajes que van hacia casa tienen mayor probabilidad de aceptación? 

Después de diferentes iteraciones a prueba y error, terminé construyendo dos motores de ingesta: 
 1.  Una webapp que va capturando en campo y en tiempo real todos los timestamps + posicion geografica de los eventos  típicos de una misón, desde T0 buscando viajes, aceptación, recogida, espera... hasta finalizacón. 
 2. Mientras que el primer motor captura lo que ocurre, no cuenta la historia completa. La otra parte implicaría capturar todo lo que aparece sobre mi pantalla, de tal manera que quedara registrado todas aquellas ofertas rechazadas,junto con sus tiempos, destinos, etc. 

 Así, durante 6 semanas, armé un dataset de 256 viajes aceptados y completados (motor 1) y 4700 ofertas capturadas y procesadas via Gemini API (motor 2).

 Para que esto funcionara este dataset debía ser un espejo fiel de mi realidad, primero conductor, luego científico. El dataset se tenía que acoplar a mis tiempos, y no al revés a fin de capturar más datos. Como acostumbro a tomar dos shifts de 3-4 horas cada uno, uno por la mañana y otro por la tarde, lo que hice fue etiquetar cada viaje rechazado - y aquellos pocos aceptados - capturados via OCR, estrictamente después de cada sesión.

Diseñé 6 etiquetas de rechazo mutuamente excluyentes (aunque debo aceptar que al principio sí tenía mas de una clase por observación, pero vi como esto se podría convertir en una complicación innecesaria más adelante) diseñadas para mimicar el procoeso cognitivo de por que decido si aceptar o no un viaje. Con una tasa de aceptación de apenas el 7%, las etiquetas canónicas son las siguientes:

 Viabilidad geógrafica: 
  1. dropoff_non_operational
  2. dropoff_proxy
Viabilidad económica:
 3. long_pickup_time
 4. low_profitability
 Clases nuanced:
 5. strategic_mismatch
 6. expected_value_gamble
 7. NULL -> aceptación

Al diseñarlo así, pretrendí ortogonalizar mis decisiones al asignar  solamente 1 etiqueta por observación, al final del día, aunque un viaje oudeira teneer mas de 1 etiqueta, ese orden representaba el punto de quiebre al momento de la decisión.

 Así, este periodo de adquisición duró 6 semanas, del 22 de agosto al 1 de octubre de 2025. Desde su concepción el proyecto sería exclusivamente de carácter investigativo, así que la no viabilidad de que existiesen estas etiquetas humanas en producción sería una feature, no un bug. 


 Octubre y Noviembre constituyeron la fase de limpieza de datos, reconciliacion vs los records oficiales de la plataforma, y la creación de pienza.db, al final del día, no podría llamarme Data Scientist si no sabría SQL, así que fue la excusa perfecta para  aprender el resto del año a haceer queries con los mismos datos que yo diseñé y viví en la calle.

 Asimismo, me di cuenta de que mientras el motor 1 GTS WebApp me ayuba a tener KPIs y metricas sobre lo ocurrido como deadhead, payout spread promedio, etc. Este no estaba siendo capturado por el dataset principal del stream de ofertas que fungiría como vector de entrada para ML. Ya había hecho ingeniería de características como traffic_index, driver_state_at_request, pero todos los KPIs arrojados por la webapp no se habían aprovechado. Hasta este punto, la maxima granularidad temporal era HH:MM arrojado por la captura de pantalla, pero accidentalmente, al intentar extraer la localizacion via metadata de las caputas, me di cuenta que éstas tenían granularidad a segundos, y corri un script para extraer esta información. Esto desbloqueo la ingeniería de features como offer_density, ag_rolling_deadhead_sec, time_since_last_offer_sec, etc.


 ERD image


Antes de entrar de lleno a ML, y aplicando el principio de parsimonia, decidí indagar y responder todas aquellas preguntas de negocio utilizando estadística clásica y economía conductual. Así, diseñé un playbook que analiza los tiempos de espera racionales, cuando uno está siendo selectivo, antes de que esa oferta futura "mejor" se diluya por el tiempo que uno pasó buscándola.



Así, también, uno de los hallazgos más interesantes para mi fue entender - con datos duros - cómo es la estructura de pagos de la plataforma. Yo sabía que si un viaje se extiene, esté no se compensa a la par minuto a minuto, pero después de cierto tiempo, entonces ya hay una compensación. Así, logré convertir esta heurística tácita, en un modelo polinomial donde descubrí con analisis de residuales que la estructura es bastánte hetersedástica, el error estimado es mayor en tarifas altas que las bajas. Aunque sta estructura apunta hacia un mecanismo para que no se aumente deliveradamente los tiempos de un viaje, esta conclusión es meramente subjetiva. Pero al menos, aunque yo siempre procuraba terminar viajes antes o al tiempo estimado, a fin de tomar más viajes, el saber que existe una estructura fija y predecible, me ayudó a a tomar decisiones más acertadas.

No fue hasta Diciembre que me metí de lleno a ML, empezando por aprendizaje no supervisado para entender la estructura latente del mercado y mapear los hubs geográficos. Yo había hecho un geocoding de las 4,700 ofertas y confié ciegamente en que los resultaos serían los correctos. Sin embargo, al hacer un análisis de sombra, vi que los resultados del HDBSCAN, aunque parecían ser correctos por como se agrupaban las zonas, descubrí que muchos de mis datos eran espuria.

El pipeline para HDBSCAN era así:

text string -> geocoding lat lon -> cluster HDBSCAN 

El problema, aproximadamente la mitad de mis coordenadas no correspondían a la dirección de texto. Yo había confiado ciegamente en el geocoding sin hacer reverse geocoding para validar que se hubiera hecho correctamente. El cluster del AICM tenía direcciones de Cuajimalpa, el cluster del Pedregal direcciones de Santa Fe, etc.

Cuantificación de daños: Entre errores de limpiea donde propague una misma coordenada a direcciones diferentes y resultados erróneos del geocoding, esto representaba alededor de un 30-40% de las observaciones. Dado que el objetivo era clonarme y mas del 50% de mis rechazos eran meramente geográficos esto era inadmisibe. Dicimebre pasó de convertirse de un mes de ML a un mes de limpiar coordenadas. Aqui entendi que detrás del glamour de los nombres pomposos de los algoritmos de aprendizaje automático, hay mucho, mucho trabajo de limpieza. 

Para remediar esto, volví a correr el pipeline de geocoding (esta vez bounded a CDMX y con reverse geocoding) dibuje 72 microzonas del sector poniente de la ciudad a fin de validar que las coordenadas cayeran dentro del poligono del texto crudo. Una vez limpio HDBSCAN corrió sin problema dando como resultado 44 hubs geógráficos, esta vez sí con un dataset limpio (paridad 95%). (Destaca que tras la limpieza el surgió el Hub Tacubaya, cuyas direcciones de texto "Calle Insurgentes Tacubaya, Juarez...." antes apuntaban hacia la col. Juarez). 

Enseguida, y antes de iniciar la fase supervisada, descubrí H3. Por fin pude darles nombre a los hexágonos que yo veo en pantalla todos los días, que rigen las zonas y horarios de incentivos. Pero más que ello, entendí como Uber ya había resuelto exactamente los mismitos problemas a los que yo me estaba enfrentando de primera mano como científico de datos, yo con un dataset minúsculo, ellos a escala global. Aunque podia usar la grilla H3 con alguna resolución optimizada para prevenir el sobreajuste en base a la alta cardinalidad de microzonas y densidad variable de mis datos, prefería usar los poligonos que dibujé a fin de preservar la explicabilidad.


Con un vector de entrada limpio, la fase de aprendizaje supervisado duró apenas 1-2 semanas, al iniciar el año en enero 2026. Sabía también que no quería entrar directo a XGBoost, así que inicié desde Naive Bayes, solo para establecer un baseline. Con regresión logística, me di cuenta de que mi problema sí era bastante lineal, pues ya daba una macro F1 aceptable. No hubiera habido problema haberme quedado allí salvó que XGBoost sí presentó una mejora respecto a LogReg, probando así que, aunque pequeña, una parte de mis decisiones siguen una estructura no-lineal, que solo se puede explicar con árboles y modelos más robustos.


Con un dataset de coordenadas limpio, y tras ver cómo hacer geocoding implicaba muchísimo trabajo de limpieza, no importaba cuán exitoso habría sido mi XGBoost, en inferencia en vivo, jamas funcionaría. Así que se me ocurrió... ¿y si aprovecho este dataset texto -> zonas, de 4K observaciones que yo mismo limpié, y entreno un modelo clasificador de NLP que prediga la zona en base a la dirección sucia que arroja la plataforma? Y así nació miniBabel, un transformer con un resultado del 84% de accuracy, diseñado para inferencia local. 

Para febrero ya tenía dos activos de ML -> un pkl que representaba un clon digital de mi logica de decisiones como conductor, y un transformer para evitar pasar por limpieza de coordenadas de nuevo. Pero sabiendo que esto jamás escalaría hacia otros conductores o a inferencia en vivo, decidí que el proyecto siguiera hacia simulaciones generativas. 

Así entrené un cGAN via Keras con la física principal de la oferta, pues los incentivos (surge, turbo, etc) sufrieron de mode collapse al tener poca representatividad, y cree un manifold sintético de 1M filas (el mínimo para poder llamarle apenas big) hosteado en GCS y consultado en BigQuery. Aproveché entonces para migrar pienza.db a la nube tmb.

Así, en adelante el proyecto contaría con dos datasets:
pienza_mini -> datos reales hosteados en BigQuery
pienza_big -> 1M datos sinteticos como entrada para simulaciones posteriores.


///// Aunque en sus inicios el proyecto inició con un IDE apenas versionado, al ver que todo el flujo sería en libretas Jupyter (Colab), el control en Git se detuvo, pues no había encontrado la manera de hacerlo via Colab, aunque existía la manera, nunca lo formalicé. Pero como sabía que todo proyecto serio debía ser versionado en Git, a partir de enero empezé a haceerlo mediante una libreta dedicada exclusivamebte para versionar (Pienza Git Control), aunque fuera de manera arcaíca no IDE nativa. (es por eso que los primeros gits consistentes fueron a partir de enero). /////


Febrero y Marzo se lo dediqué a documentar la evolución del proyecto en Latex, mismo que servía como Knowledge Base para cualquier LLM/IA, así como utilizar el manifod sintetico y convertirlo en un grafo para hacer análisis de redes. 
Entonces, construí un grafo no dirigido de conectivdidad de zonas (usando los 72 poligonos como nodos) y un grafo dirigido mediante un tensor (mostrar tensor). 

 (((( a partir de aqui ya me cansé dew escribir pero lo dejo como WIP))))
Con esto, podría llevar el proyecto hacia el siguiente nivel: optimización dinámica mediante Markov Decision Processes. Aunque mi pkl (XGBoost) había dado resultados favorables, sufría de una limitación que todo modelo de ML clasico sufre (y no había entendido al principio)... es snapshot indiference... es un algiritmo que aprendió sí, pero es estático, no está vivo, y es indiferente al contexto reciente. Aunque las stateful features pretenden resolver eso, cada oferta que analiza es aislada. Y es aquí donde ya entra el aaprendizajke por refuerzo que se sale del alacance del proyecto. 

Aún así, el proyecto culmina con el andamiaje necesario para llevar cavo RL full scale en una etapa futura con "Pienza 2.0: 'The Knowledge' in the Age of AI".

El proyecto culmina con el desarollo de la aplicación en Streamlit, diseñado deliberademente como un white-paper interactivo para que cualquier stakeholder, técnico y no técnico, pueda interactuar con el proyecto sin tener que entrar al repositorio o leer una sola línea de código. Dado que el desarollo de la app hubiese sido muy limitada si se hiciera dentro de Colab, aproveché para migrar todo el proyecto a Codespaces / VS Code y desde entonces ha seguido un control de versiones formal que se mantiene hasta la fecha.

FIN de la Historia.


Activos de Proyect Pienza:

- poly.geojson: 72 microzonas del sector poniente de la ciudad dibujadas a mano (google my maps)
- pienza_mini: una database limpia REAL de las 4,700 ofertas + 256 viajes completado que digitaliza la experiencia operativa de alta fidelidad del conductor.
- HDBSCAN_results: segmentación "natural" resultado de meituclosa limpieza de 4.7K coordenadas.
- pkl XGBoost: el clon digital que captural la logica de deciones del agente.
- miniBabel: un clasificador transformer text2zone diseñado para inferencia local
- .keras generator: un generador sintético condicional de ofertas de viaje hiperrealistas que respeta la distribución continua del de pienza_mini.
- pienza_big: mainfold sintetico generado por el .keras de 1M de observaciones.
- grafo_topologico: 72 nodos conectivad binaria de zonas.
- mobility_tensor: un tensor R ZxZxTXC creade con el manifold sintético. (andamio para MDP)
- grafo_dirigido: tnsor colapsado en matrix para hacer analisid de redes con grafo dirigido. 




COMO NAVEGAR EL REPOSITORIO:

yada yada



🚰 Data Lineage & State Boundaries

This repository executes a sequential pipeline. To prevent state contamination, data sources are strictly bound to Phases, regardless of the chronological order in which the notebooks were created.



Phase 1 (Ground Truth): Reads from raw Google Sheets and AppScript state machines.



Phases 2 through 5 (Data Eng & Modeling): * Starts at 0111_ETL_Big_Bang_pienzadb.ipynb.



From this point on, pienza.db is the absolute Single Source of Truth (SSoT). All feature engineering, EDA, and supervised/unsupervised ML models read exclusively from this local database.



Intermediate State: Any Parquet files, CSVs, or temporary outputs generated between notebooks are written strictly to dumped/files/. This directory is ephemeral; its contents can be safely deleted and regenerated at any time.



Phase 6 (Generative Moonshots): * Notebooks 0603 and 0604 act as the bridge, migrating pienza.db and synthetic cGAN manifolds to Google BigQuery.



Everything downstream of 0604 reads strictly from BigQuery.











🔭 The Observatory (Streamlit App)

The Observatory is the user-facing Digital Twin. It acts as the final consumer of the pipeline and operates under strict data routing and architectural rules.



Data Sourcing & Security:



The Primary Engine: The Observatory is entirely downstream of notebook 0604. It reads strictly from Google BigQuery.



Sensitive Data (PII): All PII and highly sensitive data resides in a secure GCS Lakehouse and is queried exclusively through BigQuery. Sensitive data is never stored locally in the repo.



Static Assets: Safe, shareable files (e.g., layout references, images, public JSONs) are tracked directly in the repository under observatory/assets/ and read locally by the Streamlit pages.



Code Architecture (Layer 1 Modularization):

To prevent UI reruns from tangling with data fetching, the Streamlit codebase uses a strict View/Model separation pattern:



pages/000X_Name.py (The View): Contains only UI code (st.title, st.plotly_chart, st.tabs). If it renders pixels, it lives here.



pages/_000X_data.py (The Model/Data): Every page has a hidden sibling module. This is where all BigQuery fetchers (wrapped in @st.cache_data), hardcoded literals, and heavy pandas transformations live.



Rule of thumb: The main file handles the layout; the hidden _data.py sibling does the heavy lifting