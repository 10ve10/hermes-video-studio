from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

@dataclass(frozen=True)
class GenerationRequest:
    project_id: str
    source_path: Path
    target_slot: str
    identity_reference: Path
    start_seconds: float
    end_seconds: float
    prompt: str
    output_dir: Path

@dataclass(frozen=True)
class GenerationResult:
    provider: str
    task_id: str
    status: str
    output_path: Path | None = None
    message: str | None = None

class VideoBackend(Protocol):
    @property
    def name(self) -> str: ...
    def validate(self, request: GenerationRequest) -> list[str]: ...
    def submit(self, request: GenerationRequest) -> GenerationResult: ...
    def poll(self, task_id: str) -> GenerationResult: ...
