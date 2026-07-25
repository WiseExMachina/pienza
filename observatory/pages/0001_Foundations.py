import pandas as pd
import streamlit as st
from components.sidebar import build_sidebar
from components.styles import GLOBAL_CSS
from config import FAVICON, build_page_title
from pages._0001_data import COLORS, META_GROUPS, PHASES
from utils.mem_debug import log_mem

log_mem("0001 top")

st.set_page_config(layout="wide", page_title=build_page_title("Foundations"), page_icon=FAVICON)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
build_sidebar()
# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Page-specific overrides
st.markdown("""
<style>
h2 { font-size: 22px !important; font-weight: 600 !important; letter-spacing: -0.5px; }
h3 { font-size: 16px !important; font-weight: 600 !important; }
p, li { color: #555; font-size: 0.9rem; line-height: 1.7; }
/* The generic p rule above overrides the teal color the active st.tabs()
   label normally inherits from its parent button (labels are <p> tags),
   leaving the underline teal but the text gray - restore it here. */
[data-baseweb="tab"][aria-selected="true"] p { color: #21918c !important; }

/* GTS Simulator — device frame */
.sim-wrapper { display: flex; justify-content: center; padding: 12px 0 20px; }
.sim-device {
    width: 290px;
    background: #ffffff;
    border-radius: 28px;
    border: 7px solid #1a1a1a;
    padding: 0 14px 14px;
    box-shadow: 0 18px 40px rgba(0,0,0,0.18), inset 0 0 0 1px rgba(255,255,255,0.08);
    font-family: 'Inter', sans-serif !important;
}
.sim-notch {
    width: 68px; height: 6px;
    background: #1a1a1a;
    border-radius: 0 0 5px 5px;
    margin: 0 auto 16px;
}
.sim-header {
    text-align: center; color: #888;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    padding-bottom: 10px; margin-bottom: 12px;
    border-bottom: 1px solid #eee;
}
.sim-home {
    width: 80px; height: 3px;
    background: #1a1a1a; border-radius: 2px;
    margin: 14px auto 0; opacity: 0.25;
}
#timer-display {
    font-family: 'Courier New', monospace;
    font-size: 22px; font-weight: bold; color: #dc3545;
    text-align: center; margin: 8px 0; background: #fff5f5;
    padding: 6px; border-radius: 10px; border: 1px solid #ffc1c1;
}
div.stButton > button, div[data-testid="stPopover"] > button {
    width: 100%; border-radius: 10px !important; padding: 12px !important;
    font-weight: 700 !important; font-size: 13px !important;
    text-transform: none !important; border: none !important;
    transition: all 0.2s ease;
}
.summary-card {
    background-color: #f8f9fa; border: 1px solid #ddd;
    border-radius: 12px; padding: 15px; margin-top: 15px;
}
button[data-testid="baseButton-secondary"].nav-carousel {
    border: 1.5px solid rgba(33,145,140,0.7) !important;
    border-radius: 8px !important;
    background: transparent !important;
    color: #21918c !important;
    font-size: 18px !important;
    padding: 6px 20px !important;
}
button[data-testid="baseButton-secondary"].nav-carousel:hover {
    background: rgba(33,145,140,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# Foundations")
st.markdown("<h4 style='font-weight:300; color:#21918c; font-size:19px; margin:-10px 0 20px;'>Not all rejections are created equal</h4>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["Introduction", "Timeline"])

with tab1:
    st.markdown("""
<style>
.step-row    { display: flex; gap: 0; align-items: stretch; margin-bottom: 0; }
.step-spine  { display: flex; flex-direction: column; align-items: center; width: 44px; flex-shrink: 0; }
.step-circle { width: 30px; height: 30px; border-radius: 50%;
               color: #fff; font-size: 12px; font-weight: 700;
               display: flex; align-items: center; justify-content: center; flex-shrink: 0; z-index: 1; }
.step-line   { width: 2px; background: rgba(150,150,150,0.2); flex: 1; min-height: 16px; }
.step-body   { flex: 1; padding: 0 0 28px 12px; }
.step-label  { font-size: 17px; font-weight: 700; letter-spacing: 1px;
               text-transform: uppercase; margin-bottom: 8px; padding-top: 6px; color: #21918c; }
.step-body p { font-size: 13px !important; color: #475569; line-height: 1.7; margin: 0; }
.info-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 1px solid #21918c;
    background: #ffffff;
    color: #21918c;
    font-family: Georgia, 'Times New Roman', serif;
    font-style: italic;
    font-weight: 700;
    font-size: 9px;
    cursor: default;
    transition: background 0.2s ease;
    vertical-align: middle;
    margin-left: 5px;
}
.info-mark:hover { background: #f0fafa; }
</style>

<div class='step-row' style='margin-top:24px;'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>1</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label'>Scope &amp; Constraints</div>
    <p>
      Pienza explicitly rejects reverse-engineering proprietary pricing algorithms — a statistically unfeasible objective given a boutique, single-agent dataset. The analytical lens is reoriented toward <strong>the sole variable under absolute control: the agent's decisions</strong>.
    </p>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>2</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label'>Initial Hypothesis</div>
    <p>
      A pilot study (N ≈ 150, Jul–Aug 2025) observed a Payout Spread of 75–85 % of Base Fare. The hypothesis: time savings incur an implicit fare penalty. A benchmark comparison falsified this — Simple Linear Regression dominated all ML models and no meaningful non-linear signal was found. Scaling the regression approach would demand thousands of completed trips at prohibitive operational cost.<span class="fn-wrap"><span class="info-mark">i</span><span class="fn-tooltip">During Phase 3 (Exploratory Analysis), the Payout Spread inquiry was revisited and formally resolved via Causal Inference — modeling the platform's inelastic Integrity Buffer and baseline heteroscedasticity. → <a href="/Causal_Inference" target="_self" style="color:#21918c;text-decoration:none;">Causal Inference</a></span></span>
    </p>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>3</div>
    <div class='step-line'></div>
  </div>
  <div class='step-body'>
    <div class='step-label'>Pivot to Classification</div>
    <p>
      With regression abandoned, the research objective redefined from <em>price prediction</em> to <em>behavior cloning</em>. Incorporating the Negative Class (rejected offers) resolved data scarcity and exposed the full decision boundary — enabling XGBoost to model the agent's non-linear acceptance policy.
    </p>
  </div>
</div>

<div class='step-row'>
  <div class='step-spine'>
    <div class='step-circle' style='background:#21918c'>4</div>
  </div>
  <div class='step-body' style='padding-bottom:0;'>
    <div class='step-label'>Target Feature: Multiclass Classification</div>
    <p>
      The problem is defined as a <strong>multiclass classification</strong> task. Each rejected offer is assigned a single, mutually exclusive label representing the primary reason for rejection across a three-tiered triage: geospatial feasibility, economic viability, and strategic alignment. Acceptance is implicit — a <code style="color:#158237;font-family:'Source Code Pro',monospace;font-size:0.75rem;background:transparent;">NULL</code> label signals the absence of any objection. A binary accept/reject formulation was kept as a fallback in case the multiclass approach failed.
    </p>
  </div>
</div>

<div class="target-grid" style="margin-top:40px;">
  <div class="target-card">
    <div class="target-tier">Tier 1 — Geospatial</div>
    <div class="target-label">dropoff_non_operational</div>
    <div class="target-desc">Destination lies within a pre-defined zone outside the operational area.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 1 — Geospatial</div>
    <div class="target-label">dropoff_proxy</div>
    <div class="target-desc">Destination is outside the primary zone but acceptable if aligned with a homecoming vector toward <em>Anzures</em>.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 2 — Economic</div>
    <div class="target-label">low_profitability</div>
    <div class="target-desc">Offer fails baseline EPH requirements relative to estimated duration.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 2 — Economic</div>
    <div class="target-label">long_pickup_time</div>
    <div class="target-desc">Uncompensated pickup time exceeds tolerance; threshold relaxes during extreme gridlock.</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 3 — Strategic</div>
    <div class="target-label">strategic_mismatch</div>
    <div class="target-desc">High-value offer rejected due to unfavorable routing context (e.g., <em>Santa Fe → Polanco</em> during Friday peak gridlock).</div>
  </div>
  <div class="target-card">
    <div class="target-tier">Tier 3 — Strategic</div>
    <div class="target-label">expected_value_gamble</div>
    <div class="target-desc">Viable offer rejected based on the probabilistic expectation of a superior imminent event.</div>
  </div>
  <div class="target-card null-card">
    <div class="target-tier">Implicit</div>
    <div class="target-label">NULL</div>
    <div class="target-desc">Absence of objection signals an accepted offer.</div>
  </div>
</div>

<div style="background:rgba(33,145,140,0.07);border-left:3px solid #21918c;border-radius:0 8px 8px 0;padding:12px 16px;margin-top:40px;font-size:0.85rem;color:#333;line-height:1.65;">
  <strong>High-Fidelity Backtagging</strong> — The agent manually reviewed and tagged every offer to populate the multiclass target variable <span style="color:#21918c;font-family:'Courier New',monospace;font-weight:600;">reason_primary</span>. Executing this task same-day after each work shift was imperative to capture the specific, contextual nuance of each decision before operational memory decay occurred.
</div>
    """, unsafe_allow_html=True)

with tab2:
    import plotly.graph_objects as go

    df_phases = pd.DataFrame(PHASES)
    df_phases["Start"] = pd.to_datetime(df_phases["start"])
    df_phases["End"]   = pd.to_datetime(df_phases["end"])

    # ── Ribbon chart ──────────────────────────────────────────────────────
    fig = go.Figure()

    # Phase ribbon (y 0.35–0.65)
    for i, (_, row) in enumerate(df_phases.iterrows()):
        s = row["Start"].timestamp() * 1000
        e = row["End"].timestamp() * 1000
        mid_ts = (s + e) / 2
        fig.add_trace(go.Scatter(
            x=[s, e, e, s, s],
            y=[0.35, 0.35, 0.65, 0.65, 0.35],
            fill="toself",
            fillcolor=COLORS[i],
            line=dict(color=COLORS[i], width=0),
            mode="lines",
            hovertemplate=(
                f"<b>{row['phase']}: {row['label']}</b><br>"
                f"{row['date_range']}<br>"
                f"Arch: {row['arch_short'].replace('<br>', ' ')}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))
        fig.add_annotation(
            x=mid_ts, y=0.50, xref="x", yref="y",
            text=f"<b>{row['phase']}</b>",
            showarrow=False, font=dict(size=9, color="white"),
            xanchor="center", yanchor="middle",
        )
        fig.add_annotation(
            x=mid_ts, y=0.22, xref="x", yref="y",
            text=row["arch_short"],
            showarrow=False, font=dict(size=8, color="#21918c"),
            xanchor="center",
        )

    # Meta-group labels above ribbon — full-width line with centered text
    for g in META_GROUPS:
        gs = pd.Timestamp(g["start"]).timestamp() * 1000
        ge = pd.Timestamp(g["end"]).timestamp() * 1000
        gm = (gs + ge) / 2
        fig.add_shape(
            type="line",
            x0=gs, x1=ge, y0=0.88, y1=0.88,
            xref="x", yref="y",
            line=dict(color="#bbb", width=1),
        )
        fig.add_annotation(
            x=gm, y=0.88, xref="x", yref="y",
            text=f"<b>{g['label']}</b>",
            showarrow=False,
            font=dict(size=9, color="#555"),
            xanchor="center", yanchor="middle",
            bgcolor="#F5F6F7", borderpad=3,
            hovertext=g["hover"],
        )


    fig.update_layout(
        plot_bgcolor="#F5F6F7", paper_bgcolor="#F5F6F7",
        height=260,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(
            type="date", showgrid=False,
            tickformat="%b %Y", tickfont=dict(size=11, color="#555"),
            range=[pd.Timestamp("2025-08-15").timestamp()*1000,
                   pd.Timestamp("2026-06-01").timestamp()*1000],
        ),
        yaxis=dict(visible=False, range=[0.05, 1.05]),
        font=dict(family="Inter"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Vertical story with arrows ────────────────────────────────────────
    st.markdown("""
<style>
.phase-story { max-width: 760px; margin: 0 auto; }
.phase-card {
    display: flex; gap: 20px; align-items: flex-start;
    background: #fff; border: 1px solid #e8e8e8;
    border-left: 4px solid var(--phase-color);
    border-radius: 10px; padding: 18px 20px;
    margin: 0 0 0 0;
}
.phase-badge-num {
    flex-shrink: 0;
    width: 40px; height: 40px;
    background: var(--phase-color);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 14px;
}
.phase-card-body { flex: 1; }
.phase-card-title { font-weight: 700; font-size: 0.95rem; color: #121212; margin-bottom: 2px; }
.phase-card-meta { font-size: 0.78rem; color: #888; margin-bottom: 8px; }
.phase-card-meta .arch-tag {
    display: inline-block; background: rgba(33,145,140,0.07); color: #21918c;
    border: 1px solid #c2e8e5; border-radius: 4px;
    padding: 1px 6px; font-size: 0.72rem; font-weight: 600;
    margin-left: 8px;
}
.phase-card-desc { font-size: 0.85rem; color: #475569; line-height: 1.65; margin-bottom: 10px; }
.phase-bullets { display: flex; flex-wrap: wrap; gap: 6px; }
.phase-bullet {
    background: #f5f5f5; border-radius: 20px;
    padding: 3px 10px; font-size: 0.75rem; color: #444;
}
.phase-arrow {
    text-align: center; color: #ccc; font-size: 22px;
    margin: 6px 0; line-height: 1;
    user-select: none;
}
</style>
""", unsafe_allow_html=True)

    phase_html = '<div class="phase-story">'
    for i, (_, row) in enumerate(df_phases.iterrows()):
        color = COLORS[i]
        bullets_html = "".join(f'<span class="phase-bullet">{b}</span>' for b in row["bullets"])
        phase_html += f"""
<div class="phase-card" style="--phase-color:{color}">
  <div class="phase-badge-num">{i+1}</div>
  <div class="phase-card-body">
    <div class="phase-card-title">{row['label']}</div>
    <div class="phase-card-meta">{row['date_range']} <span class="arch-tag">{row['arch_short'].replace('<br>', ' ')}</span></div>
    <div class="phase-card-desc">{row['detail']}</div>
    <div class="phase-bullets">{bullets_html}</div>
  </div>
</div>
"""
        if i < len(df_phases) - 1:
            phase_html += '<div class="phase-arrow">↓</div>'

    phase_html += '</div>'
    st.markdown(phase_html, unsafe_allow_html=True)
