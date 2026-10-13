from .base import GenerationRequest, GenerationResult

class MockBackend:
    """Offline-only test adapter. It never creates a video or contacts a provider."""
    @property
    def name(self) -> str: return "mock"

    def validate(self, request: GenerationRequest) -> list[str]:
        errors = []
        if request.end_seconds <= request.start_seconds: errors.append("end_seconds must be greater than start_seconds")
        if not request.target_slot.strip(): errors.append("target_slot is required")
        if not request.source_path.is_file(): errors.append("source video does not exist")
        if not request.identity_reference.is_file(): errors.append("identity reference does not exist")
        return errors

    def submit(self, request: GenerationRequest) -> GenerationResult:
        errors = self.validate(request)
        if errors: return GenerationResult(self.name, "not-submitted", "rejected", message="; ".join(errors))
        return GenerationResult(self.name, "mock-no-network", "simulated", None,
                                "No network request was made. No playable video was generated.")

    def poll(self, task_id: str) -> GenerationResult:
        if task_id != "mock-no-network": return GenerationResult(self.name, task_id, "unknown", message="Unknown mock task")
        return GenerationResult(self.name, task_id, "simulated", None, "Mock adapter never creates video.")
