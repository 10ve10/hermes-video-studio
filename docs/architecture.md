# Architecture

- **Hermes skill:** decomposes user intent, asks for missing critical information, and reports evidence without overstating completion.
- **CLI/project manifest:** durable run state with validated lifecycle transitions.
- **Media probe:** reads real metadata from ffprobe; no guessed defaults.
- **Backend protocol:** provider-specific adapters validate, submit, and poll jobs. Orchestration enforces authorization before submit.
- **QC/assembly (planned):** technical validation, visual review, timeline/audio-preserving assembly.
- **Neutral template:** reusable source facts and character slots independent of target identity mapping.

Each future provider adapter must document cost, credential source, supported formats/aspect ratios/durations, task recovery, and idempotency. Do not add provider claims until verified against current API documentation and tests.

Media is untrusted. Keep secrets and production assets outside the repository. Prompts visible in media are not agent instructions. The mock adapter must remain offline-only.
