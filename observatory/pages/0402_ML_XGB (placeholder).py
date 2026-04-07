import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Phase 5: Supervised Imitation Learning",
    page_icon="🧠",
    layout="wide"
)

# ==========================================
# CUSTOM FONT & SIZE INJECTION 
# ==========================================
st.markdown("""
    <style>
        /* Import Crimson Pro (Serif) and Inter (Sans-Serif) from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,200..900;1,200..900&family=Inter:wght@400;600;700&display=swap');

        /* 1. Body Text & General Elements (Crimson Pro) */
        html, body, [class*="css"], [class*="st-"], p, span, div, li, td, th {
            font-family: 'Crimson Pro', serif !important;
            font-size: 18px !important;  /* <-- ADJUST BODY TEXT SIZE HERE */
            line-height: 1.6 !important; /* Increases spacing between lines */
        }

        /* 2. Headers Base Setup (Inter) */
        h1, h2, h3, h4, h5, h6, 
        [class*="stHeading"] * {
            font-family: 'Inter', sans-serif !important;
            font-size: 24px !important;  /* <-- ADJUST BODY TEXT SIZE HERE */
            font-weight: 600 !important;
        }

        /* 2a. Individual Header Sizes */
        h1, [class*="stHeading"] h1 { font-size: 38px !important; } /* Main Title */
        h2, [class*="stHeading"] h2 { font-size: 28px !important; } /* Sections */
        h3, [class*="stHeading"] h3 { font-size: 22px !important; } /* Sub-sections */

        /* 3. Code Blocks & Terminal (Monospace) */
        code, pre {
            font-family: 'Courier New', Courier, monospace !important;
            font-size: 18px !important; /* <-- ADJUST CODE BLOCK SIZE HERE */
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER & INTRODUCTION
# ==========================================
st.title("Phase 5 - Supervised Imitation Learning: From Sky to Psyche")
st.caption("**Timeline: January 3 — January 12, 2026**")

st.markdown("""
The objective of Phase 5 was to synthesize a predictive model capable of replicating the Agent’s decision policy with high fidelity. This phase documents the transition from descriptive discovery to the engineering of a predictive inference engine via a comparative algorithmic tournament.

1. Experimental Design: The Tri-League Architecture
2. Categorical Features Selection
3. Model Tournament
""")

st.divider()

# ==========================================
# 1. EXPERIMENTAL DESIGN
# ==========================================
st.header("1. Experimental Design: The Tri-League Architecture")
st.markdown("""
To evaluate the interaction between data representation and model performance, the project utilized three distinct feature sets designated as "Leagues." This framework isolates the impact of expert-led curation versus automated abstraction across different algorithmic families.
""")

# Table 1: Tri-League Architecture
league_data = {
    "League": ["League A", "League B", "League C"],
    "Basis": ["Wide Set (PCA)", "Curated (Raw)", "Curated (PCA)"],
    "Dims.": ["19 PCs", "20 Feat.", "12 PCs"],
    "Technical Objective & Alignment": [
        "**Control Group:** Retains 90% variance of the original 41-feature set to validate that L1-Lasso pruning did not destroy latent signals.",
        "**Interpretability Mandate:** Utilizes raw scaled variables to enable SHAP-based forensics and non-linear geometric splits for tree-based models.",
        "**Mathematical Purity:** Eliminates multicollinearity via orthogonal components to provide a frictionless environment for linear and Bayesian estimators."
    ]
}
df_league = pd.DataFrame(league_data)

# ✅ NEW WAY (Renders the bold text perfectly)
st.markdown(df_league.to_markdown(index=False))
st.caption("Table 1: Tri-League data representations for the algorithmic tournament (N ≈ 4,760).")

st.divider()

# ==========================================
# 2. GEOSPATIAL FEATURE COALESCENCE
# ==========================================
st.header("2. Geospatial Feature Coalescence")
st.markdown("""
To minimize cardinality and prevent signal fragmentation, the 73 manual polygons and 45 HDBSCAN clusters were consolidated into a unified spatial taxonomy. Micro-polygons were semantically concatenated into **42 Macro-Zones** to ensure sufficient observation density (N) per category. Final feature assignment (`final_zone_id`) followed a deterministic three-tier cascade:

* **Tier 1 (Manual Priority):** Human-defined Macro-Zone boundaries override density clusters to enforce strategic intent.
* **Tier 2 (Machine Fallback):** HDBSCAN clusters capture hyper-dense infrastructural nodes (*e.g., airport terminals*) located outside manual zones.
* **Tier 3 (Unassigned):** Residual coordinates are explicitly categorized as noise.
""")

# Developer Note
st.info("""
**🛠️ Developer Note (Pending Narrative Update):** Agregar que esto resuelve el problema del hdbscan, al forzar polígonos como el del itesm o el de haciendas que no incluyan zonas próximas (las águilas; san fernando) que fueron incluidas en hdbscan porque excluidas por el coalesce.
""", icon="📝")

st.divider()

# ==========================================
# 3. CATEGORICAL FEATURE SELECTION
# ==========================================
st.header("3. Categorical Feature Selection")
st.markdown("""
To finalize the feature matrix for supervised learning, a statistical audit was conducted to measure the predictive utility of all candidate categorical variables. The project utilized **Mutual Information (MI)** to identify non-linear dependencies and the **Chi-Squared (χ²)** statistic to evaluate independence between features and the decision target.
""")

# Local Image Injection
with st.container():
    st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_categorical_audit.png", use_container_width=True)
    st.caption("Figure 1: Categorical Feature Importance Audit: Mutual Information (Left) and Chi-Squared (Right) scores. The audit exposes the dominance of geospatial topology and the failure of several human-engineered abstractions.")

st.markdown("""
The audit identifies `final_zone_id` (MI: 0.671) as the optimal spatial predictor. While high-cardinality grids like H3 with resolution 9 (MI: 0.967) achieve higher raw scores, they risk memorizing the training set. Consolidating 73 polygons into 42 Macro-Zones successfully filtered geometric noise while preserving the variable's predictive power.

The results confirm that raw clock resolution significantly outperforms semantic abstractions. High-resolution features such as `hour_of_day` (MI: 0.071) and `day_of_week` (MI: 0.025) were retained as dominant drivers. Conversely, human-engineered features like `time_of_day_block` were purged, as their rigid definitions masked critical market variance.

The engineered `heuristic_flag_context` emerged as the primary non-spatial signal (MI: 0.302), validating the "Human-in-the-Loop" extraction phase. In contrast, the Agent's immediate operational state (*Idle vs. On-Trip*) was identified as statistical noise (MI: 0.002) and removed to optimize model focus.
""")

# Table 2: Final Categorical Feature Set (Using Markdown to preserve bold text)
cfs_data = {
    "Domain": ["Spatial", "Temporal", "Temporal", "Contextual", "Contextual"],
    "Feature": ["`final_zone_id`", "`hour_of_day`", "`day_of_week`", "`heuristic_flag_context`", "`product_category_fk`"],
    "MI Score": [0.6709, 0.0707, 0.0250, 0.3020, 0.0327],
    "Technical Verdict": [
        "**Keep:** High-resolution zones derived from macro-polygon and cluster coalescence.",
        "**Keep:** Captures critical high-frequency demand cycles.",
        "**Keep:** Preserves unique daily market physics.",
        "**Keep:** Primary driver; encapsulates strategic intent.",
        "**Keep:** Retained to model service-tier behavioral shifts."
    ]
}
df_cfs = pd.DataFrame(cfs_data)
st.markdown(df_cfs.to_markdown(index=False))
st.caption("Table 2: Final Categorical Feature Set advanced to Supervised Learning (N ≈ 4,760).")

st.markdown("""
> *The high-signal categorical features identified in this audit were integrated into each of the three experimental Data Leagues. This finalized feature space provides the standardized foundation for the subsequent **Algorithmic Tournament**, where various model architectures are evaluated across these refined data regimes.*
""")

st.divider()


# ==========================================
# 4. ALGORITHMIC JUSTIFICATION
# ==========================================
st.header("4. Algorithmic Justification: From First Principles to Ensemble Apex")
st.markdown("""
To identify the optimal architecture for behavioral cloning, a competitive tournament was executed across five developmental trials. Models were evaluated using the **F1-Macro** score to ensure predictive balance across the 92% class imbalance.

A priori selection of high-complexity models was rejected in favor of an iterative tournament designed to establish the statistical performance floor and quantify the non-linear complexity of the Agent’s decision policy. This sequence serves as the formal justification for the eventual deployment of gradient-boosted ensembles.

* **Trial 1: Establishing the Statistical Floor (Naive Bayes).** Gaussian Naïve Bayes was deployed to measure performance under the assumption of feature independence. This trial established the baseline "failure rate" for probabilistic models in a high-imbalance, stateful environment.
* **Trial 2: Quantifying the Linear Ceiling (Logistic Regression).** By testing linear decision boundaries across both chronological and stratified splits, the project measured the "Linear Limit" of the dataset. 
* **Trial 3: The State-Time Tension (LR Stratified).** This controlled test compared chronological purity against stratified data efficiency. It exposed the "shuffling illusion" common in boutique datasets, where over-optimistic scores can mask a failure to generalize to future market regimes.
* **Trial 4: Auditing Non-Linear Logic (Decision Tree).** A single tree was utilized as a "Scout" to audit hard logic splits. This trial provided the empirical proof that raw, uncompressed variables (*LIGA B*) significantly outperformed PCA-abstracted features (*LIGA C*) when navigating non-linear decision rules.
* **Trial 5: Architectural Apex (XGBoost).** Armed with the quantified proof of non-linearity and the superiority of raw features, the project deployed a gradient-boosted forest on a consolidated five-week "training gym." This finalized the champion architecture required to capture the nuanced interaction between market physics and agent heuristics.
""")

# Table 3: Performance Ledger
ledger_data = {
    "Trial": ["1. Floor", "2. Linear", "3. Theoretical", "4. Scout", "**5. Champion**"],
    "Algorithm": ["Gaussian NB (Hybrid)", "Logistic Regression", "Logistic Regression", "Decision Tree (d=7)", "**XGBoost Classifier**"],
    "Validation Method": ["Chronological (Custom)", "Time-Series Split", "Stratified K-Fold", "Time-Series Split", "**Stratified K-Fold**"],
    "LIGA A": ["0.257", "0.482", "0.687", "0.336", "**0.760**"],
    "LIGA B": ["0.257", "0.514", "0.716", "0.474", "**0.761**"],
    "LIGA C": ["0.256", "0.490", "0.691", "0.373", "*Retired*"]
}
df_ledger = pd.DataFrame(ledger_data)

# ✅ NEW WAY (Renders the bold text perfectly)
st.markdown(df_ledger.to_markdown(index=False))
st.caption("Table 3: Performance Ledger: F1-Macro averages across the five developmental trials (N ≈ 4,760).")


# ==========================================
# 5. CHAMPION SELECTION & CALIBRATION
# ==========================================
st.header("5. Champion Selection: XGBoost")

st.subheader("Hyperparameter Calibration: The Down-Tuning Strategy")
st.markdown("""
Following the identification of `XGBoost` as the champion architecture, a calibration phase was executed to optimize the model for generalization. The initial **RandomizedSearchCV** search identified a performance peak at `max_depth = 5`, as illustrated in the tuning radiography (Figure 2). However, subsequent learning curve audits revealed a high-variance gap, suggesting that the model was beginning to overfit the noise of the five-week training window.

To ensure robustness against the unseen Week 6 holdout set, a deliberate **Down-Tuning** strategy was implemented. By restricting the tree depth and increasing stochasticity, the algorithm was forced to prioritize broad, high-signal features over local data clusters. This increased regularization pressure traded a marginal percentage of training accuracy for a significant improvement in the model's ability to generalize to novel market regimes.
""")

# Image Placeholder (Replace with your actual tuning radiography plot later)
with st.container():
    st.image("https://via.placeholder.com/1200x400.png?text=Placeholder:+fig_tuning_radiography.png", use_container_width=True)
    st.caption("Figure 2: Tuning Radiography: Impact of `max_depth` on F1-Macro performance. While the statistical peak occurs at 5, the model was finalized at 4 to ensure defensive generalization.")

# Table 4: Final Hyperparameters
hyperparam_data = {
    "Hyperparameter": ["`n_estimators`", "`max_depth`", "`learning_rate`", "`subsample`", "`min_child_weight`", "`gamma`"],
    "Final Value": ["200", "4", "0.1", "0.7", "3", "0.5"],
    "Engineering Rationale": [
        "Balanced to allow sufficient iterations for convergence at a lower depth limit.",
        "**Down-Tuned** from 5 to increase regularization and prevent overfitting on small-N zones.",
        "Adjusted to accelerate the learning process within the shallower tree structure.",
        "**Down-Tuned** from 0.9 to introduce more randomness per tree, forcing reliance on stable global signals.",
        "Enforced to ensure each split is supported by a minimum volume of evidence.",
        "Applied to penalize split complexity and reduce model variance."
    ]
}
df_hyperparams = pd.DataFrame(hyperparam_data)
st.dataframe(df_hyperparams, use_container_width=True, hide_index=True)
st.caption("Table 4: Final `XGBoost` configuration following the robustness calibration.")

st.divider()

# ==========================================
# 6. THE "STATE VS. TIME" DILEMMA
# ==========================================
st.header("6. The \"State vs. Time\" Dilemma")
st.markdown("""
The "State vs. Time" dilemma presented a significant architectural trade-off when modeling on a restricted, short-horizon dataset. Enforcing strict chronological purity—such as sequential walk-forward splits across a mere five-week training window—severely restricts the data volume and the number of learning iterations available to the algorithm. The primary limitation encountered was not an uneven distribution of target classes over time, but rather the data starvation inherent to temporal splits on small datasets, which prevents the model from iteratively refining its logic. 

Fortunately, this structural bottleneck was mitigated by the project's pre-existing feature architecture. Because the Agent's temporal context (e.g., `hour_of_day`, `day_of_week`) and behavioral memory (e.g., `consecutive_rejects`, `accumulated_deadhead`, `cumulative_earnings`) had already been explicitly engineered into the feature space, the operative "state" and exact temporal positioning of the agent were intrinsically captured within each independent observation; hence, the algorithm does not require sequential chronological ordering to accurately interpret the context of a decision. 

Consequently, utilizing Stratified K-Fold cross-validation to shuffle the observations within the training pool does not constitute true data leakage. Instead, it serves as a vital architectural mechanism to maximize data efficiency and iterative learning volume, allowing the model to robustly map the stateful logic before facing an untouched, out-of-time evaluation in Week 6.
""")

# ==========================================
# 7. MODEL PERFORMANCE: BIMODAL LEARNING
# ==========================================
st.header("7. Model Performance: Bimodal Learning")

st.markdown("""
An audit of the normalized confusion matrix (Figure 3) reveals that the monolithic `XGBoost` champion operates across two distinct performance regimes. These regimes are defined by the degree of feature orthogonality and the presence of deterministic boundaries.
""")

# Image Placeholder (Replace with your actual confusion matrix image later)
with st.container():
    # Using columns to center the image slightly and control its width
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/800x600.png?text=Placeholder:+fig_confusion_matrix.png", use_container_width=True)
        st.caption("Figure 3: Normalized Confusion Matrix for the Monolithic `XGBoost` Champion. High-accuracy clusters (top-left) identify deterministic operational constraints, while the lower-right quadrant reveals the strategic signal decay in nuanced decision classes.")

st.subheader("Regime 1: Deterministic Operational Constraints")
st.markdown("""
The model achieves high accuracy (>85%) when evaluating physical, geographical, and hard-economic constraints: `proxy_zone` (90.2%), `low_profitability` (90.6%), `non_operational` (88.7%), and `long_pickup` (85.7%). These classes are effectively orthogonal; their boundaries are dictated by rigid geospatial coordinates or absolute time-and-fare thresholds. The gradient boosting trees isolate these patterns with minimal entropy, representing the model's "Triage" layer.
""")

st.subheader("Regime 2: Conditional Strategic Nuance")
st.markdown("""
Performance degrades significantly (41% ... 68%) when the decision boundary shifts to higher-order behavioral states: `accepted` (68.7%), `strategic_mismatch` (57.1%), and `expected_value_gamble` (41.5%). These decisions are not functions of isolated coordinates but involve dynamic calculations of opportunity cost and market velocity. The resulting "fuzzy" boundaries lead to increased entropy and predictive uncertainty.
""")

st.subheader("The Gravitational Well Effect")
st.markdown("""
The audit identifies a critical failure mode: the interaction between the majority and minority classes. Because `non_operational` constitutes ≈ 50% of the dataset, it creates a statistical **Gravitational Well**. When the algorithm encounters a nuanced observation with high strategic uncertainty—such as an `expected_value_gamble`—it yields to the Bayesian prior of the majority class. This is proven by the fact that **34.1% of true strategic gambles are incorrectly swallowed by the non-operational prediction.**
""")

st.divider()

# ==========================================
# 8. ARCHITECTURAL PIVOT
# ==========================================
st.header("8. Architectural Pivot: The Cognitive Cascade")

st.markdown("""
The audit confirms that "cheap" triage logic (geospatial/economic filters) cannibalizes "expensive" strategic logic. To eliminate this interference, the project implemented the **Hierarchical Cognitive Cascade**. This architecture decomposes the multi-class problem into a sequence of specialized inference layers:

* **Layer 1 (The Bouncer):** A classifier designed to remove the "Regime 1" noise (*Non-Op, Proxy, Long Pickup*).
* **Layer 2 (The Strategist):** A secondary model operating strictly on the high-yield, surviving observations.

By removing the gravitational pull of the non-operational class in Layer 1, the Strategist model can dedicate its full capacity to resolving the subtle economic differences between strategic rejections and acceptances, effectively breaking the performance ceiling identified in the flat architecture.
""")

st.divider()

# ==========================================
# 9. LAYER 1: THE BALANCED BOUNCER PROTOCOL
# ==========================================
st.header("9. Layer 1: The Balanced Bouncer Protocol")

st.markdown("""
Layer 1 is architected as a high-recall filter designed to isolate deterministic operational noise from strategic signal. This "Bouncer" ensures that the majority classes (*Non-Op, Low Profit*) do not overwhelm the more nuanced strategic rejections in the subsequent layer.
""")

st.subheader("The Threshold Paradox: Street vs. Code")
st.markdown("""
The calibration of this filter is driven by an identified asymmetry in risk tolerance between the physical agent and the digital system:

* **The Agent (The Street):** Prioritizes the avoidance of **False Positives** (accepting a "Trap" offer). This results in a high internal threshold and a conservative decision bias.
* **The System (The Code):** Prioritizes the avoidance of **False Negatives** (discarding a "Super Gem" as noise). Since a lost opportunity is irrecuperable, the system utilizes a low threshold to maximize the volume of nuanced signal passed to Layer 2.
""")

st.subheader("Priority-Based Decision Logic")
st.markdown(r"To operationalize this strategy, Layer 1 replaces standard $argmax$ classification with a priority-based rule. The predicted class $\hat{y}$ is determined by two calibrated thresholds:")

st.latex(r"""
\hat{y} = 
\begin{cases} 
\text{Low Profit} & \text{if } P(\text{Low Profit}) \ge 0.25 \\
\text{The Nuanced Rest} & \text{else if } P(\text{Nuanced}) \ge 0.20 \\
\text{argmax}(P) & \text{otherwise}
\end{cases}
""")

st.markdown("""
**Hierarchy:** Blocking "Low Profit" data always takes precedence over rescuing "Nuanced" signal to enforce economic discipline.
""")

st.subheader("Results: Filter Efficiency")
st.markdown("""
The performance of the filter is measured by its **Recall** (Filter Efficiency). As shown in Figure 4, the protocol achieved a 90.6% Recall for Low Profitability rejections and an 81.7% Recall for the Nuanced Rest Class.
""")

# Image Placeholder
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/800x600.png?text=Placeholder:+fig_layer1_matrix.png", use_container_width=True)
        st.caption("Figure 4: Layer 1 Confusion Matrix. The diagonal represents the filter's efficiency in removing noise, while the \"Nuanced Rest\" column represents the survival rate of strategic signal.")

st.markdown("""
> *Outcome: By using high-recall filtering, the project successfully neutralized the Gravitational Well. The observations passed to Layer 2 are statistically balanced and represent the true strategic DNA of the expert policy.*
""")

# ==========================================
# 10. LAYER 1: SHAP CONTRIBUTION ANALYSIS
# ==========================================
st.subheader("DNA Atlas: Signal Drivers for Triage")

st.markdown("""
To validate the triage logic of the Balanced Bouncer, a SHAP contribution analysis was executed for the `THE_NUANCED_REST` class. This "DNA Atlas" (Figure 5) identifies the features that qualify an offer for Layer 2 evaluation (Teal/Right) versus those that push it toward a deterministic rejection (Gray/Left).
""")

# Image Placeholder 
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/1000x500.png?text=Placeholder:+fig_nuanced_dna.png", use_container_width=True)
        st.caption("Figure 5: DNA Atlas: Signal Drivers for `THE_NUANCED_REST`. The chart illustrates the contribution of features to the triage decision. Logistical friction serves as the primary exclusion vector, while financial magnitude and strategic intent serve as the primary inclusion vectors.")

st.markdown("""
The analysis reveals three primary pillars governing the triage stage:

* **The Logistical Barrier:** `time_to_pickup_sec` is the dominant negative driver (-0.594). Regardless of potential yield, high pickup latency is the primary reason an offer fails to reach the strategic tier. This confirms the model enforces strict logistical discipline at the entry point.
* **The Financial Magnet:** `upfront_fare` (+0.470) and `eph_operational_index` (+0.326) are the primary positive drivers. High absolute and relative earnings are the strongest signals for moving an offer into the nuanced category for strategic evaluation.
* **The Strategic Intent Trigger:** The positive contribution of the `obj_end_session` flag (+0.375) confirms that the model recognizes the "Endgame" state. When this intent is active, the model categorizes offers as "nuanced" rather than "low profit," allowing the subsequent Layer 2 model to evaluate them against homecoming vectors.

> *Outcome: The Layer 1 DNA confirms that the hierarchical filter has successfully learned the Agent's triage logic. By effectively isolating logistical noise and economic failures, the system ensures that Layer 2 operates on a high-signal subset of the marketplace.*
""")

st.divider()

# ==========================================
# 11. LAYER 2: THE STRATEGIST
# ==========================================
st.header("10. Layer 2: The Strategist (Nuance Modeling)")

st.markdown("""
The second stage of the cascade represents the "Nuance Engine" of the system. Operating exclusively on the high-yield subset that survived the Layer 1 filter, this model is designed to resolve the subtle distinctions between strategic rejections and acceptances without the interference of majority-class noise.
""")

# Image Placeholder 
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/800x600.png?text=Placeholder:+fig_layer2_matrix.png", use_container_width=True)
        st.caption("Figure 6: Layer 2 Confusion Matrix. By isolating the high-yield sub-universe, the model achieves superior separation between complex strategic states.")

st.subheader("Results: Strategic Performance Lift")
st.markdown("""
The transition to a hierarchical architecture resulted in a significant accuracy lift for the strategic classes:

* **Geospatial Strategy (`strategic_mismatch`):** Accuracy reached **75.0%**, confirming the model successfully mapped complex heuristics such as "Friday Gridlock Avoidance" and "Non-Homecoming Vectors."
* **Optimal Stopping (`expected_value_gamble`):** Accuracy rose to **65.9%**, a 58% relative improvement over the monolithic baseline. This proves that removing deterministic noise allows the algorithm to better isolate opportunity-cost signals.
* **Primary Target (`ACCEPTED`):** The model achieved **85.1% accuracy** in replicating the Agent’s acceptance decisions, establishing a high-fidelity behavioral clone.
""")

st.subheader("Threshold Tuning and the Pareto Frontier")
st.markdown("""
A systematic grid search for optimal decision thresholds was conducted for the Strategist layer. However, the analysis identified a sharp **Pareto Frontier**: while the threshold for the `ACCEPTED` class could be tightened, doing so resulted in a disproportionate collapse of *Recall* for the `expected_value_gamble` and `strategic_mismatch` classes. Because the project prioritizes high-fidelity policy replication over raw binary accuracy, the thresholds were maintained at their balanced equilibrium to preserve strategic nuance.
""")

st.divider()

# ==========================================
# 12. LAYER 2: STRATEGIC DNA
# ==========================================
st.subheader("Strategic DNA: Feature Drivers for Layer 2")

st.markdown("""
To interpret the internal logic of the Strategist model, a SHAP contribution analysis was performed across the three nuanced strategic classes (Figure 7). This assessment quantifies the directional impact of features on the final classification.
""")

# Image Placeholder 
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/1000x500.png?text=Placeholder:+fig_layer2_shap_dna.png", use_container_width=True)
        st.caption("Figure 7: Hierarchical Strategic DNA Atlas: Feature contributions for Layer 2 decision classes. Teal bars indicate a positive contribution to class probability; Gray bars indicate a negative contribution.")

st.markdown("""
The analysis reveals three primary behavioral mechanics that govern the expert agent's high-level strategy:

* **The Sunk Cost Mechanic (Accepted):** While `upfront_fare` and `eph_operational_index` are the expected financial drivers, `log_total_accumulated_deadhead_sec` serves as a powerful positive predictor (+0.309). This provides empirical proof of a "Sunk Cost" effect: as uncompensated search time increases, the Agent's selectivity threshold decays, leading to a higher probability of acceptance. Conversely, `obj_end_session` acts as the strongest inhibitor (-0.550), suppressing acceptance regardless of yield.
* **The Income Targeting Mechanic (Strategic Mismatch):** This class is dominated by the `obj_end_session` context (+0.819). The model correctly identifies that high accumulated earnings (`log_cycle_cumulative_net_earnings`) pull the decision toward a mismatch rejection. This verifies the "Income Targeting" heuristic: once financial objectives are met, the Agent prioritizes homecoming vectors over marginal revenue gains.
* **The Patience Constraint (Expected Val. Gamble):** The primary predictor for the `expected_value_gamble` class is the **absence** of search fatigue. The strongest negative contributor is `log_total_accumulated_deadhead_sec` (-0.416). This identifies a critical behavioral constraint: the Agent only gambles on future offers when the current search cost is low. Prolonged search cycles eliminate the Agent's patience, causing a shift from strategic gambling back to acceptance.

> *Outcome: The Layer 2 feature assessment proves that the XGBoost champion successfully mapped the Agent's non-linear strategic logic. The quantification of the "Patience Threshold" and the "Sunk Cost Effect" provides the mathematical foundation for the generative simulation engine in Phase 6.*
""")


st.divider()

# ==========================================
# 13. THE SHADOW MODE TRIAL
# ==========================================
st.header("11. The Shadow Mode Trial: Behavioral Fidelity")

st.markdown("""
To measure the operational impact of the architectural pivot, a final performance assessment was executed on the firewalled Week 6 holdout set ($N \\approx 780$ offers). The finalized **Cognitive Cascade** was benchmarked head-to-head against the monolithic `XGBoost` baseline and the Human Agent’s actual decisions across two primary KPIs: cumulative upfront fare and strategic efficiency.
""")

# Image Placeholder 
with st.container():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.image("https://via.placeholder.com/1200x500.png?text=Placeholder:+fig_shadow_mode_results.png", use_container_width=True)
        st.caption("Figure 8: Shadow Mode Performance Results. The left plot measures total cumulative yield ($), while the right plot measures strategic efficiency via the mean EPH Index. The Cascade architecture matches the expert’s efficiency while maximizing total value capture.")

st.markdown("""
The trial results, illustrated in Figure 8, reveal three critical performance findings:

* **Efficiency Parity:** The **Cascade (Opus)** model achieved a mean EPH index of **1.33**, perfectly replicating the Human Agent’s strategic efficiency. This confirms the model successfully learned the high-yield selection criteria required to consistently outperform the market baseline (1.0).
* **Monolithic Performance Decay:** The monolithic model significantly underperformed, trailing the Human Agent by **15.7% in efficiency**. This provides empirical proof that flat architectures are unable to isolate strategic signal from geospatial noise, confirming the negative impact of the "Gravitational Well."
* **Volume Surplus (The Machine Advantage):** In a surprising outcome, the Cascade model captured **5.7% more total value** than the Human Agent ($10,312 vs. $9,750). While maintaining identical efficiency, the machine identified high-yield opportunities that the human agent may have bypassed due to operational fatigue or cognitive load.

> *Outcome: The Shadow Mode trial validates the Cognitive Cascade as a high-fidelity behavioral clone. The model demonstrates the ability to match expert strategic efficiency while providing superior consistency in total value capture across a sustained work shift.*
""")

st.divider()

# ==========================================
# 14. PHASE 5 CONCLUSION
# ==========================================
st.header("12. Phase 5 Conclusion: Breaking the Static Barrier")

st.markdown("""
The conclusion of Phase 5 marks the definitive transition from static decision mapping to temporal flow modeling. While the *Cognitive Cascade* successfully isolated the Agent's strategic logic, its performance highlights a fundamental constraint of tabular architectures: **Snapshot Indifference**. Even when enriched with stateful features, classical `XGBoost` evaluates offers as isolated events in a vacuum. 

This technical boundary provides the formal validation for the transition to the **Generative Realm**. To fully deconstruct the *expected_value_gamble*—the decision to reject a viable offer based on the probability of a future event—the framework must move beyond independent row analysis. This justifies the scope of Phase 6, where Generative Adversarial Networks (GANs) will synthesize the high-volume data manifolds required to train Recurrent Neural Networks (RNNs). By transforming the market from a sequence of static snapshots into a continuous temporal flow, the Pienza framework moves toward modeling the "Expert Rhythm," where every decision is processed as a dynamic function of the marketplace's heartbeat.
""")