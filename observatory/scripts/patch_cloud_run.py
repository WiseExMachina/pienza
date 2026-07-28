"""
Patch Cloud Run Service — Project Pienza Observatory
=====================================================
Aplica cambios puntuales al servicio pienza-observatory (env vars, resources,
scaling) sin pisar el deploy automatico del trigger de Cloud Build.

Por que existe: services().patch() con updateMask reemplaza el campo
"template.containers" completo, no hace merge. Un patch anterior hardcodeaba
la ruta de imagen manual (observatory:latest) en vez de leer cual imagen
estaba corriendo, y sin querer revertia el deploy automatico mas reciente
del trigger (que despliega imagenes con tag = commit SHA). Este script
siempre hace GET primero y reusa la imagen actual, tocando solo los campos
que el caller quiera cambiar.

Uso (como modulo, no CLI standalone):
    from patch_cloud_run import patch_service
    patch_service(env_overrides={"GCP_API_KEY": "..."})
    patch_service(cpu_idle=True)
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

PROJECT_ID   = "drivers-dilemma"
REGION       = "us-central1"
SERVICE_NAME = "pienza-observatory"
SERVICE_PATH = f"projects/{PROJECT_ID}/locations/{REGION}/services/{SERVICE_NAME}"
KEY_PATH     = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "service-account.json")


def _get_run_client():
    creds = service_account.Credentials.from_service_account_file(
        KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return build("run", "v2", credentials=creds)


def patch_service(env_overrides=None, cpu_idle=None, dry_run=False):
    """
    Lee el servicio actual, aplica solo los cambios pedidos sobre la spec
    completa del contenedor (preservando la imagen que este corriendo,
    sea la manual o la del ultimo deploy automatico), y hace patch.
    """
    svc = _get_run_client()
    current = svc.projects().locations().services().get(name=SERVICE_PATH).execute()

    container = current["template"]["containers"][0]
    current_image = container["image"]

    if env_overrides:
        env_list = container.get("env", [])
        env_map = {e["name"]: e["value"] for e in env_list if "value" in e}
        env_map.update(env_overrides)
        container["env"] = [{"name": k, "value": v} for k, v in env_map.items()]

    if cpu_idle is not None:
        container.setdefault("resources", {})["cpuIdle"] = cpu_idle

    print(f"Image preserved: {current_image}")
    if dry_run:
        print("dry-run, no patch sent")
        return current

    result = svc.projects().locations().services().patch(
        name=SERVICE_PATH,
        updateMask="template.containers,template.scaling",
        body=current,
    ).execute()

    after = svc.projects().locations().services().get(name=SERVICE_PATH).execute()
    after_image = after["template"]["containers"][0]["image"]
    assert after_image == current_image, (
        f"Image changed unexpectedly: {current_image} -> {after_image}"
    )
    print(f"Patched OK. Image confirmed unchanged: {after_image}")
    return result


if __name__ == "__main__":
    patch_service(dry_run=True)
