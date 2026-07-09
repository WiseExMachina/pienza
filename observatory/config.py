from pathlib import Path

# Absolute paths anchored to this file's location, not the process's working
# directory — Streamlit Cloud launches the app from the repo root, not from
# observatory/ like local dev does (see "How to run" in assets/CLAUDE.md),
# so a bare relative path like "assets/favicon.png" resolved to the wrong
# assets/ folder (the repo-root one) on Cloud and silently fell back to
# Streamlit's default favicon.
_ASSETS_DIR = Path(__file__).resolve().parent / "assets"

FAVICON = str(_ASSETS_DIR / "favicon.png")
ACCENT = "#21918c"
ACCENT_DARK = "#1a7576"
PAGE_TITLE = "Project Pienza | Digital Twin"
PDF_PATH = str(_ASSETS_DIR / "Pienza_Papers.pdf")
GITHUB_URL = "https://github.com/your-repo"
AUTHOR = "Bernardo Lozano Wise"
