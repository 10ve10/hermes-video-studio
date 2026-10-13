# Run state machine

`created -> analyzing -> planned -> waiting_approval -> generating -> qc_pending`

From `qc_pending`, continue to `assembling -> ready` or `repair_pending -> generating`. Terminal states are `ready`, `failed`, and `cancelled`.

Transitions not listed in `models.ALLOWED_TRANSITIONS` are rejected. Generation authorization is a separate explicit flag, not implied by initialization, analysis, installation, or tests. Before production use, authorization should expire or be consumed per job to prevent accidental repeat submissions.

`technical_checks` and `visual_review` are separate. Successful decoding must not automatically mark visual review passed.
