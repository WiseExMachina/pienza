<div align="center">

# 🚕 Project Pienza

### A digital twin of one driver's 4,700 ride-hailing decisions in Mexico City

**HDBSCAN geo-clustering → cascade XGBoost classifier → transformer NLP → cGAN-synthesized 1M-row market**

[![Live Dashboard](https://img.shields.io/badge/🔭_Observatory-Live_Demo-21918c?style=for-the-badge)](#)
[![Papers](https://img.shields.io/badge/📄_Pienza_Papers-Read_PDF-21918c?style=for-the-badge)](./The_Pienza_Papers/Pienza_Papers_Scientific.pdf)
[![Story](https://img.shields.io/badge/📖_The_Story-How_it_was_built-21918c?style=for-the-badge)](./STORY.md)

</div>

---

## What this is

A single expert agent — me, driving Uber in CDMX for two years — labeled every ride offer I saw in real time: what I accepted, what I rejected, and *why*, across a six-week field capture. That dataset became the input for a full ML pipeline that clones the decision policy, then extrapolates it into a synthetic market 200x larger than the source.

- **It is:** a policy-cloning research project — can a model learn *my* accept/reject heuristics well enough to explain them, not just predict them.
- **It is not:** an attempt to reverse-engineer or audit Uber's own pricing/dispatch algorithm. The platform is the environment; the driver is the agent under study.
- **Scope:** N=1 by design (single driver, single city, six weeks). Findings describe one expert policy, not driver behavior in general — see [Known Limitations](#known-limitations).

## Results at a glance

| | |
|---|---|
| **Real offers captured (OCR)** | 4,700 |
| **Completed trips (field-logged)** | 256 |
| **Acceptance rate** | 7% |
| **Geo hubs discovered (post-cleanup)** | 44, across 72 hand-drawn microzones |
| **Cascade XGBoost vs. logistic regression** | outperforms — confirms a nonlinear component in the decision policy |
| **miniBabel (address → zone transformer)** | 84% accuracy, local inference, replaces a paid geocoding API call |
| **Synthetic market (cGAN)** | 1,000,000 rows, hosted in GCS, queried via BigQuery |

## Pipeline

```
Acquisition (GTS WebApp + Gemini OCR)
        ↓
ETL → pienza.db (SQLite SSoT)
        ↓
Geo Remediation → HDBSCAN clustering (44 hubs / 72 microzones)
        ↓
Cascade Classifier (Naive Bayes → LogReg → XGBoost)
        ↓
miniBabel (NLP transformer, address → zone, local inference)
        ↓
cGAN → 1M-row synthetic manifold → BigQuery
        ↓
Network Graph / Mobility Tensor (MDP scaffolding)
        ↓
🔭 The Observatory (Streamlit — interactive white paper)
```

The origin story behind each of these stages — including the geocoding failure that cost a month of cleanup, and why miniBabel exists at all — is in **[STORY.md](./STORY.md)**.

## Tech stack

`Python` · `XGBoost` · `HDBSCAN` · `PyTorch` (miniBabel) · `TensorFlow/Keras` (cGAN) · `SQLite` → `BigQuery` · `Streamlit` · `Kepler.gl` · `H3` · `GCS`

## Data lineage & state boundaries

This repo executes a sequential pipeline. Data sources are strictly bound to phases, regardless of the order notebooks were created in:

| Phase | Source of truth |
|---|---|
| **1 — Acquisition & Ground Truth** | Raw Google Sheets + AppsScript state machines |
| **2–5 — Data Eng, EDA, Unsupervised & Supervised ML** | `pienza.db` (SQLite) — absolute SSoT from `0211_ETL_Big_Bang_pienzadb.ipynb` onward |
| **6 — Generative Moonshots** | `0603`/`0604` migrate `pienza.db` and the cGAN manifold to BigQuery — the bridge phase |
| **Downstream of 0604** | BigQuery only |

Intermediate Parquet/CSV outputs between notebooks live in `data/dumped_files/` — ephemeral, safe to delete and regenerate at any time.

## 🔭 The Observatory (Streamlit app)

The user-facing digital twin — an interactive white paper so any stakeholder, technical or not, can explore the project without opening a notebook.

**Data sourcing:**
- Entirely downstream of `0604` — reads strictly from BigQuery.
- All PII lives in a secured GCS lakehouse, queried only through BigQuery — never stored locally in the repo.
- Static, shareable assets (diagrams, public JSON) are tracked under `observatory/assets/` and read locally.

**Code architecture — View/Model separation:**

```
pages/000X_Name.py     View  — UI only (st.title, st.plotly_chart, st.tabs)
pages/_000X_data.py    Model — BigQuery fetchers (@st.cache_data), literals, pandas transforms
```

The page file handles layout. The hidden `_data.py` sibling does the heavy lifting.

### Run it locally

```bash
cd observatory
streamlit run main.py
```

## Repository structure

<details>
<summary><b>Click to expand full tree</b></summary>

```
pienza/
├── README.md                        # you are here
├── STORY.md                         # the narrative — how and why this got built
├── The_Pienza_Papers/
│   ├── Pienza_Papers_Scientific.pdf # full technical writeup
│   └── Pienza_Papers_Executive/     # business-facing summary
│
├── research_core/                   # curated spine notebooks (numbered for traceability)
│   ├── 0211_ETL_Big_Bang_pienzadb.ipynb
│   ├── 0305_EDA_Causal_Inference.ipynb
│   ├── 0307_EDA_Optimal_Stopping_Playbook.ipynb
│   ├── 0403_KMeans_Raw.ipynb
│   ├── 0407_Clustering_Paper_Streamlit.ipynb
│   ├── 0509_WINNER_XGB_cascade_postablation.ipynb
│   ├── 0601_NLP_Transformer_miniBabel.ipynb
│   ├── 0602_cGAN_Training.ipynb
│   └── 0603–0608_*.ipynb            # BigQuery bridge + Markov/graph scaffolding
│
├── research_archive/                # full phase-by-phase history
│   ├── Phase_1_Acquisition_and_Ground_Truth/
│   ├── Phase_2_Data_Engineering/    # ETL, temporal ledger, geospatial reconciliation
│   ├── Phase_3_Exploratory_Analysis/
│   ├── Phase_4_Unsupervised_ML/     # PCA, KMeans, HDBSCAN, polygon zones
│   ├── Phase_5_Supervised_ML/       # Naive Bayes → LogReg → XGBoost tournament
│   └── Phase_6_Generative_Moonshots/# miniBabel, cGAN, BigQuery migration
│
├── data/
│   ├── pienza.db                    # SQLite SSoT (real data)
│   └── dumped_files/                # ephemeral intermediate artifacts
│
├── observatory/                     # 🔭 the Streamlit app
│   ├── main.py                      # home page + canonical sidebar
│   ├── pages/                       # 000X_Name.py (view) + _000X_data.py (model)
│   ├── components/                  # styles.py — GLOBAL_CSS
│   ├── utils/                       # bq_client.py, gcp_client.py
│   └── assets/                      # static, shareable assets
│
└── assets/                          # private repo context/docs (gitignored)
```

</details>

## Known limitations

- **N=1 generalizability** — this clones one driver's policy under one city's incentive structure over six weeks. It is not a claim about driver behavior in general.
- **Human labels don't survive to production** — the six rejection-reason tags were assigned retrospectively by the driver after each shift. That's a deliberate research-only design choice, not a deployment path.
- **Heuristic-flag leakage risk** — some engineered features are close proxies for the label itself; treated with care in the cascade model, documented in the Papers PDF.

## Links

- 🔭 **[Live Observatory dashboard](#)** — placeholder, add live Streamlit URL
- 📄 **[Pienza Papers (Scientific)](./The_Pienza_Papers/Pienza_Papers_Scientific.pdf)**
- 📖 **[STORY.md](./STORY.md)** — the full narrative, with links to the notebooks at the moments they mattered
</div>
