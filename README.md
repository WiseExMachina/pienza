<div align="right">

[![GitHub](https://img.shields.io/badge/-%E2%98%85%20Star-f6f8fa?style=flat-square&logo=github&logoColor=24292f)](https://github.com/WiseExMachina/pienza)
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-f6f8fa?style=flat-square&logo=linkedin&logoColor=0A66C2)](https://linkedin.com/in/bernardolw)

</div>

<div align="center">

<img src="./assets/logo_rectangular.png" alt="Project Pienza — Digital Twin · CDMX" width="220" />

*An ML framework to navigate Mexico City's ride-hailing marketplace*

<img src="./assets/readme_banner.png" alt="HDBSCAN geo-clustering → Cascade XGB classifier → Transformer NLP → cGAN 1M-row market" width="700" />

</div>

---

## Overview

Project Pienza is a research project grounded in the operational reality of Mexico City's streets. It grew out of two years driving in the ride-hailing gig economy, formalized into a year-long Data Science study. Rather than relying on public, aggregated datasets from cities like San Francisco or New York, the project builds its own ground-truth dataset from scratch: a six-week field capture of 4,700 real ride offers, each labeled in real time. (full story here → [STORY.md](./STORY.md))

**It is** — a policy-cloning research project — testing whether a model can learn one expert's heuristics well enough to explain them, not just predict them.

**It is not** — an attempt to reverse-engineer or audit any ride-hailing platform's pricing or dispatch algorithm. The platform is the environment; the driver executing that policy is the agent under study.

**Scope** — N=1 by design — single driver, single city, six weeks. Findings describe one expert's policy, not driver behavior in general.

<sub><b>Tech Stack:</b> Python · XGBoost · HDBSCAN · PyTorch · TensorFlow/Keras · SQLite → BigQuery · Streamlit · Kepler.gl · H3 · GCS</sub>

![Machine-discovered hubs — kepler.gl 3D](./assets/kepler_static.png)
<sub><i>44 HDBSCAN results (height = offer density) validated against 72 hand-drawn polygons. Color = cluster ID — full hub names and metrics are available via hover in the live Observatory dashboard.</i></sub>

## Interacting with the Project

There are three ways into this project, depending on how deep you want to go:

1. **The Observatory (Streamlit app)** — an interactive white paper, built so both technical and non-technical readers can explore the project's core findings without opening the repo or reading a line of code. This isn't a prototype dashboard — it's a full replica of the project's results.
   Live app: [pienza.streamlit.app](#) *(placeholder)*

2. **LLM-readable white paper** — a LaTeX-authored technical paper structured for machine context rather than linear human reading. Feed it to an LLM to ask FAQ-style questions about the project's methodology and findings.
   [View PDF](#) · [Download PDF](#) *(placeholders)*

3. **The repository itself** — full source, notebooks, and pipeline. Structure explained below.

## Data Lineage & State Boundaries

This repository executes a sequential pipeline. To prevent state contamination, data sources are strictly bound to phases, regardless of the chronological order in which the notebooks were created.

**Phase 1 (Ground Truth):** Reads from raw Google Sheets and AppsScript state machines.

**Phases 2 through 5 (Data Eng & Modeling):** Starts at `0211_ETL_Big_Bang_pienzadb.ipynb`. From this point on, `pienza.db` is the absolute Single Source of Truth (SSoT). All feature engineering, EDA, and supervised/unsupervised ML models read exclusively from this local database.

<sub><i>Intermediate State: Any Parquet files, CSVs, or temporary outputs generated between notebooks are written strictly to `data/dumped_files/`. This directory is ephemeral; its contents can be safely deleted and regenerated at any time.</i></sub>

**Phase 6 (Generative Moonshots):** Notebooks `0603` and `0604` act as the bridge, migrating `pienza.db` and synthetic cGAN manifolds to Google BigQuery. Everything downstream of `0604` reads strictly from BigQuery.

## Repository structure

### Top Level

```
pienza/
├── README.md                # you are here
├── STORY.md                 # the narrative — how and why this got built
├── The_Pienza_Papers/       # LaTeX white paper (Scientific + Executive)
├── notebooks_core/          # curated spine notebooks (numbered for traceability)
├── notebooks_full/          # full phase-by-phase history (40+ notebooks)
├── observatory/             # the Streamlit app
└── assets/                  # tracked README/portfolio images
```

### Core Notebooks

The polished core of the pipeline. These select notebooks have been refined for a high signal-to-noise technical review. They maintain their original ####_ file prefixes to preserve their lineage, indicating exactly which phase of the `notebooks_full` directory they belong to.

<pre>
notebooks_core/
├── <a href="./notebooks_core/0102_GTS_index.html">0102_GTS_index.html</a>                          # Engine 1 — GTS WebApp
├── <a href="./notebooks_core/0208_Stateful_Features_AppsScript.js">0208_Stateful_Features_AppsScript.js</a>          # stateful feature capture
├── <a href="./notebooks_core/0211_ETL_Big_Bang_pienzadb.ipynb">0211_ETL_Big_Bang_pienzadb.ipynb</a>              # ETL → absolute SSoT (pienza.db)
├── <a href="./notebooks_core/0305_EDA_Causal_Inference.ipynb">0305_EDA_Causal_Inference.ipynb</a>               # payout structure, residual analysis
├── <a href="./notebooks_core/0307_EDA_Optimal_Stopping_Playbook.ipynb">0307_EDA_Optimal_Stopping_Playbook.ipynb</a>      # rational wait-time / selectivity analysis
├── <a href="./notebooks_core/0403_KMeans_Raw.ipynb">0403_KMeans_Raw.ipynb</a>                         # early unsupervised pass, pre-geo-cleanup
├── <a href="./notebooks_core/0407_Clustering_Paper_Streamlit.ipynb">0407_Clustering_Paper_Streamlit.ipynb</a>         # HDBSCAN, 44 hubs / 72 microzones (final)
├── <a href="./notebooks_core/0509_WINNER_XGB_cascade_postablation.ipynb">0509_WINNER_XGB_cascade_postablation.ipynb</a>    # champion cascade classifier
├── <a href="./notebooks_core/0601_NLP_Transformer_miniBabel.ipynb">0601_NLP_Transformer_miniBabel.ipynb</a>          # address → zone transformer, 84% acc
├── <a href="./notebooks_core/0602_cGAN_Training.ipynb">0602_cGAN_Training.ipynb</a>                      # conditional GAN, synthetic offer generator
├── <a href="./notebooks_core/0603_ETL_pienzadb_to_BigQuery.ipynb">0603_ETL_pienzadb_to_BigQuery.ipynb</a>           # bridge: SQLite → BigQuery
├── <a href="./notebooks_core/0604_ETL_cGAN_to_BigQuery.ipynb">0604_ETL_cGAN_to_BigQuery.ipynb</a>               # bridge: synthetic manifold → BigQuery
├── <a href="./notebooks_core/0605_cGAN_denormalization.ipynb">0605_cGAN_denormalization.ipynb</a>               # rescale synthetic outputs to real units
├── <a href="./notebooks_core/0606_cGAN_downscaling.ipynb">0606_cGAN_downscaling.ipynb</a>                   # Apache Spark, obviously
├── <a href="./notebooks_core/0607_cGAN_TSTR.ipynb">0607_cGAN_TSTR.ipynb</a>                          # Train-Synthetic-Test-Real validation
└── <a href="./notebooks_core/0608_Bridge_to_Markov_Network_Graph.ipynb">0608_Bridge_to_Markov_Network_Graph.ipynb</a>     # network graph + MDP scaffolding
</pre>

### Full Notebooks

The complete, unedited research logs of the 6-phase pipeline. Preserved intentionally in their raw state, these notebooks document the authentic engineering journey—acting as an unpolished record of the experiments, pivots, and successful model iterations that power the final Observatory.

<img src="./assets/timeline.png" alt="Timeline: Phase 1 through Phase 7, Sep 2025 to May 2026" width="800" />

```
notebooks_full/
├── Phase_1_Acquisition_and_Ground_Truth/    # GTS WebApp (2 files)
├── Phase_2_Data_Engineering/                # ETL, temporal ledger, geospatial reconciliation (16 files)
├── Phase_3_Exploratory_Analysis/            # univariate/bivariate EDA, causal inference (8 files)
├── Phase_4_Unsupervised_ML/                 # PCA, KMeans, HDBSCAN, polygon zones (8 files)
├── Phase_5_Supervised_ML/                   # Naive Bayes → LogReg → XGBoost tournament (10 files)
└── Phase_6_Generative_Moonshots/            # miniBabel, cGAN, BigQuery migration (8 files)
```

### Observatory (Streamlit App)

The Observatory is the user-facing Digital Twin. It acts as the final consumer of the pipeline and operates under strict data routing and architectural rules.

**Data Routing & Security**

- **The Primary Engine:** The Observatory is entirely downstream of notebook `0604`. It reads strictly from Google BigQuery.
- **Sensitive Data (PII):** All PII and highly sensitive data resides in a secure GCS Lakehouse and is queried exclusively through BigQuery. Sensitive data is never stored locally in the repository.
- **Static Assets:** Safe, shareable files (e.g., layout references, images, public JSONs) are tracked directly in the repository under `observatory/assets/` and read locally by the Streamlit pages.

**Strict View/Model Separation**

To prevent UI reruns from tangling with data fetching, the Streamlit codebase uses a strict View/Model separation pattern. The main file handles the layout; the hidden `_data.py` sibling does the heavy lifting:

- `pages/000X_Name.py` (The View): Contains only UI code (`st.title`, `st.plotly_chart`, `st.tabs`). If it renders pixels, it lives here.
- `pages/_000X_data.py` (The Model/Data): Every page has a hidden sibling module. This is where all BigQuery fetchers (wrapped in `@st.cache_data`), hardcoded literals, and heavy pandas transformations live.

```
observatory/
├── main.py                  # home page + canonical sidebar
├── config.py                # page config, favicon
├── _main_data.py            # main.py's data/model sibling
├── pages/                   # 000X_Name.py (view) + _000X_data.py (model), 9 pages
├── components/              # styles.py — GLOBAL_CSS
├── utils/                   # bq_client.py, gcp_client.py — BigQuery/GCS fetchers
└── assets/                  # static, shareable assets (favicon, PDFs, HTML maps)
```

---

<sub><i>Project Pienza and all associated materials are the product of an independent research initiative, aimed at formalizing sequential decision boundaries in stochastic environments. The dataset and presented architecture are fully operational and derived from authentic, high-fidelity field telemetry captured via AI-assisted optical extraction pipelines during a controlled longitudinal observation window. All models reflect real empirical execution. To ensure strict compliance with applicable personal data protection regulations, third-party terms of service, and the privacy of proprietary information, all source assets were subjected to a multi-layered, non-destructive anonymization protocol, obfuscating the platform's proprietary metrics while fully preserving the mathematical properties, probability distributions, and behavioral physics of the underlying market. The content is not intended for, and should not be used for, any commercial, financial, or business operations.</i></sub>

---

<div align="center">
<sub><b>Bernardo Lozano Wise</b><br/>
bernardolw@gmail.com · <a href="https://linkedin.com/in/bernardolw">LinkedIn</a></sub>
</div>
