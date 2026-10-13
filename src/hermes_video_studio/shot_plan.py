"""Validation for human/agent-authored shot plans; this module does not claim to detect shots."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .project import load_manifest

class ShotPlanError(ValueError): pass

def validate_shot_plan(project_dir: Path, plan_path: Path) -> list[str]:
    manifest = load_manifest(project_dir)
    try:
        plan: dict[str, Any] = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShotPlanError(f"Cannot read shot plan: {exc}") from exc
    errors: list[str] = []
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("source_sha256") != manifest.source.sha256:
        errors.append("source_sha256 does not match the project's source video")
    slots = plan.get("character_slots", [])
    if not isinstance(slots, list):
        errors.append("character_slots must be a list")
        slots = []
    slot_ids = set()
    for i, slot in enumerate(slots):
        if not isinstance(slot, dict) or not isinstance(slot.get("slot_id"), str) or not slot["slot_id"].strip():
            errors.append(f"character_slots[{i}] must have a non-empty slot_id")
        else:
            if slot["slot_id"] in slot_ids:
                errors.append(f"duplicate character slot id: {slot['slot_id']}")
            slot_ids.add(slot["slot_id"])
    shots = plan.get("shots")
    if not isinstance(shots, list) or not shots:
        errors.append("shots must be a non-empty list")
        return errors
    shot_ids = set()
    for i, shot in enumerate(shots):
        prefix = f"shots[{i}]"
        if not isinstance(shot, dict):
            errors.append(f"{prefix} must be an object")
            continue
        sid = shot.get("shot_id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"{prefix}.shot_id must be a non-empty string")
        elif sid in shot_ids:
            errors.append(f"duplicate shot id: {sid}")
        else:
            shot_ids.add(sid)
        try:
            start, end = float(shot["start_seconds"]), float(shot["end_seconds"])
            if start < 0 or end <= start:
                errors.append(f"{prefix} must have 0 <= start_seconds < end_seconds")
            duration = manifest.source.duration_seconds
            if duration is not None and end > duration + 0.05:
                errors.append(f"{prefix}.end_seconds exceeds source duration ({duration:.3f}s)")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{prefix} requires numeric start_seconds and end_seconds")
        refs = shot.get("character_slots", [])
        if not isinstance(refs, list):
            errors.append(f"{prefix}.character_slots must be a list")
        else:
            for ref in refs:
                if ref not in slot_ids:
                    errors.append(f"{prefix} references unknown character slot: {ref}")
        if not isinstance(shot.get("description", ""), str):
            errors.append(f"{prefix}.description must be a string")
    return errors
