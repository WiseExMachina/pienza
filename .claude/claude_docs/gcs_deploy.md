# GCS Deployment Workflow

Full operational reference for the GCS-only asset pipeline — one of the most load-bearing pieces of documentation in this project. Root `CLAUDE.md` has a brief summary; this file is the complete mechanics.

## Principio arquitectural — REGLA ABSOLUTA

Todo archivo consumido por el Observatory (Streamlit Cloud/Cloud Run) debe vivir en GCS. NUNCA leer desde rutas locales `/workspaces/...` ni desde el repo en una pagina `.py`. Las libretas (Codespaces) pueden leer `pienza.db` local o BigQuery — no aplica la restriccion. Bucket: `pienza-streamlit`. Compute/storage decoupling: la app es efimera y stateless.

Esta regla aplica tambien a assets de frontend (HTML/JS/CSS embebidos, no solo datos). `assets/` (raiz del repo) es contexto/documentacion privada, correctamente sin trackear. Un solo criterio para todo el repo: "assets = no trackeado/no publico", y todo lo que la app necesita en runtime (incluyendo HTML/JS de frontend, no solo parquets/JSON/pesos de modelo) migra a GCS igual que los datos, en vez de vivir como archivo local leido con `open()`.

**Aclaracion de regla (2026-07-10):** la regla GCS-only aplica a datos sensibles/PII (parquets, JSON de features, etc.) — no a assets estaticos y compartibles como PNGs/favicons, que pueden seguir leyendose local via `Path(__file__)` siempre que el archivo este trackeado en git (ej. un ERD estatico, no un dato sensible).

## IMPORTANTE — Permiso obligatorio antes de subir a GCS

El usuario esta en el free tier de GCS. NUNCA ejecutar `gcs_deploy.py` ni ningun comando que escriba a GCS sin pedir permiso explicito primero. Mostrar que se va a subir y esperar confirmacion antes de proceder.

## ESTRICTO — Nunca crear subdirectorios/carpetas en el bucket

Todo archivo se sube DIRECTO a la raiz del bucket `pienza-streamlit`, sin prefijos de carpeta (nada de `gs://pienza-streamlit/algun_directorio/archivo.ext`). El nombre del blob en GCS debe ser un nombre de archivo plano, igual al patron ya usado en el MANIFEST de `gcs_deploy.py` (ej. `260702_minibabel_holdout_audit.parquet`, no `holdout/260702_minibabel_holdout_audit.parquet`). Si un blob termina con una carpeta nueva por accidente, es un error — corregirlo y volver a subir a la raiz.

## Pipeline canonico

```
Notebook escribe → data/dumped_files/   (staging, siempre aqui primero)
                         ↓
           scripts/gcs_deploy.py        (agregar al manifiesto y correr con permiso del usuario)
                         ↓
              GCS pienza-streamlit      (unica fuente de verdad para runtime)
                         ↓
           observatory/pages/*.py       (solo lee desde GCS via gcp_client.py)
```

## Regla para cualquier IA que escriba codigo para una pagina de Observatory

1. Si la pagina necesita leer un archivo: ese archivo DEBE estar en GCS.
2. Usar `fetch_parquet_from_gcp` o `download_from_gcs` de `utils/gcp_client.py`.
3. Nunca usar `open(...)`, `pd.read_parquet("ruta/local")`, ni `json.load(open(...))` con rutas locales.
4. Si el archivo no existe en GCS todavia: agregar al manifiesto de `gcs_deploy.py`, informar al usuario, y pedir permiso para subirlo.

## Como agregar un archivo nuevo al manifiesto

Abrir `observatory/scripts/gcs_deploy.py` y agregar una entrada al array `MANIFEST`:
```python
{
    "page": "NNNN",                # numero de pagina que lo consume, ej. "0007"
    "local": "nombre_archivo.ext", # nombre exacto en data/dumped_files/ (SIEMPRE desde ahi)
    "gcs":   "nombre_archivo.ext", # nombre con el que quedara en el bucket (puede ser igual)
},
```
Nota: `local` SIEMPRE apunta a `data/dumped_files/`. Si un notebook escribe a otro lugar, corregir el notebook para que escriba a `dumped_files/` antes de agregarlo al manifiesto.

## Como correr el script (pedir permiso antes)

```bash
# subir solo los archivos de una pagina
python observatory/scripts/gcs_deploy.py --page 0007

# dry-run primero para verificar que encuentra los archivos
python observatory/scripts/gcs_deploy.py --page 0007 --dry-run

# subir todo el manifiesto
python observatory/scripts/gcs_deploy.py
```

## Patron de lectura en Streamlit (ya implementado en gcp_client.py)

```python
from utils.gcp_client import fetch_parquet_from_gcp, download_from_gcs
# parquet: fetch_parquet_from_gcp("pienza-streamlit", "archivo.parquet")
# JSON/joblib: download_from_gcs("pienza-streamlit", "archivo.json", "/tmp/archivo.json")
```

## Estado actual por pagina

**0007_Human_vs_AI_Behavioral_Cloning.py**
- `260420_resultados_torneo_iter2v3.parquet` — GCS OK
- `0508_monolith_metrics.json` — GCS OK
- `0509_cascade_metrics.json` — GCS OK
- `lasso_liga_a.json` — GCS OK (movido de `observatory/assets/` a `dumped_files/`)
- BigQuery queries al vuelo — OK

**Resto de paginas — status not re-audited since this doc was written; re-verify before trusting.** To check any page's live-call surface:
```bash
grep -n "open\|read_parquet\|read_csv\|read_json\|dumped_files\|/workspaces" observatory/pages/*.py
```

## DEUDA TECNICA — asegurar que TODAS las paginas lean assets desde GCS, nunca local

Cualquier `.py` de pagina que siga leyendo un archivo local via `Path(__file__)...` / `open()` en vez de `fetch_bytes_from_gcs` / `fetch_parquet_from_gcp` es una excepcion que nunca se migro cuando se adopto la politica GCS-only — sin importar si el archivo local "funciona" hoy por estar trackeado en git. Antes de dar por resuelta esta deuda, correr:
```bash
grep -rn 'Path(__file__).*assets\|open(.*assets' observatory/pages/*.py observatory/main.py
```
para re-confirmar la lista completa (puede haber nuevos casos si se agrega una pagina). Para cada archivo pendiente: subir a GCS bucket `pienza-streamlit` (raiz, sin subcarpetas) y cambiar el loader Python para leer desde GCS. No ejecutar la subida sin permiso explicito del usuario.

**Ya confirmados correctos (leen via GCS, no locales):**
- `kepler_3D.html` en `main.py` — via `fetch_bytes_from_gcs("pienza-streamlit", "kepler_3D.html")`. La copia local en `observatory/assets/kepler_3D.html` es un sobrante sin uso, no el loader real.
- `Pienza_ERD.png` (ej. en `0004_Data_Census_(The_Basics).py`) — leido local via `Path(__file__)`, confirmado no es deuda tecnica: es un diagrama estatico, no dato sensible, cae bajo la aclaracion de regla 2026-07-10.
