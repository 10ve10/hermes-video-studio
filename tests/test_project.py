import tempfile, unittest
from pathlib import Path
from hermes_video_studio.project import create_project, load_manifest
from hermes_video_studio.models import RunStatus
from hermes_video_studio.workflow import transition, WorkflowError, authorize_generation

class ProjectTests(unittest.TestCase):
    def test_create_and_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; source.write_bytes(b"fixture-not-a-video")
            project=root/"project"; created=create_project(source, project, "Test")
            loaded=load_manifest(project)
            self.assertEqual(created.project_id, loaded.project_id)
            self.assertEqual(loaded.source.size_bytes, len(b"fixture-not-a-video"))
            self.assertFalse(loaded.generation_authorized)
            self.assertEqual(loaded.status, RunStatus.CREATED)
    def test_nonempty_dir_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; source.write_bytes(b"x")
            project=root/"project"; project.mkdir(); (project/"keep.txt").write_text("keep")
            with self.assertRaises(FileExistsError): create_project(source, project)
    def test_invalid_transition_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; source.write_bytes(b"x"); project=root/"project"
            create_project(source, project)
            with self.assertRaises(WorkflowError): transition(project, RunStatus.GENERATING)
    def test_authorization_requires_confirm_and_valid_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; source.write_bytes(b"x"); project=root/"project"
            create_project(source, project)
            with self.assertRaises(WorkflowError): authorize_generation(project, confirmed=True)
            with self.assertRaises(WorkflowError): authorize_generation(project, confirmed=False)

if __name__ == "__main__": unittest.main()
