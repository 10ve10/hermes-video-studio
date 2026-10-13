import json, tempfile, unittest
from pathlib import Path
from hermes_video_studio.project import create_project, load_manifest, save_manifest
from hermes_video_studio.shot_plan import validate_shot_plan

class ShotPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.source = root / "source.mp4"
        self.source.write_bytes(b"fixture")
        self.project = root / "project"
        manifest = create_project(self.source, self.project)
        manifest.source.duration_seconds = 10.0
        save_manifest(self.project, manifest)
        self.plan = root / "plan.json"
        self.data = {"schema_version": 1, "source_sha256": manifest.source.sha256,
                     "character_slots": [{"slot_id": "slot_01", "neutral_role": "main_subject"}],
                     "shots": [{"shot_id": "shot_001", "start_seconds": 0, "end_seconds": 3,
                                "description": "medium shot", "character_slots": ["slot_01"]}]}
    def tearDown(self): self.tmp.cleanup()
    def test_valid_plan(self):
        self.plan.write_text(json.dumps(self.data))
        self.assertEqual(validate_shot_plan(self.project, self.plan), [])
    def test_wrong_hash_and_unknown_slot(self):
        self.data["source_sha256"] = "wrong"
        self.data["shots"][0]["character_slots"] = ["missing"]
        self.plan.write_text(json.dumps(self.data))
        errors = validate_shot_plan(self.project, self.plan)
        self.assertTrue(any("source_sha256" in e for e in errors))
        self.assertTrue(any("unknown character slot" in e for e in errors))
    def test_out_of_bounds_interval(self):
        self.data["shots"][0]["end_seconds"] = 11
        self.plan.write_text(json.dumps(self.data))
        self.assertTrue(any("exceeds source duration" in e for e in validate_shot_plan(self.project, self.plan)))

if __name__ == "__main__": unittest.main()
