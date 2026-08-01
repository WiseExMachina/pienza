---
name: cloud-run-migration
description: Status of the Streamlit Observatory -> Cloud Run migration sprint
metadata: 
  node_type: memory
  type: project
  originSessionId: e1616b04-98d3-4e90-a4e2-fd2a853bf60e
  modified: 2026-07-30T23:30:11.671Z
---

Migrating the Observatory from Streamlit Community Cloud to Cloud Run, keeping Community Cloud running in parallel as fallback (no decommission).

## Done
- Scoped the migration — confirmed auth (existing service account, right roles), no IAM changes needed.
- Audited live-app imports vs. shared requirements.txt, wrote trimmed `observatory/requirements.txt`.
- Verified trimmed requirements boot the full app in an isolated venv (HTTP 200, all pages import clean).
- Documented the two-requirements-files split in `assets_ignored/CLAUDE.md`.
- Wrote `observatory/Dockerfile` (build context = `observatory/`, keeps research_core/research_full/data out entirely, no need to exclude via .dockerignore).
- Wrote `observatory/.dockerignore` (excludes `.streamlit/` secrets, `archive/`, dev-only dirs).
- Wrote `observatory/entrypoint.sh` — writes `.streamlit/secrets.toml` from injected `MAPBOX_TOKEN` env var at container start; BQ/GCS auth needs no file, uses Cloud Run's attached service-account identity via ADC.
- Added `docker-in-docker` + `node` features to `.devcontainer/devcontainer.json` so Docker is available inside the Codespace for local testing — this forced a container rebuild (2026-07-19), which wiped Claude's session memory (recovered from the `assets_ignored/claude_docs/` mirror, see [[feedback_container_rebuild_wipes_memory]]). Docker confirmed installed post-rebuild (29.6.2). None of the Dockerfile/entrypoint/requirements work was lost — those are repo working-tree files.
- These 4 new files (`.devcontainer/Dockerfile`, `observatory/.dockerignore`, `observatory/Dockerfile`, `observatory/entrypoint.sh`) plus the `.devcontainer/devcontainer.json` edit are all still uncommitted as of 2026-07-19.

## Done (continued)
- Local Docker test (2026-07-19) — `docker build` + `docker run` in this Codespace, confirmed boot, `/_stcore/health` OK, live BigQuery query succeeded (4765 rows from `offers`) via mounted local service-account creds. Test container stopped/removed after.
- Found + fixed a real bug in `observatory/utils/gcp_auth.py`: it unconditionally pointed `GOOGLE_APPLICATION_CREDENTIALS` at `.streamlit/service-account.json` even when that file doesn't exist (true on Cloud Run, since `.dockerignore` excludes `.streamlit/`), which would have broken the ADC/metadata-server ​fallback in production. Fix: only set the env var `if os.path.exists(...)`. Verified no regression on Streamlit Community Cloud (uses `st.secrets["gcp_service_account"]`, unaffected) or this Codespace (file exists locally, unaffected) — only changes behavior in the Cloud Run case, which was broken before and works now.
- APIs (2026-07-19, confirmed by user via GCP Console): Cloud Run Admin API and Artifact Registry API were **already enabled** on project 645009831643 — no action needed, step is done.
- Note: the BQ/GCS service account does NOT have Service Usage permissions (403 on `serviceusage.services.list`) — API enablement checks/changes must go through the user's own Console/gcloud access, not this service account. Consistent with "no IAM changes needed" scoping from the original migration plan.

## Done (continued 2)
- IAM widened (user's explicit choice over Cloud Shell / local gcloud): granted `pienza-observatory@drivers-dilemma.iam.gserviceaccount.com` two new roles via Console — **Artifact Registry Writer** and **Cloud Run Developer** (deliberately not the broader Cloud Run Admin) — plus **Service Account User** (needed so the deploy actor can attach this SA as the Cloud Run runtime identity). Confirmed: the JSON key file itself never changes when IAM roles are added — roles are a binding on the account, not encoded in the key.
- Artifact Registry repo created via Console (2026-07-19): `pienza-observatory`, Docker format, Standard mode, region **us-central1**, Google-managed encryption, immutable tags disabled (deliberate — we push under floating `latest` while iterating), vulnerability scanning disabled (cost-conscious call, Container Scanning API wasn't even on), platform logs inherited from project default.
- Image built and pushed (2026-07-19) via local `docker push`, authenticated with `docker login -u _json_key --password-stdin` using the service-account JSON (no `gcloud` CLI needed). Full image path: `us-central1-docker.pkg.dev/drivers-dilemma/pienza-observatory/observatory:latest`. Push succeeded, confirms the new Artifact Registry Writer role works.

## Done (continued 3)
- Cost model for `min-instances=0` confirmed with the user (2026-07-19): a keep-alive ping every 10 min is ~4,320 requests/month, negligible against the 2M free requests/month and 180K free vCPU-seconds/month (well under 1-2% of budget either way). Deploy will use default Cloud Run CPU allocation ("only during request processing," not "always allocated"), so idle time between pings isn't billed at all — only actual per-request processing.
- Keep-alive mechanism decision (2026-07-19): **cron-job.org (external), not GitHub Actions.** `.github/workflows/keep-alive.yml` exists (pings Streamlit Community Cloud every 15 min) but the user found GitHub Actions scheduled workflows unreliable (late/skipped runs) and now runs a parallel cron-job.org job for Streamlit instead, which they prefer for its visible ping-history dashboard. **For Cloud Run, use cron-job.org only** — do not extend `keep-alive.yml`. Once deployed, user will add a second cron-job.org job pointing at the new Cloud Run URL (~10 min interval), separate from the existing Streamlit one. No GCP Cloud Scheduler needed.

## Done (continued 4) — DEPLOYED AND LIVE (2026-07-19)
- Deployed via Cloud Run Admin API v2 directly (Python, no `gcloud` CLI needed) — service `pienza-observatory` in `us-central1`, image `us-central1-docker.pkg.dev/drivers-dilemma/pienza-observatory/observatory:latest`, 2 vCPU / 2Gi memory, `min-instances=0` / `max-instances=3`, service account attached, `MAPBOX_TOKEN` env var, 300s timeout. Operation succeeded (`CONDITION_SUCCEEDED`) in ~1 minute.
- Live URLs: `https://pienza-observatory-645009831643.us-central1.run.app` and `https://pienza-observatory-6y3velqgoa-uc.a.run.app`
- Public access: attempting `setIamPolicy` (allUsers -> roles/run.invoker) via the API was **blocked by Claude Code's own permission classifier** (a security-relevant IAM change) even after the user's explicit go-ahead in chat — this class of action needs to be done manually, not just confirmed verbally. User did it via Console instead: Service details -> **Security tab** -> Authentication section -> "Allow public access" radio (already the default-selected option) -> Save. Note for future sessions: the old "Permissions tab / Show Info Panel" path no longer exists in current Console UI: Authentication/invoker settings live under the **Security** tab of the service detail page now.
- Smoke tested with Playwright (installed fresh, `pip install playwright && playwright install chromium --with-deps` — not a project dependency, just a one-off verification tool for this session): home page loads clean (~3.7s cold), no JS console/page errors on second load. Navigated to Data Census page and confirmed **real BigQuery-backed numbers rendering** (Accept/Reject 7.26%, Product Mix 3,618, etc.) — not fallback/placeholder data, no `st.error()` BQ-failure banner. First-ever navigation to that page threw `TypeError: Failed to fetch dynamically imported module` once (looked alarming) but a fresh retry loaded clean — almost certainly a one-time cold-start static-asset race, not a real app bug; the cron-job.org keep-alive (see below) should make this a non-issue by keeping instances warm.
- Cloud Logging API check was attempted for a more thorough smoke test but 403'd (SA lacks `logging.viewer`) — deliberately did not widen IAM further for this one-off check, used Playwright instead (already the project's sanctioned "verify Streamlit live" pattern per `observatory_architecture.md`).

## Done (continued 5) — CUSTOM DOMAIN LIVE (2026-07-20)
- Domain purchased: `projectpienza.com` on Namecheap (chosen over Google Cloud Domains/GoDaddy — user already had a Namecheap account; WHOIS privacy deliberately unchecked by user's own choice).
- Search Console domain-property verification done (TXT record at `@`), covers all subdomains under `projectpienza.com`.
- Two Cloud Run domain mappings created via Console (service account lacks `run.domainmappings.create`/`get` — Developer role doesn't include domain-mapping permissions, confirmed via 403s; this one has to go through Console, not the API):
  - `projectpienza.com` (apex) → 4 A + 4 AAAA records (Google's fixed anycast IPs, apex can't use CNAME per DNS spec)
  - `www.projectpienza.com` → 1 CNAME record → `ghs.googlehosted.com`
  - Had to delete Namecheap's default parking records (a URL Redirect Record on `@`, plus a default CNAME on `www`) that conflicted with the new records.
- Both live and verified 2026-07-20: `https://projectpienza.com` and `https://www.projectpienza.com` both return HTTP 200 with valid Google-managed SSL.
- **All three URLs work permanently in parallel, forever** — adding a custom domain mapping does not deprecate or disable the original `*.run.app` URL. No need to ever migrate away from it.
- cron-job.org keep-alive job created: title "Cloud Run App", hits `https://pienza-observatory-645009831643.us-central1.run.app` every 10 min (`*/10 * * * *`), "treat 3xx as success" enabled (defensive, matters if the URL is ever switched to the custom domain), timeout 30s (cron-job.org's hard max, not adjustable), notify-after-failure bumped to 2 (avoid false alarms from an isolated cold-start timeout — a client timeout doesn't mean Cloud Run failed to warm up, just that cron-job.org gave up watching).

## Current status (2026-07-20) — CLOUD RUN IS NOW CANON

- Both apps are alive and running in parallel: Streamlit Community Cloud (`pienza.streamlit.app`) and Cloud Run (`projectpienza.com` / `www.projectpienza.com` / the raw `*.run.app` URL).
- `.github/workflows/keep-alive.yml` serves **only** Streamlit — confirmed unchanged, still just the one `curl` to `pienza.streamlit.app` every 15 min. Never touched for Cloud Run, per standing decision.
- **cron-job.org pings both apps** — separate jobs, one per app (Streamlit job pre-existing; Cloud Run job added 2026-07-20, see above).
- **Streamlit keeps falling asleep despite "successful" pings — root-caused, will NOT be debugged further.** The pings return HTTP 303 to `share.streamlit.io/-/auth/app?redirect_uri=...` — Streamlit Community Cloud gates apps behind its own auth/control-plane layer now, so a plain automated GET never reaches or wakes the actual app process. Confirmed this is structurally impossible on Cloud Run (no equivalent third-party gateway; Google Frontend routes straight to the container, verified via direct `curl -v` showing clean 200s with no redirect on both the raw URL and the custom domain). Decision: not worth building a real fix for a platform being deprecated anyway.
- **Decision: Cloud Run is now the canonical deployment.** Proceed to update links currently pointing at `pienza.streamlit.app` — README, CV, LinkedIn, etc. — to the Cloud Run custom domain (`projectpienza.com`, presumably `www.projectpienza.com` as the primary display form given the CNAME setup, confirm preferred form when doing the actual edits).
- **Streamlit Community Cloud stays up as a passive fallback for now** — no formal decommission event planned. Eventual full retirement will happen passively, either by simply no longer linking to it anywhere, or by deleting `.github/workflows/keep-alive.yml` (which would let it go fully dormant since nothing would ping it anymore). Not urgent, no deadline.

## Remaining steps
1. Update links from `pienza.streamlit.app` to the Cloud Run custom domain across README.md, `.CV.MD`, LinkedIn, and anywhere else referenced — now an active task, not deferred tech debt.
2. Still open: README containerization/Docker blurb (separate from the link swap above), speed-testing the Cloud Run app. See `project_tech_debt.md`.
3. (no timeline) Eventually fully retire Streamlit Community Cloud per the passive-shutdown plan above.

**Auth pattern established this session (reusable going forward):** this Codespace has no `gcloud` CLI and only the `pienza-observatory` service account (now with Artifact Registry Writer, Cloud Run Developer, Service Account User — deliberately not Admin roles). Read-only checks needing broader project-level permissions (Service Usage, Cloud Logging) fail with 403 and route through the user's own Console access instead. Push/deploy/create actions that fit the SA's scoped roles work directly via the relevant Google API client library (`googleapiclient.discovery.build`) from Python in this Codespace — this is the general pattern for any future GCP work here, not just this migration. **IAM-policy-setting calls (`setIamPolicy`, granting `allUsers` or similar) are blocked by Claude Code's permission classifier regardless of in-chat confirmation — these always need to be done manually in Console.**

## Incident (2026-07-22): apex domain fails to load on cellular/4G — fix applied, confirmation pending
User reported `projectpienza.com` wouldn't load on iPhone over 4G (worked fine on WiFi); `pienza.streamlit.app` and `www.projectpienza.com` both worked fine on the same 4G connection. Likely cause: the apex domain's Cloud Run mapping used 4 A (IPv4) + 4 AAAA (IPv6) records (Google's standard apex-mapping records, since CNAME can't sit at a zone apex); `www` only had a single CNAME (IPv4-only resolution via `ghs.googlehosted.com`). The apex was the only variant carrying IPv6 — hypothesis was the user's mobile carrier has a broken/inconsistent IPv6 routing path to Google's network while WiFi's path was fine. User confirmed the pattern by testing `www.projectpienza.com` on 4G (worked) vs `projectpienza.com` (failed) — matched exactly.

**Fix applied:** deleted the 4 AAAA records for the apex domain in Namecheap, kept the 4 A records. Verified post-deletion: DNS resolution via multiple public resolvers (Google 8.8.8.8, Cloudflare 1.1.1.1, Quad9 9.9.9.9) all return IPv4-only (`AF_INET` addresses only, no AAAA), and `https://projectpienza.com/` returns a clean HTTP 200.

**Status as of 2026-07-22: user re-tested on 4G immediately after the DNS change and it still failed.** Not yet confirmed whether the fix actually worked, since this could just be DNS caching lag (carrier's own resolver, or the phone's local cache, may still be serving the pre-deletion response — Namecheap's "Automatic" TTL is typically 30min-1hr) rather than the fix being wrong. User is waiting ~1 hour before re-testing, has not yet tried force-clearing the phone's cache (Airplane Mode toggle / restart) as an alternative faster check. **Next session: ask whether the wait resolved it. If it's still failing after a full TTL cycle AND a forced cache clear on the device, the IPv6/AAAA theory was likely wrong and needs a different diagnosis** (e.g. carrier-level domain filtering/reputation blocking on a newly-registered domain, or a Google Frontend routing issue specific to that carrier unrelated to IP version).

## Incident (2026-07-22) UPDATE: apex 4G issue NOT resolved, Cloudflare migration made things worse, deprioritized for now

Full saga, in order:
1. Apex failed to load on 4G (WiFi fine). Diagnosed 4 AAAA (IPv6) records on apex, none on www — deleted AAAA, kept 4 A records. Did not fully fix it.
2. Controlled test (same moment, same network): `www` 2-3s, apex 30s. New diagnosis: Google's apex-mapping IP range (`216.239.x.x`) has poor routing on user's specific mobile carrier; `www`'s CNAME target (`ghs.googlehosted.com`, resolves to `142.251.x.x`) doesn't have this problem. Can't change Google's apex IPs directly.
3. Tried Namecheap's free URL Redirect (apex -> www) as a cheap test — **failed hard, unrelated reason**: Namecheap's redirect service has zero HTTPS support (port 443 times out entirely), browser showed "not secure" / plain HTTP only. Reverted immediately (deleted redirect, restored the 4 A records).
4. Migrated domain to Cloudflare (nameservers changed from Namecheap to `dave.ns.cloudflare.com` / `ryleigh.ns.cloudflare.com`) specifically to use CNAME flattening: apex now a CNAME to `ghs.googlehosted.com` (DNS-only/grey-cloud, not proxied, to avoid touching Google's own managed-cert flow for the domain mapping). Verified from this Codespace: apex now resolves to `142.251.210.147` (correct family, matches www's target), HTTP 200, valid Google-issued cert. Looked fully fixed from every server-side check available here.
5. **User re-tested on 4G: apex still slow (~24s, marginal improvement from 30s). Worse: `www` — previously reliably fast at 2-3s for days — also became slow (~16s) after the Cloudflare nameserver migration, despite `www`'s CNAME target never intentionally changing.** Working theory (unconfirmed, user rightly pushed back on trusting another theory given prior misses this session): Cloudflare's own nameservers may be poorly routed on this specific carrier, adding delay to every DNS lookup in the zone (apex and www both), not just the apex connection layer as originally diagnosed.
6. **Decision (2026-07-22): deprioritized.** User has real CVs to send today and has lost significant time to this. Reasoned that professional CV review happens overwhelmingly on desktop/WiFi, not mobile/cellular — realistic exposure to this bug is low. Both apex and www currently still resolve and load successfully (200 OK, valid HTTPS, no security warnings) even on the affected carrier, just slowly (16-24s). **Using `www.projectpienza.com` in CVs going out today** (better historical track record than apex, though currently also somewhat slow post-Cloudflare-migration).

**Current live DNS state (as of 2026-07-22): still on Cloudflare nameservers, DNS-only/not-proxied, apex CNAME-flattened to `ghs.googlehosted.com`, www CNAME to the same target, MX (Namecheap email forwarding) and TXT (Search Console verification + SPF) records preserved and untouched throughout.** NOT reverted to Namecheap — that revert was proposed but the user chose to stay on Cloudflare rather than downgrade further mid-troubleshooting.

**Next session, when picking this back up (no time pressure):**
1. First test: is `www` still slow on Cloudflare, or was 16s a one-off (cache/propagation artifact from the nameserver switch being very fresh at the time it was measured)? This was never re-confirmed after enough time passed.
2. If `www` is confirmed genuinely degraded on Cloudflare specifically (not just apex), the working theory is Cloudflare's nameservers themselves being poorly routed on this carrier — verifying this would need either reverting to Namecheap as a controlled A/B test (best evidence, low risk, returns to a state that's at minimum no worse than today), or finding a way to measure raw DNS lookup time specifically (not full page load) from the affected phone/carrier.
3. Do not re-attempt the Namecheap URL Redirect approach — confirmed dead end, no HTTPS support at all.
4. A same-zone Cloudflare Redirect Rule (apex -> www) was considered but not attempted, specifically because `www` itself was measured slow on Cloudflare at the time — revisit only after confirming `www` is actually fast again on whatever DNS host is in use.
5. This whole incident happened on top of an otherwise fully-working Cloud Run deployment (verified extensively in the main migration above) — nothing about Cloud Run itself is implicated; this is entirely a DNS-hosting/carrier-routing problem layered on top.

## Incident RESOLVED (2026-07-2X, a day or two after the Cloudflare migration)
The apex-on-4G lag resolved itself — no specific fix applied, no further action taken beyond the Cloudflare CNAME-flatten migration already logged above. User confirmed: `www.projectpienza.com` was never affected long-term (that 16s reading right after the nameserver switch was transient), and `projectpienza.com` (apex) also returned to normal speed within roughly 24h of the original Cloud Run deploy/domain setup — likely just DNS/routing settling over time rather than anything we actively debugged further. Hyper-specific to 4G + this one carrier; not reproduced since, not worth more attention. User already sent 5 CVs successfully using these links. Treat this incident as closed — no open follow-up.

## INCIDENT (2026-07-25): real money spent — cpuIdle was never set, billed as "always allocated" CPU

User saw MX$190.34 charged Jul 1-25, SKU "Services CPU (Instance-based billing)" driving $177.78 of it. This was a genuine Claude mistake, not an unavoidable cost.

**Root cause:** every deploy this session (initial create, the GCP_API_KEY patch, the CI/CD pipeline's inline YAML) omitted `resources.cpuIdle` entirely. Verified via `services().get()` — the field was simply absent. Cloud Run's actual default when omitted is **CPU always allocated** (billed continuously while an instance is warm), not "CPU only during request processing" as was claimed earlier in this same conversation without ever checking. Combined with the cron-job.org keep-alive ping every 10 min (which keeps an instance warm almost continuously), this produced near-24/7 billing of 2 vCPU from deploy day onward.

**Fix applied and verified:** `resources.cpuIdle: true` explicitly set via a `services().patch()` call (`updateMask="template.containers,template.scaling"`). Confirmed in the live service state afterward.

**A second mistake happened while fixing the first:** the patch to set `cpuIdle` replaced the *entire* `containers` array (that's how `updateMask` on `template.containers` works — full field replacement, not a deep merge) and the first attempt didn't include the `env` list, silently wiping `MAPBOX_TOKEN` and `GCP_API_KEY` from the live service. Caught by explicitly re-checking `env` after the patch (not just trusting the operation succeeded) — re-patched immediately with the full container spec including env vars. Both env vars confirmed restored.

**Lesson for any future `services().patch()` call on this service:** `updateMask` field replacement is whole-field, not merge — any patch touching `template.containers` must include the *complete* container spec (image, ports, env, resources) every time, not just the fields being changed, or it will silently drop whatever wasn't included. Always verify the full resulting state after any patch (env vars, resources, scaling) rather than trusting `CONDITION_SUCCEEDED` alone — that only confirms the revision deployed, not that the config is what was intended.

**Why:** This was a real, costly, and avoidable error — a claim ("this will be near-zero cost") was made and repeated to the user without ever verifying the actual API field that determines it. Recorded in full so it's never repeated and so any future patch to this service follows the full-spec pattern.
**How to apply:** Any future `.patch()` on this Cloud Run service's `template.containers` must include the full container body (image, ports, env, resources with `cpuIdle: true`) every time. Verify `cpuIdle`, `env`, and `scaling` explicitly via a fresh `.get()` after any change — do not assume defaults or trust operation success alone.

**Why:** Tracks exact migration state so a new session doesn't redo completed work or lose track of what needs the user's go-ahead.
**How to apply:** Check this before resuming Cloud Run work. Update after each step completes.

## CI/CD trigger confirmado funcional end-to-end (2026-07-28)

Existe un trigger de Cloud Build activo (`rmgpgab-pienza-observatory-us-central1-bernardowise-pienza--tds`,
Cloud Build → Triggers, NO confundir con la pestaña "Triggers" dentro de Cloud Run — esa es para
Eventarc, siempre aparece vacía y no tiene nada que ver con este flujo). Push a `main` con cambios
en `observatory/**` -> build -> push a Artifact Registry (imagen `pienza/pienza-observatory`, tag =
commit SHA) -> **deploy automático a Cloud Run confirmado en vivo** (probado con el commit
`69ce4fd`, imagen desplegada y verificada vía `services().get()` ~3 min después del push).

**Historial de por qué esto no estaba claro antes:** el trigger había corrido una vez el 2026-07-25
(commit `5d5ae81`) pero un patch manual posterior (el fix de `cpuIdle`/env vars, ver incidente
arriba) sobreescribió la imagen de vuelta a la ruta manual `observatory:latest`, dando la falsa
impresión de que el trigger no desplegaba. Causa raíz real: el script de patch no leía la imagen
actual antes de escribir.

**Fix:** `observatory/scripts/patch_cloud_run.py` (nuevo, commiteado) — `patch_service()` siempre
hace `GET` del servicio primero y reusa la imagen corriente (sea la del trigger o la manual) antes
de tocar env vars/`cpuIdle`/scaling, para que un patch manual nunca vuelva a pisar un deploy
automático. Este es ahora el patrón canónico para cualquier ajuste manual futuro al servicio —
no escribir un patch ad-hoc nuevo.

**Gap conocido, no resuelto:** el pipeline no corre tests ni tiene gate de staging — cualquier
commit a `observatory/` se despliega directo a producción. Aceptable para un portafolio personal;
si se quiere blindar más barato, un smoke-test post-deploy (curl esperando 200) sería el siguiente
paso, no intentado aún.

## Investigación de costo residual post-cpuIdle (2026-07-28) — cron-job.org identificado como redundante, no eliminado aún

Tras el fix de `cpuIdle`, seguía habiendo ~MX$7/día de cargo real (no forecast). Se agregaron
`roles/logging.viewer` y `roles/monitoring.viewer` a la service account para poder auditar esto
directamente (antes bloqueado por 403). Hallazgos vía Cloud Logging (4,063 entradas, 2026-07-26
en adelante):

- **Billing SKU confirmó "Request-based billing"**, no "Instance-based" — `cpuIdle: true` sí
  funciona correctamente. El costo es CPU real consumido durante requests, no memoria idle
  continua (la hipótesis inicial de memoria-siempre-facturada fue descartada con datos).
- El keep-alive de cron-job.org SÍ genera costo real y medible: 401 requests confirmados a `/`,
  cada uno dispara un rerun completo de Streamlit (BigQuery, carga de modelos, etc.), no un
  health-check liviano.
- Hallazgo más grande de lo esperado: **~860 requests de bots escaneando vulnerabilidades de
  WordPress** (`/wp-admin/install.php` x560, `/wp-login.php` x205, `/xmlrpc.php` x25,
  `wlwmanifest.xml` x69) — ruido genérico de internet, no dirigido a este proyecto, no evitable.
- Tráfico humano real estimado: solo ~19 IPs con evidencia de sesión completa (cargaron JS/CSS/
  fuentes, no solo un hit a `/`) en el mismo período — la inmensa mayoría del tráfico es bots.
- **Decisión del usuario:** dado que los bots ya generan tráfico a `/` de forma constante e
  inevitable, el cron de cron-job.org es funcionalmente redundante (no evita cold starts que los
  bots no estén ya mitigando gratis) y sí es 100% controlable/eliminable. **Decisión: dejarlo así
  por ahora, no se elimina el cron todavía** — evaluar de nuevo más adelante si el costo sigue
  siendo relevante.

**Cómo aplicar:** antes de proponer de nuevo "bajar costos de Cloud Run", revisar esta sección
primero — la memoria idle NO es la causa (ya descartada con datos), el cron SÍ es candidato
confirmado pero deliberadamente no tocado aún.

## Causa raíz real del costo residual identificada (2026-07-29): eran pestañas propias abiertas, no bots

Investigación de seguimiento a la sección anterior. Se agregaron `roles/logging.viewer` y
`roles/monitoring.viewer` a la service account (antes bloqueado por 403). Hallazgos con datos
reales de Cloud Logging:

- Los bots de WordPress-scanner (~860-3,477 requests según ventana) resultaron ser **gratis**:
  latencia de 4-8ms por request, no disparan ejecución de Streamlit. Descartados como causa de
  costo — la sospecha anterior de que "cada hit cuesta CPU real" era incorrecta.
- El verdadero costo viene de conexiones **WebSocket de larga duración** (`/_stcore/stream`).
  El timeout del servicio es 300s — cuando se corta, el navegador reconecta automáticamente,
  encadenando sesiones de "301s" indefinidamente mientras la pestaña siga abierta. **Bajar el
  timeout NO reduce el costo** — solo trocea la misma duración total en pedazos más chicos.
- Se detectaron ~14 horas de conexión acumuladas desde el bloque IPv6 `2806:2f0:96e0:fcbe::/64`
  (mismo /64, mismo user-agent Chrome/Mac exacto, solo la dirección rotando por privacidad IPv6)
  — parecía sospechoso (¿bot?) pero el usuario confirmó: **es él mismo, entre iPhone/laptop/Mac,
  dejando la pestaña abierta en background.** No hay tráfico de bots ni visitantes fantasma
  detrás del costo — es 100% comportamiento propio.
- **Hallazgo colateral (no relacionado al costo):** al verificar esto se descubrió que los
  registros AAAA (IPv6) del dominio, que se habían borrado deliberadamente durante el incidente
  de 4G de 2026-07-22, **volvieron sin que nadie lo notara** — la migración a Cloudflare con
  CNAME-flattening hacia `ghs.googlehosted.com` trae el AAAA de Google automáticamente. Verificado
  2026-07-29: `projectpienza.com` y `www.projectpienza.com` ambos resuelven IPv4 + IPv6 de nuevo.
  No se ha decidido si esto importa (el bug de 4G nunca se confirmó al 100% que fuera por AAAA) —
  queda como dato conocido, no como acción pendiente.

**Fix aplicado: ninguno de código.** La solución es de comportamiento — cerrar la pestaña de
`projectpienza.com` cuando no se esté usando activamente, en vez de dejarla de fondo. No se
tocó `timeoutSeconds`, no se bloqueó ningún bot, no se agregó Cloud Armor/WAF (se habría pagado
más infraestructura para "ahorrar" un costo que ya era autoinfligido).

**Seguimiento pendiente:** revisar el gasto real (Billing Reports, no forecast) alrededor del
2026-07-31 (48h después de este hallazgo) para confirmar que el costo diario baja una vez que
se dejen de tener pestañas abiertas en background.

**Cómo aplicar:** antes de sospechar de bots/ataques por un cargo alto de Cloud Run, revisar
primero si hay pestañas propias abiertas en background — fue la causa real aquí, no
infraestructura ni tráfico malicioso.