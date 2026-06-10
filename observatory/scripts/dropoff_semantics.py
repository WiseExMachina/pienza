import json
import os
import pandas as pd
import numpy as np
from google.cloud import bigquery, storage

# --- CONFIGURATION ---
PROJECT_ID = "645009831643"     
BUCKET_NAME = "pienza-streamlit"       
INPUT_FILE_NAME = "260422_idx_to_zone.json"
OUTPUT_FILE_NAME = "260423__idx_to_zone_to_semantics.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../.streamlit/service-account.json"

print("⏳ Starting Cloud-Native Artifact Injection (Salchichota Edition)...")

# 1. Download Current Artifact from GCS
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)
input_blob = bucket.blob(INPUT_FILE_NAME)
idx_to_poly_id = json.loads(input_blob.download_as_string())

# 2. Query Raw BigQuery Data
print("📡 Fetching raw silver_palette from BigQuery...")
bq_client = bigquery.Client(project=PROJECT_ID)
query = """
SELECT 
    dropoff_polygon_id, 
    dropoff_hdbscan_id, 
    dropoff_polygon_name, 
    dropoff_hdbscan_name 
FROM `pienza_mini.silver_palette`
"""
df_input = bq_client.query(query).to_dataframe()

# 3. CLONE COLAB LOGIC: The Salchichota Map & Foundry
print("🧬 Reconstructing the Salchichota Semantic Mesh...")
id_map = {
    -1: -1, 41: 0, 42: 0, 46: 0, 43: 1, 65: 2, 62: 2, 44: 2, 36: 2, 49: 3, 52: 3,
    35: 3, 50: 4, 58: 4, 25: 5, 31: 5, 63: 6, 39: 6, 51: 7, 33: 7, 37: 8, 53: 8,
    48: 8, 60: 9, 57: 10, 12: 10, 32: 10, 24: 11, 40: 12, 45: 13, 59: 13, 61: 14,
    38: 14, 34: 15, 30: 16, 66: 16, 17: 17, 14: 17, 22: 17, 16: 18, 13: 18, 11: 19,
    15: 20, 21: 21, 20: 21, 19: 21, 18: 22, 47: 23, 55: 23, 56: 23, 54: 24, 64: 24,
    71: 25, 9: 26, 70: 27, 69: 28, 8: 29, 6: 30, 7: 30, 23: 30, 3: 31, 2: 32,
    4: 33, 29: 33, 68: 34, 5: 35, 27: 36, 28: 36, 1: 37, 10: 38, 0: 39, 26: 40, 67: 41
}

df_input['id_agrupado'] = df_input['dropoff_polygon_id'].fillna(-1).astype(int).map(id_map).fillna(-1)

name_foundry = df_input.groupby('id_agrupado')['dropoff_polygon_name'].unique().apply(
    lambda x: " / ".join(sorted([str(i).title().replace('_', ' ') for i in x if pd.notna(i) and i != 'unassigned']))
).to_dict()
name_foundry[-1] = "Unassigned"

df_input['grouped_polyname'] = df_input['id_agrupado'].map(name_foundry)

# 4. CLONE COLAB LOGIC: Master Coalesce
conditions_id = [(df_input['id_agrupado'] >= 0), (df_input['dropoff_hdbscan_id'] > -1)]
choices_id = ["P_" + df_input['id_agrupado'].astype(int).astype(str),
              "C_" + df_input['dropoff_hdbscan_id'].fillna(-1).astype(int).astype(str)]
df_input['final_zone_id'] = np.select(conditions_id, choices_id, default="Unassigned")

conditions_name = [(df_input['id_agrupado'] >= 0), (df_input['dropoff_hdbscan_id'] > -1)]
choices_name = [df_input['grouped_polyname'], df_input['dropoff_hdbscan_name']]
df_input['final_zone_name'] = np.select(conditions_name, choices_name, default="Unassigned Area")

# 5. CLONE COLAB LOGIC: Airport Fusion
df_input['final_zone_name'] = df_input['final_zone_name'].replace({
    'terminal_1_aicm': 'Aeropuerto AICM',
    'terminal_2_aicm': 'Aeropuerto AICM'
})
df_input['final_zone_id'] = df_input['final_zone_id'].replace({'C_5': 'C_4'})

# 6. Extract the Holy Grail Dictionary
zone_map = df_input[['final_zone_id', 'final_zone_name']].drop_duplicates().set_index('final_zone_id')['final_zone_name'].to_dict()

print("🧠 Translating neural indices to real semantic names...")
idx_to_semantic_name = {}
for idx_str, raw_zone_id in idx_to_poly_id.items():
    # Find P_15 in the newly forged zone_map
    clean_name = zone_map.get(raw_zone_id, raw_zone_id)
    # Give HDBSCAN clusters a nice title format
    if clean_name and " / " not in str(clean_name):
        clean_name = str(clean_name).replace('_', ' ').title()
    idx_to_semantic_name[idx_str] = clean_name

# 7. Upload to the NEW file name
print(f"☁️ Uploading new artifact '{OUTPUT_FILE_NAME}' to GCS...")
new_blob = bucket.blob(OUTPUT_FILE_NAME)
new_blob.upload_from_string(json.dumps(idx_to_semantic_name, ensure_ascii=False, indent=4), content_type='application/json')

print(f"✅ SUCCESS: {OUTPUT_FILE_NAME} injected with Salchichota Semantics!")