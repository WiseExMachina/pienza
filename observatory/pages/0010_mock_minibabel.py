import streamlit as st
import math

st.set_page_config(page_title="miniBabel: Architecture", layout="wide")

# ── ACCENT & CONSTANTS ──────────────────────────────────────────────────────
ACCENT = '#21918c'
XS = [20, 55, 90, 125, 160]
Y  = 62

# ── EXAMPLE DATA (from design handoff) ─────────────────────────────────────
EXAMPLES = [
    {
        'ocrRaw':     '"CALLE QUERETAR0 168 ROMA NORTE 0670O CUAUHTEM0C"',
        'ocrCleaned': '"Calle Querétaro 168, Roma Norte, 06700 Cuauhtémoc"',
        'ocrFixes':   '0 → <b>O</b>&nbsp;&nbsp;·&nbsp;&nbsp;O → <b>0</b>&nbsp;&nbsp;·&nbsp;&nbsp;accents restored (Querétaro, Cuauhtémoc)',
        'standardized': 'queretaro_168',
        'soldered':     'queretaro_168',
        'tokens':       ['queretaro_168', 'roma_norte', 'cp06700', 'cuauhtemoc', '<pad>'],
        'headQueries':  ['queretaro_168', 'roma_norte', 'cuauhtemoc', 'cp06700'],
        'headWeights':  [
            [0.60, 0.15, 0.13, 0.06, 0.06],
            [0.14, 0.58, 0.14, 0.07, 0.07],
            [0.16, 0.16, 0.14, 0.54, 0.00],
            [0.16, 0.16, 0.52, 0.08, 0.08],
        ],
        'zone': 'condesa_roma_1', 'confidence': '92%',
    },
    {
        'ocrRaw':     '"CALLE PALMA DE MALL0RCA 5 BOSQUES DE LAS PALMAS 52787 HUlXQUILUCAN"',
        'ocrCleaned': '"Calle Palma de Mallorca 5, Bosques de las Palmas, 52787 Huixquilucan, Ciudad de México"',
        'ocrFixes':   '0 → <b>O</b>&nbsp;&nbsp;·&nbsp;&nbsp;l → <b>i</b>&nbsp;&nbsp;·&nbsp;&nbsp;layout reconstructed across line breaks',
        'standardized': 'palma_de_mallorca_5',
        'soldered':     'mallorca_5',
        'tokens':       ['palma_mallorca_5', 'bosques_palmas', 'cp52787', 'huixquilucan', '<pad>'],
        'headQueries':  ['palma_mallorca_5', 'bosques_palmas', 'huixquilucan', 'cp52787'],
        'headWeights':  [
            [0.58, 0.16, 0.13, 0.07, 0.06],
            [0.14, 0.56, 0.16, 0.07, 0.07],
            [0.16, 0.16, 0.50, 0.09, 0.09],
            [0.16, 0.16, 0.16, 0.52, 0.00],
        ],
        'zone': 'interlomas_1', 'confidence': '88%',
    },
    {
        'ocrRaw':     '"L0MA DEL RECUERDO 50 LOMAS DE VISTA HERM0SA CUAJIMALPA 05l00"',
        'ocrCleaned': '"Loma del Recuerdo 50, Lomas de Vista Hermosa, Cuajimalpa de Morelos, 05100 Ciudad de México"',
        'ocrFixes':   '0 → <b>O</b>&nbsp;&nbsp;·&nbsp;&nbsp;l → <b>1</b>&nbsp;&nbsp;·&nbsp;&nbsp;municipality "Cuajimalpa de Morelos" recovered',
        'standardized': 'loma_del_recuerdo_50',
        'soldered':     'recuerdo_50',
        'tokens':       ['loma_recuerdo_50', 'vista_hermosa', 'cp05100', 'cuajimalpa', '<pad>'],
        'headQueries':  ['loma_recuerdo_50', 'vista_hermosa', 'cuajimalpa', 'cp05100'],
        'headWeights':  [
            [0.60, 0.15, 0.13, 0.06, 0.06],
            [0.14, 0.58, 0.14, 0.07, 0.07],
            [0.16, 0.16, 0.52, 0.08, 0.08],
            [0.16, 0.16, 0.16, 0.52, 0.00],
        ],
        'zone': 'bosques_1', 'confidence': '90%',
    },
]

# ── SESSION STATE ───────────────────────────────────────────────────────────
if 'mb_example' not in st.session_state:
    st.session_state['mb_example'] = 0

# ── SVG HELPERS ─────────────────────────────────────────────────────────────
def make_head_svg(n, query_label, weights, token_labels):
    query_idx = token_labels.index(query_label) if query_label in token_labels else 0
    qx = XS[query_idx]
    paths, circles, labels_svg = [], [], []

    for i, w in enumerate(weights):
        if i == query_idx:
            bump = 10 + w * 26
            d = f"M {qx-7} {Y-2} C {qx-15} {Y-bump} {qx+15} {Y-bump} {qx+7} {Y-2}"
        else:
            x2 = XS[i]
            mid_x = (qx + x2) / 2
            mid_y = Y - 26 - w * 46
            d = f"M {qx} {Y} Q {mid_x} {mid_y} {x2} {Y}"
        paths.append(f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="{1+w*5:.1f}" opacity="{0.25+w*0.65:.2f}" stroke-linecap="round"/>')

    for i, label in enumerate(token_labels):
        r    = 5.5 if i == query_idx else 4
        fill = ACCENT if i == query_idx else '#ffffff'
        circles.append(f'<circle cx="{XS[i]}" cy="{Y}" r="{r}" fill="{fill}" stroke="{ACCENT}" stroke-width="1.3"/>')
        short = label[:9]
        labels_svg.append(f'<text x="{XS[i]}" y="76" font-size="7" font-family="Courier New, monospace" text-anchor="middle" fill="#888">{short}</text>')

    inner = '\n'.join(paths + circles + labels_svg)
    return f'''
<div style="border:1px solid #eaeaea; background:#f8f9fa; border-radius:8px; padding:8px 8px 6px; flex:1; min-width:140px;">
  <svg viewBox="0 0 180 80" style="width:100%; height:auto; display:block; overflow:visible;">
    {inner}
  </svg>
  <div style="font-size:10px; font-family:'Courier New',monospace; color:#555; text-align:center; margin-top:2px;">Head {n} · from "{query_label}"</div>
</div>'''

def rail(pos, total):
    if pos == 0:
        return 'position:absolute; top:21px; bottom:0; left:50%; width:2px; background:#dddddd; transform:translateX(-50%);'
    if pos == total - 1:
        return 'position:absolute; top:0; height:21px; left:50%; width:2px; background:#dddddd; transform:translateX(-50%);'
    return 'position:absolute; top:0; bottom:0; left:50%; width:2px; background:#dddddd; transform:translateX(-50%);'

def stage_row(num, emoji, title, desc, spec, sub_items, recap_html=None, rail_style=''):
    sub_rows = ''.join(f'''
      <div style="display:flex; gap:14px; align-items:flex-start; padding:9px 0;">
        <div style="flex:0 0 auto; width:3px; align-self:stretch; background:{ACCENT}; opacity:{item['opacity']}; border-radius:2px;"></div>
        <div style="flex:0 0 170px; font-weight:700; font-size:13px; color:#333;">{item['label']}</div>
        <div style="flex:1; min-width:0; font-family:'Courier New',monospace; font-size:12.5px; color:#666; line-height:1.6;">{item['value']}</div>
      </div>''' for item in sub_items)
    recap = f'<p style="font-size:13.5px; color:#333; margin:14px 0 0;">{recap_html}</p>' if recap_html else ''
    return f'''
<div style="display:flex; align-items:stretch;">
  <div style="position:relative; width:56px; flex:0 0 auto; display:flex; justify-content:center;">
    <div style="{rail_style}"></div>
    <div style="position:relative; z-index:1; margin-top:2px; width:40px; height:40px; border-radius:50%; background:{ACCENT}; color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Inter',sans-serif; font-weight:800; font-size:16px;">{num}</div>
  </div>
  <div style="flex:1; min-width:0; padding:2px 0 40px 8px;">
    <h3 style="margin:0 0 10px; font-size:21px; font-weight:800; letter-spacing:0.3px; color:{ACCENT}; text-transform:uppercase;">{emoji} {title}</h3>
    <p style="font-size:14px; color:#555; line-height:1.7; margin:0 0 10px; max-width:600px;">{desc}</p>
    <div style="font-size:13.5px; color:#333; margin-bottom:16px;">{spec}</div>
    <div style="position:relative; margin:0 0 6px;">
      <div style="position:absolute; top:2px; bottom:2px; left:1px; width:2px; background:#eeeeee;"></div>
      {sub_rows}
    </div>
    {recap}
  </div>
</div>'''

def connector():
    return f'''
<div style="display:flex; flex-direction:column; align-items:center; padding:4px 0;">
  <div style="width:2px; height:16px; background:#dddddd;"></div>
  <div style="font-size:14px; color:{ACCENT}; line-height:1; margin-top:-1px;">▾</div>
</div>'''

# ── RENDER ──────────────────────────────────────────────────────────────────
idx = st.session_state['mb_example']
ex  = EXAMPLES[idx]

# Example selector — Streamlit buttons
st.markdown(f"""
<div style="font-size:11px; font-weight:700; letter-spacing:1.5px; color:#999; text-transform:uppercase; margin-bottom:8px; margin-top:8px;">
  Run the pipeline on a real capture
</div>""", unsafe_allow_html=True)

btn_cols = st.columns(3)
labels = ["Option 1 — Roma Norte", "Option 2 — Bosques", "Option 3 — Cuajimalpa"]
for i, (col, label) in enumerate(zip(btn_cols, labels)):
    with col:
        if st.button(label, key=f"mb_ex_{i}", type="primary" if i == idx else "secondary", use_container_width=True):
            st.session_state['mb_example'] = i
            st.rerun()

# ── ATTENTION HEAD DIAGRAMS ─────────────────────────────────────────────────
head_svgs = ''.join(
    make_head_svg(i+1, ex['headQueries'][i], ex['headWeights'][i], ex['tokens'])
    for i in range(4)
)

# ── PRE-ENCODER STAGES ──────────────────────────────────────────────────────
pre_stages = [
    dict(num=1, emoji='🖨️', title='Raw OCR Capture',
         spec='scanned / photographed source · noisy character stream',
         desc='The Observatory OCR engine reads a dropoff label or handwritten slip — glyph confusables (0/O, l/1) and missing accents are common at this stage.',
         sub_items=[{'label': 'OCR Output', 'value': ex['ocrRaw'], 'opacity': 1}],
         recap_html=ex['ocrFixes']),
    dict(num=2, emoji='🔤', title='Raw Address String',
         spec='raw text · Spanish / English mixed',
         desc='The corrected, human-readable dropoff address, ready for standardization.',
         sub_items=[{'label': 'Corrected String', 'value': ex['ocrCleaned'], 'opacity': 1}]),
    dict(num=3, emoji='🧹', title='Linguistic Standardization',
         spec='5 rule passes · Level 0 preprocessing, no learned weights',
         desc='Strips slash-suffixes, unifies street prefixes, isolates postal codes, and solders street + number tokens together before anything reaches the network.',
         sub_items=[
             {'label': 'Hard-Cut Guillotine',  'value': 'drop trailing "/ colonia" suffix',            'opacity': 1.0},
             {'label': 'Accent & Unicode',      'value': 'NFKD normalize · lowercase',                 'opacity': 0.8},
             {'label': 'Prefix Unification',    'value': 'av/avenida → av · cll/calle → calle · paseo','opacity': 0.62},
             {'label': 'Postal Code Isolation', 'value': r'\d{5} → cp#####',                           'opacity': 0.45},
             {'label': 'Token Soldering',       'value': f"street + number → {ex['soldered']}",        'opacity': 0.3},
         ]),
    dict(num=4, emoji='🔢', title='Token Embedding',
         spec='nn.Embedding · scaled by √d_model before the encoder',
         desc='Each token is mapped to a learned 128-dimensional vector.',
         sub_items=[
             {'label': 'Vocabulary',     'value': '2,502 tokens',                    'opacity': 1.0},
             {'label': 'Embedding Dim',  'value': '128 (d_model)',                   'opacity': 0.7},
             {'label': 'Output Shape',   'value': '[batch, 30] → [batch, 30, 128]',  'opacity': 0.45},
         ],
         recap_html=f'2,502 tokens (<b style="border-bottom:1px dotted {ACCENT};">2,500 learned</b> + <b style="border-bottom:1px dotted {ACCENT};">2 special</b>: &lt;pad&gt;, &lt;unk&gt;)'),
    dict(num=5, emoji='🧭', title='Positional Encoding',
         spec='sinusoidal · fixed, non-learned · added element-wise',
         desc='Sin/cos signals tell the model token order — which street name came before the house number.',
         sub_items=[
             {'label': 'Function',      'value': 'sin/cos(pos / 10000^(2i/d))', 'opacity': 1.0},
             {'label': 'Max Length',    'value': '30 tokens',                   'opacity': 0.7},
             {'label': 'Output Shape',  'value': '[batch, 30, 128]',            'opacity': 0.45},
         ]),
]

post_stages = [
    dict(num=6, emoji='🌀', title='Dual Pooling Fusion',
         spec='mean-pool ⊕ max-pool, concatenated after the encoder',
         desc='Average pooling captures overall sentence context; max pooling captures the single sharpest signal, like one distinctive street name.',
         sub_items=[
             {'label': 'Mean Pool',    'value': '128-dim · avg over sequence',             'opacity': 1.0},
             {'label': 'Max Pool',     'value': '128-dim · strongest signal',              'opacity': 0.7},
             {'label': 'Output Shape', 'value': '[batch, 30, 128] → [batch, 256]',         'opacity': 0.45},
         ],
         recap_html=f'256-dim fused vector (<b style="border-bottom:1px dotted {ACCENT};">128 mean-pool</b> + <b style="border-bottom:1px dotted {ACCENT};">128 max-pool</b>)'),
    dict(num=7, emoji='💧', title='Bottleneck Dropout',
         spec='p = 0.3, applied once before the classifier',
         desc='Regularizes the fused representation, curbing overfitting on a modest 3.4k-record training set.',
         sub_items=[
             {'label': 'Dropout Rate', 'value': 'p = 0.3',              'opacity': 1.0},
             {'label': 'Applied To',   'value': '256-dim fused vector',  'opacity': 0.7},
         ]),
    dict(num=8, emoji='🎯', title='Linear Classifier',
         spec='Linear(256 → 63) → softmax',
         desc='Projects the fused vector to 63 geographic zone logits; softmax turns them into class probabilities.',
         sub_items=[
             {'label': 'Input Dim',      'value': '256',                                    'opacity': 1.0},
             {'label': 'Output Classes', 'value': '63 zones (P_ polygon · C_ cluster ids)', 'opacity': 0.7},
             {'label': 'Activation',     'value': 'softmax',                                'opacity': 0.45},
         ]),
    dict(num=9, emoji='✨', title='Predicted Zone',
         spec='argmax + confidence, returned to the Observatory UI',
         desc='The zone with highest probability wins, alongside its confidence score.',
         sub_items=[
             {'label': 'Decision Rule', 'value': 'argmax(probs)',                          'opacity': 1.0},
             {'label': 'Result',        'value': f"{ex['zone']} @ {ex['confidence']}",     'opacity': 0.7},
             {'label': 'Latency',       'value': '< 10ms, on-device',                      'opacity': 0.45},
         ]),
]

pre_html  = ''.join(stage_row(**s, rail_style=rail(i, len(pre_stages)))  for i, s in enumerate(pre_stages))
post_html = ''.join(stage_row(**s, rail_style=rail(i, len(post_stages))) for i, s in enumerate(post_stages))

# ── FULL PAGE HTML ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  .mb-wrap * {{ font-family: 'Inter', sans-serif; box-sizing: border-box; }}
</style>

<div class="mb-wrap" style="background:#fafafa; font-family:'Inter',sans-serif; padding:32px 0 90px; max-width:860px;">

  <!-- EYEBROW -->
  <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px; flex-wrap:wrap;">
    <span style="font-size:11px; font-weight:700; letter-spacing:1.5px; color:#999; text-transform:uppercase;">Project Pienza</span>
    <span style="display:inline-block; background:#f0fafa; color:{ACCENT}; border:1px solid {ACCENT}; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase;">Phase 6 · Generative Moonshots</span>
  </div>

  <!-- TITLE BLOCK -->
  <h1 style="font-weight:300; font-size:40px; letter-spacing:-1px; color:#121212; margin:0 0 6px;">miniBabel: Custom NLP Transformer</h1>
  <h4 style="font-weight:300; color:{ACCENT}; font-size:19px; margin:0 0 20px;">A Real-Time Spatial Classifier — CDMX Address → Geographic Zone</h4>
  <p style="font-size:14px; color:#555; line-height:1.75; max-width:700px; margin:0 0 36px;">
    <b style="color:#121212; font-weight:600;">ZoneClassifierTransformer</b> is a custom encoder-only Transformer trained from scratch to resolve messy, human-written Mexico City dropoff addresses into one of 63 geographic zones — benchmarked live against the Google Maps Geocoding API inside the Observatory's Phase 6 diagnostic page.
  </p>

  <!-- STAT GRID -->
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin-bottom:56px;">
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
      <div style="font-size:0.72rem; font-weight:700; color:{ACCENT}; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Vocabulary</div>
      <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">2,502</div>
      <div style="font-size:0.72rem; color:#888; margin-top:4px;">standardized tokens</div>
    </div>
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
      <div style="font-size:0.72rem; font-weight:700; color:{ACCENT}; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Model Dim</div>
      <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">128</div>
      <div style="font-size:0.72rem; color:#888; margin-top:4px;">d_model · 4 heads × 2 layers</div>
    </div>
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
      <div style="font-size:0.72rem; font-weight:700; color:{ACCENT}; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Zones Classified</div>
      <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">63</div>
      <div style="font-size:0.72rem; color:#888; margin-top:4px;">polygon + HDBSCAN clusters</div>
    </div>
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:18px 20px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
      <div style="font-size:0.72rem; font-weight:700; color:{ACCENT}; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Inference Latency</div>
      <div style="font-size:1.6rem; font-weight:800; color:#121212; letter-spacing:-0.5px;">&lt; 10ms</div>
      <div style="font-size:0.72rem; color:#888; margin-top:4px;">on-device, CPU</div>
    </div>
  </div>

  <!-- PRE-ENCODER STEPPER -->
  {pre_html}

  <!-- CONNECTOR -->
  {connector()}

  <!-- TRANSFORMER ENCODER BLOCK -->
  <div style="position:relative; border:2px dashed {ACCENT}; border-radius:16px; padding:30px 24px 24px; background:rgba(33,145,140,0.03); margin-bottom:8px;">
    <div style="position:absolute; top:-14px; left:24px; background:#fafafa; padding:0 10px; font-size:12px; font-weight:700; color:{ACCENT}; letter-spacing:0.3px;">TRANSFORMER ENCODER LAYER</div>
    <div style="position:absolute; top:-14px; right:24px; background:{ACCENT}; color:#fff; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:700; letter-spacing:0.3px;">🔁 Stacked × 2</div>

    <!-- MULTI-HEAD SELF-ATTENTION -->
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:20px 22px; box-shadow:0 4px 6px rgba(0,0,0,0.02); margin-bottom:10px;">
      <h3 style="margin:0 0 10px; font-size:18px; font-weight:800; letter-spacing:0.3px; color:{ACCENT}; text-transform:uppercase;">🧠 Multi-Head Self-Attention</h3>
      <p style="font-size:13.5px; color:#555; line-height:1.65; margin:0 0 6px;">Every token attends to every other token in the address — letting "reforma" and "115" bind together regardless of order, while separate heads specialize in street names, colonias, or postal codes.</p>
      <div style="font-size:13px; color:#333; margin-bottom:14px;">4 heads · d_k = 32 each · scaled dot-product · Add &amp; Norm</div>
      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:4px;">
        {head_svgs}
      </div>
      <p style="font-size:10.5px; color:#999; margin:6px 0 0; line-height:1.4;">Teal node = the token doing the attending; arc thickness/opacity = attention weight onto each other token.</p>
    </div>

    <!-- CONNECTOR -->
    <div style="display:flex; flex-direction:column; align-items:center; padding:2px 0;">
      <div style="width:2px; height:12px; background:#dddddd;"></div>
      <div style="font-size:13px; color:{ACCENT}; line-height:1; margin-top:-1px;">▾</div>
    </div>

    <!-- FEED-FORWARD -->
    <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:20px 22px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
      <h3 style="margin:0 0 10px; font-size:18px; font-weight:800; letter-spacing:0.3px; color:{ACCENT}; text-transform:uppercase;">🔀 Position-wise Feed-Forward</h3>
      <p style="font-size:13.5px; color:#555; line-height:1.65; margin:0 0 6px;">Expands each token's representation to 256 dimensions and back, giving the model room to combine attention outputs non-linearly before the residual Add &amp; Norm.</p>
      <div style="font-size:13px; color:#333;">Linear(128→256) → ReLU → Linear(256→128) · dropout 0.3 · Add &amp; Norm</div>
    </div>
  </div>

  <!-- CONNECTOR -->
  {connector()}

  <!-- POST-ENCODER STEPPER -->
  {post_html}

  <!-- LATENCY BENCHMARK -->
  <div style="margin-top:20px;">
    <h3 style="color:{ACCENT}; font-size:20px; font-weight:800; text-transform:uppercase; letter-spacing:0.3px; margin:0 0 6px;">Cloud API vs. Local Neural Engine</h3>
    <p style="font-size:13.5px; color:#555; line-height:1.65; margin:0 0 20px;">The Observatory's diagnostic page races miniBabel against the Google Maps Geocoding API on every scan, live.</p>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px;">
      <div style="background:#fff; border:1px solid #eaeaea; border-radius:12px; padding:22px 24px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
        <div style="font-size:14px; font-weight:700; color:#121212; margin-bottom:10px;">🌐 Google Maps API (Cloud)</div>
        <div style="font-size:1.7rem; font-weight:800; color:#121212; letter-spacing:-0.5px; margin-bottom:6px;">~150–400ms</div>
        <div style="font-size:12.5px; color:#888;">network round-trip, per request</div>
      </div>
      <div style="background:#fff; border:1px solid {ACCENT}; border-radius:12px; padding:22px 24px; box-shadow:0 4px 6px rgba(0,0,0,0.02);">
        <div style="font-size:14px; font-weight:700; color:#121212; margin-bottom:10px;">🏎️ miniBabel (Local Neural)</div>
        <div style="font-size:1.7rem; font-weight:800; color:{ACCENT}; letter-spacing:-0.5px; margin-bottom:6px;">&lt; 10ms</div>
        <div style="font-size:12.5px; color:#888;">on-device forward pass, no network</div>
      </div>
    </div>
  </div>

  <!-- FOOTER -->
  <p style="font-size:0.75rem; color:#999; margin-top:56px; font-style:italic; border-top:1px solid #eaeaea; padding-top:16px;">
    Architecture reconstructed from Phase 6: Generative Moonshots — <span style="font-family:'Courier New',monospace;">ZoneClassifierTransformer</span> ("miniBabel"), Project Pienza. Lozano Wise, B. (2026).
  </p>

</div>
""", unsafe_allow_html=True)
