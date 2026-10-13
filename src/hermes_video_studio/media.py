from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path
from .models import SourceMedia, StreamInfo
from .project import sha256_file

class MediaProbeError(RuntimeError): pass

def probe_media(path: Path) -> SourceMedia:
    path = path.expanduser().resolve()
    if not path.is_file(): raise FileNotFoundError(path)
    source = SourceMedia(str(path), sha256_file(path), path.stat().st_size)
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        source.probe_status = "unavailable_ffprobe"
        return source
    proc = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                          capture_output=True, text=True, check=False, timeout=60)
    if proc.returncode:
        raise MediaProbeError(proc.stderr.strip() or "ffprobe failed")
    data = json.loads(proc.stdout)
    try: source.duration_seconds = float(data.get("format", {})["duration"])
    except (KeyError, TypeError, ValueError): pass
    for item in data.get("streams", []):
        rate = item.get("sample_rate")
        stream = StreamInfo(index=int(item.get("index", len(source.streams))),
            codec_type=str(item.get("codec_type", "unknown")), codec_name=item.get("codec_name"),
            width=item.get("width"), height=item.get("height"),
            sample_rate=int(rate) if str(rate or "").isdigit() else None, channels=item.get("channels"))
        source.streams.append(stream)
        if stream.codec_type == "video" and source.width is None:
            source.width, source.height = stream.width, stream.height
            source.frame_rate = item.get("avg_frame_rate") or item.get("r_frame_rate")
            source.display_aspect_ratio = item.get("display_aspect_ratio")
    source.probe_status = "ok"
    return source
