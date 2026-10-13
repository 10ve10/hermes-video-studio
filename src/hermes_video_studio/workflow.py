from pathlib import Path
from .models import ALLOWED_TRANSITIONS, ProjectManifest, RunStatus, utc_now
from .project import load_manifest, save_manifest

class WorkflowError(RuntimeError): pass

def transition(project_dir: Path, new_status: RunStatus, note: str | None = None) -> ProjectManifest:
    manifest = load_manifest(project_dir)
    if new_status not in ALLOWED_TRANSITIONS[manifest.status]:
        raise WorkflowError(f"Illegal transition: {manifest.status.value} -> {new_status.value}")
    previous = manifest.status.value
    manifest.status = new_status
    manifest.events.append({"at": utc_now(), "event": "status_changed", "from": previous, "to": new_status.value, "note": note})
    save_manifest(project_dir, manifest)
    return manifest

def authorize_generation(project_dir: Path, *, confirmed: bool) -> ProjectManifest:
    if not confirmed: raise WorkflowError("Generation authorization requires explicit confirmation.")
    manifest = load_manifest(project_dir)
    if manifest.status not in {RunStatus.WAITING_APPROVAL, RunStatus.REPAIR_PENDING}:
        raise WorkflowError(f"Cannot authorize generation while status is {manifest.status.value}")
    manifest.generation_authorized = True
    manifest.events.append({"at": utc_now(), "event": "generation_authorized"})
    save_manifest(project_dir, manifest)
    return manifest

def require_generation_authorization(manifest: ProjectManifest) -> None:
    if not manifest.generation_authorized:
        raise WorkflowError("Generation blocked: no explicit authorization for this run.")
