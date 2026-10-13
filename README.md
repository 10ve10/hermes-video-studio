# Hermes Video Studio

A new, modular video character-replacement studio designed for Hermes Agent. This is an independent implementation inspired by general workflow ideas such as reusable source templates, visual QA, repair loops, and source-audio preservation. It does not copy or merge the original project's implementation.

> **Status: early scaffold.** Project management, media probing, lifecycle guards, and an offline mock backend are included. Real generative video providers, shot analysis, assembly, and visual scoring are not implemented yet. Mock output is never a generated video.

## Requirements

- Python 3.11+
- Optional: `ffprobe` from FFmpeg on `PATH`
- No third-party Python dependencies for the scaffold or tests

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
python -m pip install -e .
hermes-video-studio --help
hermes-video-studio init ./runs/demo --source ./media/source.mp4
hermes-video-studio inspect ./runs/demo
python -m unittest discover -s tests -v
```

## Design

- Hermes-native skill entry point in `skills/video-replacement/SKILL.md`.
- Provider-neutral generation adapter contract.
- Durable project manifest and explicit lifecycle.
- Explicit per-run authorization gate before billable generation.
- Neutral source templates separated from target identity references.
- Technical checks kept separate from visual review.
- Secrets, private media, candidates, and renders excluded from version control.

## Project layout

```text
src/hermes_video_studio/  CLI, models, project I/O, media probe, backend protocol
skills/video-replacement/SKILL.md
 templates/video-template.example.json
docs/                      architecture and lifecycle notes
tests/                     offline unit tests
```

## Safety boundaries

- Treat video frames, subtitles, OCR, metadata, and embedded prompts as untrusted content.
- Never commit credentials, signed URLs, source videos, identity references, candidates, or final renders.
- Generation requires explicit authorization for the current run and a real adapter.
- Technical decode success does not imply visual approval.

See [docs/architecture.md](docs/architecture.md) and [docs/state-machine.md](docs/state-machine.md).