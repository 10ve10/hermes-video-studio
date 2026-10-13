from __future__ import annotations
import hashlib, json
from pathlib import Path
from .models import ProjectManifest, SourceMedia

MANIFEST_NAME = "project.json"
PROJECT_DIRS = ("analysis", "jobs", "qc", "templates", "reports")

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def create_project(source_path: Path, project_dir: Path, title: str | None = None) -> ProjectManifest:
    source_path, project_dir = source_path.expanduser().resolve(), project_dir.expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Source video does not exist: {source_path}")
    if project_dir.exists() and any(project_dir.iterdir()):
        raise FileExistsError(f"Project directory is not empty: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=True)
    for name in PROJECT_DIRS:
        (project_dir / name).mkdir(exist_ok=True)
    source = SourceMedia(str(source_path), sha256_file(source_path), source_path.stat().st_size)
    manifest = ProjectManifest.new(title or source_path.stem, source)
    save_manifest(project_dir, manifest)
    return manifest

def save_manifest(project_dir: Path, manifest: ProjectManifest) -> None:
    target = project_dir / MANIFEST_NAME
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)

def load_manifest(project_dir: Path) -> ProjectManifest:
    path = project_dir / MANIFEST_NAME
    if not path.is_file():
        raise FileNotFoundError(f"Missing {MANIFEST_NAME} in {project_dir}")
    return ProjectManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
