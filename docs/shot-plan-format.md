# Shot plan format (schema version 1)

Shot plans are authored by Hermes or an operator after inspecting the source. The scaffold validates structure and timing; it does **not** automatically detect cuts or identify people.

```json
{
  "schema_version": 1,
  "source_sha256": "<SHA-256 from project.json>",
  "character_slots": [
    { "slot_id": "slot_01", "neutral_role": "main_subject", "notes": "blue jacket; left of frame" }
  ],
  "shots": [
    {
      "shot_id": "shot_001",
      "start_seconds": 0.0,
      "end_seconds": 3.25,
      "description": "Medium shot; subject turns toward camera",
      "character_slots": ["slot_01"],
      "camera": "mostly static",
      "occlusions": [],
      "uncertainties": ["left hand partly outside frame"]
    }
  ]
}
```

Run `hermes-video-studio validate-plan <project-dir> <plan.json>`. Validation checks schema version, source hash, unique IDs, numeric intervals, known character slots, and source-duration bounds when duration metadata is available. It does not verify the visual truth of descriptions or the presence of actual scene cuts.
