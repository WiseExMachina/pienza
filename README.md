
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