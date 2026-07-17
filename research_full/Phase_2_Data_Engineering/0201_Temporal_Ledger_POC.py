import os
import pandas as pd
from PIL import Image
import datetime
import hashlib
from tqdm import tqdm # <-- Asset Upgrade: Import progress bar library

# --- CONFIGURATION ---
ROOT_FOLDER_PATH = '/Users/wisex/Library/CloudStorage/GoogleDrive-bernardolw@gmail.com/My Drive/Opus_1_101001/Media/Screenshots' # <-- UPDATE THIS PATH
TARGET_TIMEZONE = 'America/Mexico_City'
OUTPUT_CSV_PATH = 'chrono_forge_v6_output.csv'
CHECKPOINT_INTERVAL = 100 

# --- FUNCTIONS ---
def generate_file_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""): sha256.update(byte_block)
    return sha256.hexdigest()

def get_timestamp(image_path):
    try:
        with Image.open(image_path) as img:
            if 'Creation Time' in img.info: return img.info['Creation Time'], "✅ Success (PNG metadata)"
    except Exception: pass
    try:
        with Image.open(image_path) as img:
            exif = img._getexif()
            if exif:
                for tag_id in [36867, 36868, 306]:
                    if tag_id in exif: return exif[tag_id], "✅ Success (EXIF)"
    except Exception: pass
    try:
        stat = os.stat(image_path)
        ts = pd.to_datetime(stat.st_birthtime, unit='s', utc=True).tz_convert(TARGET_TIMEZONE)
        return ts.strftime('%Y:%m:%d %H:%M:%S'), "✅ Success (File System)"
    except Exception as e:
        return "Extraction Failed", f"❌ Error: {e}"

def save_to_csv(data_list, filepath, is_checkpoint=False):
    columns = ['event_id', 'image_content_hash', 'containing_folder', 'filename', 'timestamp', 'status']
    df = pd.DataFrame(data_list, columns=columns)
    df.to_csv(filepath, index=False)
    msg = "🔄 Checkpoint saved" if is_checkpoint else "✅ Final results saved"
    # Use tqdm.write to print messages without disrupting the progress bar
    tqdm.write(f"   [{msg} to '{filepath}' ({len(df)} records)]")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print(f"--- `Operation Chrono-Forge v6 (w/ Progress Bars)` ---")
    print(f"Scanning root: {ROOT_FOLDER_PATH}")

    results = []
    
    if not os.path.isdir(ROOT_FOLDER_PATH):
        print(f"❌ ABORT: Root folder not found at '{ROOT_FOLDER_PATH}'")
    else:
        # --- ENHANCED Phase 1: Discovering files with a progress bar ---
        png_files = []
        # We wrap os.walk with tqdm to track progress per directory scanned.
        for dirpath, _, filenames in tqdm(os.walk(ROOT_FOLDER_PATH), desc="Phase 1: Discovering assets", unit=" dir"):
            for filename in filenames:
                if filename.lower().endswith('.png'):
                    png_files.append(os.path.join(dirpath, filename))
        
        total_files = len(png_files)
        print(f"Discovery complete. Found {total_files} PNG assets.")
            
        # --- ENHANCED Phase 2: Processing assets with a progress bar ---
        # We wrap the main file list with tqdm to track progress per file processed.
        process_iterator = tqdm(sorted(png_files), desc="Phase 2: Extracting data ", unit=" file")
        for i, full_path in enumerate(process_iterator, 1):
            
            timestamp, status = get_timestamp(full_path)
            image_content_hash = generate_file_hash(full_path)
            event_signature = f"{image_content_hash}::{timestamp}"
            event_id = hashlib.sha256(event_signature.encode()).hexdigest()
            
            relative_path = os.path.relpath(full_path, ROOT_FOLDER_PATH)
            results.append({
                'event_id': event_id,
                'image_content_hash': image_content_hash,
                'containing_folder': os.path.dirname(relative_path),
                'filename': os.path.basename(full_path), 
                'timestamp': timestamp, 
                'status': status
            })

            # Checkpoint system remains, but now uses tqdm.write for clean output
            if i % CHECKPOINT_INTERVAL == 0 or i == total_files:
                save_to_csv(results, OUTPUT_CSV_PATH, is_checkpoint=(i != total_files))

        print("\n--- Operation Complete ---")