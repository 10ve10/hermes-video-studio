from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
import uuid

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class RunStatus(StrEnum):
    CREATED = "created"
    ANALYZING = "analyzing"
    PLANNED = "planned"
    WAITING_APPROVAL = "waiting_approval"
    GENERATING = "generating"
    QC_PENDING = "qc_pending"
    REPAIR_PENDING = "repair_pending"
    ASSEMBLING = "assembling"
    READY = "ready"
    FAILED = "failed"
    CANCELLED = "cancelled"

ALLOWED_TRANSITIONS = {
    RunStatus.CREATED: {RunStatus.ANALYZING, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.ANALYZING: {RunStatus.PLANNED, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.PLANNED: {RunStatus.WAITING_APPROVAL, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.WAITING_APPROVAL: {RunStatus.GENERATING, RunStatus.CANCELLED, RunStatus.FAILED},
    RunStatus.GENERATING: {RunStatus.QC_PENDING, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.QC_PENDING: {RunStatus.REPAIR_PENDING, RunStatus.ASSEMBLING, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.REPAIR_PENDING: {RunStatus.GENERATING, RunStatus.QC_PENDING, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.ASSEMBLING: {RunStatus.READY, RunStatus.FAILED, RunStatus.CANCELLED},
    RunStatus.READY: set(), RunStatus.FAILED: set(), RunStatus.CANCELLED: set(),
}

@dataclass
class StreamInfo:
    index: int
    codec_type: str
    codec_name: str | None = None
    width: int | None = None
    height: int | None = None
    sample_rate: int | None = None
    channels: int | None = None

@dataclass
class SourceMedia:
    path: str
    sha256: str
    size_bytes: int
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    display_aspect_ratio: str | None = None
    frame_rate: str | None = None
    streams: list[StreamInfo] = field(default_factory=list)
    probe_status: str = "not_probed"

@dataclass
class ProjectManifest:
    schema_version: int
    project_id: str
    title: str
    created_at: str
    source: SourceMedia
    status: RunStatus = RunStatus.CREATED
    generation_authorized: bool = False
    target_slots: list[dict[str, Any]] = field(default_factory=list)
    jobs: list[dict[str, Any]] = field(default_factory=list)
    technical_checks: dict[str, Any] = field(default_factory=dict)
    visual_review: dict[str, Any] = field(default_factory=lambda: {"status": "not_reviewed", "reviewed_by": None, "notes": []})
    events: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def new(cls, title: str, source: SourceMedia) -> "ProjectManifest":
        return cls(1, str(uuid.uuid4()), title, utc_now(), source, events=[{"at": utc_now(), "event": "project_created"}])

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectManifest":
        data = dict(data)
        src = dict(data["source"])
        src["streams"] = [StreamInfo(**s) for s in src.get("streams", [])]
        data["source"] = SourceMedia(**src)
        data["status"] = RunStatus(data.get("status", "created"))
        return cls(**data)
