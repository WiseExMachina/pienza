import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Project Strategy and Scope",
    layout="wide"
)

# ==========================================
# CUSTOM FONT & SIZE INJECTION (SAFE VERSION)
# ==========================================
st.markdown("""
    <style>
        /* Import Crimson Pro (Serif) and Inter (Sans-Serif) from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');
        
        /* 1. Body Text (Crimson Pro) - Target semantic content tags only! */
        p, li, td, th {
            font-family: 'Crimson Pro', serif !important;
            font-size: 18px !important;  
            line-height: 1.6 !important; 
        }

        /* 2. Headers Base Setup (Inter) */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }

        /* 2a. Individual Header Sizes */
        h1 { font-size: 38px !important; } 
        h2 { font-size: 28px !important; } 
        h3 { font-size: 22px !important; } 

        /* 3. Expander Headers (Force them to match H3 Inter styling) */
        [data-testid="stExpander"] details summary p {
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }

        /* 4. Code Blocks & Terminal (Monospace) */
        code, pre {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 15px !important; 
        }
    </style>
""", unsafe_allow_html=True)


import streamlit as st

# ==========================================
# 1. PROJECT STRATEGY & SCOPE (Non-Collapsible Intro)
# ==========================================
st.header("Project Strategy & Scope")

st.subheader("Mission Statement")
st.markdown("""
The primary objective of **Project Pienza** is to model and optimize the decision-making policy of an expert agent within the ride-hailing ecosystem. The environment is formally defined as a *sequential, non-cooperative game* governed by intrinsic information asymmetry. 

Unlike traditional "top-down" studies relying on aggregated data, Pienza employs a **"Bottom-Up"** methodology grounded in the operational reality of Mexico City. Through the longitudinal quantification of a single Expert Agent ($N=1$), this research models the micro-economic physics of the Gig Economy.
""")

st.subheader("Scope & Constraints")
st.markdown("""
The project explicitly rejects the premise of reverse-engineering the proprietary pricing algorithms of ride-hailing platforms. Modeling a dynamic, global algorithm using a local boutique dataset is statistically unfeasible. 

Instead, Pienza reorients the analytical lens—shifting away from the fare prediction models common in public repositories—to focus on the sole variable under absolute control: **The Agent's Decision**. 
""")

# ==========================================
# 2. CORE FRAMEWORK (Collapsible Section)
# ==========================================
with st.expander("Core Framework: The Three Strategic Pillars", expanded=False):

    st.markdown("""
    The project is architected across three strategic pillars that bridge the gap between tactical fieldwork and scalable autonomous intelligence:

    1. **High-Fidelity Environment Digitization (The Foundation):** To overcome the *Survivorship Bias* inherent in ride-hailing data, a custom dual-engine ingestion pipeline was deployed to capture the **Total Offer Stream**. By utilizing OCR-based archival and geospatial triangulation, the system digitizes the "Negative Class" (rejected offers), providing the necessary ground truth to map the agent's exact decision boundary.
    
    2. **Hierarchical Policy Cloning (The Engine):** The core analytical breakthrough involves the transition from monolithic modeling to a **Cognitive Cascade**. This hierarchical inference architecture utilizes XGBoost to replicate the agent's multi-tiered decision logic—separating deterministic operational "triage" (geospatial/economic filters) from nuanced opportunity-cost "gambles".
    
    3. **Generative Synthesis & Topological Scaling (The Frontier):** The final pillar transforms the single-agent study into a scale-invariant simulation. Using **Conditional GANs (cGAN)**, the project synthesizes a 1,000,000-row data manifold that preserves the non-linear physics of the marketplace as encountered during the observation window. This environment serves as the sandbox for **Network Graph Analysis**, where the city is modeled as a *Tensor of Potentials* to orchestrate autonomous fleet routing and maximize steady-state value.
    """)

    # Handling the LaTeX Footnote with UI elegance
    st.markdown("""
    <div style="padding-top: 10px; opacity: 0.8;">
        <small><i>* <b>Note on Generative Scope:</b> The synthetic marketplace functions as an infinite Keras generator of the specific market regime and "lived experience" captured in the dataset, rather than a generalizable, dynamic model of total city-wide liquidity.</i></small>
    </div>
    """, unsafe_allow_html=True)

    st.info("""
    **Strategic Outcome:** This tripartite framework provides an end-to-end pipeline that transforms raw, biased operational fieldwork into a mathematically complete digital twin. By mapping the exact decision boundaries and replicating them via a hierarchical cascade, the system enables high-scale, generative strategy testing without requiring continuous physical data collection.
    """)


# ==========================================
# 3. INITIAL HYPOTHESIS (Collapsible Section)
# ==========================================
with st.expander("Initial Hypothesis: The Payout Spread", expanded=False):

    st.markdown("""
    Research began with a longitudinal field observation regarding fare elasticity. The hypothesis stated that the system applied an implicit efficiency penalty, observed as a discrepancy between the promised fare and realized earnings. A preliminary pilot study ($N \\approx 150$, July-August 2025 cohort) revealed a **Payout Rate (Spread)** between $75\\%$ and $85\\%$ of the Base Fare. The distribution followed session-based moving averages, suggesting intra-block temporal stability driven by market conditions.

    An initial model correlated this Spread with the **Time Delta** (the discrepancy between estimated and realized trip time). The goal was to validate whether time savings generated a fare penalty.
    """)

    st.info("""
    **Key Finding:** A benchmark comparison showed that Simple Linear Regression outperformed base Machine Learning models. No significant non-linear relationship was identified; the correlation remained weak. While basic statistics resolved the regression problem for the pilot sample, scaling this to a robust ML model would require thousands of completed trips, representing an infeasible operational time cost for marginal analytical return.
    """)



# ==========================================
# 4. STRATEGIC PIVOT (Collapsible Section)
# ==========================================
with st.expander("Strategic Pivot to Classification", expanded=False):

    st.markdown("""
    Based on logistical constraints and the low predictive value of the initial regression approach, the research objective was redefined:

    * **From:** Price variance prediction (Regression), which required scarce completed trip data.
    * **To:** Behavior modeling (Classification), which utilized the total offer stream.

    This shift resolved the data scarcity issue by enabling the inclusion of the **Negative Class** (rejected offers). By modeling decision policy rather than price, the project applies high-dimensional Machine Learning (XGBoost) to capture the agent's non-linear decision boundary.
    """)



    # ==========================================
# 5. PROJECT ROADMAP (Collapsible Section)
# ==========================================
with st.expander("Project Roadmap: Iterative Development Lifecycle", expanded=False):

    st.markdown("""
    The project followed an iterative development lifecycle where feature engineering evolved in response to the analytical findings of each stage:

    **Phase 1: Acquisition & Ground Truth (Aug 22 -- Oct 1, 2025)** High-fidelity manual capture of operational data via the bespoke *GTS Webapp*. Establishment of the target variable and the primary contextual ride attributes.

    **Phase 2: Data Engineering & Architecture (Oct 2 -- Nov 20, 2025)** Transition to a relational database (`pienza.db`) and Star Schema design. Implementation of automated OCR pipelines and normalization protocols. Creation of the stateful `engineered_features` table.

    **Phase 3: Exploratory Analysis & Causal Inference (Nov 21 -- Dec 3, 2025)** Diagnostic audit of marketplace physics and rational search time boundaries. Causal modeling of baseline heteroscedasticity and quantification of the platform's inelastic 'Integrity Buffer.'

    **Phase 4: Unsupervised Learning & Geo-Remediation (Dec 4, 2025 -- Jan 2, 2026)** Application of HDBSCAN for zone discovery and surgical coordinate cleaning using hand-crafted heuristic polygons. Generation of the **Silver Palette** (geo-semantic attributes).

    **Phase 5: Supervised Imitation Learning (Jan 3 -- Jan 12, 2026)** Model evaluation tournament and implementation of the *Cognitive Cascade* hierarchical architecture for the champion model.

    **Phase 6: Generative Moonshots (Jan 13, 2026 -- March 31, 2026)** $O(1)$ neural spatial inference and cGAN manifold synthesis. Formulation of the internal Mobility Tensor to establish the Markov Decision Process (MDP) baseline for autonomous routing.
    """)

    # Handling the LaTeX Footnote with UI elegance
    st.markdown("""
    <div style="padding-top: 10px; opacity: 0.8;">
        <small><i>* <b>Note on Phase 6 Duration:</b> The extended duration of this phase reflects a non-linear, iterative workflow; it was executed concurrently with the formal authoring of this manuscript, culminating in the simultaneous completion of Phase 6 and the first comprehensive draft of this paper.</i></small>
    </div>
    """, unsafe_allow_html=True)




    # ==========================================
# 6. SYSTEM ARCHITECTURE & EVOLUTION (Collapsible Section)
# ==========================================
with st.expander("A Note on System Architecture & Evolution", expanded=False):

    st.markdown("""
    The rigorous architecture of the data ecosystem was established as a foundational objective. The infrastructure evolved through distinct operational states to match the complexity of the inquiry:

    * **Phase 1 (Acquisition Staging):** Data ingestion from Engines 1 & 2 routed into *Google Sheets* for initial validation.
    * **Phase 2 (The Engineering Core):** Transition to a relational architecture. Execution of the idempotent ETL pipeline to forge the definitive **SQLite** asset (`pienza.db`).
    * **Phases 3--5 (The Analytical Loop):** A file-based cloud architecture where Python Notebooks interacted with `pienza.db` as the immutable Single Source of Truth.
    * **Phase 6 (Cloud Scaling):** Migration to **Google BigQuery** to support Generative AI workflows.
        * **`pienza_mini`:** A high-fidelity cloud replica of the ground-truth database, preserving the identical relational logic.
        * **`pienza_big`:** A 1,000,000-row synthetic dataset generated via GANs, persisted as Parquet artifacts and queried through BigQuery's external table interface.
    * **Interactive Deployment (Current State):** The project concludes with the transition from notebook-based exploration to an **Interactive White Paper** hosted on Streamlit. Leveraging *GitHub Codespaces* and an *orphan branch architecture*, this layer decouples the core research codebase from the operational interface, allowing for real-time model interrogation in a production-ready environment.
    """)
    