import streamlit as st
import streamlit.components.v1 as components


# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y CSS (PANTALLA COMPLETA + HEADER)
# ==============================================================================
st.set_page_config(layout="wide", page_title="Observatory - HDBSCAN Map")

st.markdown("""
    <style>
        /* Eliminar el padding general de la app */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        /* Ocultar el header (barra blanca superior) */
        header {
            display: none !important;
        }
        /* Le damos un pequeño respiro arriba (1rem) para el título y los botones */
        .block-container {
            padding-top: 1rem !important; 
            padding-bottom: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        /* Ajustamos el iframe para que deje espacio a los botones (88vh en vez de 100vh) */
        iframe {
            width: 100% !important;
            height: 88vh !important; 
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            border-radius: 8px; /* Un toque elegante para las esquinas del mapa */
        }
        /* Quitar el scroll lateral molesto de Streamlit */
        .main {
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)



# ==========================================
# PHASE 4: INTRODUCTION (Non-Collapsible)
# ==========================================
st.header("Phase 4: Unsupervised Learning & Geo-Remediation")

st.markdown("**Timeline: December 4, 2025 – January 2, 2026**")

st.markdown("""
Following the causal audits of Phase 3, the project shifted from analyzing individual variables to discovering the **latent structures** that govern the Mexico City marketplace. This phase represents the critical convergence of the Agent's tacit domain knowledge and unsupervised machine learning, moving beyond standard administrative boundaries to identify organic "Neighborhoods of Profit." 

The mission of Phase 4 was twofold: first, to deconstruct the economic and topological archetypes of the market; and second, to execute a high-stakes remediation of the coordinate data. This period was characterized by intense "Human-in-the-Loop" intervention, where automated discovery was audited against operational reality. The campaign culminated in a month-long data surgery—spanning the terminal days of 2025—to reconcile systemic semantic drift and geocoding entropy.
""")

st.divider()

# ==========================================
# TABS PLACEHOLDER
# ==========================================
# Preparing the tab architecture as requested. Ready for the content!
tab_1, tab_2, tab_3 = st.tabs([
    "PCA", 
    "K-Means", 
    "HDBSCAN & Geo-Remediation"
])





import streamlit as st
import os

# Define the base path for images
IMAGE_DIR = "/workspaces/pienza/observatory/assets/overleaf_images"

# Note: Assuming tab_1, tab_2, tab_3 were defined previously via:
# tab_1, tab_2, tab_3 = st.tabs(["PCA Discovery", "Tab 2 Title", "Tab 3 Title"])

# ==========================================
# TAB 1: PCA
# ==========================================
with tab_1:
    
    with st.expander("Market Manifold Discovery: PCA", expanded=False):

        st.markdown("""
        To isolate the pure operational signal, the initial 67-dimensional vector space underwent a rigorous filtration protocol, distilling it down to 54 candidate variables. This preparatory phase enforced several strict constraints:

        1. **Variance Purge:** Quasi-constant features (>99% identical values), such as `is_teens` and `is_imputed`, were removed to eliminate computational dead weight.
        2. **Redundancy Resolution:** High-redundancy pairs (r > 0.90) were resolved through strategic selection. The pipeline prioritized **Scale-Invariant Indexes** over raw currency and **Accumulated Earnings** over absolute clock time, identifying the former as stronger behavioral drivers. Geospatial coordinates were retained as indispensable geometric inputs.
        3. **Categorical Exclusion:** Product category labels were intentionally omitted. This forced the model to identify the underlying economic and logistical causes of a decision rather than relying on superficial categorical proxies.
        4. **Leakage Prevention:** All features containing post-offer statuses, mission outcomes, or the `_EDA` suffix were purged to maintain a strictly predictive, forward-looking environment.

        To ensure model stability and prevent the curse of dimensionality, the 54-feature matrix was distilled through a competitive selection tournament using **Lasso Regression (L1 Penalty)**. The L1 regularization acted as a strict mathematical filter, aggressively forcing the coefficients of irrelevant or noisy features to exactly zero.

        > **Human-in-the-Loop Domain Override:** While the algorithm efficiently identified primary predictors, a critical intervention was applied to the surviving features to align the machine with the Agent's operational reality. For instance, while the model temporarily selected *distance* as a strong predictor, the Agent explicitly overrode this in favor of *Time* metrics (e.g., `est_trip_time_sec`). For an Electric Vehicle (EV) operator navigating heavy urban gridlock, time is the absolute operational constraint, whereas distance is merely a flawed proxy. 

        Finally, before establishing the final matrix, physics-based variables (*fare, time, density, friction*) underwent **Log-Normal Transformations**. This corrected for distributional skewness, compressing extreme outliers to ensure that subsequent distance-based algorithms were not biased.
        """)

        # Figure 1: L1 Feature Importance
        try:
            st.image(os.path.join(IMAGE_DIR, "fig_feature_importance_l1.png"))
            st.caption("**Figure 1:** Feature Importance on the 19 Master Dimensions (L1 Regularization). The plot illustrates the absolute magnitude of the coefficients surviving the Lasso penalty. The clear dominance of `log_time_to_pickup_sec` and `log_upfront_fare` confirms the Agent's primary sensitivity to immediate operational cost and financial reward.")
        except Exception as e:
            st.error(f"Image not found: fig_feature_importance_l1.png")

        st.markdown("""
        ---
        ### Principal Component Analysis (PCA)

        As evidenced in Figure 1, the selection and intervention protocol resulted in a **19-feature whitelist** that perfectly captures the interplay between market physics and agent psychology. The hierarchy establishes *Logistical Friction* and *Magnitude* as the primary anchors of the decision boundary, while state-dependent features like `home_vector_alignment_score` and `session_progress_ratio` provide the necessary strategic context for shift-termination modeling.

        Following feature curation, this purified 19-dimensional vector space was processed using **Principal Component Analysis (PCA)**. While subsequent clustering phases utilize the raw, scaled features to maintain direct interpretability, PCA serves a critical methodological function at this stage: it maps the system into an **orthogonal** feature space where every dimension exerts an independent gravitational pull, removing the warping effect of correlated variables and revealing the true latent structure of the market.

        The PCA engine leverages the properties of the **Symmetric Covariance Matrix** ($C$). By applying the **Spectral Theorem**, the matrix is diagonalized:
        """)

        # Equation Rendering
        st.latex(r"C = Q \Lambda Q^T")

        st.markdown("""
        where $\Lambda$ is a diagonal matrix of **eigenvalues** and $Q$ is an orthogonal matrix of **eigenvectors**. This ensures that the resulting Principal Components are perfectly perpendicular (uncorrelated), and the market's total variance is cleanly sorted along the diagonal.

        Dimensionality reduction was modest, requiring 13 components to preserve 90% of the variance from the original 19-feature set. While standard PCA applications often exhibit heavy dominance in the first two components, Mexico City's ecosystem reveals a **distributed eigenvalue structure**. The absence of a dominant principal component confirms the system's high dimensionality; the agent's decision logic is driven by the interplay of multiple orthogonal factors rather than a single primary variable.
        """)

        # Figure 2: Scree Plot
        try:
            st.image(os.path.join(IMAGE_DIR, "pca_scree_plot.png"))
            st.caption("**Figure 2:** PCA Scree Plot. The gradual slope confirms a high-dimensional system where no single component explains more than 15% of the total variance.")
        except Exception as e:
            st.error(f"Image not found: pca_scree_plot.png")

        st.markdown("""
        ---
        ### Market Logic Projections

        The first three components, explaining $\approx 40\%$ of the variance, define the universal mathematical structure of the total offer stream:

        * **PC1: Time in Session:** Weighted by `session_progress`, `deadhead`, and `cumulative_earnings`. It separates early-session, low-friction states from high-search-accumulation segments toward the conclusion of a shift.
        * **PC2: Volumetric Scale:** Weighted by `upfront_fare` and *estimated trip duration*. This axis distinguishes the physical magnitude of the mission, separating high-fare, long-duration missions from low-fare, high-turnover events.
        * **PC3: Logistical Yield:** Weighted by `dispatch_lead_time` and the *EPH Index*. It identifies opportunities where the financial compensation is high relative to the required operational time investment.
        """)

        # Figure 3: PCA Subfigures mapped side-by-side
        col1, col2, col3 = st.columns(3)
        
        with col1:
            try:
                st.image(os.path.join(IMAGE_DIR, "map_market.png"))
                st.caption("(a) PC1 vs. PC2: Market Logic")
            except:
                st.error("Missing map_market.png")
                
        with col2:
            try:
                st.image(os.path.join(IMAGE_DIR, "map_efficiency.png"))
                st.caption("(b) PC1 vs. PC3: Efficiency Decay")
            except:
                st.error("Missing map_efficiency.png")
                
        with col3:
            try:
                st.image(os.path.join(IMAGE_DIR, "map_structure.png"))
                st.caption("(c) PC2 vs. PC3: Yield Structure")
            except:
                st.error("Missing map_structure.png")

        st.caption("**Figure 3:** Strategic Projection: Latent Market Manifolds. Color intensity represents the `eph_complete_index`. The maps deconstruct the interplay between session state, physical scale, and realized yield.")

        st.markdown("""
        The projection of the feature space onto the primary principal components identifies the density regions where efficiency is maximized:

        1. **PC1 vs. PC2 (Market Logic):** Identifies how the available mission types shift as the agent accumulates operational time.
        2. **PC1 vs. PC3 (Efficiency Decay):** Indicates a correlation between fresh session states and peak efficiency.
        3. **PC2 vs. PC3 (Yield Structure):** Identifies that high-magnitude missions (High PC2) tend toward average yield, while high-efficiency outliers are primarily found in low-magnitude, high-turnover segments.

        This structural analysis confirms that peak performance is not uniformly distributed but occupies a specific coordinate space within the market manifold. These findings provide the objective boundaries for the **K-Means Strategic Archetypes** in the subsequent stage.
        """)







import streamlit as st

# Note: Assuming tab_1, tab_2, tab_3 were defined previously via:
# tab_1, tab_2, tab_3 = st.tabs(["🧠 PCA", "📊 K-Means", "🚀 Remediation"])

# ==========================================
# TAB 2: K-MEANS
# ==========================================
with tab_2:
    
    with st.expander("Economic Archetypes: K-Means", expanded=False):

        st.markdown("""
        An exploratory K-Means clustering algorithm was executed on the latent dimensions ($PC_1, PC_2, PC_3$). While the algorithm successfully partitioned the data across multiple tested $k$-universes ($k=2, 3, 4, 6$), the cluster profiles proved fundamentally uninterpretable for practical business strategy. Because each Principal Component is a linear combination of all 19 underlying features, the resulting clusters became opaque "mixtures of mixtures." Ultimately, clustering on latent dimensions created a "black box," making it impossible to reverse-engineer clear behavioral policies or business rules from abstract eigenvectors. 
        
        > **Methodology Note:** The evaluation of PCA-based clustering performance and the subsequent methodological pivot are documented in the Phase 4.1 notebook: [[GitHub: Project Pienza - K-Means Trials]](https://github.com/your-repo-placeholder).

        To resolve this interpretability barrier, a deliberate methodological pivot was executed to embrace a **"Crystal Box"** approach. PCA was formally abandoned as the input matrix for the clustering phase, with the methodology shifting to execute K-Means directly on the scaled raw features. 

        An initial execution on the full 19-variable set identified a secondary interpretability barrier. While individual variables were transparent, defining mission archetypes based on 19 simultaneous dimensions resulted in a second "black box" outcome where high-level strategic signals were masked by marginal fluctuations in state and demand variables.

        To resolve this, an **Incremental Clustering** strategy was adopted. The model was initially constrained to the "Naked Physics" of the transaction: `upfront_fare`, `est_trip_time_sec`, and `est_trip_dist_km`, excluding all algorithmic incentives or agent-state features. Applying the principle of **Occam's Razor**, the project identified that the market's fundamental structure is almost entirely dictated by these spatio-temporal magnitudes.
        """)











import streamlit as st
import os

# Define the base path for images (assuming previously defined)
IMAGE_DIR = "/workspaces/pienza/observatory/assets/overleaf_images"

# ==========================================
# TAB 2: K-MEANS (Continued)
# ==========================================
with tab_2:
    
    with st.expander("Hyperparameter Selection: Optimal Cluster Count (k)", expanded=False):

        st.markdown("""
        A comparative analysis between the **Elbow Method** and **Silhouette Score** was conducted to determine the optimal cluster count ($k$) for Mexico City's marketplace.
        """)

        # Figure: K Selection
        try:
            st.image(os.path.join(IMAGE_DIR, "fig_k_selection.png"))
            st.caption("**Figure:** Hyperparameter Tournament ($k$): Elbow Method and Silhouette Score analysis for the 'Naked Physics' feature set.")
        except Exception as e:
            st.error(f"Image not found: fig_k_selection.png")

        st.markdown("""
        ---
        ### Selection Rationale

        * **Mathematical Baseline ($k=2$):** The Silhouette Score indicated a peak at $k=2$. While geometrically optimal, this trivial binary split (Short vs. Long missions) was rejected for its failure to capture the nuanced operational regimes that dictate profitability.
        * **Expert-Led Resolution ($k=6$):** A visual inspection of the Elbow Plot identified a significant reduction in inertia occurring at $k=6$. This higher-resolution setting was ratified as the optimal choice, as it provided sufficient granularity to decode the transition between distinct states in the agent’s policy.
        """)



import streamlit as st
import pandas as pd


# ==========================================
# TAB 2: K-MEANS (Continued)
# ==========================================
with tab_2:
    
    with st.expander("Market Archetypes: The Six Physical Tiers", expanded=False):

        st.markdown("""
        The analysis revealed that the marketplace fractures into six distinct physical tiers based on temporal magnitude and logistical scale.
        """)

        # ------------------------------------------
        # Table 1: Mission Tiers
        # ------------------------------------------
        tier_data = {
            "Designation": ["`Tier 1`", "`Tier 2`", "`Tier 3`", "`Tier 4`", "`Tier 5`", "`Tier 6`"],
            "Median Duration": ["12 minutes", "25 minutes", "40 minutes", "56 minutes", "80 minutes", "224+ minutes"]
        }
        df_tiers = pd.DataFrame(tier_data)
        
        # Render using Pandas to Markdown for clean UI integration
        st.markdown(df_tiers.to_markdown(index=False))
        st.caption("**Table 1:** Mexico City market archetypes based on $K=6$ clustering.")

        st.markdown("""
        > **Methodological Note on Duration:** Median duration is derived from multi-dimensional $K$-Means centroids rather than deterministic binning. Consequently, observations with identical durations may be assigned to different tiers based on the specific variance in fare magnitude and trip distance.
        """)

        st.markdown("---")

        st.markdown("""
        ### Non-Stationary Decision Policy

        Cross-referencing the Agent's historical rejections against these six tiers provides empirical evidence of a **non-stationary decision policy**. The primary decision driver shifts dynamically as the physical scale of the offer increases:

        * **Low-Magnitude Missions (Tiers 1–3):** Rejections are primarily governed by the **Economic Layer**. For "Sprints" (Tier 1), the dominant friction point is `low_profitability` ($\approx 44\%$ of rejections). The Agent's priority is yield-per-minute efficiency. 
          > *Contextual Caveat:* Although Tier 1 missions exhibit the highest quoted EPH, the agent utilized historical operational knowledge identifying these as low-yield events once uncompensated search and pickup overheads are factored in.

        * **High-Magnitude Missions (Tiers 4–6):** Rejections are governed strictly by the **Geospatial Layer**. As trip duration approaches the one-hour threshold, economic metrics are ignored. For Tier 5 missions, `dropoff_non_operational` accounts for $>98\%$ of rejections, reflecting a pure destination-based strategy.
        """)






import streamlit as st
import os

with tab_2:
    
    with st.expander("The Physics of Pricing: Base Fare Structure", expanded=False):

        st.markdown("""
        A review of the base fare structure across these tiers reveals two distinct algorithmic laws governing the market.
        
        > **Methodological Note:** Base fare is isolated by removing all incentives from the upfront quote to ensure a normalized comparison of structural pricing.
        """)

        # Figure: Pricing Physics
        try:
            st.image(os.path.join(IMAGE_DIR, "fig_pricing_physics.png"))
            st.caption("**Figure:** The Physics of Pricing: Mean yield per minute and kilometer across mission tiers. The dual-axis plot illustrates the systematic decay of distance-based rewards and the U-curve of temporal compensation.")
        except Exception as e:
            st.error(f"Image not found: fig_pricing_physics.png")

        st.markdown("""
        ---
        ### Algorithmic Laws of the Market

        1. **Compensation per kilometer:** exhibits an inverse relationship with mission scale. Yield begins at **\$17.4 MXN/km** for Tier 1 and collapses to **\$6.5 MXN/km** for Tier 6. 
        2. **Compensation per minute:** follows a non-linear "U" structure. Rates are high for Sprints (**\$5.2 MXN/min**) to offset fixed search costs, reach a minimum for mid-range urban missions (\$4.1/min), and increase again for Tier 5 and Tier 6.
        """)




import streamlit as st
import os

# Note: Assuming IMAGE_DIR and tabs were defined previously
# IMAGE_DIR = "/workspaces/pienza/observatory/assets/overleaf_images"


# ==========================================
# TAB 2: K-MEANS (Continued)
# ==========================================
with tab_2:
    
    with st.expander("Yield Analysis Across Operational Tiers", expanded=False):

        st.markdown("""
        To evaluate the economic viability of the discovered archetypes, the analysis measured the performance of each tier against the **$200/hr North Star** benchmark. As shown in the figure below, the transition from quoted potential to holistic outcome identifies how trip duration dictates final efficiency.
        """)

        # Figure: Yield Tiers
        try:
            st.image(os.path.join(IMAGE_DIR, "fig_yield_tiers.png"))
            st.caption("**Figure:** Yield Variance by Mission Tier. Bars represent the percentage deviation relative to the $200/hr target. Negative values indicate a yield below the North Star threshold rather than a net financial loss.")
        except Exception as e:
            st.error("Image not found: fig_yield_tiers.png")

        st.markdown("""
        ---
        ### The Amortization of Deadhead
        
        The result identifies the **Amortization of Deadhead** as the primary driver of mission efficiency:

        * **Search-Intensive Sprints (Tier 1):** Although quoted at $+75.7\%$ above the target, the realized yield collapses to $-49.9\%$. In these short-duration missions, the uncompensated temporal investment (searching and pickup) outweighs the revenue-generating phase.
        * **Scale Resilience (Tiers 4-6):** Long-duration missions demonstrate the highest capacity to meet the sustainability benchmark, successfully diluting fixed search costs across a larger revenue base. However, the yield for Tier 6 represents rare interstate statistical anomalies. This specific metric excludes the massive time required to return back to the city, which would halve the realized yield in a full-cycle context.
        
        > **Transitional Note:** Having established the fundamental economic archetypes, the study proceeds to the discovery of the geospatial dimension to identify the organic operational zones of the city.
        """)







import streamlit as st

# Note: Assuming tab_1, tab_2, tab_3 were defined previously via:
# tab_1, tab_2, tab_3 = st.tabs(["🧠 PCA", "📊 K-Means", "🚀 Geo-Remediation"])

# ==========================================
# TAB 3: GEO-REMEDIATION / HDBSCAN
# ==========================================
with tab_3:
    
    with st.expander("Topological Operational Model: The Dropoff Imperative", expanded=False):

        st.markdown("""
        The geospatial objective of this phase was to transform $\\approx 4,700$ raw coordinates into a **Topological Operational Model**. This mapping converts raw spatial distributions into a high-value categorical feature (`zone_id`), enabling the downstream predictive pipeline to recognize geographic intent and operational risk.
        
        ---
        ### Geospatial Constraints: The Dropoff Imperative
        
        A fundamental architectural decision in this topology was the **exclusive focus on dropoff coordinates**. Pickup locations were intentionally omitted from the feature engineering phase for two primary reasons:
        
        1. **Data Integrity:** Over 90% of raw pickup address strings exhibited extreme ambiguity, introducing high-risk noise into the dataset.
        2. **Decision Theory:** Since the Agent is geographically indifferent to pickups, the decision to accept an offer is driven by *Time-to-Pickup* (TTP) rather than the specific neighborhood of origin. Conversely, the destination (dropoff) dictates the Agent's future geographic position, making it the primary determinant of subsequent operational risk and return.
        """)




import streamlit as st

# Note: Assuming tab_1, tab_2, tab_3 were defined previously via:
# tab_1, tab_2, tab_3 = st.tabs(["🧠 PCA", "📊 K-Means", "🚀 Geo-Remediation"])

# ==========================================
# TAB 3: GEO-REMEDIATION / HDBSCAN (Continued)
# ==========================================
with tab_3:
    
    with st.expander("The Initial Clustering Attempt & The Coordinate Crisis", expanded=False):

        st.markdown("""
        To discover these organic dropoff zones, **DBSCAN** was initially deployed. However, it resulted in data fragmentation that lacked operational business logic. The architecture was subsequently upgraded to **HDBSCAN** (Hierarchical DBSCAN), which dynamically extracts clusters across multiple density scales, proving much more capable of capturing Mexico City's complex operational reality. 

        In an attempt to achieve 100% feature coverage, a **K-Nearest Neighbors (KNN)** classifier was deployed alongside HDBSCAN to re-assign unclustered noise points to their nearest cluster. This algorithmic fallback was quickly identified as a functional failure: by forcing orphaned points into the nearest core based strictly on Euclidean distance, the resulting map lost all operational relevance. 

        ---
        ### The Coordinate Crisis

        More critically, while the HDBSCAN model was mathematically sound, a deep validation audit cross-referencing the coordinate clusters against the raw `dropoff_address` text strings revealed a systemic data integrity failure. Inspection of the *AICM* (Airport) cluster, for example, revealed textual addresses belonging to distant parts of the city, such as Cuajimalpa. 

        > **Architectural Failure (GIGO):** While the algorithm had correctly identified density clusters, the underlying geocoded coordinates had become completely decoupled from their true textual addresses during the upstream ingestion phase. This "Garbage In, Garbage Out" corruption entirely invalidated the initial unsupervised topology and necessitated a major remediation campaign before any machine learning could proceed.
        """)



import streamlit as st

# Note: Assuming tab_1, tab_2, tab_3 were defined previously via:
# tab_1, tab_2, tab_3 = st.tabs(["🧠 PCA", "📊 K-Means", "🚀 Geo-Remediation"])

# ==========================================
# TAB 3: GEO-REMEDIATION / HDBSCAN (Continued)
# ==========================================
with tab_3:
    
    with st.expander("Geospatial Remediation: Root Cause Analysis & Diagnostic Engineering", expanded=False):

        st.markdown("""
        The discovery of decoupled coordinates within the initial clustering results triggered a deep **Root Cause Analysis (RCA)**. The investigation identified three compounding failure vectors responsible for the data corruption:

        1. **Validation Gap:** The initial Phase 1 data acquisition utilized forward geocoding without a reverse-validation step, allowing API hallucinations to persist undetected in the dataset.
        2. **Semantic Entropy:** Contradictory neighborhood labels within the platform's raw address strings (e.g., *"Calle Insurgentes Tacubaya, Condesa/Roma"*) caused the black-box routing API to default coordinates to entirely incorrect boroughs.
        3. **Propagation Error:** A logical bug during the Phase 2B jittering stage caused hundreds of distinct textual addresses to mistakenly collapse into a single, identical coordinate point.

        ---
        ### Diagnostic Engineering

        Before the dataset could be repaired, the corrupted records needed to be isolated without compromising the healthy data. To achieve this, a diagnostic SQL query was engineered based on a strict relational rule: **Fixed Coordinates + Changing Text = Error**. By grouping identical coordinates and counting distinct address strings, the pipeline successfully flagged the specific anomalies requiring intervention.
        """)

        st.caption("**SQL Listing:** Diagnostic Query: Isolating Jitter Propagation Errors")
        st.code("""
-- Logic: If one exact coordinate belongs to multiple distinct text addresses, it is corrupted.
SELECT offer_id,
       CASE WHEN c.num_pickups > 1 THEN 'PICKUP_ERROR'
            WHEN c.num_dropoffs > 1 THEN 'DROPOFF_ERROR'
       END as diagnostic_flag
FROM offers o
JOIN (
    SELECT pickup_lat, pickup_lon, dropoff_lat, dropoff_lon,
           COUNT(DISTINCT pickup_address) as num_pickups,
           COUNT(DISTINCT dropoff_address) as num_dropoffs
    FROM offers
    GROUP BY pickup_lat, pickup_lon, dropoff_lat, dropoff_lon
    HAVING COUNT(DISTINCT pickup_address) > 1 OR COUNT(DISTINCT dropoff_address) > 1
) c ON o.pickup_lat = c.pickup_lat AND o.dropoff_lat = c.dropoff_lat;
        """, language="sql")



import streamlit as st

# Note: Assuming tab_1, tab_2, tab_3 were defined previously

# ==========================================
# TAB 3: GEO-REMEDIATION / HDBSCAN (Continued)
# ==========================================
with tab_3:
    
    with st.expander("Human-in-the-Loop (HITL) Reconciliation Pipeline", expanded=False):

        st.markdown("""
        In addition to the Jitter Propagation Errors, a six-stage **Human-in-the-Loop (HITL)** reconciliation pipeline was executed across all 9,530 coordinate pairs:

        1. **Topological Audit:** The initial HDBSCAN output was cross-referenced against raw address strings to identify first-layer corruption, flagging offers where the semantic text contradicted the assigned geospatial cluster.
        2. **Polygon Synthesis:** The agent manually architected 72 custom heuristic polygons to serve as operational "Indifference Zones"—geographic areas defining the operational reality.
        3. **Heuristic Audit (Polygons):** A secondary manual audit verified point-in-polygon alignment, flagging offers whose string addresses did not belong to the polygon zone.
        4. **Cloud Re-geocoding:** In order to clean flagged offers and to detect anomalies invisible to visual inspection, the entire dataset was re-geocoded, both forward and reverse.
        5. **Geospatial Delta Check:** By calculating the spatial variance (in meters) between the original coordinates and the secondary baseline, records exceeding a severe geographic deviation threshold were isolated for intervention.
        6. **Deterministic Overwrite:** A bespoke ETL tool was engineered to manage the final manual corrections. The system staged flagged conflicts alongside verified API context, enabling the Agent to surgically overwrite corrupted coordinate pairs in the source tables while preventing manual entry errors.
        """)

        # Figure: Heuristic Polygons (Referenced in Step 2)
        try:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/pienza_strategic_map.png")
            st.caption("**Figure:** Polygon Synthesis. The 72 custom heuristic polygons manually architected to serve as operational 'Indifference Zones.'")
        except Exception as e:
            st.error("Image not found: pienza_strategic_map.png")

        st.markdown("""
        ---
        > *Outcome: This intervention successfully corrected over 1,500 corrupted rows—nearly one-third of the operational history. The canonical Source of Truth was updated with this purified dataset, enabling the re-execution of the clustering pipeline with high-fidelity results.*
        """)


# ==============================================================================
# 2. TOP BAR (TÍTULO Y BOTONES)
# ==============================================================================
# Usamos columnas para poner el título a la izquierda y los botones a la derecha
col1, col2 = st.columns([1, 4]) 

with col1:
    st.markdown("### 📍 HDBSCAN Results")

with col2:
    # Usamos radio horizontal porque nativamente guarda el estado y el diseño es limpio
    vista_activa = st.radio(
        "Selecciona la vista:",
        ["2D", "3D (offer_volume)"],
        horizontal=True,
        label_visibility="collapsed" # Ocultamos el texto de arriba para que se vean solo los botones
    )

st.markdown("<br>", unsafe_allow_html=True) # Un pequeño salto de línea para separar del mapa

# ==============================================================================
# 3. LÓGICA DE CARGA DE HTML
# ==============================================================================
@st.cache_data
def load_kepler_html(file_name):
    html_path = f"/workspaces/pienza/observatory/assets/{file_name}"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo en: {html_path}")
        return None

# El switch principal: decide qué archivo cargar
if vista_activa == "2D":
    html_data = load_kepler_html("kepler_2D.html")
else:
    html_data = load_kepler_html("kepler_3D.html")

# ==============================================================================
# 4. RENDERIZADO
# ==============================================================================
if html_data:
    # Renderizamos el HTML inyectando el código cargado
    components.html(html_data, height=900, scrolling=False)