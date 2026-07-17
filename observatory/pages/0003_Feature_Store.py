import re
import streamlit as st
from components.styles import GLOBAL_CSS
import streamlit.components.v1 as components
import time
import numpy as np
import pandas as pd
from config import FAVICON
from components.sidebar import build_sidebar
from pages._0003_data import (
    VISIBLE_SIDS as _VISIBLE_SIDS,
    bronze_schema,
    content as _content,
    feature_count as _feature_count,
    gold_schema,
    obf_address as _obf_address,
    obf_eph as _obf_eph,
    obf_fare as _obf_fare,
    pb_offers as _pb_offers,
    pb_offers_all as _pb_offers_all,
    pb_sessions as _pb_sessions,
    silver_schema,
)
from utils.mem_debug import log_mem

log_mem("0003 top")

st.set_page_config(layout="wide", page_title="Feature Store | Pienza", page_icon=FAVICON)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
build_sidebar()
# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Page-specific overrides (kept empty on purpose — matches the vertical
# rhythm of 0001/0002's own style block so the title sits at the same
# height across pages; this extra st.markdown() call is what supplies
# Streamlit's default inter-widget gap before the H1)
st.markdown("<style></style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Feature Store")
st.markdown("<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>Bronze → Silver → Gold — Raw Signal to Predictive Feature</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-bottom:24px;'>Raw OCR output flows through three successive enrichment layers — each adding structure, context, and predictive signal — until it becomes the feature vector consumed by the classification models.</p>", unsafe_allow_html=True)

st.markdown("""
<style>
.stepper-wrap { margin-top: 15px; }
/* Shift the Feature Pipeline stepper block left ~50px and add breathing
   room below the tab bar. Scoped via st.container(key="pipeline-content")
   -> stable st-key-pipeline-content class, not a generic tabpanel selector:
   [role="tabpanel"]:first-of-type never matched (both panels are `div`s
   preceded by other sibling `div`s, e.g. the tablist, so neither panel is
   ever the actual first-of-type `div`), which silently dropped the shift
   entirely. The earlier plain [role="tabpanel"] selector (no :first-of-type)
   matched BOTH panels, dragging Session Playback out of alignment with the
   tab bar - that's why this needs to be scoped to Feature Pipeline only.
   transform (not margin-left) so the box keeps its original width - a
   negative margin-left only moves the left edge, making the box ~50px
   wider than its parent and overflowing 2-column content off-screen. */
div[class*="st-key-pipeline-content"] { transform: translateX(-50px); margin-top: 32px !important; }
/* Steps are wrapped in st.container(key="step-...") so the spine line is a
   single ::before pseudo-element spanning the container's real rendered
   height (title + why + pills + table). Streamlit renders each st.markdown/
   st.pills call as a separate sibling element with a ~16px gap between them
   (not literally nested inside an unclosed <div>), so a flex-stretched
   .step-line inside one markdown call only ever covered the "why" text and
   left the rest of the card's height with no line at all - hence the
   visible break. The ::before line overshoots -16px past the container's
   own bottom edge to bridge that inter-element gap into the connector
   below, which mirrors the trick on both its top and bottom. */
div[class*="st-key-step-"] { position: relative; padding-bottom: 40px; }
div[class*="st-key-step-"]::before {
    content: ""; position: absolute; left: 21px; top: 15px; bottom: -16px;
    width: 2px; background: rgba(150,150,150,0.2); z-index: 0;
}
.step-circle { width: 30px; height: 30px; border-radius: 50%;
               position: absolute; top: 0; left: 7px;
               color: #fff; font-size: 12px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; z-index: 1; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 2px; padding-top: 6px;
               padding-left: 56px; }
.step-why    { font-size: 0.85rem; color: #777; line-height: 1.6; margin-bottom: 4px;
               padding-left: 56px; }

/* shared chips */
.cat-chip { display: inline-block; font-size: 0.65rem; font-weight: 600;
            padding: 2px 7px; border-radius: 3px; margin: 2px 3px 2px 0;
            background: #f4f4f5; color: #52525b; border: 1px solid #d4d4d8; }
.chip-wrap { display: inline-block; position: relative; }
.chip-wrap .cat-chip { cursor: help; border-bottom: 1px dotted #21918c; }
.chip-tip  { visibility: hidden; opacity: 0; width: 260px;
             background: #fff; color: #555; font-size: 0.76rem; line-height: 1.5;
             border: 1px solid #21918c; border-radius: 8px; padding: 9px 13px;
             position: absolute; bottom: 140%; left: 50%; transform: translateX(-50%);
             box-shadow: 0 4px 14px rgba(0,0,0,0.10); transition: opacity 0.2s ease;
             z-index: 9999; pointer-events: none; }
.chip-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
                   transform: translateX(-50%); border: 6px solid transparent;
                   border-top-color: #21918c; }
.chip-wrap:hover .chip-tip { visibility: visible; opacity: 1; }
.feat-count { font-size: 0.72rem; color: #aaa; font-weight: 600; margin-left: 10px; }

/* ── Profitability Funnel cascade ── */
.funnel-wrap  { width: calc(100% - 56px); margin-top: 8px; margin-left: 56px; display: flex; flex-direction: column; gap: 0; }
.funnel-intro { font-size: 0.77rem; color: #444; line-height: 1.55; padding: 10px 14px;
                background: #f5f5f5; border: 1px solid #e5e5e5; border-radius: 7px;
                margin-bottom: 10px; }
.funnel-tier  { background: #fff; border: 1px solid #eaeaea; border-radius: 8px; padding: 12px 16px; }
.funnel-tier-final { }
.funnel-tier-label  { font-size: 0.73rem; font-weight: 700; text-transform: uppercase;
                      letter-spacing: 0.8px; color: #21918c; margin-bottom: 2px; }
.funnel-tier-formula { font-size: 0.75rem; color: #1a1a1a; font-family: 'Courier New', monospace; margin-bottom: 8px; }
.funnel-row   { display: flex; align-items: flex-start; gap: 8px; padding: 5px 0;
                border-bottom: 1px solid #f5f5f5; }
.funnel-row:last-child { border-bottom: none; }
.funnel-id    { color: #21918c; font-weight: 700; font-family: 'Courier New', monospace;
                font-size: 0.67rem; width: 34px; flex-shrink: 0; padding-top: 2px; }
.funnel-main  { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.funnel-name-line { display: flex; align-items: center; gap: 8px; }
.funnel-name  { color: #1a1a1a; font-weight: 600; font-size: 0.83rem; }
.funnel-type  { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
                color: #94a3b8; background: #f1f5f9; padding: 1px 5px; border-radius: 3px; }
.funnel-desc  { font-size: 0.73rem; color: #666; line-height: 1.4; }
.funnel-trans { display: flex; align-items: center; gap: 10px; padding: 5px 0 5px 14px; }
.funnel-trans-label { font-size: 0.71rem; font-weight: 600; color: #555;
                      background: #f8f8f8; border: 1px solid #e5e5e5;
                      border-radius: 4px; padding: 2px 8px; }
.funnel-arrow { font-size: 0.80rem; color: #21918c; }

/* ── Style A (Bronze): 2-line rows, mono ID badge ── */
.ta-wrap { width: 100%; margin-top: 4px; }
.ta-row  { display: flex; gap: 16px; align-items: flex-start;
           padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.ta-row:last-child { border-bottom: none; }
.ta-id   { font-family: 'Courier New', monospace; font-size: 0.65rem; font-weight: 700;
           color: #21918c; background: #f0fdf9; border: 1px solid #99f6e4;
           border-radius: 4px; padding: 2px 6px; white-space: nowrap; flex-shrink: 0; }
.ta-main { flex: 1; }
.ta-top  { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.ta-name { font-size: 0.82rem; font-weight: 600; color: #1a1a1a; }
.ta-badge { font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.4px; padding: 1px 6px; border-radius: 4px;
            background: #f1f5f9; color: #64748b; }
.ta-desc { font-size: 0.75rem; color: #888; line-height: 1.5; }

/* ── Style B (Silver): left-accent card rows ── */
.tb-wrap { width: calc(100% - 56px); margin-top: 4px; margin-left: 56px; display: flex; flex-direction: column; gap: 4px; }
.tb-card { background: #fff; border-left: 3px solid #21918c; border-radius: 0 6px 6px 0;
           padding: 6px 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
           transition: box-shadow 0.2s, transform 0.2s; }
.tb-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.07); transform: translateX(2px); }
.tb-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 2px; }
.tb-id   { font-family: 'Courier New', monospace; font-size: 0.6rem; font-weight: 700;
           color: #94a3b8; }
.tb-badge { font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.4px; padding: 1px 5px; border-radius: 4px;
            background: #f1f5f9; color: #64748b; }
.tb-name { font-size: 0.8rem; font-weight: 700; color: #1a1a1a; margin-bottom: 2px; }
.tb-desc { font-size: 0.72rem; color: #777; line-height: 1.45; }
.tb-warn-wrap { display: inline-block; position: relative; margin-left: 7px; vertical-align: middle; }
.tb-star { display: inline-block; font-size: 0.58rem; font-weight: 700;
           background: #21918c; color: #fff; border-radius: 3px;
           padding: 1px 7px; margin-left: 8px; vertical-align: middle; }
.tb-warn-badge { display: inline-flex; align-items: center; justify-content: center;
                 width: 16px; height: 16px; border-radius: 50%;
                 background: #fef3c7; border: 1px solid #f59e0b;
                 color: #b45309; font-size: 0.6rem; font-weight: 800;
                 cursor: help; line-height: 1; }
.tb-warn-tip { visibility: hidden; opacity: 0; width: 280px;
               background: #fffbeb; color: #78350f; font-size: 0.74rem; line-height: 1.5;
               border: 1px solid #f59e0b; border-radius: 8px; padding: 9px 13px;
               position: absolute; bottom: 140%; left: 50%; transform: translateX(-50%);
               box-shadow: 0 4px 14px rgba(0,0,0,0.10); transition: opacity 0.2s ease;
               z-index: 9999; pointer-events: none; }
.tb-warn-tip::after { content: ""; position: absolute; top: 100%; left: 50%;
                      transform: translateX(-50%); border: 6px solid transparent;
                      border-top-color: #f59e0b; }
.tb-warn-wrap:hover .tb-warn-tip { visibility: visible; opacity: 1; }

/* ── Style C (Gold): zebra + teal ID column ── */
.tc-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; margin-top: 4px; }
.tc-table th { font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: 0.6px; color: #aaa; padding: 0 12px 6px 0;
               border-bottom: 2px solid #eee; }
.tc-table th:first-child { padding-left: 10px; }
.tc-table tr:nth-child(even) td { background: #fafafa; }
.tc-table tr:nth-child(odd)  td { background: #ffffff; }
.tc-table td { padding: 8px 12px 8px 0; vertical-align: top; color: #444;
               border-bottom: 1px solid #f0f0f0; }
.tc-id   { color: #21918c !important; font-family: 'Courier New', monospace;
           font-weight: 700; font-size: 0.7rem; background: #f0fdf9 !important;
           padding-left: 10px !important; width: 50px; }
.tc-name { font-weight: 600; color: #1a1a1a !important; width: 200px; }
.tc-type { color: #21918c; font-size: 0.7rem; font-weight: 600; white-space: nowrap; }

/* domain pills — st.pills styling */
[data-testid="stPills"] { margin-bottom: 6px; }
/* Indent pills to align with the step title/why text (56px = spine width
   44px + step-body's 12px left padding), instead of sitting flush left
   under the spine line. Targets the st-key-*_domain class Streamlit
   attaches via key="..._domain" on all three steppers (bronze/silver/gold)
   - not :has(), which was confirmed unreliable in this Streamlit version
   (see project_tech_debt.md). */
div[class*="st-key-"][class*="_domain"] {
    margin-left: 56px !important;
    margin-top: 14px !important;
}
[data-testid="stPills"] > label { display: none; }
[data-testid="stPills"] [role="option"] {
    font-size: 0.62rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 3px 12px !important;
    border-radius: 20px !important;
    border: 1px solid #21918c !important;
    background: #f0fafa !important;
    color: #21918c !important;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stPills"] [role="option"]:hover {
    background: #e0f5f5 !important;
}
[data-testid="stPills"] [role="option"][aria-selected="true"] {
    background: #21918c !important;
    color: #ffffff !important;
}

/* Session Playback: teal-accented nav buttons (Back/Next/Restart), matching
   the rest of the site's custom button look instead of Streamlit default
   grey-border buttons. Targeted via key= class, not element type, so it
   only affects these three. */
div[class*="st-key-pb_back_btn"] button,
div[class*="st-key-pb_next_btn"] button,
div[class*="st-key-pb_restart_btn"] button {
    border: 1.5px solid #21918c !important;
    color: #21918c !important;
    background: #ffffff !important;
    font-weight: 600 !important;
}
div[class*="st-key-pb_back_btn"] button:hover,
div[class*="st-key-pb_next_btn"] button:hover,
div[class*="st-key-pb_restart_btn"] button:hover {
    background: rgba(33,145,140,0.08) !important;
    border-color: #1a7576 !important;
    color: #1a7576 !important;
}
div[class*="st-key-pb_back_btn"] button:disabled {
    border-color: #d4d4d8 !important;
    color: #aaa !important;
}

/* Session Playback: style the session selectbox like a card instead of
   Streamlit's default flat grey control. */
div[class*="st-key-pb_sess_select"] [data-baseweb="select"] > div {
    border: 1px solid #eaeaea !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
div[class*="st-key-pb_sess_select"] [data-baseweb="select"] > div:hover {
    border-color: #21918c !important;
}

/* Session Playback: wrap State Machine Context's stat grid + EPH funnel in
   one outer card matching Platform Offer's card exactly (border/radius/
   padding/background), so the two columns read as a matched pair of bento
   cards instead of one boxed card next to a loose stack of smaller ones. */
div[class*="st-key-sm-card"] {
    border: 1px solid #eaeaea !important;
    border-radius: 10px !important;
    padding: 16px !important;
    background: #ffffff !important;
    min-height: 450px !important;
    box-sizing: border-box !important;
}

/* Session Playback: wrap the whole per-offer display (meta line, both
   columns, Decision) in a "control center" panel - same grey as the
   sidebar (#ECECEE) - so the white data cards read as instrument
   readouts against a console background. */
div[class*="st-key-mission-control"] {
    background: #ECECEE !important;
    border: 1px solid #21918c !important;
    border-radius: 14px !important;
    padding: 28px !important;
    margin-top: 8px !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
}
</style>
<div class="stepper-wrap">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEATURE DATA
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _render_table_b(features):
    rows = ""
    for f in features:
        warn = f.get("warning", "")
        warn_html = f"""<span class='tb-warn-wrap'>
            <span class='tb-warn-badge'>!</span>
            <span class='tb-warn-tip'>{warn}</span>
        </span>""" if warn else ""
        star_html = "<span class='tb-star'>★ Target Feature</span>" if f.get("star") else ""
        rows += f"""<div class='tb-card'>
            <div class='tb-meta'><span class='tb-id'>{f['id']}</span><span class='tb-badge'>{f['type']}</span></div>
            <div class='tb-name'>{f['name']}{warn_html}{star_html}</div>
            <div class='tb-desc'>{_content(f)}</div>
        </div>"""
    return f"<div class='tb-wrap'>{rows}</div>"

def _render_funnel(features):
    def _row(fid, name, type_label, desc):
        return f"""<div class='funnel-row'>
            <span class='funnel-id'>{fid}</span>
            <div class='funnel-main'>
                <div class='funnel-name-line'><span class='funnel-name'>{name}</span><span class='funnel-type'>{type_label}</span></div>
                <div class='funnel-desc'>{desc}</div>
            </div>
        </div>"""

    def _trans(label):
        return f"<div class='funnel-trans'><span class='funnel-trans-label'>{label}</span><span class='funnel-arrow'>↓</span></div>"

    intro = """<div class='funnel-intro'>
        Each offer is audited across four successive EPH checkpoints — Earnings Per Hour —
        each adding a layer of operational cost to the denominator. The reference target is
        <strong>$200 MXN/hr</strong>: the agent's North Star. This funnel quantifies the
        <em>Information Asymmetry gap</em> where high-nominal offers may resolve as low-yield operations.
    </div>"""

    t1 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 1 · Direct EPH</div>
      <div class='funnel-tier-formula'>Upfront Fare ÷ Est Trip Time</div>
      {_row('F49','eph_direct','Float','Platform raw signal — the quoted fare divided by estimated trip time.')}
      {_row('F50','eph_direct_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F51','eph_direct_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t2 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 2 · Operational EPH</div>
      <div class='funnel-tier-formula'>Upfront Fare ÷ (Est Time + Pickup Time)</div>
      {_row('F52','eph_operational','Float','First reality check — adds uncompensated pickup time to the cost denominator.')}
      {_row('F53','eph_operational_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F54','eph_operational_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t3 = f"""<div class='funnel-tier'>
      <div class='funnel-tier-label'>Tier 3 · Realized EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Est Trip Time</div>
      {_row('F55','eph_realized','Float',"Rolling feature — corrects the quoted fare using the historical spread observed across all rides completed prior to this offer. Updates only after a ride is fully completed, never mid-trip, ensuring zero leakage. Captures the agent's recent financial performance as a behavioral signal.")}
      {_row('F56','eph_realized_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F57','eph_realized_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    t4 = f"""<div class='funnel-tier funnel-tier-final'>
      <div class='funnel-tier-label'>Tier 4 · Complete EPH</div>
      <div class='funnel-tier-formula'>Adjusted Fare ÷ Total Cycle Time  (Est Trip + Pickup + Deadhead Looking for Rides + Deadhead Waiting for Passenger)</div>
      {_row('F58','eph_complete','Float','Same rolling logic as Tier 3 — updates only after ride completion, no leakage — but the denominator now carries the full accumulated deadhead cost of the cycle, making this the most conservative and complete yield signal available at decision time.')}
      {_row('F59','eph_complete_index','Float','Ratio: EPH ÷ $200 MXN/hr. Exactly 1.0 = at target; above 1.0 = Premium; below 1.0 = Discount.')}
      {_row('F60','eph_complete_label','Categorical','Binary classification derived from the index → <span class="cat-chip">Premium</span><span class="cat-chip">Discount</span>')}
    </div>"""

    return f"""<div class='funnel-wrap'>
      {intro}
      {t1}
      {_trans('+ Pickup Time')}
      {t2}
      {_trans('+ Spread Correction  (Quoted → Realized Fare)')}
      {t3}
      {_trans('+ Full Cycle Cost  (Pickup + Deadhead Looking for Rides + Deadhead Waiting for Passenger)')}
      {t4}
    </div>"""

def _render_step(circle_color, label, count, why, schema, radio_key, table_fn, domain_renderers=None):
    with st.container(key=f"step-{radio_key}"):
        st.markdown(f"""
        <div class='step-circle' style='background:{circle_color}'>{label[0]}</div>
        <div class='step-label' style='color:{circle_color}'>{label} <span class='feat-count'>· {count} features</span></div>
        <div class='step-why'>{why}</div>
        """, unsafe_allow_html=True)

        import re
        domains = list(schema.keys())
        labels = [re.sub(r'^[^\w]+\s*', '', d).strip() for d in domains]
        label_to_domain = dict(zip(labels, domains))
        selected_label = st.pills("", labels, default=labels[0], key=radio_key, label_visibility="collapsed")
        selected = label_to_domain[selected_label or labels[0]]
        renderer = (domain_renderers or {}).get(selected, table_fn)
        st.markdown(renderer(schema[selected]), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
pipeline_tab, pb_tab = st.tabs(["Feature Pipeline", "Session Playback"])

with pipeline_tab:
    with st.container(key="pipeline-content"):
        _render_step(
            circle_color="#cd7f32",
            label="Bronze · Raw Canonical Schema",
            count=_feature_count(bronze_schema),
            why="Direct output of the OCR pipeline: offer physics, geospatial coordinates, incentive flags, rider profile, and the decision label. No derivations — the contract between raw data and the engineering layer.",
            schema=bronze_schema,
            radio_key="bronze_domain",
            table_fn=_render_table_b,
        )

        _render_step(
            circle_color="#94a3b8",
            label="Silver · Stateful Engineered Features",
            count=33,
            why="Session-dependent features computed by a sequential state machine. Captures market pressure, agent fatigue, yield trajectory, and operational EPH variants. Strict no-look-ahead rule: _ML features use only data available at decision time; _EDA features are firewalled.",
            schema=silver_schema,
            radio_key="silver_domain",
            table_fn=_render_table_b,
            domain_renderers={"💹 Profitability Funnel": _render_funnel},
        )

        _render_step(
            circle_color="#b8860b",
            label="Gold · Spatial + Volatility",
            count=_feature_count(gold_schema),
            why="Causal analysis in Phase 3 revealed the ex-ante traffic index is a poor proxy for operational risk. This layer adds H3 spatial indexing and a volatility suite derived from the 2 min/km market baseline — the final predictive signal layer.",
            schema=gold_schema,
            radio_key="gold_domain",
            table_fn=_render_table_b,
        )

        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SESSION PLAYBACK
# ═══════════════════════════════════════════════
with pb_tab:
    with st.container(key="pb-content"):
        _NORTH_STAR = 200.0

        # ── Session state init ──
        for _k, _v in [("pb_sid", None), ("pb_df", None), ("pb_idx", 0)]:
            if _k not in st.session_state:
                st.session_state[_k] = _v

        # ── Header ──
        st.markdown(
            "<p style='font-size:14px;font-weight:400;color:#475569;line-height:1.7;margin-top:32px;margin-bottom:24px;'>"
            "Step through a real field session offer by offer. Each card shows exactly what the platform "
            "presented and what the state machine computed at that moment in the session.</p>",
            unsafe_allow_html=True
        )

        # ── Session picker ──
        df_sess = _pb_sessions()
        if df_sess is None or df_sess.empty:
            st.error("Could not load sessions from BigQuery.")
            st.stop()

        # Only show a curated subset of sessions - the rest stay hidden from
        # the selectbox (not deleted, just filtered out of what's offered).
        df_sess = df_sess[df_sess["session_fk"].isin(_VISIBLE_SIDS)].reset_index(drop=True)
        if df_sess.empty:
            st.error("None of the curated sessions were found in BigQuery.")
            st.stop()

        def _sess_label(r):
            ts  = str(r.get("session_start", ""))[:10]
            n   = int(r.get("offer_count", 0))
            a   = int(r.get("accepted_count", 0))
            pct = f"{a/n*100:.0f}%" if n > 0 else "—"
            return f"{r['session_fk']}  ·  {ts}  ·  {n} offers  ·  {a} accepted ({pct})"

        sess_labels  = df_sess.apply(_sess_label, axis=1).tolist()
        sess_ids     = df_sess["session_fk"].tolist()
        label_to_id  = dict(zip(sess_labels, sess_ids))

        sel_label = st.selectbox("Session", sess_labels, key="pb_sess_select", label_visibility="collapsed")
        sel_id    = label_to_id[sel_label]

        if sel_id != st.session_state.pb_sid:
            st.session_state.pb_sid = sel_id
            st.session_state.pb_df  = _pb_offers(sel_id)
            st.session_state.pb_idx = 0
            st.session_state.pop("pb_jump", None)
            st.rerun()

        if st.session_state.pb_df is None or st.session_state.pb_df.empty:
            st.warning("No offers found for this session.")
            st.stop()

        df    = st.session_state.pb_df
        idx   = st.session_state.pb_idx
        total = len(df)

        # ── Session complete ──
        if idx >= total:
            acc_mask  = df["str_action"].str.lower().str.startswith("accept").fillna(False)
            accepted  = int(acc_mask.sum())
            rejected  = total - accepted

            # Pull final-row state machine values (last offer = end-of-session state)
            last       = df.iloc[-1]
            deadhead   = float(last.get("total_accumulated_deadhead_sec") or 0)
            earnings   = float(last.get("cycle_cumulative_net_earnings")  or 0)
            spread     = float(last.get("cycle_rolling_avg_spread")       or 0)
            max_consec = int(df["consecutive_rejects"].fillna(0).max())

            # Session duration
            try:
                t0  = pd.to_datetime(df["offer_timestamp"].iloc[0])
                t1  = pd.to_datetime(df["offer_timestamp"].iloc[-1])
                dur = int((t1 - t0).total_seconds())
            except Exception:
                dur = None

            # EPH averages (accepted offers only)
            acc_df = df[acc_mask]
            eph_d_avg = acc_df["eph_direct"].dropna().mean()    if "eph_direct"    in df.columns else None
            eph_o_avg = acc_df["eph_operational"].dropna().mean() if "eph_operational" in df.columns else None

            def _hms_s(sec):
                if sec is None: return "—"
                s = int(sec); h, r = divmod(s, 3600); m, s = divmod(r, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"

            st.markdown("<span class='phase-badge'>Session Complete</span>", unsafe_allow_html=True)
            st.markdown("### Session Summary")

            # Row 1 — decision KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Offers",      total)
            c2.metric("Accepted",          f"{accepted}  ({accepted/total*100:.0f}%)")
            c3.metric("Rejected",          rejected)
            c4.metric("Max Consec. Rejects", max_consec)

            st.markdown("---")

            # Row 2 — state machine KPIs
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Acc. Deadhead",       _hms_s(deadhead))
            c6.metric("Session Duration",    _hms_s(dur))
            c7.metric("Cumulative Earnings", f"${_obf_eph(earnings)} MXN")
            c8.metric("Avg Spread Ratio",    f"{spread:.3f}" if spread else "—")

            st.markdown("---")

            # Row 3 — EPH averages (accepted offers only)
            c9, c10, _, _ = st.columns(4)
            c9.metric("Avg Direct EPH",      f"${_obf_eph(eph_d_avg)}/hr" if eph_d_avg else "—")
            c10.metric("Avg Operational EPH", f"${_obf_eph(eph_o_avg)}/hr" if eph_o_avg else "—")

            st.markdown(
                "<div style='border-left:4px solid #f59e0b;background:#fffbeb;padding:12px 16px;"
                "border-radius:0 7px 7px 0;font-size:0.82rem;color:#78350f;line-height:1.7;margin-top:8px;'>"
                "<strong>⚠ Snapshot caveat — by design</strong><br>"
                "These figures reflect the state machine at the timestamp of the <em>last offer presented</em>, "
                "not the true end of the session. Deadhead, earnings, and session duration do <strong>not</strong> "
                "include time or income accrued after completing the final accepted ride. This is intentional: the state machine was engineered as an <strong>ML feature pipeline</strong>. "
                "The model's decision boundary is the accept/reject moment — so the input vector is defined "
                "strictly <em>before</em> the last outcome is known."
                "</div>",
                unsafe_allow_html=True
            )
            st.markdown("")
            if st.button("↺ Replay Session", key="pb_restart", use_container_width=False):
                st.session_state.pb_idx = 0
                st.session_state.pop("pb_jump", None)
                st.rerun()
            st.stop()

        row = df.iloc[idx]

        # If a button fired last render, apply its target to the slider key NOW
        # (must happen before st.slider is instantiated)
        _nav = st.session_state.pop("_pb_nav", None)
        if _nav is not None:
            st.session_state["pb_jump"] = _nav

        # ── Slider (jump to any offer) ──
        jump = st.slider("", min_value=1, max_value=total, key="pb_jump",
                         label_visibility="collapsed")
        if jump - 1 != idx:
            st.session_state.pb_idx = jump - 1
            st.rerun()

        # ── Navigation buttons (centered) ──
        _, nb1, nb2, nb3, _ = st.columns([2, 1.2, 1.2, 1.2, 2])
        with nb1:
            if st.button("← Back", key="pb_back_btn", use_container_width=True, disabled=(idx == 0)):
                st.session_state.pb_idx  = idx - 1
                st.session_state["_pb_nav"] = idx     # consumed next render, before slider
                st.rerun()
        with nb2:
            nxt_label = "→ Next" if idx < total - 1 else "→ Summary"
            if st.button(nxt_label, key="pb_next_btn", use_container_width=True):
                st.session_state.pb_idx  = idx + 1
                st.session_state["_pb_nav"] = idx + 2
                st.rerun()
        with nb3:
            if st.button("↺ Restart", key="pb_restart_btn", use_container_width=True):
                st.session_state.pb_idx  = 0
                st.session_state.pop("pb_jump", None)
                st.session_state["_pb_nav"] = 1
                st.rerun()

        with st.container(key="mission-control"):
            st.markdown(
                f"<div style='font-size:0.78rem;color:#888;margin-bottom:14px;margin-top:4px;'>"
                f"Offer <strong style='color:#1a1a1a;'>{idx+1}</strong> of {total} &nbsp;·&nbsp; "
                f"{str(row.get('day_type','') or '')} &nbsp;·&nbsp; "
                f"{str(row.get('time_of_day_block','') or '')} &nbsp;·&nbsp; "
                f"{str(row.get('day_of_week','') or '')}"
                f"</div>",
                unsafe_allow_html=True
            )

            # ── Main columns ──
            offer_col, sm_col = st.columns(2, gap="large")

            def _v(val, fmt="{}", fb="—"):
                try:
                    return fmt.format(val) if val is not None and str(val) not in ("None","nan","") else fb
                except Exception:
                    return fb

            def _hms(sec):
                if sec is None or str(sec) in ("None", "nan", ""):
                    return "—"
                s = int(float(sec))
                h, r = divmod(abs(s), 3600)
                m, s = divmod(r, 60)
                return f"{h:02d}:{m:02d}:{s:02d}"

            with offer_col:
                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-bottom:8px;'>Platform Offer "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(what was presented)</span></div>",
                    unsafe_allow_html=True,
                )

                bonuses = []
                if row.get("is_surge"):      bonuses.append(f"+${_v(row.get('surge_amount'), '{:.0f}')} Surge")
                if row.get("is_turbo_plus"): bonuses.append(f"+${_v(row.get('turbo_plus_amount'), '{:.0f}')} Turbo+")
                bonus_html = " ".join(
                    f"<span style='background:#fef3c7;color:#92400e;border:1px solid #fde68a;"
                    f"border-radius:3px;font-size:0.62rem;font-weight:700;padding:1px 6px;'>{b}</span>"
                    for b in bonuses
                )

                _raw_pickup  = _obf_address(row.get("pickup_address"))
                _raw_dropoff = _obf_address(row.get("dropoff_address"))
                pickup_str   = (_raw_pickup[:38]  + "…") if len(_raw_pickup)  > 38 else _raw_pickup
                dropoff_str  = (_raw_dropoff[:38] + "…") if len(_raw_dropoff) > 38 else _raw_dropoff
                product_name = re.sub(r"(?i)uberx\b", "X", _v(row.get("str_product"), "{}", "Unknown"))

                # decision vars (used below offer card)
                action   = str(row.get("str_action", "—") or "—")
                reason   = str(row.get("str_reason",  "—") or "—")
                acc      = action.lower().startswith("accept")
                d_icon   = "<span style='color:#22c55e;'>✓</span>" if acc else "<span style='color:#ef4444;'>✕</span>"
                d_label  = "Accepted" if acc else action.capitalize()
                reason_line = (
                    f"<span style='font-size:0.88rem;font-weight:700;color:#334155;margin-left:8px;'>"
                    f"{reason}</span>"
                    if reason not in ("—", "NULL", "None", "nan") else ""
                )

                ts = str(row.get('offer_timestamp', '') or '')[:19]

                _no_screenshot = all(
                    row.get(f) is None or str(row.get(f)) in ("None", "nan", "")
                    for f in ("upfront_fare", "time_to_pickup_sec", "est_trip_time_sec")
                )
                if _no_screenshot:
                    st.markdown(
                        "<div style='background:#fefce8;border:2px solid #facc15;border-radius:7px;"
                        "padding:8px 14px;font-size:0.8rem;color:#713f12;font-weight:600;margin-bottom:8px;'>"
                        "📷 No screenshot was captured for this offer — platform fields unavailable."
                        "</div>",
                        unsafe_allow_html=True
                    )

                st.markdown(f"""
                <div style='border:1px solid #eaeaea;border-radius:10px;padding:16px;background:#fff;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>
                    <div style='font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#21918c;'>
                      {product_name} {bonus_html}
                    </div>
                    <div style='font-size:0.65rem;font-family:monospace;color:#aaa;font-weight:400;'>{ts}</div>
                  </div>
                  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;'>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Upfront Fare</div>
                      <div style='font-size:1.5rem;font-weight:800;color:#1a1a1a;'>${ _obf_fare(row.get('upfront_fare')) }<span style='font-size:0.75rem;font-weight:400;color:#aaa;'> MXN</span></div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Driver State</div>
                      <div style='font-size:1.0rem;font-weight:600;color:#1a1a1a;'>{_v(row.get('str_driver_state'))}</div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Pickup</div>
                      <div style='font-size:0.95rem;font-weight:600;color:#1a1a1a;'>{_hms(row.get('time_to_pickup_sec'))} &nbsp;<span style='color:#aaa;font-size:0.75rem;'>/ {_v(row.get('dist_to_pickup_km'),'{:.1f}')} km</span></div>
                    </div>
                    <div>
                      <div style='font-size:0.6rem;color:#bbb;font-weight:700;text-transform:uppercase;margin-bottom:2px;'>Est Trip</div>
                      <div style='font-size:0.95rem;font-weight:600;color:#1a1a1a;'>{_hms(row.get('est_trip_time_sec'))} &nbsp;<span style='color:#aaa;font-size:0.75rem;'>/ {_v(row.get('est_trip_dist_km'),'{:.1f}')} km</span></div>
                    </div>
                  </div>
                  <div style='font-size:0.7rem;color:#666;border-top:1px solid #f5f5f5;padding-top:8px;line-height:1.8;'>
                    <div>📍 {pickup_str}</div>
                    <div>🏁 {dropoff_str}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-top:156px;margin-bottom:8px;'>Decision "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(what the agent decided)</span></div>",
                    unsafe_allow_html=True,
                )
                st.html(
                    f"<div style='border-left:3px solid #21918c;border-radius:0 4px 4px 0;padding:4px 10px;"
                    f"background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.04);display:inline-block;'>"
                    f"<span style='font-size:0.68rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;'>"
                    f"{d_label} {d_icon}</span>"
                    f"{reason_line}</div>"
                )


            with sm_col:
                st.markdown(
                    "<div style='font-size:0.85rem;font-weight:700;letter-spacing:0.8px;"
                    "text-transform:uppercase;color:#21918c;margin-bottom:8px;'>State Machine Context "
                    "<span style='font-size:0.75rem;font-weight:400;text-transform:none;letter-spacing:0;color:#888;'>"
                    "(at decision time)</span></div>",
                    unsafe_allow_html=True,
                )

                with st.container(key="sm-card"):
                    deadhead    = float(row.get("total_accumulated_deadhead_sec") or 0)
                    consec      = int(row.get("consecutive_rejects") or 0)
                    earnings    = float(row.get("cycle_cumulative_net_earnings") or 0)
                    spread      = float(row.get("cycle_rolling_avg_spread") or 1.0)
                    traffic     = float(row.get("traffic_index_base_120") or 1.0)
                    home_v      = row.get("home_vector_alignment_score")
                    since_last  = row.get("time_since_last_offer")
                    accepted_so_far = int(
                        df.iloc[:idx]["str_action"].str.lower().str.startswith("accept").fillna(False).sum()
                    )

                    cr_color = "#e05252" if consec >= 5 else "#f59e0b" if consec >= 3 else "#1a1a1a"
                    ti_color = "#e05252" if traffic > 1.2 else "#f59e0b" if traffic > 1.05 else "#21918c"

                    def _stat(label, value, color="#1a1a1a"):
                        return (f"<div style='border:1px solid #eaeaea;border-radius:7px;padding:7px 4px;text-align:center;overflow:hidden;'>"
                                f"<div style='font-size:0.58rem;color:#bbb;font-weight:700;text-transform:uppercase;'>{label}</div>"
                                f"<div style='font-size:0.82rem;font-weight:700;color:{color};white-space:nowrap;'>{value}</div>"
                                f"</div>")

                    st.html(
                        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px;'>" +
                        _stat("Acc. Deadhead", _hms(deadhead)) +
                        _stat("Since Last Offer",  _hms(since_last)) +
                        _stat("Consec. Rejects",   consec,          cr_color) +
                        _stat("Accepted",          accepted_so_far) +
                        _stat("Cum Earnings",       f"${_obf_eph(earnings)}") +
                        _stat("Spread Ratio",      f"{spread:.3f}") +
                        _stat("Traffic Index",     f"{traffic:.2f}x", ti_color) +
                        _stat("Home Vector Score", f"{float(home_v):.2f}" if home_v is not None else "—") +
                        "</div>"
                    )

                    # EPH funnel (precomputed from view)
                    def _eph_row(title, formula, eph_val, downgrade=False):
                        if eph_val is None or str(eph_val) in ("None", "nan", ""):
                            return (f"<div style='border:1px solid #f0f0f0;border-radius:7px;padding:7px 12px;"
                                    f"margin-bottom:5px;color:#ccc;font-size:0.7rem;'>{title} — N/A</div>")
                        v    = float(eph_val)
                        ix   = v / _NORTH_STAR
                        lbl  = "Premium" if ix >= 1.0 else "Discount"
                        clr  = "#21918c" if ix >= 1.0 else "#71717a"
                        dg   = ("<span style='font-size:0.6rem;color:#f59e0b;margin-left:5px;'>⚠ downgrade</span>"
                                if downgrade else "")
                        return f"""<div style='border:1px solid #eaeaea;border-radius:7px;padding:7px 12px;margin-bottom:5px;background:#fff;'>
                          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;'>
                            <span style='font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#21918c;'>{title}</span>
                            <span style='font-size:0.6rem;color:#bbb;font-family:monospace;'>{formula}</span>
                          </div>
                          <div style='display:flex;align-items:center;gap:8px;'>
                            <span style='font-size:0.98rem;font-weight:700;color:#1a1a1a;'>${_obf_eph(v)}<span style='font-size:0.64rem;font-weight:400;color:#aaa;'> /hr</span></span>
                            <span style='font-size:0.74rem;font-weight:700;color:{clr};'>{ix:.1f}x</span>
                            <span style='font-size:0.63rem;font-weight:700;color:#fff;background:{clr};padding:1px 6px;border-radius:3px;'>{lbl}</span>
                            {dg}
                          </div>
                        </div>"""

                    st.html(
                        _eph_row("T1 · Direct",      "Fare ÷ Trip",                     row.get("eph_direct")) +
                        _eph_row("T2 · Operational", "Fare ÷ (Trip+Pickup)",            row.get("eph_operational"),  bool(row.get("is_operational_downgrade"))) +
                        _eph_row("T3 · Realized",    f"Fare×{spread:.2f} ÷ Trip",      row.get("eph_realized_ML"), bool(row.get("is_spread_downgrade_ML"))) +
                        _eph_row("T4 · Complete",    f"Fare×{spread:.2f} ÷ Cycle",     row.get("eph_complete_ML"), bool(row.get("is_total_cycle_downgrade_ML")))
                    )





