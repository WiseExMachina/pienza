"""
Canonical Graphviz recipe for research_core notebook flowchart PNGs (A/B diagrams).

Established 2026-07-19 while re-rendering 0407_Clustering_Paper_Streamlit_A.png to match
the existing _B.png style (which came from an external "Claude Design" tool we can't
invoke locally). Style was reverse-engineered by sampling _B's pixel colors and measuring
its absolute node/font size in pixels — NOT scaled relative to canvas width.

Key lesson learned the hard way: do NOT render big and downscale to fit a fixed canvas
width. The existing pipeline keeps node/font size CONSTANT in absolute pixels across all
diagrams and places them on a big fixed-width transparent canvas (simple diagrams look
small with lots of margin; dense ones fill more of it). Rendering at the "natural" size
(dpi=96) and centering on a 3600px-wide transparent canvas is what matches _B's approach.
Scaling the whole render up/down breaks the match.

Font/box size (fontsize=26, height=0.75in) was bumped up once from the initial pixel-exact
match to _B (fontsize=19, height=0.55in) — the exact match read as too small/cramped once
embedded at the notebook's fixed `width=1400` <img> tag, since simple diagrams (few nodes)
leave a lot of empty canvas margin. Confirmed by the user on 0403's diagram1. This bumped
size is the current canon — re-render 0407_A at the same settings if strict consistency
across notebooks matters more than exact-B pixel match.

Usage: copy NODE_STYLE/EDGE_STYLE below into a new .dot file, add your own nodes/edges,
then run through `render_and_center()`.
"""

import subprocess
from PIL import Image

# Sampled from 0407_Clustering_Paper_Streamlit_B.png (Counter of RGBA-on-white pixels)
FILL_COLOR = "#d9efed"
STROKE_COLOR = "#21918c"   # matches CLAUDE.md canonical teal
TEXT_COLOR = "#123f3c"

NODE_STYLE = (
    'node [shape=box, style="rounded,filled", fillcolor="{fill}", color="{stroke}", '
    'penwidth=2.5, fontname="Helvetica", fontsize=26, fontcolor="{text}", '
    'margin="0.28,0.18", height=0.75];'
).format(fill=FILL_COLOR, stroke=STROKE_COLOR, text=TEXT_COLOR)

EDGE_STYLE = 'edge [color="{stroke}", penwidth=2.5, arrowsize=0.85, arrowhead=vee];'.format(
    stroke=STROKE_COLOR
)

DOT_HEADER = """digraph G {{
    rankdir=TD;
    bgcolor="transparent";
    splines=ortho;
    nodesep=0.6;
    ranksep=0.7;
    {node_style}
    {edge_style}
"""


def render_and_center(dot_body: str, out_path: str, canvas_width: int = 3600, pad: int = 20):
    """dot_body: the node/edge lines only (no digraph wrapper). Renders at dpi=96,
    then centers the natural-size PNG on a transparent canvas_width-wide canvas."""
    dot_src = DOT_HEADER.format(node_style=NODE_STYLE, edge_style=EDGE_STYLE) + dot_body + "\n}\n"
    dot_path = out_path + ".dot"
    raw_path = out_path + ".raw.png"
    with open(dot_path, "w") as f:
        f.write(dot_src)
    subprocess.run(["dot", "-Tpng", "-Gdpi=96", dot_path, "-o", raw_path], check=True)

    im = Image.open(raw_path).convert("RGBA")
    w, h = im.size
    x = (canvas_width - w) // 2
    canvas = Image.new("RGBA", (canvas_width, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(im, (max(x, 0), pad), im)
    canvas.save(out_path)
    return canvas.size


if __name__ == "__main__":
    # Example / smoke test reproducing 0407_A
    body = """
    A2 [label="pienza.db: offers"];
    A  [label="assets/poly.geojson\\n(72 hand-drawn polygons)"];
    B  [label="Phase 1\\nPolygon geometry:\\nID injection, centroids"];
    C  [label="Phase 2\\nHDBSCAN clustering:\\n44 auto-discovered zones,\\nnaming fix"];
    D  [label="Phase 3\\nH3 hexagon grid\\n(resolution 9)"];
    E  [label="Phase 4\\nLabel generation:\\nweighted centroids,\\nmanual mapping, ID fix"];
    F  [label="Phase 5\\nValidation (Folium)\\n+ Golden Master export"];
    { rank=same; A2; A; }
    A -> B; A2 -> C; B -> C; C -> D; C -> E; D -> E; E -> F;
    """
    print(render_and_center(body, "/tmp/0407_A_smoketest.png"))
