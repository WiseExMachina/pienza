from pathlib import Path
from PIL import Image

# Absolute paths anchored to this file's location, not the process's working
# directory — Streamlit Cloud launches the app from the repo root, not from
# observatory/ like local dev does (see "How to run" in assets/CLAUDE.md),
# so a bare relative path like "assets/favicon.png" resolved to the wrong
# assets/ folder (the repo-root one) on Cloud.
_ASSETS_DIR = Path(__file__).resolve().parent / "assets"

# page_icon as a PIL.Image instead of a path string — Streamlit has to
# classify a string page_icon as emoji vs URL vs local path before loading
# it, and that classification has had known unreliable behavior on
# Streamlit Community Cloud specifically. Passing an already-loaded
# PIL.Image sidesteps that classification entirely (fixing the absolute
# path alone did not resolve the favicon still showing Streamlit's default
# on the deployed app).
FAVICON = Image.open(_ASSETS_DIR / "favicon.png")
ACCENT = "#21918c"
PDF_PATH = str(_ASSETS_DIR / "Pienza_Papers.pdf")
# Hosted on GitHub Pages (published from main branch root), not GCS/local —
# The_Pienza_Papers/Pienza_Papers_Scientific.pdf is the real committed
# source file; the URL below mirrors that exact repo path.
PDF_URL = "https://wiseexmachina.github.io/pienza/The_Pienza_Papers/Pienza_Papers_Scientific.pdf"
GITHUB_URL = "https://github.com/WiseExMachina/pienza"
AUTHOR = "Bernardo Lozano Wise"

# Browser-tab title convention: "Pienza · Observatory · <page name>". Every
# page passes its own short name; main.py's is "Home".
TITLE_PREFIX = "Pienza · Observatory"


def build_page_title(name: str) -> str:
    return f"{TITLE_PREFIX} · {name}"
