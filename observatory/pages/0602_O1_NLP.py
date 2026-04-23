import streamlit as st
import time
import requests
import regex as re
import unicodedata
import torch
import torch.nn as nn
import math
import json
import os
from transformers import AutoTokenizer, AutoModel

# IMPORT YOUR CLOUD CLIENT HERE
# Assuming: def download_from_gcs(bucket_name, source_blob_name, destination_file_name)
from utils.gcp_client import download_from_gcs  

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Phase 6: O(1) Engine Room", page_icon="⚡", layout="wide")

# ==========================================
# PHASE 2: LINGUISTIC PIPELINE (Hard-Cut)
# ==========================================
def standardize_mexico_city_address(text, debug=False):
    if not isinstance(text, str) or text.lower() in ['null', 'n/a']:
        return "unknown_address", {}

    t = text.lower()
    t = "".join(c for c in unicodedata.normalize('NFKD', t) if not unicodedata.combining(c))
    states = {"raw": t}

    # 1. HARD-CUT (The Guillotine)
    t = re.sub(r'\s*\S+\s*/.*$', '', t)
    states["post_cut"] = t

    # 2. Heuristics & Grammar
    t = t.replace('sante fe', 'santa fe').replace('sta fe', 'santa fe').replace('aicm', 'aeropuerto')
    t = re.sub(r'\b(av|ave|avenida|av\.|av_)\b', 'av', t)
    t = re.sub(r'\b(cll|calle|cll\.|cl\.)\b', 'calle', t)
    t = re.sub(r'\b(pº|p de|paseo de|pso|p\.º)\b', 'paseo', t)

    # 3. Zip Codes
    t = re.sub(r'\b(\d{5})\b', r'cp\1', t)
    states["post_grammar_zip"] = t

    # 4. Soldering
    for _ in range(3):
        t = re.sub(r'(\b\p{L}+(?:_\p{L}+|_\d+)*)\s+(\d{1,4}|norte|sur|este|oeste|poniente|oriente)\b', r'\1_\2', t)
    states["post_fusion"] = t

    # 5. Purge
    t = re.sub(r'[^a-z0-9áéíóúüñ_\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    states["final"] = t

    if debug:
        return t, states
    return t

# ==========================================
# PHASE 3: MODEL ARCHITECTURES
# ==========================================
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class ZoneClassifierTransformer(nn.Module):
    def __init__(self, vocab_size, num_classes, d_model=256, nhead=8, num_layers=2, dropout=0.3):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=256, dropout=dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(d_model * 2, num_classes)
        self.d_model = d_model

    def forward(self, x):
        x = self.embedding(x) * math.sqrt(self.d_model)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x)
        avg_pool = x.mean(dim=1)
        max_pool, _ = x.max(dim=1)
        fused_features = torch.cat((avg_pool, max_pool), dim=1)
        fused_features = self.dropout(fused_features)
        return self.classifier(fused_features)

class BETOWithCustomHead(nn.Module):
    def __init__(self, model_name, num_classes, dropout_rate=0.3):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(768 * 2, num_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
        
        sum_embeddings = torch.sum(hidden_states * input_mask_expanded, 1)
        sum_mask = input_mask_expanded.sum(1)
        sum_mask = torch.clamp(sum_mask, min=1e-9)
        avg_pool = sum_embeddings / sum_mask
        
        hidden_states_masked = hidden_states.masked_fill(input_mask_expanded == 0, -1e9)
        max_pool, _ = torch.max(hidden_states_masked, dim=1)
        
        fused_features = torch.cat((avg_pool, max_pool), dim=1)
        fused_features = self.dropout(fused_features)
        return self.classifier(fused_features)

# ==========================================
# RESOURCE LOADER (Runs Once)
# ==========================================
@st.cache_resource(show_spinner="Booting Pienza Inference Engines from GCS...")
def load_cloud_assets():
    BUCKET_NAME = "pienza-streamlit" 
    os.makedirs("/tmp/pienza_models", exist_ok=True)
    
    # 1. Download Dictionaries
    token_path = "/tmp/pienza_models/token_to_idx.json"
    zone_path = "/tmp/pienza_models/idx_to_zone.json"
    download_from_gcs(BUCKET_NAME, "260422_token_to_idx.json", token_path)
    download_from_gcs(BUCKET_NAME, "260423__idx_to_zone_to_semantics.json", zone_path)
    
    with open(token_path, 'r', encoding='utf-8') as f:
        token_to_idx = json.load(f)
    with open(zone_path, 'r', encoding='utf-8') as f:
        idx_to_zone = json.load(f)
        
    num_classes = len(idx_to_zone)
    vocab_size = len(token_to_idx)

    # 2. Load miniBabel (Champion)
    babel_path = "/tmp/pienza_models/babel.pth"
    download_from_gcs(BUCKET_NAME, "260422_pienza_babel_champion.pth", babel_path)
    
    minibabel = ZoneClassifierTransformer(vocab_size=vocab_size, num_classes=num_classes)
    minibabel.load_state_dict(torch.load(babel_path, map_location="cpu"))
    minibabel.eval()

    # 3. Load miniBETO (Heavyweight - FP16)
    beto_path = "/tmp/pienza_models/beto.pth"
    download_from_gcs(BUCKET_NAME, "260422_pienza_babel_beto_fp16.pth", beto_path)
    
    tokenizer = AutoTokenizer.from_pretrained("dccuchile/bert-base-spanish-wwm-cased")
    minibeto = BETOWithCustomHead("dccuchile/bert-base-spanish-wwm-cased", num_classes=num_classes)
    
    # Load the FP16 weights, but cast to float32 for stable CPU inference in Streamlit
    minibeto.load_state_dict(torch.load(beto_path, map_location="cpu"))
    minibeto.float() 
    minibeto.eval()
    
    return minibabel, minibeto, tokenizer, token_to_idx, idx_to_zone

# ==========================================
# INFERENCE LOGIC
# ==========================================
def get_google_maps_latency(address: str):
    api_key = st.secrets.get("GCP_API_KEY", "")
    if not api_key: return "API Key Missing", 0.0
    formatted_address = requests.utils.quote(f"{address}, CDMX, Mexico")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
    
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=5)
        latency = (time.perf_counter() - start_time) * 1000
        if response.status_code == 200 and response.json()['status'] == 'OK':
            return response.json()['results'][0]['formatted_address'], latency
        return "API Error", latency
    except:
        return "Network Timeout", (time.perf_counter() - start_time) * 1000

# ==========================================
# UI RENDERING
# ==========================================
# Initialize session state for address logging
if 'address_history' not in st.session_state:
    st.session_state['address_history'] = []

st.title("⚡ The O(1) Engine Room")
# --- MANUAL CACHE OVERRIDE ---
if st.button("🔄 Force Clear Cache", type="secondary"):
    st.cache_resource.clear()
    st.cache_data.clear()
    st.success("RAM cleared! Click 'Execute Pipeline' to pull fresh models.")
    st.rerun()
st.markdown("Benchmarking the Latency-Precision Frontier. Watch the architectural trade-offs unfold in real-time.")

try:
    minibabel, minibeto, beto_tokenizer, token_to_idx, idx_to_zone = load_cloud_assets()
    st.success("✅ Neural Engines Armed and Loaded from GCS.")
except Exception as e:
    st.error(f"⚠️ Cloud Asset Load Failed: {e}. Check your GCP Client and Bucket Name.")
    st.stop()

st.divider()

col_input, _ = st.columns([2, 1])
with col_input:
    raw_address = st.text_input("Raw Edge String (Try typos, missing zip codes, or noise):", value="Paseo de la Reforma 222 / Roma Norte")

if st.button("🚀 Execute Pipeline", type="primary"):
    
    # 1. PHASE 2: LINGUISTIC PIPELINE (Preprocessing)
    clean_text, states = standardize_mexico_city_address(raw_address, debug=True)
    
    st.subheader("Phase 2: The Linguistic Guillotine")
    st.code(f"""
    1. Raw Input:   {states['raw']}
    2. Hard-Cut:    {states['post_cut']}
    3. Zip/Grammar: {states['post_grammar_zip']}
    4. Soldered:    {states['post_fusion']}
    5. Final Array: [{clean_text}]
    """, language="text")

    st.divider()

    # 2. PHASE 3: THE TOURNAMENT (Inference)
    st.subheader("Phase 3: The Inference Waterfall")
    
    # --- Execute Google Maps ---
    gmap_res, gmap_lat = get_google_maps_latency(raw_address)
    
    # --- Execute miniBETO ---
    start_beto = time.perf_counter()
    encoded = beto_tokenizer(clean_text, return_tensors='pt', max_length=64, padding='max_length', truncation=True)
    with torch.no_grad():
        logits_beto = minibeto(encoded['input_ids'], encoded['attention_mask'])
        probs_beto = torch.softmax(logits_beto, dim=1)
        conf_beto, pred_idx_beto = torch.max(probs_beto, dim=1)
    beto_lat = (time.perf_counter() - start_beto) * 1000
    beto_res_label = f"{idx_to_zone.get(str(pred_idx_beto.item()), 'Unknown')} ({conf_beto.item():.1%} Conf)"

    # --- Execute miniBabel ---
    start_babel = time.perf_counter()
    tokens = clean_text.split()
    indices = [token_to_idx.get(t, token_to_idx.get('<unk>', 1)) for t in tokens]
    indices = indices[:30] + [token_to_idx.get('<pad>', 0)] * max(0, 30 - len(indices))
    tensor_in = torch.tensor(indices, dtype=torch.long).unsqueeze(0)
    with torch.no_grad():
        logits_babel = minibabel(tensor_in)
        probs_babel = torch.softmax(logits_babel, dim=1)
        conf_babel, pred_idx_babel = torch.max(probs_babel, dim=1)
    babel_lat = (time.perf_counter() - start_babel) * 1000
    babel_res_label = f"{idx_to_zone.get(str(pred_idx_babel.item()), 'Unknown')} ({conf_babel.item():.1%} Conf)"

    # 3. DISPLAY CURRENT RESULTS (The 3 Columns)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🌐 Google Maps API**")
        st.metric("Latency", f"{gmap_lat:.1f} ms")
        st.info(gmap_res)

    with col2:
        st.markdown("**🧠 miniBETO (FP16)**")
        st.metric("Latency", f"{beto_lat:.1f} ms")
        st.success(beto_res_label)

    with col3:
        st.markdown("**🏎️ miniBabel**")
        st.metric("Latency", f"{babel_lat:.1f} ms", delta=f"{(gmap_lat/babel_lat):.1f}x faster", delta_color="normal")
        st.success(babel_res_label)

    # 4. STATE PERSISTENCE (Log to History)
    new_entry = {
        "address": raw_address,
        "gmaps": {"lat": gmap_lat, "res": gmap_res},
        "beto": {"lat": beto_lat, "res": beto_res_label},
        "babel": {"lat": babel_lat, "res": babel_res_label},
        "timestamp": time.strftime("%H:%M:%S")
    }
    st.session_state['address_history'].insert(0, new_entry)

st.divider()
st.subheader("📜 Live Session Audit Trail")

if st.session_state['address_history']:
    for i, entry in enumerate(st.session_state['address_history']):
        with st.container(border=True):
            cols = st.columns([2, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"**{len(st.session_state['address_history']) - i}. Input:** `{entry['address']}`")
                st.caption(f"Captured at {entry['timestamp']}")
            
            with cols[1]:
                st.markdown("**🌐 G-Maps**")
                st.caption(f"{entry['gmaps']['lat']:.1f}ms")
                st.write(f"_{entry['gmaps']['res']}_")
                
            with cols[2]:
                st.markdown("**🧠 BETO**")
                st.caption(f"{entry['beto']['lat']:.1f}ms")
                st.write(entry['beto']['res'])
                
            with cols[3]:
                # miniBabel is highlighted as the efficiency champion
                st.markdown("**🏎️ Babel**")
                st.caption(f":green[{entry['babel']['lat']:.1f}ms]")
                st.write(f"**{entry['babel']['res']}**")

    if st.button("🗑️ Clear Audit Log"):
        st.session_state['address_history'] = []
        st.rerun()
else:
    st.info("The Engine Room is idling. Execute the pipeline to populate the audit log.")

st.divider()
st.info(f""" log of all adresses inputed in the end; map P_ to its semantic zone; map displaying the points of the resuls, etc """)