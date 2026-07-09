"""
GCS Deploy Script — Project Pienza Observatory
===============================================
Sube artefactos a GCS bucket pienza-streamlit desde dos fuentes posibles:
- data/dumped_files/      -> salida de notebooks (Run All)
- observatory/assets/     -> assets de frontend que nunca pasan por un notebook
  (PDFs, HTML, imagenes, JS/geojson), ver cada entrada del MANIFEST para su "source".
Correr desde Codespaces despues de un Run All que genere artefactos nuevos,
o cuando se agregue/actualice un asset de frontend.

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
OBS_ASSETS   = os.path.join(os.path.dirname(__file__), "..", "assets")
KEY_PATH     = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")

SOURCES = {
    "dumped_files": DUMPED_FILES,
    "assets": OBS_ASSETS,
}

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_PATH

# --- MANIFIESTO ---
# Cada entrada puede llevar "source": "dumped_files" (default, notebook output)
# o "source": "assets" (observatory/assets/, archivo de frontend que nunca vivio
# en dumped_files).
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
    {
        "page": "0007",
        "local": "0509_shap_l1_nuanced.parquet",
        "gcs":   "0509_shap_l1_nuanced.parquet",
    },
    {
        "page": "0007",
        "local": "0509_shap_l2.parquet",
        "gcs":   "0509_shap_l2.parquet",
    },
    {
        "page": "0007",
        "local": "260505_0509_learning_curve_L1.parquet",
        "gcs":   "260505_0509_learning_curve_L1.parquet",
    },
    {
        "page": "0007",
        "local": "260505_0509_learning_curve_L2.parquet",
        "gcs":   "260505_0509_learning_curve_L2.parquet",
    },
    {
        "page": "0007",
        "local": "260505_0509_spartan_learning_curve.parquet",
        "gcs":   "260505_0509_spartan_learning_curve.parquet",
    },
    {
        "page": "0007",
        "local": "0508_monolith_proba.parquet",
        "gcs":   "0508_monolith_proba.parquet",
    },
    {
        "page": "0007",
        "local": "0509_spartan_proba.parquet",
        "gcs":   "0509_spartan_proba.parquet",
    },
    # 0008 - The Quest to O1 NLP
    {
        "page": "0008",
        "local": "260702_minibabel_holdout_audit.parquet",
        "gcs":   "260702_minibabel_holdout_audit.parquet",
    },
    {
        "page": "0008",
        "local": "260422_pienza_babel_champion.pth",
        "gcs":   "260422_pienza_babel_champion.pth",
    },
    {
        "page": "0008",
        "local": "260422_token_to_idx.json",
        "gcs":   "260422_token_to_idx.json",
    },
    {
        "page": "0008",
        "local": "260423__idx_to_zone_to_semantics.json",
        "gcs":   "260423__idx_to_zone_to_semantics.json",
    },
    # NOTE: Pienza_Papers.pdf, kepler_3D.html, model_audit_map.html,
    # latency_test_map.html, zone-paths.js and poly.geojson used to be
    # manifest entries here, but were reclassified as public/non-sensitive
    # static assets and are now git-tracked directly in observatory/assets/
    # (see .gitignore exceptions and assets/CLAUDE.md) instead of living in
    # GCS. Only genuinely private data (real OCR screenshots, parquets,
    # model weights) belongs in this manifest going forward.
    # 0002 - Acquisition Pipelines (OCR offer card screenshots, private data)
    {
        "page": "0002",
        "local": "offer_cards/01_IMG_1691.PNG",
        "gcs":   "01_IMG_1691.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/02_IMG_3428.PNG",
        "gcs":   "02_IMG_3428.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/03_IMG_4346.PNG",
        "gcs":   "03_IMG_4346.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/04_IMG_5813.PNG",
        "gcs":   "04_IMG_5813.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/05_IMG_6624.PNG",
        "gcs":   "05_IMG_6624.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/06_IMG_0038.PNG",
        "gcs":   "06_IMG_0038.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/07_IMG_3679.PNG",
        "gcs":   "07_IMG_3679.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/08_IMG_9029.PNG",
        "gcs":   "08_IMG_9029.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/09_IMG_2793.PNG",
        "gcs":   "09_IMG_2793.PNG",
        "source": "assets",
    },
    {
        "page": "0002",
        "local": "offer_cards/10_IMG_9277.PNG",
        "gcs":   "10_IMG_9277.PNG",
        "source": "assets",
    },
    # 9002 - Network Graph (archive, treated as active; private trip data)
    {
        "page": "9002",
        "local": "0608_260513_tensor_arcos_w_eph_maestro.csv",
        "gcs":   "0608_260513_tensor_arcos_w_eph_maestro.csv",
        # already in data/dumped_files/, source defaults to "dumped_files"
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
        source_dir = SOURCES[e.get("source", "dumped_files")]
        local_path = os.path.join(source_dir, e["local"])
        if upload(bucket, local_path, e["gcs"], dry_run=args.dry_run):
            ok += 1

    print("-" * 60)
    print(f"{'DRY-RUN' if args.dry_run else 'DONE'}: {ok}/{len(entries)} archivos procesados")


if __name__ == "__main__":
    main()
