import json
import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from components.styles import GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Infinite Manifold: cGAN Keras | Pienza")

def build_sidebar():
    with st.sidebar:
        st.markdown("Project Pienza")
        st.markdown("---")
        st.page_link("main.py", label="Home")
        st.page_link("pages/0001_Foundations.py", label="Foundations")
        st.page_link("pages/0002_Acquisition_Pipelines.py", label="Acquisition Pipelines")
        st.page_link("pages/0003_Feature_Store.py", label="Feature Store")
        st.page_link("pages/0004_Data_Census_(The_Basics).py", label="Data Census: The Basics")
        st.page_link("pages/0005_The_Cost_of_Patience.py", label="The Cost of Patience: Optimal Stopping")
        st.page_link("pages/0006_Payout_Physics_Causal_Inference.py", label="Payout Physics: Causal Inference")
        st.page_link("pages/0007_Human_vs_AI_Behavioral_Cloning.py", label="Human vs AI: Behavioral Cloning")
        st.page_link("pages/0008_The_Quest_to_O1_NLP.py", label="The Quest to (O)1: NLP Transformer")
        st.page_link("pages/0009_Infinite_Manifold:_cGAN_Keras.py", label="Infinite Manifold: cGAN Keras")
        st.markdown("---")
        st.markdown("**Archive**")
        st.page_link("pages/9001_cGAN_Engine.py", label="cGAN Keras Engine")
        st.page_link("pages/9002_Network_Graph.py", label="Network Graph Analysis: Tensor vs Topological")
        st.page_link("pages/9003_Markov_Fleet_Sim_Dashboard.py", label="Markov Fleet Simulator")
        st.markdown("---")
        st.markdown("**Author:** Bernardo Lozano Wise")
        st.markdown("**Domain:** Autonomous AV Simulation")
        st.markdown("**Stack:** Python, TensorFlow, BigQuery, Pydeck")
        st.markdown("---")
        try:
            with open("assets/Pienza_Papers.pdf", "rb") as f:
                pdf_data = f.read()
            st.download_button("📄 Download 91-Page Report (PDF)", data=pdf_data, file_name="Project_Pienza_Full_Report.pdf", mime="application/pdf")
        except FileNotFoundError:
            pass
        st.markdown("[🔗 View GitHub Repository](https://github.com/your-repo)")
        st.markdown("---")

build_sidebar()

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# --- Page-specific type: JetBrains Mono for the industrial/blueprint readouts ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&family=JetBrains+Mono:wght@400;500;700;800&display=swap');
/* Force white background on native bordered containers (st.container(border=True)) to match
   the hand-styled bento cards elsewhere on this page (e.g. the cGAN circuit box). */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff !important;
    border-radius: 4px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 4px 24px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="max-width:1100px; margin:0 auto; padding:16px 0 60px; font-family:'Inter',sans-serif; color:#121212;">

<h1 style="font-size:44px; font-weight:900; letter-spacing:-1.5px; line-height:1.03; margin:8px 0 44px; color:#121212; white-space:nowrap;">GENERATIVE MOONSHOTS</h1>

<!-- SECTION LABEL -->
<div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; letter-spacing:3px; color:#94a3b8; text-transform:uppercase; white-space:nowrap;">// cGAN &middot; Keras Engine</div>
<div style="flex:1; height:1px; background:rgba(0,0,0,0.12);"></div>
</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:14px; color:#21918c; letter-spacing:0.3px; margin-bottom:18px;">5,123 real rides in &rarr; 1,010,001 synthetic rides out</div>

<!-- ============ CIRCUIT ============ -->
<div style="border:1px solid #eaeaea; border-radius:4px; padding:28px 24px; background:#fff; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
<div style="overflow-x:auto; padding-bottom:6px;">
<div style="display:flex; flex-wrap:nowrap; align-items:center; justify-content:flex-start; gap:10px 6px; width:max-content; margin:0 auto;">

<!-- inputs -->
<div style="display:flex; flex-direction:column; gap:10px; width:150px;">
<div style="border:1px solid rgba(33,145,140,0.5); background:rgba(33,145,140,0.06); border-radius:2px; padding:12px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1px; color:#21918c; text-transform:uppercase; margin-bottom:4px;">Latent Noise</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:16px; font-weight:800; color:#121212;">z ~ N(100)</div>
</div>
<div style="border:1px solid #eaeaea; border-radius:2px; padding:10px 12px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1px; color:#888; text-transform:uppercase; margin-bottom:6px; text-align:center;">Context (6)</div>
<div style="display:flex; flex-wrap:wrap; gap:4px; justify-content:center;">
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">hour</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">day</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">product</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">dropoff</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">pickup</span>
<span style="font-family:'JetBrains Mono',monospace; font-size:9px; background:#f8f9fa; border:1px solid #eaeaea; border-radius:2px; padding:2px 6px; color:#555;">reason</span>
</div>
</div>
</div>

<div style="text-align:center; color:#21918c; font-size:16px; font-family:'JetBrains Mono',monospace;">&rarr;</div>

<!-- generator -->
<div>
<div style="background:#21918c; border-radius:2px; padding:18px 16px; width:150px;">
<div style="font-size:17px; font-weight:800; color:#fff; margin-bottom:8px;">Generator</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:rgba(255,255,255,0.85); line-height:1.5;">133-dim &rarr; 512&rarr;1024&rarr;2048 &rarr; tanh(5)</div>
</div>
<div style="text-align:center; font-family:'JetBrains Mono',monospace; font-size:10px; color:#888; margin-top:8px;">2.72M params</div>
</div>

<div style="text-align:center; color:#21918c; font-size:16px; font-family:'JetBrains Mono',monospace;">&rarr;</div>

<!-- fake physics -->
<div>
<div style="border:1px dashed rgba(33,145,140,0.5); border-radius:2px; padding:12px; width:128px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1px; color:#21918c; text-transform:uppercase; margin-bottom:6px; text-align:center;">Fake Physics (5)</div>
<div style="display:flex; flex-direction:column; gap:3px; font-family:'JetBrains Mono',monospace; font-size:10px; color:#555;">
<div>fare</div><div>trip time</div><div>trip dist</div><div>dist&rarr;pickup</div><div>time&rarr;pickup</div>
</div>
</div>
</div>

<div style="text-align:center; color:#888; font-size:16px; font-family:'JetBrains Mono',monospace;">&rarr;</div>

<!-- discriminator -->
<div>
<div style="background:#fff; border:1.5px solid #555; border-radius:2px; padding:18px 16px; box-shadow:0 4px 10px rgba(0,0,0,0.04); width:150px;">
<div style="font-size:17px; font-weight:800; color:#121212; margin-bottom:8px;">Discriminator</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#666; line-height:1.5;">38-dim &rarr; 1024&rarr;512&rarr;256 &rarr; sigmoid</div>
</div>
<div style="text-align:center; font-family:'JetBrains Mono',monospace; font-size:10px; color:#888; margin-top:8px;">697K params</div>
<div style="text-align:center; color:#888; font-size:13px; font-family:'JetBrains Mono',monospace; margin-top:14px;">&uarr;</div>
<div style="border:1px solid #eaeaea; border-radius:2px; padding:9px 10px; display:flex; align-items:center; justify-content:center; gap:6px; margin-top:6px; width:150px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:1px;">Real Rides</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#121212; font-weight:700;">5,123</div>
</div>
</div>

<div style="text-align:center; color:#888; font-size:16px; font-family:'JetBrains Mono',monospace;">&rarr;</div>

<!-- verdict -->
<div>
<div style="width:96px; height:96px; border-radius:50%; background:#121212; display:flex; align-items:center; justify-content:center; text-align:center;">
<div>
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#fff; text-transform:uppercase; letter-spacing:1px;">Verdict</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:12px; color:#2dd4bf; font-weight:800; margin-top:4px;">real / fake</div>
</div>
</div>
</div>

<div style="color:#888; font-size:16px; font-family:'JetBrains Mono',monospace;">&rarr;</div>

<!-- 1M manifold output -->
<div>
<div style="border:1.5px solid #21918c; border-radius:2px; padding:16px 18px; background:rgba(33,145,140,0.06); width:150px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Out</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:15px; font-weight:800; color:#121212;">1M Manifold</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#888; margin-top:4px;">1,010,001 rows</div>
</div>
</div>
</div>
</div>

<!-- feedback loop caption -->
<div style="position:relative; border-top:1.5px dashed rgba(33,145,140,0.45); margin:22px 60px 0; padding-top:14px;">
<span style="position:absolute; top:2px; left:50%; transform:translateX(-50%); background:#fff; padding:0 10px; font-family:'JetBrains Mono',monospace; font-size:10px; color:#21918c; font-weight:700; white-space:nowrap;">&larr; gradient feedback sharpens the Generator every batch</span>
</div>
</div>

<div style="height:24px;"></div>

<!-- ============ SPECIFICS STRIP ============ -->
<div style="display:grid; grid-template-columns:repeat(5,1fr); gap:1px; background:#eaeaea; border:1px solid #eaeaea; border-radius:4px; overflow:hidden; margin-bottom:36px;">
<div style="background:#fff; padding:16px 14px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:800; color:#121212;">64</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">batch size</div>
</div>
<div style="background:#fff; padding:16px 14px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:800; color:#121212;">2e-4</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">G / D lr</div>
</div>
<div style="background:#fff; padding:16px 14px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:800; color:#121212;">0.1</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">label smoothing</div>
</div>
<div style="background:#fff; padding:16px 14px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:800; color:#121212;">1-2-3</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">X&middot;Mid-Tier&middot;Black</div>
</div>
<div style="background:#fff; padding:16px 14px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:800; color:#121212;">67</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">operational zones</div>
</div>
</div>

<!-- ============ CLOSING LINE ============ -->
<div style="font-size:0.9rem; color:#64748b; line-height:1.7; max-width:760px; text-align:center; margin:0 auto;">
Point the trained Generator at any hour &middot; zone &middot; product combination and it hallucinates fare, timing and distance that pass the Discriminator's scrutiny &mdash; that's the engine behind the <b style="color:#121212;">1,010,001-row</b> synthetic manifold.
</div>

<!-- ============ CLOUD MIGRATION ============ -->
<div style="margin-top:64px;">
<div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; letter-spacing:3px; color:#94a3b8; text-transform:uppercase; white-space:nowrap;">// Cloud Migration: ELT</div>
<div style="flex:1; height:1px; background:rgba(0,0,0,0.12);"></div>
</div>

<div style="display:flex; flex-wrap:wrap; gap:14px; justify-content:center;">
<div style="border:1px solid #eaeaea; border-radius:2px; padding:16px 18px; background:#fff; width:230px; min-height:112px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Load &rarr; GCS/BigQuery</div>
<div style="font-size:0.78rem; color:#666; line-height:1.5;">1,010,001-row manifold persisted to <b style="color:#121212;">GCS</b>, queried through BigQuery's external table interface.</div>
</div>
<div style="align-self:center; color:#888; font-family:'JetBrains Mono',monospace; font-size:16px;">&rarr;</div>
<div style="border:1px solid #eaeaea; border-radius:2px; padding:16px 18px; background:#fff; width:230px; min-height:112px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Denormalization</div>
<div style="font-size:0.78rem; color:#666; line-height:1.5;"><b style="color:#121212;">Apache Spark</b> reconstitutes the flat physics + switches back into full ride records via <b style="color:#121212;">broadcast joins</b>.</div>
</div>
<div style="align-self:center; color:#888; font-family:'JetBrains Mono',monospace; font-size:16px;">&rarr;</div>
<div style="border:1px solid #eaeaea; border-radius:2px; padding:16px 18px; background:#fff; width:230px; min-height:112px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Downscaling</div>
<div style="font-size:0.78rem; color:#666; line-height:1.5;">Aggregated zones redistributed back down to real microzones.</div>
</div>
</div>
</div>

<!-- ============ STACK (sub-piece of Cloud Migration) ============ -->
<div style="margin-top:36px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1.5px; color:#aab1bc; text-transform:uppercase; text-align:center; margin-bottom:14px;">storage & compute</div>

<div style="display:grid; grid-template-columns:repeat(2,1fr); gap:1px; background:#eaeaea; border:1px solid #eaeaea; border-radius:2px; overflow:hidden; max-width:560px; margin:0 auto;">
<div style="background:#fff; padding:20px 18px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:0.92rem; font-weight:800; color:#121212; margin-bottom:8px;">Google Cloud Storage</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.8px;">Lakehouse</div>
</div>
<div style="background:#fff; padding:20px 18px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:0.92rem; font-weight:800; color:#121212; margin-bottom:8px;">BigQuery</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:0.8px;">Computation</div>
</div>
</div>
</div>

<!-- ============ DEFINITIVE ARCHITECTURE (sub-piece of Cloud Migration) ============ -->
<div style="margin-top:36px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1.5px; color:#aab1bc; text-transform:uppercase; text-align:center; margin-bottom:14px;">single source of truth</div>

<div style="display:grid; grid-template-columns:1fr 1fr; gap:1px; background:#eaeaea; border:1px solid #eaeaea; border-radius:2px; overflow:hidden; max-width:820px; margin:0 auto;">
<div style="background:#fff; padding:24px 22px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem; font-weight:800; color:#121212; margin-bottom:10px;">pienza_mini</div>
<div style="font-size:0.82rem; color:#666; line-height:1.65;">A high-fidelity cloud replica of the ground-truth database (<b style="color:#121212;">pienza.db</b>), preserving the identical relational logic.</div>
</div>
<div style="background:#fff; padding:24px 22px; border-left:2px solid #21918c;">
<div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem; font-weight:800; color:#21918c; margin-bottom:10px;">pienza_big</div>
<div style="font-size:0.82rem; color:#666; line-height:1.65;">A 1,010,001-row synthetic dataset generated via cGANs, persisted as Parquet artifacts and queried through BigQuery's external table interface.</div>
</div>
</div>
</div>

<!-- ============ WHERE PIENZA GOES NEXT ============ -->
<div style="margin-top:56px;">
<div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
<div style="font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; letter-spacing:3px; color:#94a3b8; text-transform:uppercase; white-space:nowrap;">// Scaffolding Toward Pienza 2.0</div>
<div style="flex:1; height:1px; background:rgba(0,0,0,0.12);"></div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# --- BLOCK 1: Topological / Undirected Graph — wrapped in a native bordered container so the
# card boundary can span across the raw-HTML stats strip AND the three.js iframe component
# (a plain <div> can't span two separate st.markdown/components.html calls). ---
_block1 = st.container(border=True)
with _block1:
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1.5px; color:#aab1bc; text-transform:uppercase; text-align:center; margin-bottom:14px;">topological / undirected graph &middot; 72 nodes</div>

<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#eaeaea; border:1px solid #eaeaea; border-radius:4px; overflow:hidden; max-width:520px; margin:0 auto 24px;">
<div style="background:#fff; padding:16px 12px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:800; color:#121212;">4.11</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">sigma</div>
</div>
<div style="background:#fff; padding:16px 12px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:800; color:#121212;">-0.27</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">omega</div>
</div>
<div style="background:#fff; padding:16px 12px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:800; color:#121212;">20.5%</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">reforma_palmas share</div>
</div>
</div>
""", unsafe_allow_html=True)

# --- Ego-network subgraph: nodo_reforma_palmas + its real 2-hop neighborhood (14 of 72 nodes) ---
    _edges_3d = [
        ('nodo_reforma_palmas', 'lomas_altas'), ('nodo_reforma_palmas', 'reforma_regina'),
        ('nodo_reforma_palmas', 'bosque_3'), ('nodo_reforma_palmas', 'ahuehuetes_norte'),
        ('nodo_reforma_palmas', 'lomas_barrilaco'), ('nodo_reforma_palmas', 'nodo_monte_libano'),
        ('nodo_reforma_palmas', 'lomas_trastevere'),
        ('lomas_altas', 'reforma_bnp'), ('lomas_altas', 'reforma_regina'), ('lomas_altas', 'bosque_3'),
        ('bosque_3', 'bosque_2'), ('bosque_3', 'lomas_trastevere'),
        ('lomas_virreyes', 'bosque_2'), ('lomas_virreyes', 'lomas_trastevere'),
        ('ahuehuetes_norte', 'de_las_fuentes'),
        ('lomas_barrilaco', 'lomas_prado_norte'), ('lomas_barrilaco', 'fuentes_casino'),
        ('lomas_barrilaco', 'lomas_trastevere'), ('lomas_barrilaco', 'nodo_monte_libano'),
        ('nodo_monte_libano', 'fuentes_casino'), ('nodo_monte_libano', 'de_las_fuentes'),
        ('lomas_prado_norte', 'fuentes_casino'), ('lomas_prado_norte', 'lomas_trastevere'),
        ('fuentes_casino', 'de_las_fuentes'),
    ]

    G_test = nx.Graph()
    G_test.add_edges_from(_edges_3d)
    pos_3d = nx.spring_layout(G_test, dim=3, seed=42)

    # Boundary/leaf nodes: the outer edge of the 2-hop traversal — real graph continues past these.
    _leaf_nodes = ['reforma_bnp', 'bosque_2', 'de_las_fuentes', 'lomas_prado_norte', 'fuentes_casino', 'lomas_virreyes']

    # 3D render via three.js embedded in an HTML component (k3d/pythreejs are ipywidgets that need
    # a live Jupyter kernel to sync state, which Streamlit doesn't have — both are themselves built
    # on three.js, so this is the faithful Streamlit-native equivalent, same WebGL engine).
    _nodes_json = json.dumps([
        {"id": n, "x": pos_3d[n][0], "y": pos_3d[n][1], "z": pos_3d[n][2],
         "center": n == "nodo_reforma_palmas", "leaf": n in _leaf_nodes}
        for n in G_test.nodes()
    ])
    _edges_json = json.dumps([[u, v] for u, v in G_test.edges()])

    _threejs_html = f"""
    <div id="three-container" style="position:relative; width:100%; height:520px; background:transparent; overflow:hidden;"></div>
    <script src="https://unpkg.com/three@0.128.0/build/three.min.js"></script>
    <script src="https://unpkg.com/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://unpkg.com/three@0.128.0/examples/js/renderers/CSS2DRenderer.js"></script>
    <script>
    const nodes = {_nodes_json};
    const edges = {_edges_json};
    const posById = {{}};
    nodes.forEach(n => posById[n.id] = n);

    const container = document.getElementById('three-container');
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, container.clientWidth / 520, 0.1, 1000);
    camera.position.set(2.2, 2.2, 2.2);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    renderer.setSize(container.clientWidth, 520);
    container.appendChild(renderer.domElement);

    const labelRenderer = new THREE.CSS2DRenderer();
    labelRenderer.setSize(container.clientWidth, 520);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0';
    labelRenderer.domElement.style.left = '0';
    labelRenderer.domElement.style.pointerEvents = 'none';
    container.appendChild(labelRenderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    const SCALE = 3.0;
    nodes.forEach(n => {{
      const geo = new THREE.SphereGeometry(n.center ? 0.09 : 0.05, 32, 32);
      const mat = new THREE.MeshBasicMaterial({{ color: n.center ? 0x21918c : 0xd9dcdf }});
      const sphere = new THREE.Mesh(geo, mat);
      sphere.position.set(n.x * SCALE, n.y * SCALE, n.z * SCALE);
      scene.add(sphere);

      const labelDiv = document.createElement('div');
      labelDiv.textContent = n.id;
      labelDiv.style.fontFamily = 'JetBrains Mono, monospace';
      labelDiv.style.fontSize = n.center ? '11px' : '9px';
      labelDiv.style.fontWeight = n.center ? '700' : '400';
      labelDiv.style.color = n.center ? '#21918c' : '#555';
      labelDiv.style.background = 'rgba(255,255,255,0.85)';
      labelDiv.style.padding = '1px 4px';
      labelDiv.style.borderRadius = '2px';
      labelDiv.style.whiteSpace = 'nowrap';
      const label = new THREE.CSS2DObject(labelDiv);
      label.position.set(0, n.center ? 0.14 : 0.09, 0);
      sphere.add(label);
    }});

    edges.forEach(([u, v]) => {{
      const a = posById[u], b = posById[v];
      const geo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(a.x * SCALE, a.y * SCALE, a.z * SCALE),
        new THREE.Vector3(b.x * SCALE, b.y * SCALE, b.z * SCALE),
      ]);
      const mat = new THREE.LineBasicMaterial({{ color: 0xaab1bc, transparent: true, opacity: 0.6 }});
      scene.add(new THREE.Line(geo, mat));
    }});

    // Dangling "stub" edges on leaf/boundary nodes — signal the real graph continues past this
    // 2-hop ego-network preview (convention borrowed from ego-network / cut-net diagrams).
    const centerPos = nodes.find(n => n.center);
    nodes.filter(n => n.leaf).forEach(n => {{
      const dir = new THREE.Vector3(n.x - centerPos.x, n.y - centerPos.y, n.z - centerPos.z).normalize();
      const base = new THREE.Vector3(n.x * SCALE, n.y * SCALE, n.z * SCALE);
      const stubLen = 0.5;
      const segments = 3;
      for (let i = 0; i < segments; i++) {{
        const p0 = base.clone().add(dir.clone().multiplyScalar(i * stubLen / segments));
        const p1 = base.clone().add(dir.clone().multiplyScalar((i + 1) * stubLen / segments));
        const geo = new THREE.BufferGeometry().setFromPoints([p0, p1]);
        const mat = new THREE.LineBasicMaterial({{ color: 0xaab1bc, transparent: true, opacity: 0.5 - i * 0.15 }});
        scene.add(new THREE.Line(geo, mat));
      }}
    }});

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));
    const pointLight = new THREE.PointLight(0xffffff, 0.6);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    function animate() {{
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    }}
    animate();
    </script>
    """
    components.html(_threejs_html, height=530)
    st.markdown("<div style='text-align:center; font-size:0.78rem; color:#666; max-width:640px; margin:8px auto 0;'>Node positions above use a force-directed layout (<code>nx.spring_layout</code>, seed=42) for readability &mdash; not real geography. Super-Node <b style=\"color:#121212;\">nodo_reforma_palmas</b> controls 20.5% of all optimal routing paths and its 7 direct connections are shown above &mdash; the network's highest degree (&sigma;=4.11, &omega;=-0.27 confirm it's small-world efficient).</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:0.78rem; color:#666; max-width:640px; margin:8px auto 0;'><b style=\"color:#121212;\">Ego-network preview</b> &mdash; 2-hop neighborhood of <b style=\"color:#121212;\">nodo_reforma_palmas</b> (14 of 72 nodes in the undirected topological graph). Fading stub lines mark the boundary nodes where the real graph continues beyond this preview.</div>", unsafe_allow_html=True)

# --- BLOCK 2: Mobility Tensor / Directed Graph ---
_block2 = st.container(border=True)
with _block2:
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1.5px; color:#aab1bc; text-transform:uppercase; text-align:center; margin-bottom:14px;">mobility tensor / directed graph &middot; synthetic manifold</div>

<div style="display:flex; align-items:center; justify-content:center; gap:14px; flex-wrap:wrap; max-width:820px; margin:0 auto 20px;">
<div style="border:1px solid #eaeaea; border-radius:2px; padding:14px 18px; font-size:0.78rem; color:#333; font-weight:600; background:#fff; text-align:center;">
Mobility Tensor
<div style="font-family:'JetBrains Mono',monospace; font-style:normal; font-size:0.68rem; color:#888; font-weight:400; margin-top:4px;">&#119977; &isin; &#8477;<span style="font-size:0.58rem; vertical-align:super;">Z&times;Z&times;H&times;D&times;P&times;C</span></div>
</div>
<span style="color:#888; font-family:'JetBrains Mono',monospace; font-size:16px;">&rarr;</span>
<div style="border:1px solid #eaeaea; border-radius:2px; padding:14px 18px; font-size:0.78rem; color:#333; font-weight:600; background:#fff;">72&times;72 Route Matrix</div>
</div>

<div style="display:grid; grid-template-columns:repeat(2,1fr); gap:1px; background:#eaeaea; border:1px solid #eaeaea; border-radius:4px; overflow:hidden; max-width:400px; margin:0 auto;">
<div style="background:#fff; padding:16px 12px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:800; color:#121212;">461,003</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">IPF rows (45.6%)</div>
</div>
<div style="background:#fff; padding:16px 12px; text-align:center;">
<div style="font-family:'JetBrains Mono',monospace; font-size:1.05rem; font-weight:800; color:#121212;">2</div>
<div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">IPF diameter</div>
</div>
</div>
""", unsafe_allow_html=True)

# --- BLOCK 3: Bridge to Markov ---
_block3 = st.container(border=True)
with _block3:
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; letter-spacing:1.5px; color:#aab1bc; text-transform:uppercase; text-align:center; margin-bottom:14px;">bridge to markov</div>

<div style="text-align:center; margin-bottom:16px;">
<div style="display:inline-block; background:#21918c; border-radius:2px; padding:14px 18px; font-size:0.78rem; color:#fff; font-weight:600;">Markov Decision Process</div>
</div>

<div style="font-size:0.85rem; color:#64748b; line-height:1.7; max-width:640px; margin:0 auto; text-align:center;">
The weighted 72&times;72 matrix feeds the <b style="color:#121212;">Bellman Equation</b>, computing a State-Value function <b style="color:#121212;">V(s)</b> across the network. The result is a <b style="color:#121212;">Q-Matrix</b> policy &mdash; the mathematical scaffolding that lets an autonomous fleet plan multi-step mission sequences by long-term value, not just the fare sitting in front of it.
</div>
""", unsafe_allow_html=True)

# --- RESULT ---
st.markdown("""
<div style="max-width:1100px; margin:0 auto; font-family:'Inter',sans-serif; color:#121212;">
<div style="border:1px solid #eaeaea; border-radius:2px; padding:18px 20px; max-width:640px; margin:32px auto 0; background:#fff;">
<div style="font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700; color:#21918c; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Looking ahead &rarr; Pienza 2.0: The Knowledge in the Age of AI</div>
<div style="font-size:0.8rem; color:#666; line-height:1.6;">This steady-state scaffolding becomes the training ground for high-frequency Reinforcement Learning and Markov Chain Monte Carlo &mdash; moving from a static map of the city's economics to real-time, dynamic optimization.</div>
</div>
</div>
""", unsafe_allow_html=True)
