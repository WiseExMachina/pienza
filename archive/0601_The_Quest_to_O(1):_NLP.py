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

# ==========================================
# PHASE 6: HEADER & INTRO (Non-Collapsible)
# ==========================================
st.title("The Quest to $O(1)$ Inference: NLP Transformers")

st.markdown("""
In high-frequency dispatch environments, inference latency is the primary constraint for the viability of a real-time decision agent. To satisfy the requirements of *Online Transaction Processing* (OLTP), the project analyzed three generations of urban inference through the lens of algorithmic efficiency and system scalability.

The current (Phases 1-5) architecture relies on external geocoding APIs and Point-in-Polygon (PiP) algorithms, constrained by $O(N \\times M)$ geometric complexity and high network I/O latency (>500ms). To bypass this bottleneck, the project engineered **miniBabel**: a locally-hosted Transformer that maps raw urban syntax directly to a `zone_id`. By treating geographic resolution as a task of semantic pattern recognition, the system collapses the search space into constant-time $O(1)$ neural inference. This architecture reduces end-to-end latency to <10ms and provides a strategic bridge toward the high-availability horizon of bitwise H3 integer indexing.

While the internal complexity of the attention mechanism is quadratic to the sequence length $L$, the bounded nature of urban address strings transforms the inference into a fixed-cost operation relative to the number of strategic zones.
""")

# Table 1: Comparative Efficiency Ledger
efficiency_data = {
    "Architecture": ["External API", "**miniBabel**", "Uber H3"],
    "Method": ["Geometric PiP", "**Neural Inference**", "Hash Lookup"],
    "Complexity": ["$O(N \\times M)$", "**$O(1)$**", "$O(1)$ (Bitwise)"],
    "Latency": ["High (>500ms)", "**Low (<10ms)**", "Ultra-Low (<1ms)"],
    "Strategic Value": [
        "Research-only; high I/O risk.",
        "**Production-ready; autonomous.**",
        "Ideal target for fleet-scale telemetry."
    ]
}
df_efficiency = pd.DataFrame(efficiency_data)

# ✅ Render bold text natively via Markdown
st.markdown(df_efficiency.to_markdown(index=False))
st.caption("Table 1: Comparative Efficiency Ledger: Algorithmic complexity and latency classes for urban inference.")

st.markdown("""
The transition to neural inference required a multi-stage pipeline, beginning with the transformation of raw urban syntax into high-density signals via hierarchical linguistic engineering. This foundation enabled a comparative tournament between a custom-built, lightweight Transformer (**miniBabel**) and a pre-trained **BETO** baseline, both optimized through rigorous regularization to handle the high entropy of Mexico City’s address landscape. While the large-scale BERT model achieved peak precision, the lightweight miniBabel successfully resolved spatial clusters with highly competitive accuracy—establishing an optimal latency-precision trade-off that secures the $<10$ms inference threshold required for real-time autonomous dispatch.

**👇 Explore the linguistic engineering, architectural trade-offs, and performance audits in the collapsible sections below, or jump directly to the Pienza Babel Interactive Dashboard.**
""")







# ==========================================
# 1. LINGUISTIC FEATURE ENGINEERING
# ==========================================
with st.expander("1. Linguistic Feature Engineering: From Urban Syntax to Neural Signal", expanded=False):

    st.markdown("""
    To transform high-entropy address strings into high-density neural signals, the project implemented a hierarchical preprocessing pipeline. This stage focused on strategic data augmentation to ensure the model generalizes across the Mexico City urban landscape:

    * **Deterministic Normalization:** Collapsed thousands of syntactic variations (*e.g., Av, Ave, Avenida*) into unified canonical tokens. This artificially increased signal density, allowing the subsequent neural architecture to focus on geographic disambiguation rather than basic syntactic learning.
    * **Token Soldering:** Utilized high-precision Regular Expressions to fuse numeric and cardinal qualifiers with primary street identifiers (*e.g., "Eje 6 Sur" → `eje_6_sur`*). This prevents the model from treating structural modifiers as isolated noise, anchoring them to their relevant spatial context.
    * **Target Leakage Mitigation:** Deployed a "Slash-Purge" protocol to remove platform-generated neighborhood labels (*e.g., "Roma/Condesa"*) from the raw strings. By pruning these explicit identifiers, the model is forced to learn latent geographic features—such as street-level syntax and intersection patterns.
    * **Zip Code Standardization:** Standardized all 5-digit postal codes by prepending a unique `cp` prefix (*e.g., "11590" → `cp11590`*). This transformation isolates zip codes from other numerical data, creating high-precision spatial anchors for the neural engine.
    * **Semantic Embedding (Word2Vec):** This Skip-gram architecture was used as a tool to explore spatial proximity within the urban lexicon. By encoding tokens into 64-dimensional vectors, the model internalizes the semantic relationship between adjacent zones.
    """)

    st.markdown("""
    A **Token Lift** analysis validated the preprocessing pipeline by identifying words with disproportionately high frequencies in specific zones relative to their global usage.
    """)

    # Local Image Injection: Linguistic Signature
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.image("/workspaces/pienza/observatory/assets/overleaf_images/fig_linguistic_signature.png", use_container_width=True)
            st.caption("Figure 2: The Linguistic Signature of CDMX: Top tokens by Linguistic Lift. Standardized zip codes and distinct landmarks provide the strongest geographic signals for the neural engine.")

    st.markdown("""
    As illustrated in Figure 2, the audit revealed three critical structural advantages:

    * **Zip Code Dominance:** Prefixed postal codes (*e.g.,* `cp06100`) emerged as the strongest predictors for major hubs, validating their isolation from general numerical noise.
    * **Linguistic Specificity:** Iterative pruning successfully separated distinct neighborhood markers (*e.g.,* `manca`, `granada`) from generic urban vocabulary.
    * **Infrastructural Anchors:** High-lift keywords like `terminal_1` effectively resolve dense transit nodes, complementing the spatial HDBSCAN clusters discovered in Phase 4.
    """)





    # ==========================================
# 3. MODEL ARCHITECTURES & OPTIMIZATION
# ==========================================
with st.expander("2. Model Architectures & Optimization Constraints", expanded=False):

    st.subheader("Model Architectures: Custom vs. Pre-trained")
    st.markdown("""
    To identify the optimal mapping function between urban syntax and strategic zones, the project benchmarked a custom-built Transformer against a state-of-the-art pre-trained baseline.
    """)

    st.markdown("**Model A: miniBabel (Custom Urban Transformer)**")
    st.markdown("""
    To prevent catastrophic overfitting on the boutique dataset, the **miniBabel** architecture was restricted to two attention layers and utilized a high-dropout bottleneck ($p=0.2$) prior to the classifier. To ensure high-value spatial anchors (*e.g., specific street names*) were not diluted during processing, the model replaced standard Global Average Pooling with a **fused Max-Average pooling** mechanism. This allows the classifier to ingest both the holistic context of the address and its sharpest geometric signals simultaneously.
    """)

    st.markdown("**Model B: miniBETO (Spanish BERT Adaptation)**")
    st.markdown("""
    For comparative benchmarking, the project adapted **BETO** (a pre-trained Spanish BERT model). Adapting a model trained on standard prose to condensed urban syntax required the replacement of the default classification head. To ensure a scientifically valid comparison, the modified miniBETO was equipped with the identical fused pooling and bottleneck constraints utilized in the custom miniBabel architecture.
    """)

    st.divider()

    st.subheader("Optimization and Training Constraints")
    st.markdown("""
    Due to the inherent class imbalance of the `zone_id` distribution, both models utilized the **Weighted F1-Score** as the primary evaluation criterion. Training was governed by a multi-layered regularization protocol:

    * **Dynamic Early Stopping:** Triggered by F1-Score plateauing to prevent over-training and preserve generalization.
    * **Label Smoothing (0.1):** Applied to the loss function to penalize overconfident logit generation and improve the calibration of the final probability scores.
    * **Bottleneck Regularization:** Aggressive dropout was enforced across both models to ensure the resulting spatial identifiers remain robust to the high-entropy noise of real-world address strings.
    """)





    # ==========================================
# 4. PERFORMANCE BENCHMARKING
# ==========================================
with st.expander("3. Performance Benchmarking: Precision vs. Complexity", expanded=False):

    st.markdown("""
    To evaluate the efficacy of $O(1)$ neural inference, both the custom **miniBabel** and the adapted **BETO** models were benchmarked across identical training constraints. Performance metrics were selected to account for geographic class imbalances and operational throughput requirements.
    """)

    # Table: NLP Benchmarks
    nlp_bench_data = {
        "Architecture": ["Custom Transformer (*miniBabel*)", "**BETO (Spanish BERT)**"],
        "Params": ["$\\approx 1.5$M", "**$\\approx 110$M**"],
        "Epochs": ["22", "**17**"],
        "Acc.": ["83.04%", "**86.58%**"],
        "Macro F1": ["0.79", "**0.84**"],
        "Weighted F1": ["0.8266", "**0.8622**"]
    }
    df_nlp_bench = pd.DataFrame(nlp_bench_data)
    
    # ✅ Siamic Table Rendering
    st.markdown(df_nlp_bench.to_markdown(index=False))
    st.caption("Table 2: Comparative performance metrics for the NLP urban inference tournament.")

    st.markdown("""
    The results demonstrate that the pre-trained **BETO** architecture achieves the highest absolute performance, leveraging its 110-million parameter representation to generalize across minority zones with a 0.86 Weighted F1. However, the **miniBabel** model achieved a highly competitive 0.8266 score despite possessing less than 2% of the parameter count of the BERT baseline. This confirms that the hierarchical linguistic engineering phase successfully condensed the urban syntax into high-density signals, allowing a lightweight 2-layer attention mechanism to resolve spatial clusters with high accuracy. 

    The selection between these architectures represents a fundamental trade-off between absolute precision and **Inference Latency**. While BETO provides a $\\approx 3.5$% gain in F1 performance, miniBabel's ultra-low parameter count is uniquely optimized for resource-constrained OLTP environments. By prioritizing the custom Transformer, the framework ensures inference latency remains below the 10ms threshold required for real-time dispatch operations.
    """)

    st.divider()

    st.subheader("Qualitative Inference Audit")
    st.markdown("""
    To assess the qualitative performance of the **miniBabel** engine, a diagnostic audit was performed on raw, unstructured address strings. The following table illustrates the model's ability to resolve spatial context from linguistic markers while maintaining address-number obfuscation for privacy.
    """)

    # Table: Qualitative Audit
    audit_data = {
        "Raw Input Address (Obfuscated)": [
            "`av universidad anahuac_## col lomas...`",
            "`av santa fe_### col santa fe...`",
            "`blvd loma real_## cp52774...`",
            "`anillo periferico blvd manuel...`"
        ],
        "Ground Truth": ["`anahuac_norte`", "`sf_centro_com`", "`bosque_real`", "`lomas_chapultepec`"],
        "Prediction": ["`anahuac_norte`", "`sf_centro_com`", "`interlomas_hub`", "`polanco_grupo_m`"],
        "Conf.": ["97.6%", "87.2%", "29.5%", "76.7%"],
        "Result": ["HIT", "HIT", "**MISS**", "**MISS**"]
    }
    df_audit = pd.DataFrame(audit_data)

    # ✅ Siamic Table Rendering
    st.markdown(df_audit.to_markdown(index=False))
    st.caption("Table 3: Pienza Babel qualitative inference audit with address-number obfuscation.")

    st.markdown("""
    The audit identifies two distinct behavioral characteristics of the neural inference engine:
    1. **Confidence-Based Filtering:** The miss on *Bosque Real* was accompanied by a low confidence score (29.5%), allowing the system to flag the prediction as unreliable. 
    2. **Topological Adjacency Errors:** The high-confidence miss on *Anillo Periférico* highlights the limitation of purely linguistic models for arterial roads that are on the limit of adjacent zones.
    """)

    st.info("""
    **Strategic Outcome:** While miniBabel successfully decouples dispatch from high-latency APIs via $O(1)$ probabilistic routing, topological boundary errors confirm that neural inference remains a statistical approximation. Its ultimate value lies in acting as an **offline compiler** to map the address corpus into deterministic Uber H3 indices, establishing the foundation for sub-millisecond dispatch.
    """)





