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
    color: #21918c;
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
    font-size: 12px !important;
}

.block-container { padding-top: 2rem; }

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
</style>
"""
