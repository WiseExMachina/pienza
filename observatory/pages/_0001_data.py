"""Data literals and pure helpers used by 0001_Foundations.py (Layer 1 extraction)."""

import base64
from pathlib import Path

import streamlit as st


@st.cache_data
def load_favicon_b64() -> str:
    """Reads the local favicon PNG and returns its base64-encoded string."""
    favicon_bytes = (Path(__file__).resolve().parent.parent / "assets" / "favicon.png").read_bytes()
    return base64.b64encode(favicon_bytes).decode()


# Timeline tab: one entry per project phase (label, dates, architecture, narrative).
PHASES: list[dict] = [
    {
        "phase": "Phase 1", "label": "Acquisition & Ground Truth",
        "arch_short": "OCR<br>+<br>Sheets",
        "date_range": "Aug 22 – Oct 1, 2025",
        "detail": "Implementation of the dual-engine acquisition pipeline. Definition of the ride attributes schema and target variable taxonomy. Manual same-day backtagging of 4,700 offers to populate <code style=\"color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;\">reason_primary</code>.",
        "bullets": ["GTS Webapp", "OCR automation", "Target variable definition", "Ride attributes schema"],
        "start": "2025-08-22", "end": "2025-10-01",
    },
    {
        "phase": "Phase 2", "label": "Data Engineering & Architecture",
        "arch_short": "SQLite<br>+<br>Colab",
        "date_range": "Oct 2 – Nov 20, 2025",
        "detail": "Transition to a relational database (<code style=\"color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;\">pienza.db</code>) and Star Schema design. Implementation of normalization protocols and idempotent ETL pipelines. Creation of the stateful <code style=\"color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;\">engineered_features</code> table.",
        "bullets": ["Star Schema design", "Idempotent ETL pipeline", "Normalization protocols", "engineered_features table"],
        "start": "2025-10-02", "end": "2025-11-20",
    },
    {
        "phase": "Phase 3", "label": "Exploratory Analysis & Causal Inference",
        "arch_short": "SQLite<br>+<br>Colab",
        "date_range": "Nov 21 – Dec 3, 2025",
        "detail": "Diagnostic audit of marketplace physics and rational search time boundaries. Causal modeling of baseline heteroscedasticity and quantification of the platform's inelastic Integrity Buffer.",
        "bullets": ["Marketplace physics audit", "Optimal stopping boundary", "Integrity Buffer quantification", "Heteroscedasticity causal model"],
        "start": "2025-11-21", "end": "2025-12-03",
    },
    {
        "phase": "Phase 4", "label": "Unsupervised Learning & Geo-Remediation",
        "arch_short": "SQLite<br>+<br>Colab",
        "date_range": "Dec 4, 2025 – Jan 2, 2026",
        "detail": "Application of HDBSCAN for zone discovery and surgical coordinate cleaning using hand-crafted heuristic polygons. Generation of the volatility suite and geo-semantic attributes.",
        "bullets": ["HDBSCAN zone discovery", "Heuristic polygon cleaning", "Volatility Suite", "44 geo-semantic clusters"],
        "start": "2025-12-04", "end": "2026-01-02",
    },
    {
        "phase": "Phase 5", "label": "Supervised Imitation Learning",
        "arch_short": "SQLite<br>+<br>Colab",
        "date_range": "Jan 3 – Jan 12, 2026",
        "detail": "Model evaluation tournament and implementation of the Cognitive Cascade hierarchical architecture for the champion model.",
        "bullets": ["Model tournament", "Cognitive Cascade architecture", "Hierarchical XGBoost champion", "Binary + multiclass evaluation"],
        "start": "2026-01-03", "end": "2026-01-12",
    },
    {
        "phase": "Phase 6", "label": "Generative Moonshots",
        "arch_short": "BigQuery<br>+<br>Colab",
        "date_range": "Jan 13 – Mar 31, 2026",
        "detail": "O(1) neural spatial inference and cGAN manifold synthesis. Formulation of the internal Mobility Tensor to establish the Markov Decision Process (MDP) baseline for autonomous routing.",
        "bullets": ["O(1) NLP spatial inference", "cGAN · 1M-row synthesis", "Mobility Tensor formulation", "MDP scaffold for autonomy"],
        "start": "2026-01-13", "end": "2026-03-31",
    },
    {
        "phase": "Phase 7 ✦", "label": "Streamlit: Pienza Observatory",
        "arch_short": "BigQuery<br>+<br>VS Code",
        "date_range": "Apr 1, 2026 – May, 31 2026",
        "detail": "Migration from Colab notebooks to a production-ready development environment. The research pipeline now runs entirely within GitHub Codespaces and VS Code — enabling live model interrogation, iterative Observatory builds, and a stable, reproducible workspace with full BigQuery connectivity.",
        "bullets": ["GitHub Codespaces", "VS Code", "BigQuery live queries", "Streamlit Observatory"],
        "start": "2026-04-01", "end": "2026-05-31",
    },
]

# Ribbon-chart palette, one color per PHASES entry (same order/length).
COLORS: list[str] = ["#0d4a47", "#21918c", "#2db3ad", "#47c4be", "#6dcfca", "#9eddd9", "#c8eeec"]

# Ribbon chart: coarser meta-groups spanning multiple phases, with their own hover copy.
META_GROUPS: list[dict] = [
    {
        "label": "Acquisition", "start": "2025-08-22", "end": "2025-10-01",
        "color": "#0d4a47",
        "hover": "<b>Phase 1</b><br>Manual field capture via GTS Webapp",
    },
    {
        "label": "Engineering /<br>Statistics", "start": "2025-10-02", "end": "2025-12-03",
        "color": "#21918c",
        "hover": "<b>Phases 2–3</b><br>Relational DB · ETL · Causal Inference",
    },
    {
        "label": "Classical ML", "start": "2025-12-04", "end": "2026-01-12",
        "color": "#2db3ad",
        "hover": "<b>Phases 4–5</b><br>HDBSCAN geo-remediation · XGBoost imitation learning",
    },
    {
        "label": "Deep Learning", "start": "2026-01-13", "end": "2026-03-31",
        "color": "#47c4be",
        "hover": "<b>Phase 6</b><br>O(1) NLP · cGAN · Mobility Tensor · MDP<br><i>† Iterative correction of past phases applied throughout</i>",
    },
    {
        "label": "Streamlit", "start": "2026-04-01", "end": "2026-05-31",
        "color": "#6dcfca",
        "hover": "<b>Phase 7</b><br>Pienza Observatory — production deployment",
    },
]
