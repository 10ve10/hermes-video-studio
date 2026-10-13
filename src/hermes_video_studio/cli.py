import argparse, json, sys
from pathlib import Path
from .media import MediaProbeError, probe_media
from .models import RunStatus
from .project import create_project, load_manifest, save_manifest
from .shot_plan import ShotPlanError, validate_shot_plan
from .workflow import WorkflowError, authorize_generation, transition

def build_parser():
    parser = argparse.ArgumentParser(prog="hermes-video-studio", description="Hermes-native video production workflow")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create project manifest and working directories")
    init.add_argument("project_dir", type=Path); init.add_argument("--source", required=True, type=Path); init.add_argument("--title")
    inspect = sub.add_parser("inspect", help="Probe source metadata and show project manifest")
    inspect.add_argument("project_dir", type=Path)
    status = sub.add_parser("status", help="Show project state"); status.add_argument("project_dir", type=Path)
    move = sub.add_parser("transition", help="Change state with lifecycle validation")
    move.add_argument("project_dir", type=Path); move.add_argument("status", choices=[s.value for s in RunStatus]); move.add_argument("--note")
    validate = sub.add_parser("validate-plan", help="Validate an authored shot plan against this source project")
    validate.add_argument("project_dir", type=Path); validate.add_argument("plan_json", type=Path)
    auth = sub.add_parser("authorize-generation", help="Explicitly authorize potentially billable jobs")
    auth.add_argument("project_dir", type=Path); auth.add_argument("--confirm", action="store_true")
    return parser

def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            manifest = create_project(args.source, args.project_dir, args.title)
            print(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2)); return 0
        if args.command == "inspect":
            manifest = load_manifest(args.project_dir); manifest.source = probe_media(Path(manifest.source.path))
            save_manifest(args.project_dir, manifest)
            print(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2))
            if manifest.source.probe_status != "ok": print("NOTICE: ffprobe unavailable; metadata not inferred.", file=sys.stderr)
            return 0
        if args.command == "status":
            print(json.dumps(load_manifest(args.project_dir).to_dict(), ensure_ascii=False, indent=2)); return 0
        if args.command == "transition":
            print(transition(args.project_dir, RunStatus(args.status), args.note).status.value); return 0
        if args.command == "validate-plan":
            errors = validate_shot_plan(args.project_dir, args.plan_json)
            if errors:
                print("\\n".join(f"- {e}" for e in errors), file=sys.stderr); return 2
            print("shot plan valid"); return 0
        if args.command == "authorize-generation":
            authorize_generation(args.project_dir, confirmed=args.confirm); print("generation_authorized=true"); return 0
    except (OSError, ValueError, MediaProbeError, WorkflowError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 2
    return 1

if __name__ == "__main__": raise SystemExit(main())
