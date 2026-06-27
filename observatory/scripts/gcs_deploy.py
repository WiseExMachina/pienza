"""
GCS Deploy Script — Project Pienza Observatory
===============================================
Sube artefactos de data/dumped_files/ a GCS bucket pienza-streamlit.
Correr desde Codespaces despues de un Run All que genere artefactos nuevos.

Uso:
    python observatory/scripts/gcs_deploy.py              # sube todo el manifiesto
    python observatory/scripts/gcs_deploy.py --page 0007  # solo los de una pagina
    python observatory/scripts/gcs_deploy.py --dry-run    # muestra que subiria sin subir
"""

import os
import sys
import argparse
from google.cloud import storage

# --- CONFIG ---
BUCKET_NAME  = "pienza-streamlit"
DUMPED_FILES = os.path.join(os.path.dirname(__file__), "..", "..", "data", "dumped_files")
KEY_PATH     = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# --- MANIFIESTO ---
# Agregar aqui cada archivo que una pagina necesite leer desde GCS.
# Formato: { "page": "NNNN", "local": "nombre_en_dumped_files", "gcs": "nombre_en_bucket" }
MANIFEST = [
    # 0007 - Human vs AI Behavioral Cloning
    {
        "page": "0007",
        "local": "0508_monolith_metrics.json",
        "gcs":   "0508_monolith_metrics.json",
    },
    {
        "page": "0007",
        "local": "0509_cascade_metrics.json",
        "gcs":   "0509_cascade_metrics.json",
    },
    {
        "page": "0007",
        "local": "260420_resultados_torneo_iter2v3.parquet",
        "gcs":   "260420_resultados_torneo_iter2v3.parquet",
    },
    {
        "page": "0007",
        "local": "lasso_liga_a.json",
        "gcs":   "lasso_liga_a.json",
    },
    {
        "page": "0007",
        "local": "0509_l1_proba.parquet",
        "gcs":   "0509_l1_proba.parquet",
    },
    {
        "page": "0007",
        "local": "0509_l2_proba.parquet",
        "gcs":   "0509_l2_proba.parquet",
    },
    {
        "page": "0007",
        "local": "0509_sim_proba.parquet",
        "gcs":   "0509_sim_proba.parquet",
    },
    # Agregar entradas para otras paginas aqui cuando se auditen
]


def upload(bucket, local_path, gcs_name, dry_run=False):
    if not os.path.exists(local_path):
        print(f"  SKIP (no existe): {local_path}")
        return False
    size_kb = os.path.getsize(local_path) / 1024
    if dry_run:
        print(f"  DRY-RUN  {os.path.basename(local_path)} ({size_kb:.1f} KB) -> gs://{BUCKET_NAME}/{gcs_name}")
        return True
    blob = bucket.blob(gcs_name)
    blob.upload_from_filename(local_path)
    print(f"  OK  {os.path.basename(local_path)} ({size_kb:.1f} KB) -> gs://{BUCKET_NAME}/{gcs_name}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--page",    default=None, help="Filtrar por pagina, ej. 0007")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar que subiria sin subir")
    args = parser.parse_args()

    entries = [e for e in MANIFEST if args.page is None or e["page"] == args.page]
    if not entries:
        print(f"No hay entradas en el manifiesto para --page {args.page}")
        sys.exit(1)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    print(f"\nBucket: gs://{BUCKET_NAME}")
    print(f"Archivos a subir: {len(entries)}")
    print("-" * 60)

    ok = 0
    for e in entries:
        local_path = os.path.join(DUMPED_FILES, e["local"])
        if upload(bucket, local_path, e["gcs"], dry_run=args.dry_run):
            ok += 1

    print("-" * 60)
    print(f"{'DRY-RUN' if args.dry_run else 'DONE'}: {ok}/{len(entries)} archivos procesados")


if __name__ == "__main__":
    main()
