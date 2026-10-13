import tempfile, unittest
from pathlib import Path
from hermes_video_studio.backends.base import GenerationRequest
from hermes_video_studio.backends.mock import MockBackend

class MockBackendTests(unittest.TestCase):
    def test_mock_never_claims_video_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; identity=root/"identity.png"
            source.write_bytes(b"fixture"); identity.write_bytes(b"image fixture")
            request=GenerationRequest("test", source, "slot_01", identity, 0, 2, "prompt", root/"out")
            result=MockBackend().submit(request)
            self.assertEqual(result.status, "simulated")
            self.assertIsNone(result.output_path)
            self.assertIn("No network", result.message)
    def test_invalid_window_rejected(self):
        backend=MockBackend()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/"source.mp4"; identity=root/"identity.png"
            source.write_bytes(b"x"); identity.write_bytes(b"x")
            request=GenerationRequest("test", source, "slot", identity, 3, 1, "", root)
            self.assertTrue(backend.validate(request))

if __name__ == "__main__": unittest.main()
