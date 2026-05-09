# ==============================================================================
# VOLCADO_GCS_ROOT.PY: GDRIVE -> GCS ROOT (VERSION SIN CARPETAS)
# ==============================================================================
import os
import pandas as pd
import gspread
from google.cloud import storage
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io

# --- 1. CONFIGURACIÓN ---
DATE_PREFIX = "260509"
SERVICE_ACCOUNT_PATH = '/workspaces/pienza/secrets/service-account.json'
GCS_BUCKET_NAME = "pienza_big_bang"

TARGETS = {
    "raw_Offers": {"id": "19ktNpGvWjXdvhnYKEnpvy44eI-BzbcVqggcS1bi75nw", "tabs": ["raw_requests_messy", "diamond_offers"]},
    "GTS-4": {"id": "1VeRJPPxkfyLvd2f4MFQmJRSdNEZhhc9KNPjGXpmrAjQ", "tabs": ["trip_events"]},
    "platform_data": {"id": "1ZKRtTUkWlwRVuGh11pxt-krWflIqSDpj7NC19aiJOFo", "tabs": ["activity_earnings", "lifetime_trips"]},
    "ConsoMaster": {"id": "18azMpad6BbVY9Vn2BH_W85uFrAxBJBa-WsDO2IpkdgU", "tabs": ["Sheet1"]},
    "Engineered_Features": {"id": "16kuO1VDwFKiwS1_adc2dGw4YnQeR4SHWqF-3LFw2Qrg", "tabs": ["Sheet2", "silver_palette"]},
    "Master_Clustering": {"id": "1Ahjq17ufUvlxG5tjQuvqFLKwqkKhTwx4UxQpr9nfyOA", "tabs": ["Sheet1"]}
}

PHYSICAL_FILES = ["schema_v251122.sql"]

# --- 2. AUTH & CLIENTS ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/cloud-platform']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH, scopes=SCOPES)
gc = gspread.authorize(creds)
drive_service = build('drive', 'v3', credentials=creds)
storage_client = storage.Client(credentials=creds, project=creds.project_id)
bucket = storage_client.bucket(GCS_BUCKET_NAME)

def upload_to_bucket_root(data_list, filename, is_csv=True):
    """Sube el contenido directamente a la raíz del bucket."""
    if is_csv:
        df = pd.DataFrame(data_list)
        blob = bucket.blob(f"{DATE_PREFIX}_{filename}.csv")
        stream = io.StringIO()
        # Mantenemos el lodo: todo como texto, sin procesar encabezados
        df.to_csv(stream, index=False, header=False)
        content = stream.getvalue()
        mimetype = 'text/csv'
    else:
        # Para archivos planos como el .sql
        blob = bucket.blob(f"{DATE_PREFIX}_{filename}")
        content = data_list
        mimetype = 'application/sql'

    blob.upload_from_string(content, content_type=mimetype)
    print(f"   ✅ [ROOT] {blob.name}")

# --- 3. EJECUCIÓN ---
print(f"🚀 Iniciando volcado directo a la raíz del bucket: {GCS_BUCKET_NAME}...\n")

# A. GSheets
for alias, info in TARGETS.items():
    print(f"📦 Extrayendo: {alias}...")
    sh = gc.open_by_key(info['id'])
    for tab in info['tabs']:
        try:
            ws = sh.worksheet(tab)
            # get_all_values() garantiza que no haya errores de tipos o headers duplicados
            dirty_data = ws.get_all_values() 
            
            file_label = f"{alias}_{tab}".lower()
            upload_to_bucket_root(dirty_data, file_label)
        except Exception as e:
            print(f"   ❌ Error en pestaña {tab}: {str(e)}")

# B. SQL
print(f"\n📂 Extrayendo archivos físicos...")
for fn in PHYSICAL_FILES:
    q = f"name = '{fn}' and trashed = false"
    res = drive_service.files().list(q=q, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
    for f in res.get('files', []):
        content = drive_service.files().get_media(fileId=f['id']).execute()
        upload_to_bucket_root(content, f['name'], is_csv=False)

print("\n" + "="*70)
print(f"🏁 MISIÓN CUMPLIDA. La data ahora vive en la raíz de {GCS_BUCKET_NAME}.")
print("="*70)