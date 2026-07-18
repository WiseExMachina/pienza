# gemini_ocr_pipeline.py
# WiseX Ex Machina - Motor de Ingesta Automatizado v4.1 (The Original Baseline)

import os
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd
from PIL import Image
from tqdm import tqdm
import argparse
import re
import io
import time

# Load environment variables from .env file
load_dotenv()

def configure_api():
    """Configura la API de Gemini usando una variable de entorno."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Error: La variable de entorno GOOGLE_API_KEY no está configurada o el archivo .env no se encontró.")
    genai.configure(api_key=api_key)
    print("[INFO] API de Google Gemini configurada correctamente.")

def generate_prompt(filename: str) -> str:
    """Genera un prompt dinámico y optimizado para el API."""
    return f"""
**Objective:**
Analyze the attached screenshot from the Uber Driver app. The image  might contain a background with an in-progress ride, and a **main pop-up card in the center with a NEW ride request.** Your task is to extract information ONLY from this new ride request card.

**Critical Instructions:**
1.  **Scope Limitation:** All data to be extracted is located within the central pop-up card that shows the new fare.
2.  **Exclusion Rule:** You MUST IGNORE any address information located at the very top section of the screen. This information belongs to the *current* ride and is NOT part of the new request.
3.  **Filename Association:** The image provided is associated with the filename: **'{filename}'**. This must be the value in the 'Filename' column.

**Required Table Structure (Extract ONLY from the new ride request card):**
1.  **Filename**: '{filename}'.
2.  **Time_taken**: The time from the device's status bar.
3.  **Ride_Type**: e.g., UberX, Comfort.
4.  **Fare**: The quoted price from the new request card (numeric only).
5.  **Driver_Rating**: The star rating and number of ratings of the new passenger.  Beware: do not include in this tab the trip details nor the driver distance. If the source field has min or km then it must be disregarded.
6.  **Driver_Distance**: Time and distance to the new pickup location. Format: 18 min (3.9 km). Attention: Follow strict format; do not include "A " before the value.
7.  **Pickup_location**: The full pickup address for the new ride.
8.  **Trip_Duration**: The estimated time and distance of the new trip itself. Format: 18 min (3.9 km). Do not write "Viaje: " before the value.
9.  **Destination**: The full destination address for the new ride. 
10. **Special_note**: A combined field for ALL other details from the card (Exclusivo, VIP, surge, etc.), comma-separated.

**Output Format:**
Respond ONLY with the markdown table.
"""

def clean_and_parse_response(response_text: str) -> pd.DataFrame:
    """Limpia la respuesta de Gemini y la convierte en un DataFrame de Pandas."""
    match = re.search(r"\|.*\|[\s\S]*\|.*\|", response_text)
    if not match:
        return None
    markdown_table = match.group(0)
    try:
        data = io.StringIO(markdown_table)
        df = pd.read_csv(data, sep='|', header=0, skipinitialspace=True)
        if 'Unnamed: 0' in df.columns: df = df.drop('Unnamed: 0', axis=1)
        if df.columns[-1].startswith('Unnamed:'): df = df.drop(df.columns[-1], axis=1)
        df = df.iloc[1:].reset_index(drop=True)
        df.columns = [col.strip() for col in df.columns]
        if len(df.columns) != 10: return None
        for col in df.columns: df[col] = df[col].astype(str).str.strip()
        return df
    except Exception:
        return None

# === THE ORIGINAL, NON-RETRYING 'process_image_folder' FUNCTION ===
def process_image_folder(folder_path: str) -> pd.DataFrame:
    """
    Procesa todas las imágenes en una carpeta de forma ordenada y robusta.
    """
    model_name = 'models/gemini-2.0-flash' # The model from your original script
    print(f"[INFO] Usando el modelo: {model_name}")
    model = genai.GenerativeModel(model_name)

    image_extensions = ['.png', '.jpg', '.jpeg']
    print("[INFO] Buscando archivos de imagen...")
    image_paths = []
    try:
        file_list = sorted(os.listdir(folder_path))
        for f in file_list:
            if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in image_extensions:
                image_paths.append(os.path.join(folder_path, f))
    except Exception as e:
        print(f"[CRITICAL] No se pudo leer la carpeta de imágenes: {folder_path}. Error: {e}")
        return pd.DataFrame()

    if not image_paths:
        print(f"[WARNING] No se encontraron imágenes en la carpeta: {folder_path}")
        return pd.DataFrame()

    print(f"[INFO] Se encontraron {len(image_paths)} imágenes. Iniciando procesamiento ordenado.")
    all_data = []

    for img_path in tqdm(image_paths, desc="Procesando Imágenes"):
        filename = os.path.basename(img_path)
        try:
            img = Image.open(img_path)
            prompt = generate_prompt(filename)
            response = model.generate_content([prompt, img])
            df_row = clean_and_parse_response(response.text)

            if df_row is not None and not df_row.empty:
                all_data.append(df_row)
            else:
                all_data.append(pd.DataFrame([{'Filename': filename, 'Error': 'Failed to parse'}]))
        except Exception as e:
            all_data.append(pd.DataFrame([{'Filename': filename, 'Error': str(e)}]))
        time.sleep(1) # The original, simple 1-second delay

    if not all_data:
        print("[INFO] No se pudo extraer información de ninguna imagen.")
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)

# === THE MAIN EXECUTION BLOCK ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline OCR de WiseX Ex Machina v4.1")
    parser.add_argument("folder_path", type=str, help="Ruta a la carpeta de imágenes.")
    parser.add_argument("-o", "--output", type=str, default="raw_requests_extracted.csv", help="Archivo CSV de salida.")
    args = parser.parse_args()
    try:
        configure_api()
        results_df = process_image_folder(args.folder_path)
        if results_df is not None and not results_df.empty:
            results_df.to_csv(args.output, index=False, encoding='utf-8')
            print(f"\n[SUCCESS] ¡Proceso completado! Los datos han sido guardados en '{args.output}'.")
    except Exception as e:
        print(f"\n[CRITICAL] Un error irrecuperable ha ocurrido: {e}")