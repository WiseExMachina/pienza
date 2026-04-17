import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import confusion_matrix, classification_report

# THIS is how you "insert" the logic
from utils.gcp_client import fetch_parquet_from_gcp

# ==========================================
# PHASE 5 INTRO: SUPERVISED IMITATION LEARNING (Non-Collapsible)
# ==========================================
st.header("Phase 5: Supervised Imitation Learning")

st.markdown("""
Phase 5 marks the critical transition from descriptive data discovery to predictive behavioral cloning. The primary objective was to engineer an inference engine capable of replicating the expert Agent's decision policy with high fidelity. To establish a rigorous foundation, the phase began with the "Tri-League Architecture," evaluating how different data representations (PCA vs. raw variables) interact with various algorithmic families. Through rigorous statistical audits using Mutual Information and Chi-Squared metrics, the project coalesced fragmented geospatial data into semantic Macro-Zones and executed a critical Ablation Study—purging unrealistic human-engineered "cheat codes" to force the models to learn autonomous market physics strictly from objective telemetry.

To identify the optimal architecture for capturing these non-linear behavioral mechanics, the project executed a competitive five-trial algorithmic tournament. By benchmarking algorithms from Gaussian Naïve Bayes up to Logistic Regression across a highly imbalanced target variable (92% majority class), the tournament established the statistical floor and the linear ceiling of the dataset. This rigorous sequence ultimately proved the superiority of raw, uncompressed variables, crowning a monolithic XGBoost gradient-boosted forest as the champion baseline architecture.

For a comprehensive deep-dive into the raw statistical audits, the Tri-League data representations, and the Ablation Study justification, please review the formal technical documentation below.

`[STREAMLIT PLACEHOLDER: Insert Download/Link Button here -> Project_Pienza_Phase_5_Tournament_Architecture.pdf]`
""")

st.divider()


import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import confusion_matrix, classification_report

# --- PIENZA STYLE CONSTANTS ---
PIENZA_BG = "#FAFAFA"
PIENZA_TEAL = "#21918c"
PIENZA_PURPLE = "#440154"
PIENZA_TEXT = "#333333"
pienza_cmap = [[0, "#FFFFFF"], [1, PIENZA_TEAL]]

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import confusion_matrix, classification_report

# --- PIENZA STYLE CONSTANTS ---
PIENZA_BG = "#FAFAFA"
PIENZA_TEAL = "#21918c"
PIENZA_PURPLE = "#440154"
PIENZA_TEXT = "#333333"
pienza_cmap = [[0, "#FFFFFF"], [1, PIENZA_TEAL]]

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.metrics import confusion_matrix, classification_report

# --- PIENZA STYLE CONSTANTS ---
PIENZA_BG = "#FAFAFA"
PIENZA_TEAL = "#21918c"
PIENZA_PURPLE = "#440154"
PIENZA_TEXT = "#333333"
pienza_cmap = [[0, "#FFFFFF"], [1, PIENZA_TEAL]]

# ==========================================
# LAYER 1: DIAGNOSTIC TABS
# ==========================================
st.subheader("Layer 1: Isolating Signal from Noise")

st.markdown("""
Optimizing the confidence threshold for the `THE_NUANCED_REST` class allows the system to recover signal that would otherwise be masked. **Adjust the lever below to observe the trade-off between Precision and Recall.**
""")

# Initialize the 4-Tab Architecture
tab1, tab2, tab3, tab4 = st.tabs([
    "🧮 Confusion Matrix & Report", 
    "📈 ROC-AUC & PR-AUC", 
    "📉 Learning Curve", 
    "🧬 SHAP DNA"
])

with tab1:
    # --- 1. THE INTERACTIVE LEVER ---
    t_nuanced = st.slider(
        "Nuanced Classification Threshold (The Gema)", 
        min_value=0.10, 
        max_value=0.50, # <--- Capped at 0.50 per request
        value=0.40, 
        step=0.05,
        help="Lowering the threshold makes the Bouncer more permissive for nuanced offers."
    )

    # --- 2. THE REAL DATA FETCH ---
    df_l1 = fetch_parquet_from_gcp(
        bucket_name="pienza-streamlit", 
        file_name="260417_layer1_probabilitiesv3.parquet"
    )

    if not df_l1.empty:
        # --- THE HARDCODE OVERRIDE (Forcing the Anchor) ---
        classes_l1 = [
            "THE_NUANCED_REST", 
            "Long Pickup Time", 
            "Low Profitability", 
            "Dropoff: Non-Operational", 
            "Dropoff: Proxy Zone"
        ]

        # --- 3. DYNAMIC INFERENCE ENGINE ---
        def apply_triage_logic(row, threshold):
            if row['prob_nuanced'] >= threshold:
                return "THE_NUANCED_REST"
            return row['base_prediction']

        df_l1['dynamic_pred'] = df_l1.apply(lambda row: apply_triage_logic(row, t_nuanced), axis=1)

        # --- 4. RENDER DYNAMIC MATRIX (PIENZA STYLE) ---
        cm = confusion_matrix(df_l1['true_label'], df_l1['dynamic_pred'], labels=classes_l1, normalize='true')
        
        fig = px.imshow(
            cm, 
            x=classes_l1, 
            y=classes_l1,
            labels=dict(x="Bouncer Decision (Predicted)", y="True Category (Actual)", color="Recall"),
            text_auto=".1%", 
            color_continuous_scale=pienza_cmap,
            aspect="auto"
        )
        
        fig.update_layout(
            title=dict(
                text=f"Portero: Impacto en Sensibilidad (Gema T={t_nuanced:.2f})",
                font=dict(size=18, family="Inter", color=PIENZA_PURPLE)
            ),
            paper_bgcolor=PIENZA_BG,
            plot_bgcolor=PIENZA_BG,
            font=dict(color=PIENZA_TEXT),
            xaxis=dict(title_font=dict(size=14, family="Inter", weight="bold")),
            yaxis=dict(title_font=dict(size=14, family="Inter", weight="bold")),
            margin=dict(l=0, r=0, t=60, b=0)
        )
        fig.update_coloraxes(showscale=False)
        
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- 5. DYNAMIC CLASSIFICATION REPORT ---
        st.markdown(f"At a threshold of **{t_nuanced:.2f}**, the dynamic report confirms the operational balance.")
        
        report_dict = classification_report(
            df_l1['true_label'], 
            df_l1['dynamic_pred'], 
            labels=classes_l1, 
            target_names=classes_l1, 
            output_dict=True, 
            zero_division=0
        )
        
        display_rows = []
        for cls in classes_l1:
            display_rows.append({
                "Class Label": f"`{cls}`",
                "Precision": f"{report_dict[cls]['precision']:.2f}",
                "Recall": f"{report_dict[cls]['recall']:.2f}",
                "F1-Score": f"{report_dict[cls]['f1-score']:.2f}",
                "Support": str(int(report_dict[cls]['support']))
            })
        
        display_rows.append({
            "Class Label": "**Macro Average**",
            "Precision": f"**{report_dict['macro avg']['precision']:.2f}**",
            "Recall": f"**{report_dict['macro avg']['recall']:.2f}**",
            "F1-Score": f"**{report_dict['macro avg']['f1-score']:.2f}**",
            "Support": f"**{int(report_dict['macro avg']['support'])}**"
        })
        
        st.markdown(pd.DataFrame(display_rows).to_markdown(index=False))
    
    else:
        st.error("GCP Data Fetch Failed. Verify file: 260417_layer1_probabilitiesv3.parquet")


# ------------------------------------------
# TAB 2: ROC-AUC & PR-AUC
# ------------------------------------------
with tab2:
    st.markdown("""
    While ROC-AUC measures discriminatory capacity in balanced datasets, the significant class imbalance in this project necessitates the implementation of Precision-Recall (PR) analysis. Unlike the ROC framework, PR-AUC ignores easily predicted True Negatives, focusing strictly on the model's accuracy in capturing rare positive signals. 
    
    Analysis of the `THE_NUANCED_REST` class yields an **AUC of 0.87** and an **Average Precision of 0.76**. Overall, a **Macro AP of 0.7969**, shows a robust stability for the nuanced signal; these results ensure that inputs to the subsequent layer are statistically prioritized.
    """)

    # Local Image Injection: Side-by-Side Curves
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer1_roc.png", use_container_width=True)
            st.caption("(a) ROC Curves: Filtering Power")
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer1_pr.png", use_container_width=True)
            st.caption("(b) PR Curves: Precision Stability")
            
        st.caption("Figure X: Layer 1 Performance Curves. The high AUC for deterministic rejections confirms the model's efficiency in protecting the subsequent layer from data contamination.")

    st.divider()

    # Data Payload for Macro Performance
    macro_performance_data = {
        "Aggregate Metric": ["Macro AUC-ROC", "Macro Average Precision (AP)"],
        "Value": ["**0.9415**", "**0.7969**"],
        "Technical Verdict": [
            "**EXCELLENT:** Near-total separation of deterministic noise.",
            "**ROBUST:** High precision stability for the nuanced signal."
        ]
    }
    df_macro_performance = pd.DataFrame(macro_performance_data)
    
    st.markdown(df_macro_performance.to_markdown(index=False))
    st.caption("Table X: Layer 1 Macro Performance Summary.")

# ------------------------------------------
# TAB 3: LEARNING CURVE
# ------------------------------------------
with tab3:
    st.markdown("""
    To ensure model stability and identify data constraints, a Learning Curve audit was executed. This analysis monitors the performance delta between training and validation scores as the training sample size ($N$) increases, identifying the transition from high-variance noise to stable logic.
    """)

    # Local Image Injection: Learning Curve
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer1_learning.png", use_container_width=True)
            st.caption("Figure X: Layer 1 Learning Curve. The narrowing delta between the training and validation scores indicates successful logic convergence, while the upward trajectory of the validation curve suggests a data-starved state.")

    st.divider()

    # Data Payload for Learning Curve Diagnostics
    learning_curve_data = {
        "Diagnostic Metric": ["Final Validation Score", "Generalization Gap"],
        "Value": ["**0.8103**", "0.1245"],
        "Technical Verdict": [
            "**STABLE:** Model generalizes effectively to unseen data.",
            "**MODERATE:** Variance is narrowing as training volume increases."
        ]
    }
    df_learning_curve = pd.DataFrame(learning_curve_data)
    
    st.markdown(df_learning_curve.to_markdown(index=False))
    st.caption("Table X: Learning Curve Diagnostic Summary.")

    st.markdown("""
    The persistent upward slope of the validation curve identifies a **data-starved state**; while the current model is operationally valid, the performance ceiling remains active, indicating that accuracy would likely scale linearly with additional ground-truth samples.
    """)

# ------------------------------------------
# TAB 4: SHAP DNA
# ------------------------------------------
with tab4:
    st.markdown("""
    To interpret the internal logic of the first-tier filter, a SHAP (Shapley Additive exPlanations) audit was performed on the `THE_NUANCED_REST` class. This analysis identifies the features that qualify an offer for Layer 2 evaluation versus those that drive a deterministic rejection.
    """)

    # Local Image Injection: SHAP DNA
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer1_shapv2.png", use_container_width=True)
            st.caption("Figure X: Layer 1 Signal Drivers. Teal bars indicate features that push an offer into the 'Nuanced' category for evaluation; gray bars indicate features that drive a deterministic rejection.")

    st.divider()

    st.markdown("""
    The SHAP audit reveals the structural separation between deterministic rejections and the nuanced selection signal. The triage logic is governed by three primary mechanics:

    * **The Topographic Filter (Exclusion):** The primary drivers for rejection are geospatial. Destinations in the `Unassigned Area` ($-0.332$) and proxy zones like `Roma/Condesa` ($-0.196$) trigger immediate exclusion. This confirms that at the first tier, the Agent prioritizes "Where" over "How much".
    
    * **The Traffic Chaser Heuristic (Inclusion):** Contrary to standard assumptions, high congestion serves as a positive inclusion signal. The `historical_rolling_avg_traffic_index` ($+0.144$) and `traffic_index` ($+0.106$) push offers into the Nuanced category. This validates the strategy of targeting high-friction market states to secure EPH premiums that are often absent in fluid, low-demand regimes.
    
    * **Volatility vs. Friction:** While known traffic is desirable, unpredicted risk is not. The `traffic_volatility_index_ml` ($-0.068$) acts as a negative driver. Rejection is triggered not by friction itself, but by the **uncertainty** of the algorithm's prediction. High volatility signals the risk of operational margin erosion. This justifies the late-stage engineering of the volatility suite following the causal inference audit.
    """)




# ==========================================
# TRANSITION: THE ARCHITECTURAL VERDICT
# ==========================================
st.divider() 

st.subheader("Layer 2: Nuance Engine")
st.markdown("""
The second stage of the hierarchy resolves the distinctions between strategic rejections and final acceptance. By operating exclusively on the high-signal sub-universe, the engine achieves separation between complex decision states.
""")

# Initialize the 4-Tab Architecture for Layer 2
tab1, tab2, tab3, tab4 = st.tabs([
    "🧮 Confusion Matrix & Report", 
    "📈 ROC-AUC & PR-AUC", 
    "📉 Learning Curve", 
    "🧬 SHAP DNA"
])

# ------------------------------------------
# TAB 1: CONFUSION MATRIX & CLASSIFICATION REPORT
# ------------------------------------------
with tab1:
    
    # Local Image Injection: Layer 2 Confusion Matrix
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_matrixv2.png", use_container_width=True)
            st.caption("Figure X: Layer 2 Confusion Matrix. The model separates nuanced classes with high precision after the removal of deterministic noise.")

    st.divider()

    st.markdown("""
    The model achieved a **Macro F1-score of 0.91** on the holdout set ($N=164$). The result represents a significant lift over the monolithic baseline and confirms that isolating intent from deterministic noise enables the engine to perfectly replicate expert policy.
    """)

    # Data Payload for Layer 2 Classification Report
    layer2_report_data = {
        "Class Label": ["`ACCEPTED`", "`strategic_mismatch`", "`expected_value_gamble`", "**Macro Average**"],
        "Precision": ["0.92", "0.96", "0.84", "**0.91**"],
        "Recall": ["0.91", "0.95", "0.88", "**0.91**"],
        "F1-Score": ["0.92", "0.95", "0.86", "**0.91**"],
        "Support": ["67", "56", "41", "**164**"]
    }
    df_layer2_report = pd.DataFrame(layer2_report_data)
    
    # Render Table
    st.markdown(df_layer2_report.to_markdown(index=False))
    st.caption("Table X: Layer 2 Classification Report: Strategic decision cloning performance.")

# ------------------------------------------
# TAB 2: ROC-AUC & PR-AUC
# ------------------------------------------
with tab2:
    st.markdown("""
    The ROC-AUC and PR-AUC analyses identify the successful neutralization of the signal-masking effect[cite: 447]. All decision classes—including the `expected_value_gamble` (AUC: 0.97)—reach performance levels near the theoretical maximum[cite: 448].
    """)

    # Local Image Injection: Side-by-Side Curves
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_roc.png", use_container_width=True)
            st.caption("(a) ROC Curves: Separation Capacity [cite: 462]")
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_pr.png", use_container_width=True)
            st.caption("(b) PR Curves: Decision Stability [cite: 468]")
            
        st.caption("Figure X: Layer 2 Performance Curves. The proximity of the functions to the upper-right coordinate confirms high fidelity in replicating expert intent[cite: 469].")

    st.divider()

    # Data Payload for Layer 2 Macro Performance
    layer2_macro_data = {
        "Aggregate Metric": ["Macro AUC-ROC", "Macro Average Precision (AP)", "`ACCEPTED` Class Uplift"],
        "Value": ["**0.9814**", "**0.9613**", "**+56.3 pts**"],
        "Technical Verdict": [
            "**ELITE:** Near-total separation of nuanced intent[cite: 470].",
            "**ELITE:** Exceptional precision stability[cite: 470].",
            "**SIGNIFICANT:** Model AP (97.2%) vs. Random Baseline (40.9%)[cite: 470]."
        ]
    }
    df_layer2_macro = pd.DataFrame(layer2_macro_data)
    
    st.markdown(df_layer2_macro.to_markdown(index=False))
    st.caption("Table X: Layer 2 Macro Performance and Class-Specific Uplift Summary[cite: 471].")

    st.markdown("""
    The most significant result is the PR stability of the `ACCEPTED` class[cite: 472]. As shown in the performance summary, achieving an Average Precision of **97.2%** represents a 56.3-point lift over the random baseline[cite: 473].
    """)

# ------------------------------------------
# TAB 3: LEARNING CURVE
# ------------------------------------------
with tab3:
    st.markdown("""
    Although initial results appeared promising, holdout testing revealed that the Layer 2 model had overfitted rather than generalized to unseen data[cite: 475]. Due to the limited sample size ($N=787$), the model suffered from the curse of dimensionality[cite: 476]. 
    
    As shown in the learning curves below, the high feature count relative to the small subset size compromised stability[cite: 477]. To resolve this, a refined "lightweight" configuration utilizing only six core features was engineered[cite: 478].
    """)

    # Data Payload for Lightweight Features
    lightweight_features_data = {
        "Feature Name": [
            "`session_progress_ratio`", 
            "`total_acc_deadhead_sec`", 
            "`cycle_rolling_avg_spread`", 
            "`eph_operational_index`", 
            "`cycle_cum_net_earnings`", 
            "`home_vector_alignment_score`"
        ]
    }
    df_lightweight_features = pd.DataFrame(lightweight_features_data)
    
    # Render Table
    st.markdown(df_lightweight_features.to_markdown(index=False))
    st.caption("Table X: The distilled feature set for the lightweight model.")

    st.divider()

    # Local Image Injection: Side-by-Side Curves
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_learning_raw.png", use_container_width=True)
            st.caption("(a) Full Feature Set (Raw)")
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_learning_light.png", use_container_width=True)
            st.caption("(b) Lightweight Matrix (6 Features)")
            
        st.caption("Figure X: Layer 2 Generalization Audit. The comparison illustrates the tension between capturing intent (high variance) and achieving stable generalization (high bias).")

    st.divider()

    st.markdown("""
    While the full feature set resulted in a 23.8% gap between training and validation scores, the lightweight configuration narrowed this gap to 10.6%, with the tradeoff, however, of losing predictive capacity[cite: 499].
    """)

    # Data Payload for Layer 2 Robustness Audit
    layer2_robustness_data = {
        "Configuration": ["Full Feature Set", "Lightweight Matrix"],
        "Train F1": ["0.9373", "0.7182"],
        "Val F1": ["**0.6986**", "**0.6116**"],
        "Gap ($\Delta$)": ["0.2387", "**0.1066**"],
        "Diagnostic Verdict": [
            "**HIGH VARIANCE:** The model overfitted to the training set.",
            "**HIGH BIAS:** A 10% gap means the model generalized better, with the tradeoff of losing predictive capacity."
        ]
    }
    df_layer2_robustness = pd.DataFrame(layer2_robustness_data)
    
    st.markdown(df_layer2_robustness.to_markdown(index=False))
    st.caption("Table X: Layer 2 Robustness Audit: Comparative performance and generalization gap.")

    st.info("""
    **Strategic Outcome:** Within the limitations of the available dataset, this audit identifies the current ceiling for policy optimization[cite: 502]. Consequently, it is recommended that both the high-variance and lightweight configurations be evaluated in a production setting through shadow deployment or A/B testing[cite: 503]. Identifying the optimal balance between strategic nuance and operational stability would require live verification, irrespective of these specific offline metrics[cite: 504].
    """)

# ------------------------------------------
# TAB 4: SHAP DNA
# ------------------------------------------
with tab4:
    st.markdown("""
    To interpret the internal logic of the Nuance Engine, a SHAP contribution audit was performed across the three classes. These plots represent the behavioral genome of the expert agent, quantifying the non-linear psychological and economic shifts that occur during a work shift.
    """)

    # Local Image Injection: SHAP DNA for Layer 2
    with st.container():
        col1, col2, col3 = st.columns([1, 8, 1])
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_layer2_shap_dna_v2.png", use_container_width=True)
            st.caption("Figure X: Hierarchical Strategic DNA Atlas: Feature contributions for Layer 2 decision classes. Teal bars indicate a positive contribution to class probability; gray bars indicate a negative contribution.")

    st.divider()

    st.markdown("""
    **Diagnostic Findings:** The audit identifies primary behavioral mechanics that govern the expert agent's high-level strategy:

    * **The Sunk Cost Mechanic:** `log_total_accumulated_deadhead_sec` ($+0.287$) serves as the primary driver for `ACCEPTED` outcomes. This provides empirical proof of the **Sunk Cost Fallacy**: as uncompensated search time increases, the agent's selectivity threshold decays. Conversely, this feature is the strongest negative driver for `expected_value_gamble` ($-0.417$), proving that patience is a finite resource; strategic gambling is abandoned once search costs become excessive.
    
    * **The Endgame Transition:** The `session_progress_ratio` ($+0.431$) is the dominant driver for `strategic_mismatch` rejections. This confirms the policy transition from an *Economic Maximizer* at shift commencement to a *Positional Optimizer* as the ratio approaches $1.0$. The negative impact of `home_vector_alignment_score` ($-0.289$) confirms that homecoming vectors toward *Anzures* suppress this rejection type.
    
    * **Income Targeting:** In the `strategic_mismatch` class, high `cycle_cumulative_net_earnings` ($+0.285$) pull the decision toward rejection. This verifies the **Target Income** heuristic: once the daily financial quota is secured, the agent prioritizes session termination over marginal revenue gains.
    
    * **Economic Gravity:** Across all classes, `log_upfront_fare` and `eph_operational_index` remain the baseline anchors. High financial magnitude remains the primary inclusion vector for acceptance, while its absence is the primary driver for low-level rejections.
    """)

    st.info("""
    **Strategic Outcome:** The Layer 2 SHAP audit validates the Hierarchical Cascade architecture. By stripping away deterministic noise in Layer 1, the Nuance Engine successfully extracted complex human psychological phenomena—such as the Sunk Cost Fallacy and Target Income heuristics—directly from objective telemetry. This proves the engine is not merely matching statistical probabilities, but actually replicating the expert agent's dynamic economic reasoning.
    """)




