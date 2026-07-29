from config import ACCENT

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p {
    font-family: 'Inter', sans-serif !important;
}

h1 {
    font-size: 36px !important;
    font-weight: 300 !important;
    color: #121212;
    letter-spacing: -1px;
}
h2 {
    color: #21918c;
    font-size: 30px !important;
    font-weight: 300 !important;
    margin-top: -10px;
}
h3 {
    color: #21918c !important;
    font-size: 26px !important;
    font-weight: 400 !important;
    margin-top: -10px;
}
h4 {
    color: #21918c;
    font-weight: 100 !important;
    margin-top: -10px;
}

[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
    font-size: 11.8px !important;
}

/* Sidebar canon (2026-07-09 teal redesign) */
[data-testid="stSidebar"] {
    background-color: #ECECEE !important;
    border-right: 1px solid #eaeaea;
}
[data-testid="stSidebar"] a,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #31333F !important;
}
[data-testid="stSidebar"] hr {
    border-top: 1px solid rgba(0,0,0,0.12) !important;
}

/* Streamlit's own page-link element-containers ship with a built-in
   -6px/-6px margin (a tightening hack Streamlit applies internally),
   which fights any flex `gap` smaller than 12px on the parent
   stVerticalBlock (net negative = overlapping teal active/hover boxes).
   We neutralize that built-in margin on page-link containers specifically
   so `gap` alone controls spacing and can go tighter than 12px. */
[data-testid="stSidebar"] .stElementContainer:has(> .stPageLink) {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
[data-testid="stSidebar"] .stVerticalBlock {
    gap: 0px !important;
}

[data-testid="stSidebar"] .st-key-sb-footer {
    margin-top: 50px;
}


/* Brand header */
.sb-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 20px 2px 50px 2px;
}
.sb-brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 11px;
    background: rgba(33,145,140,0.12);
    flex-shrink: 0;
}
.sb-brand-text-title {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.25rem;
    font-weight: 800;
    color: #121212 !important;
    letter-spacing: -0.2px;
    line-height: 1.15;
}
.sb-brand-text-sub {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem;
    font-weight: 500;
    color: #21918c !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

/* Section labels (e.g. "MODULES", "ARCHIVE") */
.sb-section-label {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    color: #7a7d87 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 14px 0 20px 4px !important;
}

/* Nav links */
[data-testid="stSidebar"] .stPageLink a {
    text-decoration: none !important;
    padding: 3px 8px 3px 4px !important;
    border-radius: 8px !important;
    border-left: 3px solid transparent !important;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stSidebar"] .stPageLink a:hover {
    background-color: rgba(33,145,140,0.10) !important;
}
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] {
    background-color: rgba(33,145,140,0.14) !important;
    border-left: 3px solid #21918c !important;
}
[data-testid="stSidebar"] .stPageLink a[aria-current="page"] p {
    font-weight: 700 !important;
    color: #146560 !important;
}
[data-testid="stSidebar"] .stPageLink svg {
    color: #21918c !important;
}

/* Archive expander */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    padding: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    color: #7a7d87 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {
    padding: 2px 0 0 0 !important;
}

/* Sidebar footer buttons (PDF / Flush Cache) - teal-outlined, matches nav-card style */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] .stDownloadButton button {
    background-color: #ffffff !important;
    border: 1px solid #21918c !important;
    color: #21918c !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    border-radius: 8px !important;
    transition: background-color 0.15s ease, color 0.15s ease;
}
[data-testid="stSidebar"] .stButton button:hover,
[data-testid="stSidebar"] .stDownloadButton button:hover {
    background-color: #21918c !important;
    color: #ffffff !important;
    border-color: #21918c !important;
}

/* Discreet inline PDF link, styled as plain text to match the
   Author/Domain/Stack meta-line rather than looking like a button. */
.sb-pdf-link {
    color: #21918c !important;
    text-decoration: underline;
    text-decoration-color: rgba(33,145,140,0.35);
}
.sb-pdf-link:hover {
    text-decoration-color: #21918c;
}

.sb-meta-line {
    font-size: 0.75rem !important;
    color: #555 !important;
    line-height: 1.6;
}
.sb-meta-line b { color: #31333F !important; }

.block-container { padding-top: 2rem; }

/* Streamlit's theme.backgroundColor doesn't reliably paint the fixed top header bar,
   leaving a mismatched white strip — force it to match the canonical app background. */
[data-testid="stHeader"] { background: #F5F6F7 !important; background-color: #F5F6F7 !important; }

.kpi-box {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #21918c;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}

.bento-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
    margin-top: 10px;
}
.bento-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.bento-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    border-color: #21918c;
}
.bento-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #121212;
    line-height: 1.1;
    letter-spacing: -1px;
    margin-bottom: 5px;
}
.bento-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #21918c;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.bento-desc {
    font-size: 0.8rem;
    color: #555;
    line-height: 1.4;
}

.ingestion-panel {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 30px;
    margin: 40px 0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.ingestion-panel:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    border-color: #21918c;
}
/* main.py's "A Look Ahead" panel — a st.container(key=...) so the page_link
   Explore Module button renders inside the same bordered box as the text,
   instead of falling outside it like a bare unwrapped page_link would. */
.st-key-rag-lookahead-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 30px;
    margin: 40px 0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.st-key-rag-lookahead-card:hover {
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    border-color: #21918c;
}
.st-key-rag-lookahead-card [data-testid="stPageLink"] a {
    background: #f0f2f6;
    border-radius: 8px;
    padding: 10px 16px;
    display: flex;
    justify-content: center;
    text-decoration: none !important;
}
.st-key-rag-lookahead-card [data-testid="stPageLink"] a p {
    text-align: center;
}
.ingestion-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #21918c;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}
.ingestion-heading {
    font-size: 1.6rem;
    font-weight: 800;
    color: #121212;
    letter-spacing: -0.5px;
    margin-bottom: 12px;
}
.ingestion-body {
    font-size: 0.9rem;
    color: #555555;
    line-height: 1.5;
    margin-bottom: 24px;
}
.ingestion-action {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: #21918c;
    color: #ffffff !important;
    padding: 12px 28px;
    border-radius: 6px;
    text-decoration: none !important;
    font-size: 0.85rem;
    font-weight: 600;
    transition: background-color 0.2s ease;
}
.ingestion-action:hover {
    background-color: #1a7576;
}

.story-section {
    border-left: 3px solid #21918c;
    padding-left: 20px;
    margin-bottom: 32px;
}
.story-section p { font-size: 0.88rem; color: #555; line-height: 1.75; margin: 0; }
.story-pill {
    display: inline-block;
    background: #f0fafa;
    border: 1px solid #21918c;
    color: #21918c;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.story-footnote {
    font-size: 0.75rem;
    color: #999;
    margin-top: 10px;
    font-style: italic;
}
.story-footnote a { color: #21918c; text-decoration: none; }
.story-footnote a:hover { text-decoration: underline; }
.fn-wrap { display: inline-block; position: relative; }
.fn-mark {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    color: #21918c;
    vertical-align: super;
    cursor: default;
    border-bottom: 1px dotted #21918c;
}
.info-mark {
    display: inline-flex; align-items: center; justify-content: center;
    width: 13px; height: 13px; border-radius: 50%; border: 1px solid #21918c;
    background: #ffffff; color: #21918c; font-family: Georgia, 'Times New Roman', serif;
    font-style: italic; font-weight: 700; font-size: 9px; cursor: default;
    transition: background 0.2s ease; vertical-align: middle; margin-left: 5px;
}
.info-mark:hover { background: #f0fafa; }
.fn-wrap .fn-tooltip {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: #ffffff;
    color: #555;
    font-size: 0.78rem;
    line-height: 1.5;
    border: 1px solid #21918c;
    border-radius: 8px;
    padding: 10px 14px;
    position: absolute;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    transition: opacity 0.15s ease 0.1s, visibility 0.15s ease 0.1s;
    z-index: 9999;
    pointer-events: auto;
    font-weight: 400;
}
.fn-wrap .fn-tooltip::before {
    content: "";
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    height: 16px;
}
.fn-wrap .fn-tooltip::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: #21918c;
}
.fn-wrap:hover .fn-tooltip,
.fn-wrap .fn-tooltip:hover { visibility: visible; opacity: 1; transition-delay: 0s; }

.placeholder-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 12px;
    padding: 48px 32px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    color: #aaa;
    font-size: 0.9rem;
    font-family: 'Inter', sans-serif;
}
.placeholder-card span {
    font-size: 2rem;
    display: block;
    margin-bottom: 12px;
    color: #ccc;
}

.phase-badge {
    display: inline-block;
    background-color: #f0fafa;
    color: #21918c;
    border: 1px solid #21918c;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.target-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 8px;
    margin-bottom: 8px;
}
.target-card {
    background: #ffffff;
    border: 1px solid #eaeaea;
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    transition: all 0.25s ease;
}
.target-card:hover {
    border-color: #21918c;
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,0.07);
}
.target-card.null-card { border-style: dashed; border-color: #ccc; background: #fafafa; }
.target-card.null-card:hover { border-color: #21918c; border-style: dashed; }
.target-tier {
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #aaa;
    margin-bottom: 4px;
}
.target-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #21918c;
    font-family: 'Courier New', monospace;
    margin-bottom: 6px;
}
.target-desc { font-size: 0.78rem; color: #555; line-height: 1.5; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Hide the anchor-link (chain icon) Streamlit auto-adds to every heading on hover */
[data-testid="stHeaderActionElements"] { display: none !important; }

/* Replace Streamlit's default running-script icon (a running man / bike,
   depending on version) with a spinning teal taxi, matching the single-color
   feather-style icon set used on main.py's nav-cards (#21918c stroke, not
   OS emoji). Unofficial hack: targets Streamlit's internal data-testid,
   which is not public API and can break on a future Streamlit upgrade if
   they rename this element. */
[data-testid="stStatusWidgetRunningIcon"],
[data-testid="stStatusWidgetRunningManIcon"] {
    opacity: 0 !important;
}
[data-testid="stStatusWidget"] {
    position: relative;
}
[data-testid="stStatusWidget"]::before {
    content: "";
    position: absolute;
    left: 4px;
    top: 50%;
    width: 18px;
    height: 18px;
    transform: translateY(-50%);
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2321918c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M5 17h-2v-6l2 -5h9l4 5h1a2 2 0 0 1 2 2v4h-2m-4 0h-6m-6 0a2 2 0 1 0 4 0a2 2 0 0 0 -4 0m10 0a2 2 0 1 0 4 0a2 2 0 0 0 -4 0'/></svg>");
    background-repeat: no-repeat;
    background-size: contain;
    animation: pienza-taxi-drive 0.9s ease-in-out infinite;
    pointer-events: none;
}
@keyframes pienza-taxi-drive {
    0%, 100% { transform: translateY(-50%) translateX(0); }
    50%      { transform: translateY(-50%) translateX(6px); }
}
</style>
""".replace("#21918c", ACCENT)
